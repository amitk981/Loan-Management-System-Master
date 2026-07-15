import hashlib
import json
import uuid
from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.approvals.modules import approval_case_engine
from sfpcl_credit.approvals.modules import document_checklist_facts
from sfpcl_credit.applications.models import LoanApplication, Witness
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.shared.masking import redact_sensitive_mapping
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
def complete_item(
    *, actor, checklist_item_id, payload, metadata, terminal_security_evidence=None
):
    require_item_completion_actor(actor)
    request = (
        payload
        if isinstance(payload, ChecklistItemCompletionRequest)
        else ChecklistItemCompletionRequest.parse(payload)
    )
    values = request.as_values()
    application_id = (
        ChecklistItem.objects.filter(pk=checklist_item_id)
        .values_list("document_checklist__loan_application_id", flat=True)
        .first()
    )
    if application_id is None:
        raise NotFound
    LoanApplication.objects.select_for_update().get(pk=application_id)
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
    terminal_evidence = _terminal_evidence(
        item=item,
        document=document,
        terminal_security_evidence=terminal_security_evidence,
    )
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
        "terminal_evidence_digest": _evidence_digest(terminal_evidence),
        "verified_by_user_id": str(actor.pk),
        "verified_at": item.verified_at.isoformat(),
        "required_flag": item.required_flag,
        "applicable_flag": item.applicable_flag,
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
        canonical_role_code=_completion_role(actor),
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
def _approve(
    *, actor, document_checklist_id, payload, metadata, action_type,
    terminal_security_evidence=None,
):
    require_stage_actor(actor, action_type)
    request = (
        payload
        if isinstance(payload, ChecklistApprovalRequest)
        else ChecklistApprovalRequest.parse(payload)
    )
    stage = _STAGE[action_type]
    application_id = (
        DocumentChecklist.objects.filter(pk=document_checklist_id)
        .values_list("loan_application_id", flat=True)
        .first()
    )
    if application_id is None:
        raise NotFound
    LoanApplication.objects.select_for_update().get(pk=application_id)
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
        _reconcile_completion_actions(
            checklist=checklist,
            case=case,
            terminal_security_evidence=terminal_security_evidence,
        )
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
        canonical_role_code=stage["role"],
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


def _terminal_evidence(*, item, document, terminal_security_evidence=None):
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
    required_parties = {
        "poa": {"borrower", "nominee"},
        "tri_party_agreement": {"borrower", "nominee"},
        "sh4": {"borrower", "witness"},
        "term_sheet": {"borrower", "nominee"},
        "loan_agreement": {"borrower", "witness"},
    }.get(item.item_code, set())
    if not required_parties <= party_types:
        raise EvidenceBlocked(
            f"{item.item_label} requires its exact canonical signatures."
        )
    application = document.loan_application
    expected_party_ids = {
        "borrower": {str(application.member_id)},
        "nominee": {str(application.nominee_id)} if application.nominee_id else set(),
        "witness": {
            str(value)
            for value in Witness.objects.filter(
                loan_application_id=application.pk,
                verification_status="verified",
                shareholder_verified_flag=True,
            ).values_list("witness_id", flat=True)
        },
    }
    for party_type in required_parties:
        retained_ids = {
            str(row["signer_party_id"])
            for row in signatures
            if row["signer_party_type"] == party_type and row["signer_party_id"]
        }
        if retained_ids != expected_party_ids[party_type]:
            raise EvidenceBlocked(
                f"{item.item_label} signature identity is not current."
            )
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
        director_ids = {
            str(value)
            for value in (case.committee_projection_json if case else {}).get(
                "director_user_ids", []
            )
            if value
        }
        excluded_ids = {
            str(row.get("user_id"))
            for row in (case.excluded_approvers_json if case else [])
            if isinstance(row, dict) and row.get("user_id")
        }
        eligible_director_ids = director_ids - excluded_ids
        try:
            frozen = approval_case_engine.validated_frozen_terminal_facts(case)
            above_threshold = Decimal(str(frozen["recommended_amount"])) > Decimal("500000.00")
        except (KeyError, TypeError, ValidationError) as exc:
            raise EvidenceBlocked("Canonical frozen Term Sheet routing is unavailable.") from exc
        signed_directors = signed_user_ids & eligible_director_ids
        if (
            not {"borrower", "nominee"} <= party_types
            or not cfo_id
            or cfo_id not in signed_user_ids
            or (above_threshold and len(signed_directors) < 2)
        ):
            raise EvidenceBlocked("Term Sheet requires borrower, nominee, and frozen CFO signatures.")
    evidence["signature_record_ids"] = [
        str(row["signature_record_id"]) for row in signatures
    ]
    if item.item_code in {"poa", "sh4", "cdsl_pledge", "blank_dated_cheque", "cancelled_cheque"}:
        security = (
            terminal_security_evidence(
                item_code=item.item_code,
                application_id=item.document_checklist.loan_application_id,
                document=document,
            )
            if terminal_security_evidence is not None
            else None
        )
        if not security:
            raise EvidenceBlocked("Current source-owned security evidence is required.")
        evidence["security_ledger"] = security
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


def _completion_role(actor):
    roles = set(auth_service.effective_role_codes(actor))
    allowed = {"compliance_team_member", "company_secretary"}
    primary = actor.primary_role.role_code
    if primary in roles & allowed:
        return primary
    return sorted(roles & allowed)[0]


def _evidence_digest(evidence):
    canonical = json.dumps(
        evidence,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


@transaction.atomic
def borrower_safe_completed_item_ids(checklist, *, terminal_security_evidence=None):
    """Project only completion evidence reconciled by the checklist owner."""
    if terminal_security_evidence is None:
        return set()
    application = (
        LoanApplication.objects.select_for_update()
        .filter(pk=checklist.loan_application_id)
        .first()
    )
    checklist = (
        DocumentChecklist.objects.select_for_update()
        .filter(pk=checklist.pk, loan_application=application)
        .first()
    )
    if application is None or checklist is None:
        return set()
    try:
        case = _require_stage4_scope(checklist)
    except (EvidenceBlocked, Conflict, ValidationError):
        return set()
    items = list(
        checklist.items.select_for_update(of=("self",)).select_related("loan_document")
    )
    actions = ChecklistAction.objects.select_related(
        "workflow_event", "audit_log", "version_history"
    ).filter(
        document_checklist=checklist, action_type=ChecklistAction.TYPE_ITEM_COMPLETION)
    by_item = {}
    for action in actions:
        by_item.setdefault(action.checklist_item_id, []).append(action)
    histories = VersionHistory.objects.filter(
        versioned_entity_type="checklist_item_completion",
        versioned_entity_id__in=[item.pk for item in items])
    by_history = {}
    for history in histories:
        by_history.setdefault(history.versioned_entity_id, []).append(history)
    completed = set()
    for item in items:
        item_actions, item_histories = by_item.get(item.pk, []), by_history.get(item.pk, [])
        if len(item_actions) != 1 or len(item_histories) != 1:
            continue
        action, history = item_actions[0], item_histories[0]
        retained = history.new_value_json or {}
        terminal = retained.get("consumed_terminal_evidence")
        expected = {
            "checklist_action_id": str(action.pk),
            "loan_application_id": str(checklist.loan_application_id),
            "document_checklist_id": str(checklist.pk),
            "checklist_item_id": str(item.pk), "item_code": item.item_code,
            "loan_document_id": str(item.loan_document_id), "remarks": item.remarks or None,
            "verified_by_user_id": str(item.verified_by_user_id),
            "verified_at": item.verified_at.isoformat() if item.verified_at else None,
            "required_flag": item.required_flag, "applicable_flag": item.applicable_flag,
            "actor_user_id": str(action.actor_user_id),
            "canonical_role_code": action.canonical_role_code,
            "approval_case_id": str(case.pk),
            "request_id": action.request_id,
        }
        workflow = action.workflow_event
        audits = list(AuditLog.objects.filter(
            action="document_checklist.item_completion",
            entity_type="checklist_item", entity_id=item.pk)[:2])
        try:
            document = _current_document(
                application_id=checklist.loan_application_id,
                item=item,
                loan_document_id=item.loan_document_id,
            )
            current_terminal = _terminal_evidence(
                item=item,
                document=document,
                terminal_security_evidence=terminal_security_evidence,
            )
        except (EvidenceBlocked, ValidationError):
            continue
        if (item.required_flag and item.applicable_flag
                and item.completion_status == ChecklistItem.STATUS_COMPLETE
                and item.loan_document_id and item.verified_by_user_id
                and action.loan_document_id == item.loan_document_id
                and action.actor_user_id == item.verified_by_user_id
                and action.signed_at == item.verified_at
                and workflow.entity_type == "checklist_item"
                and workflow.entity_id == item.pk
                and workflow.from_state == ChecklistItem.STATUS_PENDING
                and workflow.to_state == ChecklistItem.STATUS_COMPLETE
                and workflow.triggered_by_user_id == action.actor_user_id
                and workflow.trigger_reason == ChecklistAction.TYPE_ITEM_COMPLETION
                and action.audit_log_id == audits[0].pk if len(audits) == 1 else False
                and action.version_history_id == history.pk
                and audits[0].actor_user_id == action.actor_user_id
                and (audits[0].new_value_json or {}) == retained
                and history.author_user_id == action.actor_user_id
                and history.change_summary == "document_checklist.item_completion"
                and history.version_number == "1"
                and all(retained.get(key) == value for key, value in expected.items())
                and terminal == current_terminal
                and retained.get("terminal_evidence_digest") == _evidence_digest(current_terminal)):
            completed.add(item.pk)
    return completed


def _reconcile_completion_actions(*, checklist, case, terminal_security_evidence):
    items = list(
        checklist.items.select_for_update(of=("self",))
        .select_related("loan_document")
        .filter(required_flag=True, applicable_flag=True)
        .order_by("display_order", "checklist_item_id")
    )
    actions = list(
        ChecklistAction.objects.select_for_update()
        .filter(
            document_checklist=checklist,
            action_type=ChecklistAction.TYPE_ITEM_COMPLETION,
        )
        .order_by("checklist_action_id")
    )
    by_item = {row.checklist_item_id: row for row in actions}
    if len(actions) != len(items) or len(by_item) != len(items):
        raise EvidenceBlocked(
            "Every current required applicable item needs exactly one completion action."
        )
    for item in items:
        action = by_item.get(item.pk)
        if (
            action is None
            or item.completion_status != ChecklistItem.STATUS_COMPLETE
            or not item.loan_document_id
            or not item.verified_by_user_id
            or not item.verified_at
            or action.loan_document_id != item.loan_document_id
            or action.actor_user_id != item.verified_by_user_id
            or (action.comments or "") != (item.remarks or "")
            or action.signed_at != item.verified_at
            or not action.audit_log_id
            or not action.version_history_id
            or action.canonical_role_code
            not in {"compliance_team_member", "company_secretary"}
        ):
            raise EvidenceBlocked("Checklist item and completion action evidence do not match.")
        document = _current_document(
            application_id=checklist.loan_application_id,
            item=item,
            loan_document_id=item.loan_document_id,
        )
        terminal = _terminal_evidence(
            item=item,
            document=document,
            terminal_security_evidence=terminal_security_evidence,
        )
        histories = list(
            VersionHistory.objects.filter(
                versioned_entity_type="checklist_item_completion",
                versioned_entity_id=item.pk,
            )[:2]
        )
        if (
            len(histories) != 1
            or action.version_history_id != histories[0].pk
            or (histories[0].new_value_json or {}).get("checklist_action_id")
            != str(action.pk)
        ):
            raise EvidenceBlocked("Completion action history is missing or ambiguous.")
        history = histories[0]
        retained = history.new_value_json or {}
        expected = {
            "loan_application_id": str(checklist.loan_application_id),
            "document_checklist_id": str(checklist.pk),
            "checklist_item_id": str(item.pk),
            "item_code": item.item_code,
            "loan_document_id": str(item.loan_document_id),
            "remarks": item.remarks or None,
            "verified_by_user_id": str(item.verified_by_user_id),
            "verified_at": item.verified_at.isoformat(),
            "required_flag": True,
            "applicable_flag": True,
            "approval_case_id": str(case.pk),
            "terminal_evidence_digest": _evidence_digest(terminal),
            "actor_user_id": str(action.actor_user_id),
            "actor_user_name_snapshot": action.actor_user_name_snapshot,
            "canonical_role_code": action.canonical_role_code,
            "request_id": action.request_id,
        }
        if any(retained.get(key) != value for key, value in expected.items()):
            raise EvidenceBlocked("Completion action does not match current terminal evidence.")
        audits = list(
            AuditLog.objects.filter(
                action="document_checklist.item_completion",
                entity_type="checklist_item",
                entity_id=item.pk,
            )[:2]
        )
        workflow = action.workflow_event
        if (
            len(audits) != 1
            or action.audit_log_id != audits[0].pk
            or audits[0].actor_user_id != action.actor_user_id
            or (audits[0].old_value_json or {})
            != {"status": ChecklistItem.STATUS_PENDING}
            or (audits[0].new_value_json or {}) != retained
            or history.author_user_id != action.actor_user_id
            or history.version_number != "1"
            or history.change_summary != "document_checklist.item_completion"
            or (history.old_value_json or {})
            != {"status": ChecklistItem.STATUS_PENDING}
            or workflow.entity_type != "checklist_item"
            or workflow.entity_id != item.pk
            or workflow.from_state != ChecklistItem.STATUS_PENDING
            or workflow.to_state != ChecklistItem.STATUS_COMPLETE
            or workflow.triggered_by_user_id != action.actor_user_id
            or workflow.trigger_reason != ChecklistAction.TYPE_ITEM_COMPLETION
        ):
            raise EvidenceBlocked(
                "Completion action audit, workflow, and version evidence do not match."
            )
        retained_terminal = retained.get("consumed_terminal_evidence")
        if (
            retained_terminal != terminal
            or _evidence_digest(retained_terminal) != retained.get("terminal_evidence_digest")
        ):
            raise EvidenceBlocked("Retained completion evidence body and digest do not match.")


def _create_action(
    *, actor, checklist, item, document, action_type, meaning, comments,
    previous_status, new_status, context, metadata, canonical_role_code,
):
    action_id = uuid.uuid4()
    audit_id = uuid.uuid4()
    version_id = uuid.uuid4()
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
    )
    evidence = _redact(
        {
            **context,
            "checklist_action_id": str(action_id),
            "workflow_event_id": str(workflow.pk),
            "audit_log_id": str(audit_id),
            "version_history_id": str(version_id),
            "action_type": action_type,
            "meaning": meaning,
            "actor_user_id": str(actor.pk),
            "actor_user_name_snapshot": actor.full_name,
            "canonical_role_code": canonical_role_code,
            "actor_role_codes": auth_service.effective_role_codes(actor),
            "actor_team_codes": actor.team_codes(),
            "request_id": metadata.request_id,
            "ip_address": metadata.ip_address,
            "user_agent": metadata.user_agent,
        }
    )
    audit = AuditLog.objects.create(
        audit_log_id=audit_id,
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
    history = VersionHistory.objects.create(
        version_history_id=version_id,
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
        canonical_role_code=canonical_role_code,
        request_id=metadata.request_id,
        workflow_event=workflow,
        audit_log=audit,
        version_history=history,
        signed_at=item.verified_at if item else timezone.now(),
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


_redact = redact_sensitive_mapping


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
