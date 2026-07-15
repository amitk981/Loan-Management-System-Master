"""Immutable application-owned bank and cancelled-cheque verification decisions."""

import hashlib
import json
import uuid
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.approvals.modules import document_checklist_facts as approval_facts
from sfpcl_credit.applications.models import BankVerificationDecision, LoanApplication
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import BankAccount, CancelledCheque
from sfpcl_credit.workflows.models import WorkflowEvent


class AccessDenied(Exception):
    pass


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str = ""
    user_agent: str = ""


def require_verifier(actor):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or "documents.checklist.update" not in permissions
        or not roles.intersection({"compliance_team_member", "company_secretary"})
    ):
        raise AccessDenied


@transaction.atomic
def record_decision(*, actor, application_id, payload, metadata):
    require_verifier(actor)
    values = _parse(payload)
    request_id = (metadata.request_id or "").strip()
    if not request_id:
        raise ValidationError({"request_id": "X-Request-ID is required."})
    application = (
        LoanApplication.objects.select_for_update()
        .filter(pk=application_id)
        .first()
    )
    if application is None:
        raise AccessDenied
    if application.application_status != LoanApplication.STATUS_APPROVED_BY_SANCTION:
        # Documentation actors have source-defined global access only to approved
        # applications requiring Stage-4 work. Treat every other parent as absent
        # before resolving evidence so no immutable ledger can escape that scope.
        raise AccessDenied
    terminal_facts = approval_facts.resolve_approved_facts(application_id=application.pk)
    if terminal_facts is None:
        raise AccessDenied
    bank = BankAccount.objects.select_for_update().filter(pk=values["bank_account_id"]).first()
    cheque = (
        CancelledCheque.objects.select_for_update()
        .filter(pk=values["cancelled_cheque_id"])
        .first()
    )
    if bank is None or cheque is None:
        raise Conflict("The selected bank verification sources are not current.")
    document = DocumentFile.objects.select_for_update().filter(pk=cheque.document_id).first()
    if document is None or not document.checksum_sha256:
        raise Conflict("The cancelled-cheque file has no immutable checksum provenance.")
    _require_exact_sources(application=application, bank=bank, cheque=cheque)
    previous = (
        BankVerificationDecision.objects.filter(loan_application=application)
        .order_by("-decision_version", "-bank_verification_decision_id")
        .first()
    )
    version = (previous.decision_version if previous else 0) + 1
    if previous is not None and _same_decision(
        previous, bank=bank, cheque=cheque, document=document,
        status=values["decision_status"], request_id=request_id,
        terminal_facts=terminal_facts,
    ):
        return previous
    decision_id = uuid.uuid4()
    workflow_id = uuid.uuid4()
    audit_id = uuid.uuid4()
    version_id = uuid.uuid4()
    verified_at = timezone.now()
    verifier_role = _verifier_role(actor)
    evidence = {
        "bank_verification_decision_id": str(decision_id),
        "loan_application_id": str(application.pk),
        "member_id": str(application.member_id),
        "bank_account_id": str(bank.pk),
        "cancelled_cheque_id": str(cheque.pk),
        "cancelled_cheque_document_id": str(document.pk),
        "cancelled_cheque_checksum_sha256": document.checksum_sha256,
        "bank_account_hash_snapshot": bank.account_number_hash,
        "ifsc_snapshot": bank.ifsc,
        "branch_name_snapshot": bank.branch_name or cheque.branch_name or "",
        "decision_status": values["decision_status"],
        "verifier_user_id": str(actor.pk),
        "verifier_role_code": verifier_role,
        "verified_at": verified_at.isoformat(),
        "request_id": request_id,
        "decision_version": version,
        "approval_case_id": str(terminal_facts.approval_case_id),
        "sanction_decision_id": str(terminal_facts.sanction_decision_id),
        "workflow_event_id": str(workflow_id),
        "audit_log_id": str(audit_id),
        "version_history_id": str(version_id),
    }
    digest = evidence_digest(evidence)
    workflow = WorkflowEvent.objects.create(
        workflow_event_id=workflow_id,
        workflow_name="bank_verification",
        entity_type="bank_verification_decision",
        entity_id=decision_id,
        from_state=previous.decision_status if previous else "pending",
        to_state=values["decision_status"],
        triggered_by_user=actor,
        trigger_reason="bank_verification.decision_recorded",
        created_at=verified_at,
    )
    audit = AuditLog.objects.create(
        audit_log_id=audit_id,
        actor_user=actor,
        actor_type="user",
        action="bank_verification.decision_recorded",
        entity_type="bank_verification_decision",
        entity_id=decision_id,
        old_value_json=(
            {"decision_status": previous.decision_status, "decision_version": previous.decision_version}
            if previous else {"decision_status": "pending", "decision_version": 0}
        ),
        new_value_json={**evidence, "evidence_digest": digest},
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
        created_at=verified_at,
    )
    history = VersionHistory.objects.create(
        version_history_id=version_id,
        versioned_entity_type="bank_verification_decision",
        versioned_entity_id=decision_id,
        version_number=str(version),
        change_summary="bank_verification.decision_recorded",
        author_user=actor,
        old_value_json=audit.old_value_json,
        new_value_json={**evidence, "evidence_digest": digest},
        effective_from=timezone.localdate(),
        created_at=verified_at,
    )
    return BankVerificationDecision.objects.create(
        bank_verification_decision_id=decision_id,
        loan_application=application,
        member=application.member,
        bank_account=bank,
        cancelled_cheque=cheque,
        cancelled_cheque_document=document,
        cancelled_cheque_checksum_sha256=document.checksum_sha256,
        bank_account_hash_snapshot=bank.account_number_hash,
        ifsc_snapshot=bank.ifsc,
        branch_name_snapshot=bank.branch_name or cheque.branch_name or "",
        decision_status=values["decision_status"],
        verifier_user=actor,
        verifier_role_code=verifier_role,
        verified_at=verified_at,
        request_id=request_id,
        decision_version=version,
        approval_case_id_snapshot=terminal_facts.approval_case_id,
        sanction_decision_id_snapshot=terminal_facts.sanction_decision_id,
        workflow_event=workflow,
        audit_log=audit,
        version_history=history,
        evidence_digest=digest,
    )


def evidence_digest(evidence):
    payload = json.dumps(evidence, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def decision_evidence(decision):
    return {
        "bank_verification_decision_id": str(decision.pk),
        "loan_application_id": str(decision.loan_application_id),
        "member_id": str(decision.member_id),
        "bank_account_id": str(decision.bank_account_id),
        "cancelled_cheque_id": str(decision.cancelled_cheque_id),
        "cancelled_cheque_document_id": str(decision.cancelled_cheque_document_id),
        "cancelled_cheque_checksum_sha256": decision.cancelled_cheque_checksum_sha256,
        "bank_account_hash_snapshot": decision.bank_account_hash_snapshot,
        "ifsc_snapshot": decision.ifsc_snapshot,
        "branch_name_snapshot": decision.branch_name_snapshot,
        "decision_status": decision.decision_status,
        "verifier_user_id": str(decision.verifier_user_id),
        "verifier_role_code": decision.verifier_role_code,
        "verified_at": decision.verified_at.isoformat(),
        "request_id": decision.request_id,
        "decision_version": decision.decision_version,
        "approval_case_id": (
            str(decision.approval_case_id_snapshot)
            if decision.approval_case_id_snapshot else None
        ),
        "sanction_decision_id": (
            str(decision.sanction_decision_id_snapshot)
            if decision.sanction_decision_id_snapshot else None
        ),
        "workflow_event_id": str(decision.workflow_event_id),
        "audit_log_id": str(decision.audit_log_id),
        "version_history_id": str(decision.version_history_id),
    }


def action_response(decision):
    workflow = decision.workflow_event
    return {
        **decision_evidence(decision),
        "entity_type": workflow.entity_type,
        "entity_id": str(workflow.entity_id),
        "previous_status": workflow.from_state,
        "new_status": workflow.to_state,
        "available_actions": [],
    }


def _parse(payload):
    if not isinstance(payload, dict):
        raise ValidationError({"body": "A JSON object is required."})
    allowed = {"bank_account_id", "cancelled_cheque_id", "decision_status"}
    unknown = set(payload) - allowed
    missing = allowed - set(payload)
    if unknown or missing:
        errors = {field: "Unknown field." for field in sorted(unknown)}
        errors.update({field: "This field is required." for field in sorted(missing)})
        raise ValidationError(errors)
    parsed = {}
    for field in ("bank_account_id", "cancelled_cheque_id"):
        try:
            parsed[field] = uuid.UUID(str(payload[field]))
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValidationError({field: "Must be a valid UUID."}) from exc
    status = payload["decision_status"]
    if status not in BankVerificationDecision.STATUSES:
        raise ValidationError({"decision_status": "Must be verified or rejected."})
    parsed["decision_status"] = status
    return parsed


def _require_exact_sources(*, application, bank, cheque):
    if (
        application.bank_account_id != bank.pk
        or application.cancelled_cheque_id != cheque.pk
        or bank.owner_party_type != "member"
        or bank.owner_party_id != application.member_id
        or bank.cancelled_cheque_id != cheque.pk
        or cheque.loan_application_id != application.pk
        or cheque.member_id != application.member_id
        or not bank.account_number_hash
        or bank.account_number_hash != cheque.account_number_hash
        or bank.ifsc != cheque.ifsc
        or bank.account_number_last4 != cheque.account_number_last4
        or bank.status != "active"
    ):
        raise Conflict("The selected bank verification sources are not current.")


def _verifier_role(actor):
    roles = set(auth_service.effective_role_codes(actor))
    if actor.primary_role.role_code in roles.intersection(
        {"compliance_team_member", "company_secretary"}
    ):
        return actor.primary_role.role_code
    return sorted(roles.intersection({"compliance_team_member", "company_secretary"}))[0]


def _same_decision(
    decision, *, bank, cheque, document, status, request_id, terminal_facts
):
    return (
        decision.bank_account_id == bank.pk
        and decision.cancelled_cheque_id == cheque.pk
        and decision.cancelled_cheque_document_id == document.pk
        and decision.cancelled_cheque_checksum_sha256 == document.checksum_sha256
        and decision.bank_account_hash_snapshot == bank.account_number_hash
        and decision.ifsc_snapshot == bank.ifsc
        and decision.branch_name_snapshot == (bank.branch_name or cheque.branch_name or "")
        and decision.decision_status == status
        and decision.request_id == request_id
        and decision.approval_case_id_snapshot == terminal_facts.approval_case_id
        and decision.sanction_decision_id_snapshot == terminal_facts.sanction_decision_id
    )
