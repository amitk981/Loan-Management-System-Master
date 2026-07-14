import uuid
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.approvals.modules import approval_case_engine
from sfpcl_credit.approvals.modules import document_checklist_facts
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.legal_documents.models import (
    ChecklistAction,
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
    NotarisationRecord,
    SignatureRecord,
    StampDutyRecord,
)
from sfpcl_credit.legal_documents.request_contracts import (
    ChecklistApprovalRequest,
    ChecklistItemCompletionRequest,
)
from sfpcl_credit.workflows.events import record_workflow_event


ITEM_COMPLETE_PERMISSION = "documents.checklist.update"


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


class AccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"):
        self.error_code = error_code
        super().__init__(error_code)


class NotFound(Exception):
    pass


class Conflict(Exception):
    def __init__(self, message, error_code="CHECKLIST_ACTION_CONFLICT"):
        self.error_code = error_code
        super().__init__(message)


class EvidenceBlocked(Conflict):
    def __init__(self, message):
        super().__init__(message, "CHECKLIST_EVIDENCE_INCOMPLETE")


_STAGE = {
    ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL: {
        "permission": "documents.checklist.approve_cs",
        "role": "company_secretary",
        "meaning": "all documents verified and attached",
        "from_status": DocumentChecklist.STATUS_IN_PROGRESS,
        "to_status": DocumentChecklist.STATUS_CS_APPROVED,
        "signature_field": "company_secretary_signature",
    },
    ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL: {
        "permission": "documents.checklist.approve_credit",
        "role": "credit_manager",
        "meaning": "loan limits reviewed and confirmed",
        "from_status": DocumentChecklist.STATUS_CS_APPROVED,
        "to_status": DocumentChecklist.STATUS_CREDIT_APPROVED,
        "signature_field": "credit_manager_signature",
    },
    ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL: {
        "permission": "documents.checklist.approve_sanction",
        "role": "director",
        "meaning": "final approval per matrix",
        "from_status": DocumentChecklist.STATUS_CREDIT_APPROVED,
        "to_status": DocumentChecklist.STATUS_SANCTION_APPROVED,
        "signature_field": "sanction_committee_signature",
    },
}

_DOCUMENT_TYPE_BY_ITEM = {
    "witness_pan_aadhaar": "witness_pan_aadhaar",
    "cancelled_cheque": "cancelled_cheque",
    "blank_dated_cheque": "blank_dated_cheque",
    "poa": "power_of_attorney",
    "tri_party_agreement": "tri_party_agreement",
    "sh4": "sh4",
    "cdsl_pledge": "cdsl_pledge_evidence",
    "term_sheet": "term_sheet",
    "loan_agreement": "loan_agreement",
    "bank_verification_letter": "bank_verification_letter",
    "final_checklist": "document_checklist",
}

_SENSITIVE_KEY_PARTS = (
    "aadhaar",
    "account_number",
    "bo_account",
    "cheque_hash",
    "cheque_number",
    "pan_number",
)


def require_item_completion_actor(actor):
    _require_actor(
        actor,
        permission=ITEM_COMPLETE_PERMISSION,
        roles={"compliance_team_member", "company_secretary"},
    )


def require_stage_actor(actor, action_type):
    stage = _STAGE[action_type]
    _require_actor(actor, permission=stage["permission"], roles={stage["role"]})


def require_finance_actor(actor):
    _require_actor(
        actor,
        permission="documents.checklist.sign_disbursement_complete",
        roles={"senior_manager_finance"},
    )


def _require_actor(actor, *, permission, roles):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
        or not (set(auth_service.effective_role_codes(actor)) & roles)
    ):
        raise AccessDenied


@transaction.atomic
def complete_item(*, actor, checklist_item_id, payload, metadata):
    require_item_completion_actor(actor)
    request = (
        payload
        if isinstance(payload, ChecklistItemCompletionRequest)
        else ChecklistItemCompletionRequest.parse(payload)
    )
    values = request.as_values()
    item = (
        ChecklistItem.objects.select_for_update()
        .select_related("document_checklist", "document_checklist__loan_application")
        .filter(pk=checklist_item_id)
        .first()
    )
    if item is None:
        raise NotFound
    checklist = item.document_checklist
    case = _require_stage4_scope(checklist)
    existing = (
        ChecklistAction.objects.select_related("workflow_event")
        .filter(
            checklist_item=item,
            action_type=ChecklistAction.TYPE_ITEM_COMPLETION,
        )
        .first()
    )
    if existing is not None:
        if (
            existing.actor_user_id == actor.pk
            and existing.loan_document_id == values["loan_document_id"]
            and existing.comments == values["remarks"]
        ):
            return _action_response(existing)
        raise Conflict("Checklist item completion evidence is immutable.")
    if checklist.checklist_status != DocumentChecklist.STATUS_IN_PROGRESS:
        raise Conflict("Approved checklists cannot be reopened through item completion.")
    if not item.required_flag or not item.applicable_flag:
        raise EvidenceBlocked("Only a current required and applicable item can be completed.")
    if item.completion_status != ChecklistItem.STATUS_PENDING:
        raise Conflict("Retained completion has no durable 008K action identity.")
    document = _current_document(
        application_id=checklist.loan_application_id,
        item=item,
        loan_document_id=values["loan_document_id"],
    )
    terminal_evidence = _terminal_evidence(item=item, document=document)
    previous_status = item.completion_status
    item.loan_document = document
    item.completion_status = ChecklistItem.STATUS_COMPLETE
    item.verified_by_user = actor
    item.verified_at = timezone.now()
    item.remarks = values["remarks"] or ""
    item.save(
        update_fields=[
            "loan_document",
            "completion_status",
            "verified_by_user",
            "verified_at",
            "remarks",
        ]
    )
    context = {
        "loan_application_id": str(checklist.loan_application_id),
        "document_checklist_id": str(checklist.pk),
        "checklist_item_id": str(item.pk),
        "item_code": item.item_code,
        "loan_document_id": str(document.pk),
        "remarks": values["remarks"],
        "consumed_terminal_evidence": terminal_evidence,
        "approval_case_id": str(case.pk),
    }
    action = _create_action(
        actor=actor,
        checklist=checklist,
        item=item,
        document=document,
        action_type=ChecklistAction.TYPE_ITEM_COMPLETION,
        meaning="required applicable item verified complete",
        comments=values["remarks"],
        previous_status=previous_status,
        new_status=ChecklistItem.STATUS_COMPLETE,
        context=context,
        metadata=metadata,
    )
    return _action_response(action)


def approve_company_secretary(**kwargs):
    return _approve(
        action_type=ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL, **kwargs
    )


def approve_credit_manager(**kwargs):
    return _approve(
        action_type=ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL, **kwargs
    )


def approve_sanction_committee(**kwargs):
    return _approve(
        action_type=ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL, **kwargs
    )


@transaction.atomic
def _approve(*, actor, document_checklist_id, payload, metadata, action_type):
    require_stage_actor(actor, action_type)
    request = (
        payload
        if isinstance(payload, ChecklistApprovalRequest)
        else ChecklistApprovalRequest.parse(payload)
    )
    stage = _STAGE[action_type]
    checklist = (
        DocumentChecklist.objects.select_for_update()
        .select_related("loan_application")
        .filter(pk=document_checklist_id)
        .first()
    )
    if checklist is None:
        raise NotFound
    case = _require_stage4_scope(checklist)
    if action_type == ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL:
        _require_eligible_frozen_director(actor, case)
    existing = (
        ChecklistAction.objects.select_related("workflow_event")
        .filter(document_checklist=checklist, action_type=action_type)
        .first()
    )
    if existing is not None:
        if existing.actor_user_id == actor.pk and existing.comments == request.comments:
            return _action_response(existing)
        raise Conflict("Checklist approval evidence is immutable.")
    if checklist.checklist_status != stage["from_status"]:
        raise Conflict(
            "Checklist approvals must follow Company Secretary, Credit Manager, then Sanction Committee.",
            "CHECKLIST_APPROVAL_OUT_OF_ORDER",
        )
    prior = list(
        ChecklistAction.objects.filter(document_checklist=checklist)
        .exclude(action_type=ChecklistAction.TYPE_ITEM_COMPLETION)
        .order_by("signed_at", "checklist_action_id")
    )
    if any(row.actor_user_id == actor.pk for row in prior):
        raise Conflict("Checklist approval stages require distinct signers.")
    if action_type == ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL:
        incomplete = checklist.items.filter(
            required_flag=True,
            applicable_flag=True,
        ).exclude(completion_status=ChecklistItem.STATUS_COMPLETE)
        if incomplete.exists():
            raise EvidenceBlocked("Every required applicable checklist item must be complete.")
    if action_type == ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL:
        try:
            approval_case_engine.validated_frozen_terminal_facts(case)
        except (KeyError, TypeError, ValidationError) as exc:
            raise EvidenceBlocked("Canonical frozen loan-limit review is unavailable.") from exc
    context = {
        "loan_application_id": str(checklist.loan_application_id),
        "document_checklist_id": str(checklist.pk),
        "approval_case_id": str(case.pk),
        "meaning": stage["meaning"],
        "comments": request.comments,
        "prior_approval_action_ids": [str(row.pk) for row in prior],
        "completed_item_action_ids": list(
            checklist.actions.filter(
                action_type=ChecklistAction.TYPE_ITEM_COMPLETION
            ).values_list("checklist_action_id", flat=True)
        ),
    }
    previous_status = checklist.checklist_status
    action = _create_action(
        actor=actor,
        checklist=checklist,
        item=None,
        document=None,
        action_type=action_type,
        meaning=stage["meaning"],
        comments=request.comments,
        previous_status=previous_status,
        new_status=stage["to_status"],
        context=context,
        metadata=metadata,
    )
    setattr(checklist, stage["signature_field"], action)
    checklist.checklist_status = stage["to_status"]
    checklist.updated_at = timezone.now()
    checklist.save(
        update_fields=[stage["signature_field"], "checklist_status", "updated_at"]
    )
    return _action_response(action)


@transaction.atomic
def sign_disbursement_complete(*, actor, document_checklist_id, payload, metadata):
    require_finance_actor(actor)
    request = (
        payload
        if isinstance(payload, ChecklistApprovalRequest)
        else ChecklistApprovalRequest.parse(payload)
    )
    checklist = (
        DocumentChecklist.objects.select_for_update()
        .filter(pk=document_checklist_id)
        .first()
    )
    if checklist is None:
        raise NotFound
    _require_stage4_scope(checklist)
    existing = (
        ChecklistAction.objects.select_related("workflow_event")
        .filter(
            document_checklist=checklist,
            action_type=ChecklistAction.TYPE_DISBURSEMENT_SIGNATURE,
        )
        .first()
    )
    if existing is not None:
        if existing.actor_user_id == actor.pk and existing.comments == request.comments:
            return _action_response(existing)
        raise Conflict("Disbursement signature evidence is immutable.")
    raise Conflict(
        "A real successful disbursement aggregate is required before this signature.",
        "DISBURSEMENT_EVIDENCE_UNAVAILABLE",
    )


def _require_stage4_scope(checklist):
    facts = document_checklist_facts.resolve_approved_facts(
        application_id=checklist.loan_application_id
    )
    case = (
        ApprovalCase.objects.filter(loan_application_id=checklist.loan_application_id)
        .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
        .first()
    )
    creation = (
        AuditLog.objects.filter(
            action="document_checklist.created",
            entity_type="document_checklist",
            entity_id=checklist.pk,
        )
        .order_by("created_at", "audit_log_id")
        .values_list("new_value_json", flat=True)
        .first()
    )
    if (
        facts is None
        or case is None
        or creation is None
        or creation.get("approval_case_id") != str(facts.approval_case_id)
        or creation.get("sanction_decision_id") != str(facts.sanction_decision_id)
        or case.pk != facts.approval_case_id
    ):
        raise NotFound
    return case


def _require_eligible_frozen_director(actor, case):
    committee = case.committee_projection_json
    director_ids = {
        str(user_id) for user_id in committee.get("director_user_ids", []) if user_id
    }
    excluded_ids = {
        str(row.get("user_id"))
        for row in case.excluded_approvers_json
        if isinstance(row, dict) and row.get("user_id")
    }
    if str(actor.pk) not in director_ids or str(actor.pk) in excluded_ids:
        raise AccessDenied("OBJECT_ACCESS_DENIED")


def _current_document(*, application_id, item, loan_document_id):
    expected_type = _DOCUMENT_TYPE_BY_ITEM[item.item_code]
    latest_id = selectors.latest_generated_metadata_by_type(
        application_id=application_id, document_types={expected_type}
    ).get(expected_type)
    if loan_document_id != latest_id:
        raise EvidenceBlocked(
            "The item requires its exact current-renderer same-application document type."
        )
    document = (
        LoanDocument.objects.select_for_update(of=("self",))
        .select_related("document")
        .filter(
            pk=loan_document_id,
            loan_application_id=application_id,
            document_type=expected_type,
            generation_status=LoanDocument.GENERATION_GENERATED,
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=F("document_id"),
            renderer_validated_checksum_sha256=F("document__checksum_sha256"),
        )
        .first()
    )
    if document is None:
        raise EvidenceBlocked(
            "The item requires its exact current-renderer same-application document type."
        )
    if (
        item.item_code
        not in {"cancelled_cheque", "blank_dated_cheque", "poa", "sh4", "cdsl_pledge"}
        and document.verification_status != "verified"
    ):
        raise EvidenceBlocked("The current legal document is not verified.")
    return document


def _terminal_evidence(*, item, document):
    evidence = {
        "renderer_contract_version": document.renderer_contract_version,
        "document_file_id": str(document.document_id),
        "document_checksum_sha256": document.renderer_validated_checksum_sha256,
        "verification_status": document.verification_status,
        "verified_by_user_id": (
            str(document.verified_by_user_id) if document.verified_by_user_id else None
        ),
    }
    signatures = list(
        SignatureRecord.objects.filter(loan_document=document).values(
            "signature_record_id",
            "signer_party_type",
            "signer_party_id",
            "signature_status",
            "signature_mismatch_flag",
            "mismatch_resolution_type",
            "signed_at",
            "captured_by_user_id",
        )
    )
    if any(
        row["signature_status"] != "signed"
        or row["signature_mismatch_flag"]
        or row["signed_at"] is None
        or row["captured_by_user_id"] is None
        for row in signatures
    ):
        raise EvidenceBlocked("Every retained document signature must be terminal and mismatch-free.")
    party_types = {row["signer_party_type"] for row in signatures}
    if item.item_code == "loan_agreement" and not {"borrower", "witness"} <= party_types:
        raise EvidenceBlocked("Loan Agreement requires borrower and witness signatures.")
    if item.item_code == "term_sheet":
        case = (
            ApprovalCase.objects.filter(loan_application_id=document.loan_application_id)
            .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
            .first()
        )
        cfo_id = str((case.committee_projection_json if case else {}).get("cfo_user_id") or "")
        signed_user_ids = {
            str(row["signer_party_id"])
            for row in signatures
            if row["signer_party_type"] == "user" and row["signer_party_id"]
        }
        if not {"borrower", "nominee"} <= party_types or not cfo_id or cfo_id not in signed_user_ids:
            raise EvidenceBlocked("Term Sheet requires borrower, nominee, and frozen CFO signatures.")
    evidence["signature_record_ids"] = [
        str(row["signature_record_id"]) for row in signatures
    ]
    if item.item_code == "poa":
        if item.poa_status != "active" or item.poa_execution_status != "executed":
            raise EvidenceBlocked("Power of Attorney must be terminally active and executed.")
        evidence.update(
            {"poa_status": item.poa_status, "poa_execution_status": item.poa_execution_status}
        )
    elif item.item_code == "sh4":
        projection = selectors.sh4_projection_for_application(
            application_id=item.document_checklist.loan_application_id
        )
        if not projection or projection.get("form_status") != "held_in_custody":
            raise EvidenceBlocked("Physical SH-4 must be held in custody.")
        if projection.get("loan_document_id") != str(document.pk):
            raise EvidenceBlocked("Physical SH-4 custody does not match the current document.")
        evidence["security_ledger"] = projection
    elif item.item_code == "cdsl_pledge":
        projection = selectors.cdsl_pledge_projection_for_application(
            application_id=item.document_checklist.loan_application_id
        )
        if (
            not projection
            or projection.get("pledge_status") != "created"
            or projection.get("pledge_acceptance_status") != "accepted"
            or not projection.get("evidence_document_id")
            or projection.get("evidence_document_id") != str(document.document_id)
        ):
            raise EvidenceBlocked("Demat pledge must be accepted and created from retained evidence.")
        evidence["security_ledger"] = projection
    elif item.item_code in {"blank_dated_cheque", "cancelled_cheque"}:
        projection = selectors.blank_cheque_projection_for_application(
            application_id=item.document_checklist.loan_application_id
        )
        cancelled = (projection or {}).get("cancelled_cheque") or {}
        if (
            not projection
            or projection.get("cheque_status") != "held"
            or projection.get("cheque_number") != "******"
            or cancelled.get("verification_status") != "verified"
            or not projection.get("prepared_by_user_id")
            or not projection.get("custodian_user_id")
            or projection.get("prepared_by_user_id") == projection.get("custodian_user_id")
            or not projection.get("custody_workflow_event_id")
        ):
            raise EvidenceBlocked(
                "Blank-cheque custody and canonical cancelled-cheque verification are required."
            )
        evidence["security_ledger"] = projection
    if item.item_code in {"poa", "loan_agreement"}:
        stamp = StampDutyRecord.objects.filter(loan_document=document).first()
        notary = NotarisationRecord.objects.filter(loan_document=document).first()
        if not stamp or stamp.status != "adequate" or not notary or notary.status != "completed":
            raise EvidenceBlocked("Adequate stamp and completed notarisation are required.")
        evidence.update(
            {
                "stamp_duty_record_id": str(stamp.pk),
                "notarisation_record_id": str(notary.pk),
            }
        )
    return _redact(evidence)


def _create_action(
    *, actor, checklist, item, document, action_type, meaning, comments,
    previous_status, new_status, context, metadata,
):
    action_id = uuid.uuid4()
    evidence = _redact(
        {
            **context,
            "checklist_action_id": str(action_id),
            "action_type": action_type,
            "meaning": meaning,
            "actor_user_id": str(actor.pk),
            "actor_user_name_snapshot": actor.full_name,
            "canonical_role_code": auth_service.effective_role_codes(actor)[0],
            "actor_role_codes": auth_service.effective_role_codes(actor),
            "actor_team_codes": actor.team_codes(),
            "request_id": metadata.request_id,
            "ip_address": metadata.ip_address,
            "user_agent": metadata.user_agent,
        }
    )
    entity_type = "checklist_item" if item else "document_checklist"
    entity_id = item.pk if item else checklist.pk
    workflow = record_workflow_event(
        actor=actor,
        workflow_name="documentation_checklist",
        entity_type=entity_type,
        entity_id=entity_id,
        from_state=previous_status,
        to_state=new_status,
        trigger_reason=action_type,
        action_code=action_type,
        metadata=evidence,
    )
    action = ChecklistAction.objects.create(
        checklist_action_id=action_id,
        document_checklist=checklist,
        checklist_item=item,
        loan_document=document,
        action_type=action_type,
        meaning=meaning,
        comments=comments,
        actor_user=actor,
        actor_user_name_snapshot=actor.full_name,
        canonical_role_code=auth_service.effective_role_codes(actor)[0],
        request_id=metadata.request_id,
        workflow_event=workflow,
    )
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=f"document_checklist.{action_type}",
        entity_type=entity_type,
        entity_id=entity_id,
        old_value_json={"status": previous_status},
        new_value_json=evidence,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type=(
            "checklist_item_completion" if item else "document_checklist_approval"
        ),
        versioned_entity_id=entity_id,
        version_number=str(
            VersionHistory.objects.filter(
                versioned_entity_type=(
                    "checklist_item_completion"
                    if item
                    else "document_checklist_approval"
                ),
                versioned_entity_id=entity_id,
            ).count()
            + 1
        ),
        change_summary=f"document_checklist.{action_type}",
        author_user=actor,
        old_value_json={"status": previous_status},
        new_value_json=evidence,
        effective_from=timezone.localdate(),
    )
    return action


def _action_response(action):
    workflow = action.workflow_event
    return {
        "checklist_action_id": str(action.pk),
        "entity_type": workflow.entity_type,
        "entity_id": str(workflow.entity_id),
        "previous_status": workflow.from_state,
        "new_status": workflow.to_state,
        "workflow_event_id": str(workflow.pk),
        "available_actions": [],
    }


def _redact(value, key=""):
    if isinstance(value, dict):
        return {item_key: _redact(item_value, item_key) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [_redact(item, key) for item in value]
    if any(part in key.lower() for part in _SENSITIVE_KEY_PARTS):
        if isinstance(value, str) and "*" in value:
            return value
        return None if value is None else "[REDACTED]"
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
