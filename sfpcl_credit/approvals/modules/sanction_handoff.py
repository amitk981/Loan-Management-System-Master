"""Approval-owned persistence and read contract for sanction handoffs."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.approvals.modules import approval_case_engine
from sfpcl_credit.approvals.modules.conflict_of_interest import ConflictOfInterestModule
from sfpcl_credit.approvals.modules import exception_register
from sfpcl_credit.approvals.modules.approval_case_projection import (
    refresh_approval_case_projection,
)
from sfpcl_credit.approvals.modules.approval_matrix import resolve_approval_matrix
from sfpcl_credit.approvals.modules.sanction_committee import resolve_sanction_committee
from sfpcl_credit.applications import services as application_services
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
from sfpcl_credit.communications import services as communication_services
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainNotFound,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.models import User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.workflows.events import record_workflow_event


SANCTION_SUBMIT_PERMISSION = "credit.appraisal.submit_sanction"
CASE_CREATE_PERMISSION = "approvals.case.create"
EXCEPTION_CONDITION = "exceeds_permissible_limit"


@dataclass(frozen=True)
class SanctionHandoffResult:
    snapshot: dict


class SanctionHandoffModule:
    """Own immutable numbered sanction cycles and their public projection."""

    @transaction.atomic
    def submit_reviewed_appraisal(
        self,
        *,
        actor,
        application_id,
        payload,
        request_meta=None,
        actor_permissions=None,
    ):
        prepared = AppraisalWorkflow().prepare_sanction_handoff(
            actor=actor,
            application_id=application_id,
            payload=payload,
            actor_permissions=actor_permissions,
        )
        application = prepared.application
        appraisal_note = prepared.appraisal_note
        prior_cases = list(
            ApprovalCase.objects.select_for_update(of=("self",))
            .filter(loan_application=application)
            .order_by("cycle_number", "approval_case_id")
        )
        previous_case = prior_cases[-1] if prior_cases else None
        if previous_case is not None:
            if previous_case.current_status != ApprovalCase.STATUS_RETURNED:
                raise DomainInvalidStateError(
                    "Only a returned approval cycle can be resubmitted."
                )
            corrections = [
                audit
                for audit in AuditLog.objects.filter(
                        action="appraisal.updated",
                        entity_type="loan_appraisal_note",
                        entity_id=appraisal_note.pk,
                        created_at__gt=previous_case.closed_at,
                    ).order_by("-created_at", "-audit_log_id")
                if audit.new_value_json.get("changed_fields")
            ]
            if not corrections:
                raise DomainInvalidStateError(
                    "A returned appraisal must be corrected before resubmission."
                )
            latest_correction = corrections[0]
            if (
                previous_case.closed_at is None
                or prepared.latest_review.decided_at <= latest_correction.created_at
            ):
                raise DomainInvalidStateError(
                    "A fresh Credit Manager review is required before resubmission."
                )
        cycle_number = previous_case.cycle_number + 1 if previous_case else 1
        appraisal_revision = (
            previous_case.appraisal_revision + len(corrections)
            if previous_case
            else 1
        )
        now = timezone.now()
        case = ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=appraisal_note,
            appraisal_review_decision=prepared.latest_review,
            appraisal_revision=appraisal_revision,
            cycle_number=cycle_number,
            exception_required_flag=prepared.exception_required_flag,
            submission_remarks=payload["remarks"].strip(),
            submitted_by_user=actor,
            submitted_at=now,
        )
        refresh_approval_case_projection(case)
        application.application_status = LoanApplication.STATUS_SUBMITTED_TO_SANCTION
        application.save(update_fields=["application_status"])
        appraisal_note.appraisal_status = appraisal_note.STATUS_SUBMITTED_TO_SANCTION
        appraisal_note.save(update_fields=["appraisal_status"])
        request_meta = request_meta or {}
        AuditLog.objects.create(
            actor_user=actor,
            action="appraisal.submitted_to_sanction",
            entity_type="loan_appraisal_note",
            entity_id=appraisal_note.pk,
            old_value_json={
                "application_status": prepared.previous_application_status,
                "appraisal_status": prepared.previous_appraisal_status,
            },
            new_value_json={
                "approval_case_id": str(case.pk),
                "loan_application_id": str(application.pk),
                "loan_appraisal_note_id": str(appraisal_note.pk),
                "appraisal_review_decision_id": str(prepared.latest_review.pk),
                "application_status": application.application_status,
                "appraisal_status": appraisal_note.appraisal_status,
                "submission_status": case.current_status,
                "cycle_number": case.cycle_number,
                "exception_required_flag": prepared.exception_required_flag,
                "submitted_by_user_id": str(actor.pk),
                "submitted_at": timezone.localtime(now).isoformat(),
                "request_id": request_meta.get("request_id"),
            },
            ip_address=request_meta.get("ip_address", ""),
            user_agent=request_meta.get("user_agent", ""),
        )
        event = record_workflow_event(
            actor=actor,
            workflow_name="sanction_submission",
            entity_type="loan_application",
            entity_id=application.pk,
            from_state=prepared.previous_appraisal_status,
            to_state=appraisal_note.appraisal_status,
            trigger_reason=(
                f"Appraisal {appraisal_note.pk} submitted as approval case {case.pk} "
                f"from review decision {prepared.latest_review.pk}."
            ),
            action_code="appraisal.submitted_to_sanction",
            metadata={
                "approval_case_id": str(case.pk),
                "appraisal_review_decision_id": str(prepared.latest_review.pk),
            },
        )
        case.workflow_event = event
        case.save(update_fields=["workflow_event"])
        refresh_approval_case_projection(case)
        return SanctionHandoffResult(
            snapshot=self.serialize(case, prepared.latest_review)
        )

    def get_pending(self, *, actor, application_id, actor_permissions=None):
        application = LoanApplication.objects.filter(pk=application_id).first()
        if application is None:
            raise DomainNotFound("Loan application was not found.")
        object_access = application_services.evaluate_application_object_access(
            application,
            actor,
            SANCTION_SUBMIT_PERMISSION,
            actor_permissions,
        )
        if not object_access.allowed:
            raise DomainObjectAccessDenied(object_access)
        case = (
            ApprovalCase.objects.select_related(
                "loan_application",
                "loan_appraisal_note",
                "submitted_by_user",
            )
            .filter(
                loan_application=application,
                current_status=ApprovalCase.STATUS_PENDING,
            )
            .order_by("-cycle_number")
            .first()
        )
        if case is None:
            raise DomainNotFound("Pending sanction case was not found.")
        latest_review = case.appraisal_review_decision
        return SanctionHandoffResult(
            snapshot=self.serialize(case, latest_review)
        )

    @transaction.atomic
    def enrich_pending(
        self, *, actor, application_id, payload, request_meta=None, actor_permissions=None
    ):
        permissions = actor_permissions or auth_service.effective_permission_codes(actor)
        if CASE_CREATE_PERMISSION not in permissions:
            raise DomainPermissionDenied(
                "You do not have permission to create approval cases."
            )
        application = LoanApplication.objects.filter(pk=application_id).first()
        if application is None:
            raise DomainNotFound("Loan application was not found.")
        object_access = application_services.evaluate_application_object_access(
            application, actor, CASE_CREATE_PERMISSION, permissions
        )
        if not object_access.allowed:
            raise DomainObjectAccessDenied(object_access)
        facts = AppraisalWorkflow().prepare_approval_case_enrichment(
            application_id=application_id
        )
        case = (
            ApprovalCase.objects.select_for_update(of=("self",))
            .select_related("loan_appraisal_note", "workflow_event")
            .filter(loan_application=application)
            .order_by("-cycle_number")
            .first()
        )
        if case is None:
            raise DomainNotFound("Pending sanction case was not found.")
        normalized = self._validate_enrichment_payload(
            payload, facts.recommended_amount, facts.exception_required_flag
        )
        if case.current_status != ApprovalCase.STATUS_PENDING:
            raise DomainInvalidStateError("Only a pending approval case can be enriched.")
        if case.approval_matrix_rule_id is not None:
            if self._matches_enrichment(case, normalized, facts):
                return SanctionHandoffResult(
                    snapshot=self.serialize(case, facts.latest_review)
                )
            raise DomainInvalidStateError(
                "The approval case already has a different immutable routing snapshot."
            )
        condition_code = (
            EXCEPTION_CONDITION
            if normalized["force_exception_route"] or facts.exception_required_flag
            else None
        )
        matrix = resolve_approval_matrix(
            decision_type="loan_sanction",
            amount=facts.recommended_amount,
            condition_code=condition_code,
            decision_date=facts.decision_date,
        )
        committee = resolve_sanction_committee(facts.decision_date)
        required_approvers = self._required_approvers(matrix, committee)
        matrix_projection = {
            "approval_matrix_rule_id": str(matrix.approval_matrix_rule_id),
            "version_number": matrix.version_number,
            "decision_type": matrix.decision_type,
            "amount": f"{matrix.amount:.2f}",
            "amount_min": f"{matrix.amount_min:.2f}" if matrix.amount_min is not None else None,
            "amount_max": f"{matrix.amount_max:.2f}" if matrix.amount_max is not None else None,
            "condition_code": matrix.condition_code,
            "decision_date": matrix.decision_date.isoformat(),
            "required_approver_roles": list(matrix.required_approver_roles),
            "required_director_count": matrix.required_director_count,
            "joint_approval_required": matrix.joint_approval_required,
            "register_required": matrix.register_required,
        }
        committee_projection = {
            "sanction_committee_id": str(committee.sanction_committee_id),
            "version_number": committee.version_number,
            "decision_date": committee.decision_date.isoformat(),
            "cfo_user_id": str(committee.cfo_user_id),
            "director_user_ids": [
                str(committee.director_1_user_id), str(committee.director_2_user_id)
            ],
        }
        case.approval_matrix_rule_id = matrix.approval_matrix_rule_id
        case.approval_matrix_rule_version = matrix.version_number
        case.sanction_committee_id = committee.sanction_committee_id
        case.sanction_committee_version = committee.version_number
        case.required_approvers_json = required_approvers
        case.excluded_approvers_json = []
        case.amount = matrix.amount
        case.related_entity_type = "loan_application"
        case.related_entity_id = application.pk
        case.reason_for_approval = normalized["reason_for_approval"]
        case.exception_condition_code = condition_code or ""
        case.exception_reason = (
            normalized["business_reason"] if condition_code else ""
        )
        case.matrix_projection_json = matrix_projection
        case.committee_projection_json = committee_projection
        case.loan_limit_provenance_json = facts.loan_limit_provenance
        case.appraisal_facts_json = approval_case_engine.serialize_case_review_facts(
            case
        )
        conflict_assessment = ConflictOfInterestModule().evaluate_for_case(case)
        case.excluded_approvers_json = list(conflict_assessment.exclusions)
        case.general_meeting_evidence_required = (
            conflict_assessment.general_meeting_evidence_required
        )
        if not ConflictOfInterestModule.authority_is_satisfiable(case):
            case.current_status = ApprovalCase.STATUS_BLOCKED_CONFLICT
            case.conflict_block_reason = (
                ConflictOfInterestModule.authority_gap_reason(case)
            )
            case.closed_at = timezone.now()
        case.decision_date = facts.decision_date
        case.version += 1
        case.save(update_fields=[
            "approval_matrix_rule", "approval_matrix_rule_version",
            "sanction_committee", "sanction_committee_version",
            "required_approvers_json", "excluded_approvers_json", "amount",
            "related_entity_type", "related_entity_id", "reason_for_approval",
            "exception_condition_code", "exception_reason", "matrix_projection_json",
            "committee_projection_json", "loan_limit_provenance_json", "decision_date",
            "appraisal_facts_json", "general_meeting_evidence_required",
            "current_status", "conflict_block_reason", "closed_at", "version",
        ])
        refresh_approval_case_projection(case)
        request_meta = request_meta or {}
        if condition_code:
            exception_register.create_for_case(
                actor=actor,
                case=case,
                exception_type=normalized["exception_type"],
                business_reason=normalized["business_reason"],
                risk_assessment=normalized["risk_assessment"],
                actor_permissions=permissions,
                request_meta=request_meta,
            )
        AuditLog.objects.create(
            actor_user=actor,
            action="approval_case.enriched",
            entity_type="approval_case",
            entity_id=case.pk,
            old_value_json={"version": case.version - 1, "routed": False},
            new_value_json={
                "version": case.version,
                "approval_matrix_rule_id": str(case.approval_matrix_rule_id),
                "sanction_committee_id": str(case.sanction_committee_id),
                "request_id": request_meta.get("request_id"),
            },
            ip_address=request_meta.get("ip_address", ""),
            user_agent=request_meta.get("user_agent", ""),
        )
        record_workflow_event(
            actor=actor,
            workflow_name="approval_case_enrichment",
            entity_type="approval_case",
            entity_id=case.pk,
            from_state="unrouted",
            to_state="routed",
            trigger_reason=f"Approval case {case.pk} received its immutable authority snapshot.",
            action_code="approval_case.enriched",
        )
        if case.current_status == ApprovalCase.STATUS_BLOCKED_CONFLICT:
            communication_services.create_internal_team_communication(
                sender=actor,
                team_code="credit_assessment",
                related_entity_type="approval_case",
                related_entity_id=case.pk,
                subject="Sanction approval blocked by conflict",
                body=case.conflict_block_reason,
                action_label="Open approval case",
                action_url=f"/sanctions/{case.pk}",
                request_meta=request_meta,
            )
        return SanctionHandoffResult(snapshot=self.serialize(case, facts.latest_review))

    @staticmethod
    def _validate_enrichment_payload(
        payload, recommended_amount, assessment_requires_exception
    ):
        allowed = {
            "approval_type",
            "amount",
            "reason_for_approval",
            "force_exception_route",
            "business_reason",
            "risk_assessment",
            "exception_type",
        }
        errors = {key: "Unknown field." for key in sorted(set(payload) - allowed)}
        if payload.get("approval_type") != ApprovalCase.TYPE_SANCTION:
            errors["approval_type"] = "Must be sanction."
        try:
            amount = Decimal(str(payload.get("amount")))
        except (InvalidOperation, TypeError, ValueError):
            amount = None
            errors["amount"] = "Must be a valid amount."
        if amount is not None and amount != recommended_amount:
            errors["amount"] = "Must match the reviewed appraisal recommendation."
        reason = payload.get("reason_for_approval")
        if not isinstance(reason, str) or not reason.strip():
            errors["reason_for_approval"] = "This field must not be blank."
        forced = payload.get("force_exception_route")
        if not isinstance(forced, bool):
            errors["force_exception_route"] = "Must be a boolean."
        exception_requested = forced is True or assessment_requires_exception
        supplied_exception_type = payload.get("exception_type")
        exception_type = None
        if supplied_exception_type is not None:
            try:
                exception_type = exception_register.validate_exception_type(
                    supplied_exception_type
                )
            except ValidationError:
                errors["exception_type"] = "Unknown exception type."
        if assessment_requires_exception:
            if exception_type not in (None, "exceeds_loan_limit"):
                errors["exception_type"] = (
                    "A frozen loan-limit exception must use exceeds_loan_limit."
                )
            exception_type = "exceeds_loan_limit"
        elif forced is True and exception_type not in {"stage_bypass", "waiver"}:
            errors["exception_type"] = (
                "A forced within-limit exception must use stage_bypass or waiver."
            )
        elif not exception_requested and supplied_exception_type is not None:
            errors["exception_type"] = "This field is only valid for an exception route."
        business_reason = payload.get("business_reason")
        if exception_requested and (
            not isinstance(business_reason, str) or not business_reason.strip()
        ):
            errors["business_reason"] = "This field must not be blank."
        risk_assessment = payload.get("risk_assessment")
        if risk_assessment is not None and not isinstance(risk_assessment, str):
            errors["risk_assessment"] = "Must be a string."
        if errors:
            from sfpcl_credit.domain_errors import DomainValidationError
            raise DomainValidationError(errors)
        return {
            "approval_type": ApprovalCase.TYPE_SANCTION,
            "amount": amount,
            "reason_for_approval": reason.strip(),
            "force_exception_route": forced,
            "business_reason": (
                business_reason.strip()
                if isinstance(business_reason, str) and business_reason.strip()
                else None
            ),
            "risk_assessment": (
                risk_assessment.strip()
                if isinstance(risk_assessment, str) and risk_assessment.strip()
                else None
            ),
            "exception_type": exception_type,
        }

    @staticmethod
    def _required_approvers(matrix, committee):
        users = User.objects.in_bulk(
            [committee.cfo_user_id, committee.director_1_user_id, committee.director_2_user_id]
        )
        approvers = []
        for role in matrix.required_approver_roles:
            if role == "cfo":
                ids = [committee.cfo_user_id]
            elif role == "director":
                ids = [committee.director_1_user_id, committee.director_2_user_id][
                    : matrix.required_director_count
                ]
            else:
                raise DomainInvalidStateError("The matrix contains an unsupported approver role.")
            approvers.extend(
                {"role_code": role, "user_id": str(user_id), "full_name": users[user_id].full_name}
                for user_id in ids
            )
        return approvers

    @staticmethod
    def _matches_enrichment(case, normalized, facts):
        expected_exception = (
            normalized["force_exception_route"]
            or facts.exception_required_flag
        )
        return (
            case.approval_type == normalized["approval_type"]
            and case.amount == normalized["amount"]
            and case.amount == facts.recommended_amount
            and case.reason_for_approval == normalized["reason_for_approval"]
            and bool(case.exception_condition_code) == expected_exception
            and case.exception_reason == (
                normalized["business_reason"] if expected_exception else ""
            )
            and (
                not expected_exception
                or (
                    hasattr(case, "exception_register_entry")
                    and case.exception_register_entry.exception_type
                    == normalized["exception_type"]
                    and case.exception_register_entry.risk_assessment
                    == normalized["risk_assessment"]
                )
            )
            and case.exception_required_flag == facts.exception_required_flag
            and case.decision_date == facts.decision_date
            and case.loan_application_id == facts.application.pk
            and case.related_entity_id == facts.application.pk
            and case.loan_appraisal_note_id == facts.appraisal_note.pk
            and case.loan_limit_provenance_json == facts.loan_limit_provenance
        )

    @staticmethod
    def serialize(case, latest_review_decision):
        snapshot = {
            "approval_case_id": str(case.pk),
            "cycle_number": case.cycle_number,
            "loan_application_id": str(case.loan_application_id),
            "loan_appraisal_note_id": str(case.loan_appraisal_note_id),
            "appraisal_review_decision_id": (
                str(case.appraisal_review_decision_id)
                if case.appraisal_review_decision_id
                else (str(latest_review_decision.pk) if latest_review_decision else None)
            ),
            "workflow_event_id": str(case.workflow_event_id) if case.workflow_event_id else None,
            "application_status": case.loan_application.application_status,
            "appraisal_status": case.loan_appraisal_note.appraisal_status,
            "submission_status": case.current_status,
            "exception_required_flag": case.exception_required_flag,
            "submitted_by": {
                "user_id": str(case.submitted_by_user_id),
                "full_name": case.submitted_by_user.full_name,
            },
            "submitted_at": timezone.localtime(case.submitted_at).isoformat(),
            "available_actions": [],
        }
        if case.approval_matrix_rule_id is not None:
            snapshot.update(approval_case_engine.serialize_case_snapshot(case))
            snapshot["required_approvers"] = case.required_approvers_json
        return snapshot
