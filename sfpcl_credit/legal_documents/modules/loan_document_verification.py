from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.approvals.modules import document_checklist_facts
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.legal_documents.models import ChecklistItem
from sfpcl_credit.legal_documents.modules import document_authority
from sfpcl_credit.legal_documents.request_contracts import LoanDocumentVerificationRequest
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.models import WorkflowEvent


VERIFY_PERMISSION = "documents.loan_document.verify"
ACTION = "loan_document.tri_party_verified"


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


AccessDenied = document_authority.AccessDenied
NotFound = document_authority.NotFound


class Conflict(Exception):
    pass


def require_verify_actor(actor):
    document_authority.require_mutation_actor(actor=actor, permission=VERIFY_PERMISSION)
    try:
        document_authority.require_company_secretary(actor)
    except document_authority.RoleAuthorityDenied:
        raise AccessDenied


def verify(*, actor, loan_document_id, payload, metadata):
    require_verify_actor(actor)
    request = (
        payload
        if isinstance(payload, LoanDocumentVerificationRequest)
        else LoanDocumentVerificationRequest.parse(payload)
    )
    values = request.as_values()
    with transaction.atomic():
        try:
            document = document_authority.resolve_current_stage4_target(
                actor=actor,
                permission=VERIFY_PERMISSION,
                loan_document_id=loan_document_id,
                for_update=True,
            )
        except document_authority.ProvenanceConflict:
            raise Conflict("Retained output is not bound to the current renderer contract.")
        if document.document_type != "tri_party_agreement":
            raise NotFound
        facts = document_checklist_facts.resolve_approved_facts(
            application_id=document.loan_application_id
        )
        if facts is None or facts.subsidiary_route is not True:
            raise Conflict(
                "Frozen subsidiary repayment applicability is not unanimously true."
            )
        rows = selectors.execution_signature_facts_for_document(
            application_id=document.loan_application_id,
            loan_document_id=document.pk,
            for_update=True,
        )
        _validate_execution_rows(document, rows, actor)
        _require_projection_target(document)
        old = serialize(document)
        if (
            document.verification_status == "verified"
            and document.verification_remarks == values["remarks"]
        ):
            workflow_event = (
                WorkflowEvent.objects.filter(
                    workflow_name="loan_document_verification",
                    entity_id=document.pk,
                )
                .order_by("-created_at", "-workflow_event_id")
                .first()
            )
            if workflow_event is None:
                raise Conflict("Verified execution has no retained workflow identity.")
            return _action_response(document, workflow_event)
        document.verification_status = "verified"
        document.verification_remarks = values["remarks"]
        document.verified_by_user = actor
        document.verified_at = timezone.now()
        document.save(
            update_fields=[
                "verification_status",
                "verification_remarks",
                "verified_by_user",
                "verified_at",
            ]
        )
        result = serialize(document)
        workflow_event = _record_evidence(actor, document, rows, old, result, metadata)
        return _action_response(document, workflow_event)


def _validate_execution_rows(document, rows, actor):
    expected = {
        "borrower": document.loan_application.member_id,
        "nominee": document.loan_application.nominee_id,
    }
    by_type = {row["signer_party_type"]: row for row in rows}
    valid = len(rows) == 2 and expected["nominee"] is not None
    for party_type, party_id in expected.items():
        row = by_type.get(party_type)
        valid = valid and bool(
            row
            and row["signer_party_id"] == party_id
            and row["signer_name_snapshot"].strip()
            and row["signature_status"] == "signed"
            and row["signed_at"] is not None
            and not row["signature_mismatch_flag"]
            and row["mismatch_resolution_type"] is None
            and row["captured_by_user_id"] is not None
            and row["captured_by_user_id"] != actor.pk
        )
    if not valid:
        raise Conflict(
            "Distinct current borrower and nominee execution signatures are required."
        )


def _require_projection_target(document):
    item = (
        ChecklistItem.objects.select_for_update()
        .filter(
            document_checklist__loan_application_id=document.loan_application_id,
            item_code="tri_party_agreement",
        )
        .first()
    )
    if (
        item is None
        or not item.required_flag
        or not item.applicable_flag
        or item.loan_document_id != document.pk
    ):
        raise Conflict(
            "Current applicable tri-party checklist projection was not found."
        )


def serialize(document):
    return {
        "loan_document_id": str(document.pk),
        "loan_application_id": str(document.loan_application_id),
        "document_type": document.document_type,
        "verification_status": document.verification_status,
        "verified_by_user_id": (
            str(document.verified_by_user_id) if document.verified_by_user_id else None
        ),
        "verified_at": (
            document.verified_at.isoformat().replace("+00:00", "Z")
            if document.verified_at
            else None
        ),
        "remarks": document.verification_remarks,
    }


def _action_response(document, workflow_event):
    return {
        "entity_type": "loan_document",
        "entity_id": str(document.pk),
        "previous_status": workflow_event.from_state,
        "new_status": workflow_event.to_state,
        "workflow_event_id": str(workflow_event.pk),
        "available_actions": [],
    }


def _record_evidence(actor, document, rows, old, new, metadata):
    context = {
        **new,
        "borrower_member_id": str(document.loan_application.member_id),
        "nominee_id": str(document.loan_application.nominee_id),
        "signature_record_ids": [str(row["signature_record_id"]) for row in rows],
        "consumed_signatures": [
            {
                "signature_record_id": str(row["signature_record_id"]),
                "signer_party_type": row["signer_party_type"],
                "signer_party_id": str(row["signer_party_id"]),
                "signer_name_snapshot": row["signer_name_snapshot"],
                "captured_by_user_id": str(row["captured_by_user_id"]),
                "signed_at": row["signed_at"].isoformat().replace("+00:00", "Z"),
            }
            for row in rows
        ],
        "actor_role_codes": actor.role_codes(),
        "actor_team_codes": actor.team_codes(),
        "request_id": metadata.request_id,
        "ip_address": metadata.ip_address,
        "user_agent": metadata.user_agent,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=ACTION,
        entity_type="loan_document",
        entity_id=document.pk,
        old_value_json=old,
        new_value_json=context,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type="loan_document_verification",
        versioned_entity_id=document.pk,
        version_number=str(
            VersionHistory.objects.filter(
                versioned_entity_type="loan_document_verification",
                versioned_entity_id=document.pk,
            ).count()
            + 1
        ),
        change_summary=ACTION,
        author_user=actor,
        old_value_json=old,
        new_value_json=context,
        effective_from=timezone.localdate(),
    )
    return record_workflow_event(
        actor=actor,
        workflow_name="loan_document_verification",
        entity_type="loan_document",
        entity_id=document.pk,
        from_state=old["verification_status"],
        to_state="verified",
        trigger_reason=ACTION,
        action_code=ACTION,
        metadata=context,
    )


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
