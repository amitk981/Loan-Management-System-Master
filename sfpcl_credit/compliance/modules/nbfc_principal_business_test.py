import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db import IntegrityError, transaction

from sfpcl_credit.compliance.models import (
    ComplianceEvidence,
    ComplianceTask,
    NbfcPrincipalBusinessTest,
)
from sfpcl_credit.compliance.modules.compliance_control_tracker import (
    ComplianceConflict,
    ComplianceDenied,
    ComplianceInvalid,
    ComplianceMissing,
    permission_codes,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.documents.models import DocumentFile


class NbfcPrincipalBusinessTestModule:
    CREATE_PERMISSION = "compliance.nbfc_test.create"
    READ_PERMISSION = "compliance.nbfc_test.read"
    REVIEW_PERMISSION = "compliance.evidence.review"
    MONEY_QUANTUM = Decimal("0.01")
    RATIO_QUANTUM = Decimal("0.0001")
    STATUTORY_THRESHOLD = Decimal("50.0000")

    @classmethod
    def calculate(cls, *, actor, period_id, payload):
        if cls.CREATE_PERMISSION not in permission_codes(actor):
            raise ComplianceDenied()
        financial_year, quarter, task, evidence = cls._context(
            actor=actor, period_id=period_id, payload=payload
        )
        amounts = {
            field: cls._amount(payload, field)
            for field in (
                "financial_assets_amount",
                "total_assets_amount",
                "financial_income_amount",
                "gross_income_amount",
            )
        }
        for field in ("total_assets_amount", "gross_income_amount"):
            if amounts[field] == 0:
                raise ComplianceInvalid({field: "Denominator must be greater than zero."})
        threshold = cls._ratio(payload, "early_warning_threshold_ratio")
        if threshold > cls.STATUTORY_THRESHOLD:
            raise ComplianceInvalid(
                {"early_warning_threshold_ratio": "Threshold cannot exceed 50%."}
            )
        input_snapshot = {
            "financial_year": financial_year,
            "quarter": quarter,
            **{field: str(value) for field, value in amounts.items()},
            "early_warning_threshold_ratio": str(threshold),
            "compliance_task_id": str(task.pk),
            "compliance_evidence_id": str(evidence.pk),
        }
        existing = NbfcPrincipalBusinessTest.objects.filter(
            financial_year=financial_year, quarter=quarter
        ).first()
        if existing is not None:
            return cls._replay(existing, input_snapshot)

        raw_asset_ratio = (
            amounts["financial_assets_amount"]
            / amounts["total_assets_amount"]
            * Decimal("100")
        )
        raw_income_ratio = (
            amounts["financial_income_amount"]
            / amounts["gross_income_amount"]
            * Decimal("100")
        )
        asset_ratio = raw_asset_ratio.quantize(cls.RATIO_QUANTUM, rounding=ROUND_HALF_UP)
        income_ratio = raw_income_ratio.quantize(cls.RATIO_QUANTUM, rounding=ROUND_HALF_UP)
        asset_over = raw_asset_ratio > cls.STATUTORY_THRESHOLD
        income_over = raw_income_ratio > cls.STATUTORY_THRESHOLD
        result_snapshot = {
            "financial_asset_ratio": str(asset_ratio),
            "financial_income_ratio": str(income_ratio),
            "registration_triggered_flag": asset_over and income_over,
            "one_ratio_above_statutory_flag": asset_over != income_over,
            "early_warning_flag": raw_asset_ratio >= threshold or raw_income_ratio >= threshold,
        }
        values = {
            **amounts,
            "financial_asset_ratio": asset_ratio,
            "financial_income_ratio": income_ratio,
            "early_warning_threshold_ratio": threshold,
            **{
                key: value
                for key, value in result_snapshot.items()
                if key.endswith("_flag")
            },
            "task": task,
            "evidence": evidence,
            "prepared_by_user": actor,
            "reviewer_user": task.reviewer_user,
            "input_snapshot_json": input_snapshot,
            "result_snapshot_json": result_snapshot,
            "reviewer_snapshot_json": {
                "reviewer_user_id": str(task.reviewer_user_id),
                "role_code": task.reviewer_user.primary_role.role_code,
            },
            "evidence_snapshot_json": {
                "compliance_evidence_id": str(evidence.pk),
                "document_id": str(evidence.document_id),
                "review_status": evidence.review_status,
                "source_period": evidence.source_period,
            },
        }
        try:
            with transaction.atomic():
                row = NbfcPrincipalBusinessTest.objects.create(
                    financial_year=financial_year,
                    quarter=quarter,
                    **values,
                )
                cls._audit(actor, row)
        except IntegrityError as exc:
            existing = NbfcPrincipalBusinessTest.objects.filter(
                financial_year=financial_year, quarter=quarter
            ).first()
            if existing is not None:
                return cls._replay(existing, input_snapshot)
            raise exc
        return row

    @classmethod
    def retrieve(cls, *, actor, result_id):
        if cls.READ_PERMISSION not in permission_codes(actor):
            raise ComplianceDenied()
        try:
            row = NbfcPrincipalBusinessTest.objects.select_related(
                "task", "evidence", "prepared_by_user", "reviewer_user"
            ).get(pk=result_id)
        except (NbfcPrincipalBusinessTest.DoesNotExist, ValueError, TypeError) as exc:
            raise ComplianceMissing() from exc
        return cls.serialize(row, actor)

    @classmethod
    def submit_for_review(cls, *, actor, result_id):
        if cls.CREATE_PERMISSION not in permission_codes(actor):
            raise ComplianceDenied()
        try:
            with transaction.atomic():
                row = NbfcPrincipalBusinessTest.objects.select_for_update().get(pk=result_id)
                if row.prepared_by_user_id != actor.pk:
                    raise ComplianceDenied()
                if row.review_decision:
                    raise ComplianceConflict("NBFC principal test review is already final.")
                if row.submitted_for_review_at is None:
                    from django.utils import timezone

                    row.submitted_for_review_at = timezone.now()
                    row.save(update_fields=["submitted_for_review_at"])
                    cls._audit(
                        actor, row, action="compliance.nbfc_test.submitted_for_review"
                    )
        except NbfcPrincipalBusinessTest.DoesNotExist as exc:
            raise ComplianceMissing() from exc
        return cls.serialize(row, actor)

    @classmethod
    def review(
        cls, *, actor, result_id, decision, comments, presented_to_board_flag,
        board_document_id=None,
    ):
        if cls.REVIEW_PERMISSION not in permission_codes(actor):
            raise ComplianceDenied()
        decision = str(decision or "").strip().lower()
        comments = str(comments or "").strip()
        if decision not in {"accepted", "rejected"}:
            raise ComplianceInvalid({"decision": "Use accepted or rejected."})
        if not comments:
            raise ComplianceInvalid({"comments": "Review comments are required."})
        if not isinstance(presented_to_board_flag, bool):
            raise ComplianceInvalid(
                {"presented_to_board_flag": "Must be true or false."}
            )
        try:
            with transaction.atomic():
                row = NbfcPrincipalBusinessTest.objects.select_for_update().get(pk=result_id)
                if row.reviewer_user_id != actor.pk or row.prepared_by_user_id == actor.pk:
                    raise ComplianceDenied()
                if row.submitted_for_review_at is None:
                    raise ComplianceInvalid(
                        {"result_id": "Test must be submitted for review first."}
                    )
                if row.review_decision:
                    raise ComplianceConflict("NBFC principal test review is already final.")
                board_document, board_snapshot = cls._board_evidence(
                    actor=actor,
                    document_id=board_document_id,
                    required=(
                        presented_to_board_flag
                        or (decision == "accepted" and row.registration_triggered_flag)
                    ),
                )
                if decision == "accepted" and row.registration_triggered_flag and not presented_to_board_flag:
                    raise ComplianceInvalid(
                        {"presented_to_board_flag": "Triggered test requires Board presentation."}
                    )
                from django.utils import timezone

                row.review_decision = decision
                row.review_comments = comments
                row.presented_to_board_flag = presented_to_board_flag
                row.board_document = board_document
                row.board_evidence_snapshot_json = board_snapshot
                row.reviewed_at = timezone.now()
                row.save(
                    update_fields=[
                        "review_decision",
                        "review_comments",
                        "presented_to_board_flag",
                        "board_document",
                        "board_evidence_snapshot_json",
                        "reviewed_at",
                    ]
                )
                cls._audit(actor, row, action="compliance.nbfc_test.reviewed")
        except NbfcPrincipalBusinessTest.DoesNotExist as exc:
            raise ComplianceMissing() from exc
        return cls.serialize(row, actor)

    @classmethod
    def serialize(cls, row, actor):
        permissions = permission_codes(actor)
        available_actions = []
        if (
            not row.review_decision
            and row.submitted_for_review_at is None
            and row.prepared_by_user_id == actor.pk
            and cls.CREATE_PERMISSION in permissions
        ):
            available_actions.append("submit_for_review")
        if (
            not row.review_decision
            and row.submitted_for_review_at is not None
            and row.reviewer_user_id == actor.pk
            and cls.REVIEW_PERMISSION in permissions
        ):
            available_actions.append("review")
        return {
            "nbfc_principal_test_id": str(row.pk),
            "financial_year": row.financial_year,
            "quarter": row.quarter,
            "financial_assets_amount": f"{row.financial_assets_amount:.2f}",
            "total_assets_amount": f"{row.total_assets_amount:.2f}",
            "financial_asset_ratio": f"{row.financial_asset_ratio:.4f}",
            "financial_income_amount": f"{row.financial_income_amount:.2f}",
            "gross_income_amount": f"{row.gross_income_amount:.2f}",
            "financial_income_ratio": f"{row.financial_income_ratio:.4f}",
            "early_warning_threshold_ratio": f"{row.early_warning_threshold_ratio:.4f}",
            "registration_triggered_flag": row.registration_triggered_flag,
            "one_ratio_above_statutory_flag": row.one_ratio_above_statutory_flag,
            "early_warning_flag": row.early_warning_flag,
            "presented_to_board_flag": row.presented_to_board_flag,
            "compliance_task_id": str(row.task_id),
            "compliance_evidence_id": str(row.evidence_id),
            "prepared_by_user_id": str(row.prepared_by_user_id),
            "reviewer_user_id": str(row.reviewer_user_id),
            "prepared_at": row.prepared_at.isoformat(),
            "reviewed_at": row.reviewed_at.isoformat() if row.reviewed_at else None,
            "submitted_for_review_at": (
                row.submitted_for_review_at.isoformat()
                if row.submitted_for_review_at else None
            ),
            "review_status": (
                row.review_decision
                or ("pending" if row.submitted_for_review_at else "draft")
            ),
            "review_comments": row.review_comments,
            "board_document_id": str(row.board_document_id) if row.board_document_id else None,
            "available_actions": available_actions,
        }

    @staticmethod
    def _board_evidence(*, actor, document_id, required):
        if document_id is None:
            if required:
                raise ComplianceInvalid(
                    {"board_document_id": "Governed Board evidence is required."}
                )
            return None, {}
        try:
            document = DocumentFile.objects.get(pk=document_id)
        except (DocumentFile.DoesNotExist, ValueError, TypeError) as exc:
            raise ComplianceInvalid(
                {"board_document_id": "Governed Board evidence was not found."}
            ) from exc
        if (
            document.sensitivity_level != DocumentFile.SENSITIVITY_RESTRICTED
            or document.uploaded_by_user_id != actor.pk
        ):
            raise ComplianceInvalid(
                {"board_document_id": "Current reviewer-owned restricted Board evidence is required."}
            )
        return document, {
            "board_document_id": str(document.pk),
            "file_name": document.file_name,
            "sensitivity_level": document.sensitivity_level,
        }

    @classmethod
    def _context(cls, *, actor, period_id, payload):
        allowed = {
            "financial_year",
            "quarter",
            "financial_assets_amount",
            "total_assets_amount",
            "financial_income_amount",
            "gross_income_amount",
            "early_warning_threshold_ratio",
            "compliance_evidence_id",
        }
        unknown = set(payload) - allowed
        if unknown:
            raise ComplianceInvalid(
                {field: "Derived and review values are server-owned." for field in unknown}
            )
        financial_year = str(payload.get("financial_year") or "").strip()
        quarter = str(payload.get("quarter") or "").strip()
        match = re.fullmatch(r"FY(\d{4})-(\d{2})", financial_year)
        if match is None or int(match.group(2)) != (int(match.group(1)) + 1) % 100:
            raise ComplianceInvalid({"financial_year": "Use FYyyyy-yy with consecutive years."})
        if quarter not in {"Q1", "Q2", "Q3", "Q4"}:
            raise ComplianceInvalid({"quarter": "Use Q1, Q2, Q3, or Q4."})
        try:
            task = ComplianceTask.objects.select_related(
                "control", "reviewer_user__primary_role"
            ).get(pk=period_id)
        except (ComplianceTask.DoesNotExist, ValueError, TypeError) as exc:
            raise ComplianceInvalid({"period_id": "Quarterly compliance task was not found."}) from exc
        expected_period = (
            f"{int(match.group(1)) + (int(quarter[1]) >= 4)}-"
            f"Q{(int(quarter[1]) % 4) + 1}"
        )
        if (
            task.control.control_code != "NBFC_PRINCIPAL_TEST"
            or task.control.frequency != "quarterly"
            or task.task_period != expected_period
        ):
            raise ComplianceInvalid({"period_id": "Task does not match the NBFC test period."})
        if task.assigned_to_user_id != actor.pk:
            raise ComplianceDenied()
        try:
            evidence = ComplianceEvidence.objects.select_related("document").get(
                pk=payload.get("compliance_evidence_id"), task=task
            )
        except (ComplianceEvidence.DoesNotExist, ValueError, TypeError) as exc:
            raise ComplianceInvalid(
                {"compliance_evidence_id": "Matching governed task evidence is required."}
            ) from exc
        if (
            task.current_evidence_id != evidence.pk
            or evidence.review_status != ComplianceEvidence.REVIEW_ACCEPTED
            or evidence.source_period != task.task_period
        ):
            raise ComplianceInvalid(
                {"compliance_evidence_id": "Current accepted period evidence is required."}
            )
        if task.reviewer_user_id == actor.pk:
            raise ComplianceInvalid({"period_id": "Test maker and reviewer must differ."})
        return financial_year, quarter, task, evidence

    @classmethod
    def _amount(cls, payload, field):
        try:
            value = Decimal(str(payload.get(field))).quantize(
                cls.MONEY_QUANTUM, rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ComplianceInvalid({field: "Use a decimal amount."}) from exc
        if not value.is_finite():
            raise ComplianceInvalid({field: "Use a finite decimal amount."})
        if value < 0:
            raise ComplianceInvalid({field: "Amount cannot be negative."})
        if len(value.as_tuple().digits) > 18:
            raise ComplianceInvalid({field: "Amount exceeds the supported precision."})
        return value

    @classmethod
    def _ratio(cls, payload, field):
        try:
            value = Decimal(str(payload.get(field))).quantize(
                cls.RATIO_QUANTUM, rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ComplianceInvalid({field: "Use a decimal percentage."}) from exc
        if not value.is_finite():
            raise ComplianceInvalid({field: "Use a finite decimal percentage."})
        if value < 0:
            raise ComplianceInvalid({field: "Threshold cannot be negative."})
        return value

    @staticmethod
    def _replay(existing, input_snapshot):
        if existing.input_snapshot_json != input_snapshot:
            raise ComplianceConflict("Changed NBFC period replay was rejected.")
        return existing

    @staticmethod
    def _audit(actor, row, action="compliance.nbfc_test.created"):
        values = {
            "actor_role_code": actor.primary_role.role_code,
            "input_snapshot": row.input_snapshot_json,
            "result_snapshot": row.result_snapshot_json,
            "reviewer_snapshot": row.reviewer_snapshot_json,
            "evidence_snapshot": row.evidence_snapshot_json,
        }
        if action.endswith("reviewed"):
            values.update(
                {
                    "decision": row.review_decision,
                    "comments": row.review_comments,
                    "reviewed_at": row.reviewed_at.isoformat(),
                    "presented_to_board_flag": row.presented_to_board_flag,
                    "board_document_id": (
                        str(row.board_document_id) if row.board_document_id else None
                    ),
                    "board_evidence_snapshot": row.board_evidence_snapshot_json,
                }
            )
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action=action,
            entity_type="nbfc_principal_test",
            entity_id=row.pk,
            new_value_json=values,
        )


__all__ = ["NbfcPrincipalBusinessTestModule"]
