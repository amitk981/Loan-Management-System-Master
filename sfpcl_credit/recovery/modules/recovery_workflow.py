from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.approvals.modules.recovery_handoff import (
    RecoveryApprovalRouteUnavailable,
    create_or_reuse_recovery_case,
)
from sfpcl_credit.defaults.models import DefaultCase, NonPaymentNote
from sfpcl_credit.defaults.modules.default_workflow import _scoped_case_candidates
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.modules.non_payment_note_document import (
    generate_non_payment_note_document,
)
from sfpcl_credit.workflows.events import record_workflow_event


CREATE_PERMISSION = "defaults.non_payment_note.create"
SUBMIT_PERMISSION = "defaults.non_payment_note.submit"


class RecoveryValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class RecoveryPermissionDenied(Exception):
    pass


class RecoveryNotFound(Exception):
    pass


class RecoveryConflict(Exception):
    pass


class RecoveryWorkflow:
    @classmethod
    def create_non_payment_note(
        cls, *, actor, default_case_id, payload, request=None
    ):
        _require_creator(actor)
        cleaned = _validate_create_payload(payload)
        scoped_case_ids = _scoped_case_candidates(actor=actor).values("pk")
        with transaction.atomic():
            row = (
                DefaultCase.objects.select_for_update(of=("self", "loan_account"))
                .select_related("loan_account")
                .filter(pk=default_case_id, pk__in=scoped_case_ids)
                .first()
            )
            if row is None:
                raise RecoveryNotFound
            existing = NonPaymentNote.objects.filter(default_case=row).first()
            if existing is not None:
                if _create_replay_matches(existing, cleaned):
                    return existing
                if (
                    existing.status == NonPaymentNote.STATUS_SUBMITTED
                    and existing.approval_case_id is not None
                    and existing.approval_case.current_status == "returned_for_clarification"
                ):
                    return _correct_returned_note(
                        note=existing,
                        row=row,
                        actor=actor,
                        cleaned=cleaned,
                        request=request,
                    )
                raise RecoveryConflict(
                    "The default case already has a different Non-Payment Note."
                )
            extension = row.extension_note
            assessment = row.current_assessment
            account = row.loan_account
            if (
                row.default_case_status != "extension_expired"
                or extension is None
                or extension.status != extension.STATUS_EXPIRED
                or assessment is None
                or account.principal_outstanding <= 0
                or account.closed_at is not None
            ):
                raise RecoveryConflict(
                    "Only an open, unpaid case after extension expiry is eligible."
                )
            canonical_principal = account.principal_outstanding.quantize(Decimal("0.01"))
            canonical_interest = account.interest_outstanding.quantize(Decimal("0.01"))
            amount_errors = {}
            if cleaned["outstanding_principal_amount"] != canonical_principal:
                amount_errors["outstanding_principal_amount"] = (
                    "Must match the current canonical servicing balance."
                )
            if cleaned["outstanding_interest_amount"] != canonical_interest:
                amount_errors["outstanding_interest_amount"] = (
                    "Must match the current canonical servicing balance."
                )
            if amount_errors:
                raise RecoveryValidation(amount_errors)
            frozen_case_facts = {
                "borrower_name": row.member.display_name or row.member.legal_name,
                "original_due_date": row.scheduled_due_date.isoformat(),
                "grace_period_start_date": row.grace_period_start_date.isoformat(),
                "grace_period_end_date": row.grace_period_end_date.isoformat(),
                "extension_start_date": extension.extension_start_date.isoformat(),
                "extension_end_date": extension.extension_end_date.isoformat(),
                "extension_reason": extension.extension_reason,
                "extension_status": extension.status,
                "grace_outcome_summary": "Grace period expired unpaid.",
                "extension_outcome_summary": "One-year extension expired unpaid.",
                "current_assessment_id": str(assessment.pk),
                "assessment_type": assessment.assessment_type,
                "prior_payment_failure_classification": (
                    assessment.payment_failure_classification
                ),
                "assessment_reason_summary": assessment.reason_summary,
                "assessment_recommended_action": assessment.recommended_action,
                "prepared_by_user_id": str(actor.pk),
                "prepared_by_name": actor.full_name,
            }
            note_id = uuid4()
            loan_document = generate_non_payment_note_document(
                note_id=note_id,
                loan_application_id=account.loan_application_id,
                actor=actor,
                facts={
                    "default_case_id": str(row.pk),
                    "loan_account_id": str(account.pk),
                    "borrower_name": row.member.display_name or row.member.legal_name,
                    "original_due_date": row.scheduled_due_date.isoformat(),
                    "grace_period_end_date": row.grace_period_end_date.isoformat(),
                    "extension_end_date": extension.extension_end_date.isoformat(),
                    "grace_outcome_summary": "Grace period expired unpaid.",
                    "extension_outcome_summary": "One-year extension expired unpaid.",
                    "extension_reason": extension.extension_reason,
                    "source_assessment_classification": assessment.payment_failure_classification,
                    "source_assessment_reason": assessment.reason_summary,
                    "outstanding_principal_amount": f"{canonical_principal:.2f}",
                    "outstanding_interest_amount": f"{canonical_interest:.2f}",
                    "intentionality_assessment": cleaned["intentionality_assessment"],
                    "reason_for_non_payment": cleaned["reason_for_non_payment"],
                    "recommended_recovery_action": cleaned[
                        "recommended_recovery_action"
                    ],
                    "evidence_document_ids": list(assessment.evidence_document_ids_json),
                    "prepared_by": actor.full_name,
                    "reviewed_by": "Pending Credit Manager review",
                    "submitted_at": "Not submitted",
                },
            )
            note = NonPaymentNote.objects.create(
                non_payment_note_id=note_id,
                default_case=row,
                loan_account=account,
                extension_note=extension,
                current_assessment=assessment,
                prepared_by_user=actor,
                reason_for_non_payment=cleaned["reason_for_non_payment"],
                intentionality_assessment=cleaned["intentionality_assessment"],
                outstanding_principal_amount=canonical_principal,
                outstanding_interest_amount=canonical_interest,
                recommended_recovery_action=cleaned[
                    "recommended_recovery_action"
                ],
                evidence_document_ids_json=list(assessment.evidence_document_ids_json),
                frozen_case_facts_json=frozen_case_facts,
                loan_document=loan_document,
                status=NonPaymentNote.STATUS_DRAFT,
            )
            old_case_status = row.default_case_status
            row.default_case_status = "non_payment_under_review"
            row.save(update_fields=["default_case_status"])
            AuditLog.objects.create(
                actor_user=actor,
                action="non_payment_note.created",
                entity_type="non_payment_note",
                entity_id=note.pk,
                old_value_json={"default_case_status": old_case_status},
                new_value_json={
                    **serialize_non_payment_note(note),
                    "default_case_status": row.default_case_status,
                },
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            record_workflow_event(
                actor=actor,
                workflow_name="default_case",
                entity_type="default_case",
                entity_id=row.pk,
                from_state=old_case_status,
                to_state=row.default_case_status,
                trigger_reason=note.reason_for_non_payment,
                action_code="non_payment_note.created",
                metadata={"non_payment_note_id": str(note.pk)},
            )
            return note

    @classmethod
    def submit_for_recovery_approval(cls, *, actor, non_payment_note_id, request=None):
        _require_submitter(actor)
        scoped_case_ids = _scoped_case_candidates(actor=actor).values("pk")
        with transaction.atomic():
            note = (
                NonPaymentNote.objects.select_for_update(
                    of=("self", "loan_account", "default_case")
                )
                .select_related("loan_account", "default_case")
                .filter(pk=non_payment_note_id, default_case_id__in=scoped_case_ids)
                .first()
            )
            if note is None:
                raise RecoveryNotFound
            if note.status == NonPaymentNote.STATUS_SUBMITTED:
                if note.approval_case_id is None:
                    raise RecoveryConflict(
                        "The submitted note has no retained approval case."
                    )
                return note
            if note.status != NonPaymentNote.STATUS_DRAFT:
                raise RecoveryConflict(
                    "Only a draft Non-Payment Note can be submitted."
                )
            account = note.loan_account
            if (
                note.default_case.default_case_status
                not in {"extension_expired", "non_payment_under_review"}
                or account.closed_at is not None
                or account.principal_outstanding <= 0
                or account.principal_outstanding != note.outstanding_principal_amount
                or account.interest_outstanding != note.outstanding_interest_amount
            ):
                raise RecoveryConflict(
                    "The current case or servicing balances no longer match the draft."
                )
            submitted_at = timezone.now()
            try:
                approval_case = create_or_reuse_recovery_case(
                    note=note, actor=actor, submitted_at=submitted_at
                )
            except RecoveryApprovalRouteUnavailable as exc:
                raise RecoveryConflict(str(exc)) from exc
            old_state = note.status
            note.loan_document = generate_non_payment_note_document(
                note_id=note.pk,
                loan_application_id=account.loan_application_id,
                actor=actor,
                facts=_document_facts(
                    note=note,
                    reviewed_by=actor.full_name,
                    submitted_at=submitted_at.isoformat().replace("+00:00", "Z"),
                ),
            )
            note.approval_case = approval_case
            note.submitted_to_sanction_committee_at = submitted_at
            note.status = NonPaymentNote.STATUS_SUBMITTED
            note.save(
                update_fields=[
                    "approval_case",
                    "loan_document",
                    "submitted_to_sanction_committee_at",
                    "status",
                ]
            )
            row = note.default_case
            old_case_status = row.default_case_status
            row.default_case_status = "recovery_decision_pending"
            row.save(update_fields=["default_case_status"])
            AuditLog.objects.create(
                actor_user=actor,
                action="non_payment_note.submitted",
                entity_type="non_payment_note",
                entity_id=note.pk,
                old_value_json={"status": old_state},
                new_value_json={
                    **serialize_non_payment_note(note),
                    "default_case_status": row.default_case_status,
                },
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            record_workflow_event(
                actor=actor,
                workflow_name="default_case",
                entity_type="default_case",
                entity_id=row.pk,
                from_state=old_case_status,
                to_state=row.default_case_status,
                trigger_reason=note.recommended_recovery_action,
                action_code="non_payment_note.submitted",
                metadata={"approval_case_id": str(approval_case.pk)},
            )
            return note


def serialize_non_payment_note(note):
    return {
        "non_payment_note_id": str(note.pk),
        "default_case_id": str(note.default_case_id),
        "loan_account_id": str(note.loan_account_id),
        "reason_for_non_payment": note.reason_for_non_payment,
        "intentionality_assessment": note.intentionality_assessment,
        "outstanding_principal_amount": f"{note.outstanding_principal_amount:.2f}",
        "outstanding_interest_amount": f"{note.outstanding_interest_amount:.2f}",
        "recommended_recovery_action": note.recommended_recovery_action,
        "evidence_document_ids": list(note.evidence_document_ids_json),
        "frozen_case_facts": dict(note.frozen_case_facts_json),
        "document_id": str(note.loan_document_id),
        "prepared_by_user_id": str(note.prepared_by_user_id),
        "status": note.status,
        "approval_case_id": str(note.approval_case_id) if note.approval_case_id else None,
        "submitted_to_sanction_committee_at": (
            note.submitted_to_sanction_committee_at.isoformat().replace("+00:00", "Z")
            if note.submitted_to_sanction_committee_at
            else None
        ),
        "available_actions": [],
    }


def can_read_non_payment_note(*, actor, note):
    roles = set(auth_service.effective_role_codes(actor))
    if "credit_manager" in roles or "credit_assessment" in actor.team_codes():
        return True
    if "internal_auditor" in roles:
        return True
    return bool(
        note.approval_case_id
        and note.approval_case.required_approver_index.filter(user_id=actor.pk).exists()
    )


def serialize_recovery_submission(note):
    case = note.approval_case
    return {
        "entity_type": "non_payment_note",
        "entity_id": str(note.pk),
        "previous_status": NonPaymentNote.STATUS_DRAFT,
        "new_status": NonPaymentNote.STATUS_SUBMITTED,
        "workflow_event_id": str(case.workflow_event_id),
        "approval_case_id": str(case.pk),
        "submitted_to_sanction_committee_at": (
            note.submitted_to_sanction_committee_at.isoformat().replace("+00:00", "Z")
        ),
        "available_actions": [],
    }


def api_create_non_payment_note(*, actor, default_case_id, payload, request=None):
    return serialize_non_payment_note(
        RecoveryWorkflow.create_non_payment_note(
            actor=actor,
            default_case_id=default_case_id,
            payload=payload,
            request=request,
        )
    )


def api_submit_non_payment_note(*, actor, non_payment_note_id, payload, request=None):
    if payload:
        raise RecoveryValidation(
            {field: "Unknown request field." for field in sorted(payload)}
        )
    return serialize_recovery_submission(
        RecoveryWorkflow.submit_for_recovery_approval(
            actor=actor,
            non_payment_note_id=non_payment_note_id,
            request=request,
        )
    )


def _require_creator(actor):
    if (
        not actor.can_authenticate()
        or CREATE_PERMISSION not in auth_service.effective_permission_codes(actor)
        or "credit_assessment" not in actor.team_codes()
    ):
        raise RecoveryPermissionDenied


def _require_submitter(actor):
    if (
        not actor.can_authenticate()
        or SUBMIT_PERMISSION not in auth_service.effective_permission_codes(actor)
        or "credit_manager" not in auth_service.effective_role_codes(actor)
    ):
        raise RecoveryPermissionDenied


def _validate_create_payload(payload):
    allowed = {
        "reason_for_non_payment",
        "intentionality_assessment",
        "outstanding_principal_amount",
        "outstanding_interest_amount",
        "recommended_recovery_action",
    }
    errors = {field: "Unknown request field." for field in sorted(set(payload) - allowed)}
    cleaned = {}
    for field, maximum in (
        ("reason_for_non_payment", 5000),
        ("recommended_recovery_action", 100),
    ):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = "This field is required."
        elif len(value) > maximum:
            errors[field] = f"Must be at most {maximum} characters."
        else:
            cleaned[field] = value.strip()
    intentionality = payload.get("intentionality_assessment")
    if intentionality not in {"intentional", "non_intentional", "unclear"}:
        errors["intentionality_assessment"] = (
            "Must be intentional, non_intentional, or unclear."
        )
    else:
        cleaned["intentionality_assessment"] = intentionality
    for field in ("outstanding_principal_amount", "outstanding_interest_amount"):
        try:
            value = Decimal(str(payload.get(field))).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError, ValueError):
            errors[field] = "Must be a valid non-negative amount."
            continue
        if not value.is_finite() or value < 0:
            errors[field] = "Must be a valid non-negative amount."
        else:
            cleaned[field] = value
    if errors:
        raise RecoveryValidation(errors)
    return cleaned


def _create_replay_matches(note, cleaned):
    return all(
        getattr(note, field) == cleaned[field]
        for field in (
            "reason_for_non_payment",
            "intentionality_assessment",
            "outstanding_principal_amount",
            "outstanding_interest_amount",
            "recommended_recovery_action",
        )
    )


def _correct_returned_note(*, note, row, actor, cleaned, request):
    account = row.loan_account
    canonical_principal = account.principal_outstanding.quantize(Decimal("0.01"))
    canonical_interest = account.interest_outstanding.quantize(Decimal("0.01"))
    errors = {}
    if cleaned["outstanding_principal_amount"] != canonical_principal:
        errors["outstanding_principal_amount"] = (
            "Must match the current canonical servicing balance."
        )
    if cleaned["outstanding_interest_amount"] != canonical_interest:
        errors["outstanding_interest_amount"] = (
            "Must match the current canonical servicing balance."
        )
    if errors:
        raise RecoveryValidation(errors)
    old_projection = serialize_non_payment_note(note)
    note.status = NonPaymentNote.STATUS_RETURNED
    note.save(update_fields=["status"])
    AuditLog.objects.create(
        actor_user=actor,
        action="non_payment_note.returned",
        entity_type="non_payment_note",
        entity_id=note.pk,
        old_value_json={"status": NonPaymentNote.STATUS_SUBMITTED},
        new_value_json={
            "status": NonPaymentNote.STATUS_RETURNED,
            "approval_case_id": str(note.approval_case_id),
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    record_workflow_event(
        actor=actor,
        workflow_name="non_payment_note",
        entity_type="non_payment_note",
        entity_id=note.pk,
        from_state=NonPaymentNote.STATUS_SUBMITTED,
        to_state=NonPaymentNote.STATUS_RETURNED,
        trigger_reason="Approval owner returned the note for correction.",
        action_code="non_payment_note.returned",
    )
    note.reason_for_non_payment = cleaned["reason_for_non_payment"]
    note.intentionality_assessment = cleaned["intentionality_assessment"]
    note.outstanding_principal_amount = canonical_principal
    note.outstanding_interest_amount = canonical_interest
    note.recommended_recovery_action = cleaned["recommended_recovery_action"]
    note.loan_document = generate_non_payment_note_document(
        note_id=note.pk,
        loan_application_id=account.loan_application_id,
        actor=actor,
        facts={
            "default_case_id": str(row.pk),
            "loan_account_id": str(account.pk),
            "borrower_name": note.frozen_case_facts_json["borrower_name"],
            "original_due_date": row.scheduled_due_date.isoformat(),
            "grace_period_end_date": row.grace_period_end_date.isoformat(),
            "extension_end_date": note.extension_note.extension_end_date.isoformat(),
            "grace_outcome_summary": note.frozen_case_facts_json[
                "grace_outcome_summary"
            ],
            "extension_outcome_summary": note.frozen_case_facts_json[
                "extension_outcome_summary"
            ],
            "extension_reason": note.extension_note.extension_reason,
            "source_assessment_classification": note.frozen_case_facts_json[
                "prior_payment_failure_classification"
            ],
            "source_assessment_reason": note.frozen_case_facts_json[
                "assessment_reason_summary"
            ],
            "outstanding_principal_amount": f"{canonical_principal:.2f}",
            "outstanding_interest_amount": f"{canonical_interest:.2f}",
            "intentionality_assessment": cleaned["intentionality_assessment"],
            "reason_for_non_payment": cleaned["reason_for_non_payment"],
            "recommended_recovery_action": cleaned["recommended_recovery_action"],
            "evidence_document_ids": list(note.evidence_document_ids_json),
            "prepared_by": note.frozen_case_facts_json["prepared_by_name"],
            "reviewed_by": "Pending Credit Manager review",
            "submitted_at": "Not submitted",
        },
    )
    note.approval_case = None
    note.submitted_to_sanction_committee_at = None
    note.status = NonPaymentNote.STATUS_DRAFT
    note.save(
        update_fields=[
            "reason_for_non_payment",
            "intentionality_assessment",
            "outstanding_principal_amount",
            "outstanding_interest_amount",
            "recommended_recovery_action",
            "loan_document",
            "approval_case",
            "submitted_to_sanction_committee_at",
            "status",
        ]
    )
    old_case_status = row.default_case_status
    row.default_case_status = "non_payment_under_review"
    row.save(update_fields=["default_case_status"])
    AuditLog.objects.create(
        actor_user=actor,
        action="non_payment_note.corrected_after_return",
        entity_type="non_payment_note",
        entity_id=note.pk,
        old_value_json=old_projection,
        new_value_json=serialize_non_payment_note(note),
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    record_workflow_event(
        actor=actor,
        workflow_name="non_payment_note",
        entity_type="non_payment_note",
        entity_id=note.pk,
        from_state=NonPaymentNote.STATUS_RETURNED,
        to_state=NonPaymentNote.STATUS_DRAFT,
        trigger_reason=note.reason_for_non_payment,
        action_code="non_payment_note.corrected_after_return",
    )
    record_workflow_event(
        actor=actor,
        workflow_name="default_case",
        entity_type="default_case",
        entity_id=row.pk,
        from_state=old_case_status,
        to_state=row.default_case_status,
        trigger_reason="Returned Non-Payment Note corrected as a new draft.",
        action_code="non_payment_note.corrected_after_return",
        metadata={"non_payment_note_id": str(note.pk)},
    )
    return note


def _document_facts(*, note, reviewed_by, submitted_at):
    frozen = note.frozen_case_facts_json
    return {
        "default_case_id": str(note.default_case_id),
        "loan_account_id": str(note.loan_account_id),
        "borrower_name": frozen["borrower_name"],
        "original_due_date": frozen["original_due_date"],
        "grace_period_end_date": frozen["grace_period_end_date"],
        "grace_outcome_summary": frozen["grace_outcome_summary"],
        "extension_end_date": frozen["extension_end_date"],
        "extension_outcome_summary": frozen["extension_outcome_summary"],
        "extension_reason": frozen["extension_reason"],
        "source_assessment_classification": frozen[
            "prior_payment_failure_classification"
        ],
        "source_assessment_reason": frozen["assessment_reason_summary"],
        "outstanding_principal_amount": f"{note.outstanding_principal_amount:.2f}",
        "outstanding_interest_amount": f"{note.outstanding_interest_amount:.2f}",
        "intentionality_assessment": note.intentionality_assessment,
        "reason_for_non_payment": note.reason_for_non_payment,
        "recommended_recovery_action": note.recommended_recovery_action,
        "evidence_document_ids": list(note.evidence_document_ids_json),
        "prepared_by": frozen["prepared_by_name"],
        "reviewed_by": reviewed_by,
        "submitted_at": submitted_at,
    }
