import hashlib
from decimal import Decimal, InvalidOperation
import uuid
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

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
from sfpcl_credit.loans.modules.recovery_proceeds import (
    RecoveryProceedsConflict,
    RecoveryProceedsNotFound,
    post_verified_recovery_proceeds,
)
from sfpcl_credit.recovery.models import RecoveryAction, RecoveryDecision
from sfpcl_credit.security_instruments.modules.recovery_invocation import (
    RecoverySecurityUnavailable,
    prepare_recovery_invocation,
)
from sfpcl_credit.workflows.events import record_workflow_event


CREATE_PERMISSION = "defaults.non_payment_note.create"
SUBMIT_PERMISSION = "defaults.non_payment_note.submit"
INITIATE_PERMISSION = "recovery.action.initiate"
COMPLETE_PERMISSION = "recovery.action.complete"
EXECUTION_ROLES = {"company_secretary"}


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
    def initiate_recovery_action(
        cls, *, actor, recovery_decision_id, payload, request=None
    ):
        try:
            return cls._initiate_recovery_action(
                actor=actor,
                recovery_decision_id=recovery_decision_id,
                payload=payload,
                request=request,
            )
        except (
            RecoveryValidation,
            RecoveryPermissionDenied,
            RecoveryNotFound,
            RecoveryConflict,
        ) as exc:
            _audit_recovery_denial(
                actor=actor,
                operation="initiate",
                entity_id=recovery_decision_id,
                reason_code=type(exc).__name__,
                request=request,
            )
            raise

    @classmethod
    def _initiate_recovery_action(
        cls, *, actor, recovery_decision_id, payload, request=None
    ):
        _require_recovery_executor(actor, INITIATE_PERMISSION)
        cleaned = _validate_initiation_payload(payload)
        scoped_case_ids = _scoped_case_candidates(actor=actor).values("pk")
        with transaction.atomic():
            decision = (
                RecoveryDecision.objects.select_for_update(of=("self",))
                .select_related(
                    "default_case__loan_account__loan_application",
                    "default_case__member",
                    "approval_case",
                    "non_payment_note",
                )
                .filter(
                    pk=recovery_decision_id,
                    default_case_id__in=scoped_case_ids,
                )
                .first()
            )
            if decision is None:
                raise RecoveryNotFound
            retained = RecoveryAction.objects.select_for_update().filter(
                recovery_decision=decision
            ).first()
            if retained is not None:
                if _initiation_replay_matches(retained, cleaned, actor=actor):
                    return retained
                raise RecoveryConflict(
                    "The approved route already has a different recovery action attempt."
                )
            default_case = decision.default_case
            account = default_case.loan_account
            if (
                decision.status != RecoveryDecision.STATUS_APPROVED
                or decision.decision != cleaned["action_type"]
                or decision.non_payment_note_id
                != getattr(default_case, "non_payment_note", None).pk
                or decision.approval_case_id
                != decision.non_payment_note.approval_case_id
                or decision.approval_case.current_status != "approved"
                or decision.approval_case.closed_at is None
                or default_case.default_case_status != "recovery_approved"
                or account.closed_at is not None
                or account.principal_outstanding <= 0
            ):
                raise RecoveryConflict(
                    "Only the exact approved open recovery route can be initiated."
                )
            _validate_recovery_documents(
                application_id=account.loan_application_id,
                evidence_document_ids=cleaned["all_evidence_document_ids"],
                actor=actor,
            )
            try:
                source_security = prepare_recovery_invocation(
                    action_type=cleaned["action_type"],
                    loan_application_id=account.loan_application_id,
                    member_id=default_case.member_id,
                    approval_case_id=decision.approval_case_id,
                )
            except RecoverySecurityUnavailable as exc:
                raise RecoveryConflict(str(exc)) from exc
            role_code = _execution_role(actor)
            action_id = uuid4()
            event = record_workflow_event(
                actor=actor,
                workflow_name="recovery_action",
                entity_type="recovery_action",
                entity_id=action_id,
                from_state="recovery_approved",
                to_state=RecoveryAction.STATUS_PENDING,
                trigger_reason="Approved recovery security handoff initiated.",
                action_code="recovery.action.initiated",
                metadata={
                    "recovery_decision_id": str(decision.pk),
                    "approval_case_id": str(decision.approval_case_id),
                },
            )
            action = RecoveryAction.objects.create(
                recovery_action_id=action_id,
                recovery_decision=decision,
                approval_case_id=decision.approval_case_id,
                loan_account=account,
                action_type=cleaned["action_type"],
                action_status=RecoveryAction.STATUS_PENDING,
                source_security_type=source_security["security_type"],
                source_security_id=source_security["security_id"],
                source_security_evidence_json=source_security,
                initiated_by_user=actor,
                initiated_by_role_code=role_code,
                initiated_at=cleaned["initiated_at"],
                initiation_evidence_document_ids_json=[
                    str(value) for value in cleaned["evidence_document_ids"]
                ],
                initiation_remarks=cleaned["remarks"],
                interaction_log_json=cleaned["interaction_log"],
                initiation_workflow_event=event,
            )
            old_status = default_case.default_case_status
            default_case.default_case_status = "recovery_in_progress"
            default_case.save(update_fields=["default_case_status"])
            AuditLog.objects.create(
                actor_user=actor,
                action="recovery.action.initiated",
                entity_type="recovery_action",
                entity_id=action.pk,
                old_value_json={
                    "default_case_status": old_status,
                    "recovery_decision_id": str(decision.pk),
                },
                new_value_json={
                    "recovery_action_id": str(action.pk),
                    "approval_case_id": str(action.approval_case_id),
                    "loan_account_id": str(account.pk),
                    "action_type": action.action_type,
                    "action_status": action.action_status,
                    "source_security_type": action.source_security_type,
                    "source_security_id": str(action.source_security_id),
                    "evidence_document_ids": list(
                        action.initiation_evidence_document_ids_json
                    ),
                    "interaction_count": len(action.interaction_log_json),
                    "remarks_sha256": hashlib.sha256(
                        action.initiation_remarks.encode()
                    ).hexdigest(),
                    "workflow_event_id": str(event.pk),
                    "external_sap_status": action.external_sap_status,
                    "default_case_status": default_case.default_case_status,
                },
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            return action

    @classmethod
    def complete_recovery_action(
        cls, *, actor, recovery_action_id, payload, request=None
    ):
        try:
            return cls._complete_recovery_action(
                actor=actor,
                recovery_action_id=recovery_action_id,
                payload=payload,
                request=request,
            )
        except (
            RecoveryValidation,
            RecoveryPermissionDenied,
            RecoveryNotFound,
            RecoveryConflict,
        ) as exc:
            _audit_recovery_denial(
                actor=actor,
                operation="complete",
                entity_id=recovery_action_id,
                reason_code=type(exc).__name__,
                request=request,
            )
            raise

    @classmethod
    def _complete_recovery_action(
        cls, *, actor, recovery_action_id, payload, request=None
    ):
        _require_recovery_executor(actor, COMPLETE_PERMISSION)
        cleaned = _validate_completion_payload(payload)
        scoped_case_ids = _scoped_case_candidates(actor=actor).values("pk")
        with transaction.atomic():
            action = (
                RecoveryAction.objects.select_for_update(of=("self",))
                .select_related(
                    "loan_account__loan_application",
                    "recovery_decision__default_case",
                )
                .filter(
                    pk=recovery_action_id,
                    recovery_decision__default_case_id__in=scoped_case_ids,
                )
                .first()
            )
            if action is None:
                raise RecoveryNotFound
            if action.action_status == RecoveryAction.STATUS_COMPLETED:
                if _completion_replay_matches(action, cleaned, actor=actor):
                    return action
                raise RecoveryConflict(
                    "The recovery action is already complete with different retained evidence."
                )
            if action.action_status != RecoveryAction.STATUS_PENDING:
                raise RecoveryConflict("Only a pending recovery action can be completed.")
            default_case = action.recovery_decision.default_case
            if default_case.default_case_status != "recovery_in_progress":
                raise RecoveryConflict(
                    "The default case no longer retains an in-progress recovery action."
                )
            _validate_recovery_documents(
                application_id=action.loan_account.loan_application_id,
                evidence_document_ids=cleaned["evidence_document_ids"],
                actor=actor,
            )
            try:
                posting = post_verified_recovery_proceeds(
                    actor=actor,
                    loan_account_id=action.loan_account_id,
                    recovery_action_id=action.pk,
                    amount=cleaned["amount_recovered"],
                    completed_at=cleaned["completed_at"],
                    remarks=cleaned["remarks"],
                    request=request,
                )
            except RecoveryProceedsNotFound as exc:
                raise RecoveryNotFound from exc
            except RecoveryProceedsConflict as exc:
                raise RecoveryConflict(str(exc)) from exc
            event = record_workflow_event(
                actor=actor,
                workflow_name="recovery_action",
                entity_type="recovery_action",
                entity_id=action.pk,
                from_state=RecoveryAction.STATUS_PENDING,
                to_state=RecoveryAction.STATUS_COMPLETED,
                trigger_reason="Verified recovery proceeds posted to the canonical loan balance.",
                action_code="recovery.action.completed",
                metadata={
                    "movement_reference": posting.movement_reference,
                    "posting_audit_id": posting.posting_audit_id,
                },
            )
            action.action_status = RecoveryAction.STATUS_COMPLETED
            action.completed_by_user = actor
            action.completed_at = cleaned["completed_at"]
            action.amount_recovered = cleaned["amount_recovered"]
            action.completion_evidence_document_ids_json = [
                str(value) for value in cleaned["evidence_document_ids"]
            ]
            action.completion_remarks = cleaned["remarks"]
            action.ledger_posting_json = posting.projection()
            action.completion_workflow_event = event
            action.save(
                update_fields=[
                    "action_status",
                    "completed_by_user",
                    "completed_at",
                    "amount_recovered",
                    "completion_evidence_document_ids_json",
                    "completion_remarks",
                    "ledger_posting_json",
                    "completion_workflow_event",
                ]
            )
            old_case_status = default_case.default_case_status
            if posting.total_after == "0.00":
                default_case.default_case_status = "resolved_by_repayment"
                default_case.closed_at = cleaned["completed_at"]
                default_case.save(
                    update_fields=["default_case_status", "closed_at"]
                )
            AuditLog.objects.create(
                actor_user=actor,
                action="recovery.action.completed",
                entity_type="recovery_action",
                entity_id=action.pk,
                old_value_json={
                    "action_status": RecoveryAction.STATUS_PENDING,
                    "default_case_status": old_case_status,
                },
                new_value_json={
                    "action_status": action.action_status,
                    "amount_recovered": f"{action.amount_recovered:.2f}",
                    "evidence_document_ids": list(
                        action.completion_evidence_document_ids_json
                    ),
                    "remarks_sha256": hashlib.sha256(
                        action.completion_remarks.encode()
                    ).hexdigest(),
                    "movement_reference": posting.movement_reference,
                    "posting_audit_id": posting.posting_audit_id,
                    "workflow_event_id": str(event.pk),
                    "external_sap_status": action.external_sap_status,
                    "default_case_status": default_case.default_case_status,
                },
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            return action

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


def serialize_recovery_action(action, *, actor):
    available_actions = []
    if action.action_status == RecoveryAction.STATUS_PENDING and _can_execute(
        actor, COMPLETE_PERMISSION
    ):
        available_actions.append(
            {
                "action_code": "complete_recovery",
                "required_permission": COMPLETE_PERMISSION,
            }
        )
    return {
        "recovery_action_id": str(action.pk),
        "recovery_decision_id": str(action.recovery_decision_id),
        "approval_case_id": str(action.approval_case_id),
        "loan_account_id": str(action.loan_account_id),
        "action_type": action.action_type,
        "action_status": action.action_status,
        "source_security": dict(action.source_security_evidence_json),
        "initiated_by_user_id": str(action.initiated_by_user_id),
        "initiated_by_role_code": action.initiated_by_role_code,
        "initiated_at": action.initiated_at.isoformat().replace("+00:00", "Z"),
        "evidence_document_ids": list(
            action.initiation_evidence_document_ids_json
        ),
        "remarks": action.initiation_remarks,
        "interaction_log": list(action.interaction_log_json),
        "completed_by_user_id": (
            str(action.completed_by_user_id) if action.completed_by_user_id else None
        ),
        "completed_at": (
            action.completed_at.isoformat().replace("+00:00", "Z")
            if action.completed_at
            else None
        ),
        "amount_recovered": (
            f"{action.amount_recovered:.2f}"
            if action.amount_recovered is not None
            else None
        ),
        "completion_evidence_document_ids": list(
            action.completion_evidence_document_ids_json
        ),
        "completion_remarks": action.completion_remarks,
        "failed_at": (
            action.failed_at.isoformat().replace("+00:00", "Z")
            if action.failed_at
            else None
        ),
        "failure_reason": action.failure_reason or None,
        "ledger_posting": dict(action.ledger_posting_json),
        "external_sap_status": action.external_sap_status,
        "available_actions": available_actions,
    }


def api_initiate_recovery_action(
    *, actor, recovery_decision_id, payload, request=None
):
    return serialize_recovery_action(
        RecoveryWorkflow.initiate_recovery_action(
            actor=actor,
            recovery_decision_id=recovery_decision_id,
            payload=payload,
            request=request,
        ),
        actor=actor,
    )


def api_complete_recovery_action(*, actor, recovery_action_id, payload, request=None):
    return serialize_recovery_action(
        RecoveryWorkflow.complete_recovery_action(
            actor=actor,
            recovery_action_id=recovery_action_id,
            payload=payload,
            request=request,
        ),
        actor=actor,
    )


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


def _require_recovery_executor(actor, permission):
    if not _can_execute(actor, permission):
        raise RecoveryPermissionDenied


def _can_execute(actor, permission):
    return bool(
        actor.can_authenticate()
        and permission in auth_service.effective_permission_codes(actor)
        and set(auth_service.effective_role_codes(actor)).intersection(EXECUTION_ROLES)
    )


def _execution_role(actor):
    roles = set(auth_service.effective_role_codes(actor)).intersection(EXECUTION_ROLES)
    if not roles:
        raise RecoveryPermissionDenied
    return sorted(roles)[0]


def _validate_initiation_payload(payload):
    allowed = {
        "action_type",
        "initiated_at",
        "evidence_document_ids",
        "remarks",
        "interaction_log",
    }
    errors = {
        field: "Unknown request field." for field in sorted(set(payload) - allowed)
    }
    action_type = str(payload.get("action_type", "")).strip()
    if action_type not in {
        "invoke_sh4",
        "invoke_cdsl",
        "present_blank_dated_cheque",
    }:
        errors["action_type"] = "Must identify a supported approved security route."
    initiated_at = parse_datetime(str(payload.get("initiated_at", "")))
    if initiated_at is None or timezone.is_naive(initiated_at):
        errors["initiated_at"] = "Must be a timezone-aware timestamp."
    evidence_document_ids = _uuid_list(
        payload.get("evidence_document_ids"),
        field="evidence_document_ids",
        errors=errors,
    )
    if not evidence_document_ids:
        errors["evidence_document_ids"] = "At least one evidence document is required."
    remarks = str(payload.get("remarks", "")).strip()
    if not remarks or len(remarks) > 2000:
        errors["remarks"] = "Must be nonblank and at most 2000 characters."
    interaction_log = _validate_interaction_log(
        payload.get("interaction_log"), errors=errors
    )
    if errors:
        raise RecoveryValidation(errors)
    all_evidence = set(evidence_document_ids)
    for item in interaction_log:
        all_evidence.update(uuid.UUID(value) for value in item["evidence_document_ids"])
    return {
        "action_type": action_type,
        "initiated_at": initiated_at,
        "evidence_document_ids": evidence_document_ids,
        "remarks": remarks,
        "interaction_log": interaction_log,
        "all_evidence_document_ids": sorted(all_evidence, key=str),
    }


def _validate_completion_payload(payload):
    allowed = {
        "completed_at",
        "amount_recovered",
        "evidence_document_ids",
        "remarks",
    }
    errors = {
        field: "Unknown request field." for field in sorted(set(payload) - allowed)
    }
    completed_at = parse_datetime(str(payload.get("completed_at", "")))
    if completed_at is None or timezone.is_naive(completed_at):
        errors["completed_at"] = "Must be a timezone-aware timestamp."
    try:
        amount = Decimal(str(payload.get("amount_recovered", "")))
        if not amount.is_finite() or amount.as_tuple().exponent < -2:
            raise InvalidOperation
        amount = amount.quantize(Decimal("0.01"))
        if amount < 0 or amount >= Decimal("10000000000000000"):
            raise InvalidOperation
    except (InvalidOperation, ValueError, TypeError):
        amount = None
        errors["amount_recovered"] = (
            "Must be a non-negative monetary amount with at most two decimals."
        )
    evidence_document_ids = _uuid_list(
        payload.get("evidence_document_ids"),
        field="evidence_document_ids",
        errors=errors,
    )
    if not evidence_document_ids:
        errors["evidence_document_ids"] = "At least one evidence document is required."
    remarks = str(payload.get("remarks", "")).strip()
    if not remarks or len(remarks) > 2000:
        errors["remarks"] = "Must be nonblank and at most 2000 characters."
    if errors:
        raise RecoveryValidation(errors)
    return {
        "completed_at": completed_at,
        "amount_recovered": amount,
        "evidence_document_ids": evidence_document_ids,
        "remarks": remarks,
    }


def _validate_interaction_log(value, *, errors):
    if not isinstance(value, list) or not value:
        errors["interaction_log"] = "At least one borrower interaction is required."
        return []
    cleaned = []
    allowed = {
        "interaction_at",
        "interaction_mode",
        "person_contacted",
        "summary",
        "next_action",
        "complaint_raised",
        "grievance_reference",
        "evidence_document_ids",
    }
    for index, item in enumerate(value):
        prefix = f"interaction_log.{index}"
        if not isinstance(item, dict):
            errors[prefix] = "Must be an object."
            continue
        unknown = set(item) - allowed
        if unknown:
            errors[prefix] = f"Unknown fields: {', '.join(sorted(unknown))}."
            continue
        interaction_at = parse_datetime(str(item.get("interaction_at", "")))
        if interaction_at is None or timezone.is_naive(interaction_at):
            errors[f"{prefix}.interaction_at"] = "Must be a timezone-aware timestamp."
        mode = str(item.get("interaction_mode", "")).strip()
        if mode not in {"call", "visit", "borrower_contact"}:
            errors[f"{prefix}.interaction_mode"] = "Must be call, visit, or borrower_contact."
        text_values = {}
        for field, maximum in (
            ("person_contacted", 255),
            ("summary", 2000),
            ("next_action", 1000),
            ("grievance_reference", 255),
        ):
            text = str(item.get(field, "")).strip()
            if not text or len(text) > maximum:
                errors[f"{prefix}.{field}"] = (
                    f"Must be nonblank and at most {maximum} characters."
                )
            text_values[field] = text
        complaint = item.get("complaint_raised")
        if not isinstance(complaint, bool):
            errors[f"{prefix}.complaint_raised"] = "Must be true or false."
        item_errors = {}
        item_evidence = _uuid_list(
            item.get("evidence_document_ids"),
            field="evidence_document_ids",
            errors=item_errors,
        )
        if not item_evidence:
            item_errors["evidence_document_ids"] = "At least one evidence document is required."
        for field, message in item_errors.items():
            errors[f"{prefix}.{field}"] = message
        if not any(key == prefix or key.startswith(f"{prefix}.") for key in errors):
            cleaned.append(
                {
                    "interaction_at": interaction_at.isoformat().replace("+00:00", "Z"),
                    "interaction_mode": mode,
                    **text_values,
                    "complaint_raised": complaint,
                    "evidence_document_ids": [str(value) for value in item_evidence],
                }
            )
    return cleaned


def _uuid_list(value, *, field, errors):
    if not isinstance(value, list):
        errors[field] = "Must be a list of UUIDs."
        return []
    cleaned = []
    for raw in value:
        try:
            parsed = uuid.UUID(str(raw))
        except (TypeError, ValueError, AttributeError):
            errors[field] = "Must contain only valid UUIDs."
            return []
        if parsed in cleaned:
            errors[field] = "Must not contain duplicate document IDs."
            return []
        cleaned.append(parsed)
    return cleaned


def _validate_recovery_documents(*, application_id, evidence_document_ids, actor):
    from sfpcl_credit.legal_documents.modules.recovery_evidence import (
        retain_recovery_evidence,
    )

    if not retain_recovery_evidence(
        application_id=application_id,
        document_ids=evidence_document_ids,
        actor=actor,
    ):
        raise RecoveryValidation(
            {
                "evidence_document_ids": (
                    "Every evidence document must belong to this loan file and recovery route."
                )
            }
        )


def _initiation_replay_matches(action, cleaned, *, actor):
    return (
        action.action_type == cleaned["action_type"]
        and action.initiated_by_user_id == actor.pk
        and action.initiated_at == cleaned["initiated_at"]
        and action.initiation_evidence_document_ids_json
        == [str(value) for value in cleaned["evidence_document_ids"]]
        and action.initiation_remarks == cleaned["remarks"]
        and action.interaction_log_json == cleaned["interaction_log"]
    )


def _completion_replay_matches(action, cleaned, *, actor):
    return (
        action.completed_by_user_id == actor.pk
        and action.completed_at == cleaned["completed_at"]
        and action.amount_recovered == cleaned["amount_recovered"]
        and action.completion_evidence_document_ids_json
        == [str(value) for value in cleaned["evidence_document_ids"]]
        and action.completion_remarks == cleaned["remarks"]
    )


def _audit_recovery_denial(*, actor, operation, entity_id, reason_code, request):
    if actor is None or not getattr(actor, "pk", None):
        return
    try:
        entity_uuid = uuid.UUID(str(entity_id))
    except (TypeError, ValueError, AttributeError):
        entity_uuid = uuid4()
    AuditLog.objects.create(
        actor_user=actor,
        action=f"recovery.action.{operation}_denied",
        entity_type=(
            "recovery_decision" if operation == "initiate" else "recovery_action"
        ),
        entity_id=entity_uuid,
        old_value_json=None,
        new_value_json={
            "operation": operation,
            "reason_code": reason_code,
            "actor_role_codes": auth_service.effective_role_codes(actor),
            "request_id": request.headers.get("X-Request-ID", "") if request else "",
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )


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
