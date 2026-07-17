"""Durable legal owner for staff signed copies, corrections, returns, and conditions."""

from dataclasses import dataclass
import hashlib
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
    StaffDocumentReviewAction,
    StaffSignedDocumentCopy,
)
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.workflows.events import record_workflow_event


class AccessDenied(Exception):
    pass


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str
    workspace_action_id: str | None = None


def _file_checksum(uploaded_file):
    digest = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        digest.update(chunk)
    uploaded_file.seek(0)
    return digest.hexdigest()


_APPROVAL_STAGE = {
    DocumentChecklist.STATUS_IN_PROGRESS: (
        "company_secretary",
        "company_secretary",
        "documents.checklist.approve_cs",
    ),
    DocumentChecklist.STATUS_CS_APPROVED: (
        "credit_manager",
        "credit_manager",
        "documents.checklist.approve_credit",
    ),
    DocumentChecklist.STATUS_CREDIT_APPROVED: (
        "sanction_committee",
        "director",
        "documents.checklist.approve_sanction",
    ),
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


def _actor_can_authorise(actor, role, permission):
    return (
        role in auth_service.effective_role_codes(actor)
        and permission in auth_service.effective_permission_codes(actor)
    )


def _metadata_body(actor, metadata):
    return {
        "actor_user_id": str(actor.pk),
        "actor_user_name_snapshot": actor.full_name,
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "actor_team_codes": actor.team_codes(),
        "request_id": metadata.request_id,
    }


def _history(*, actor, entity_type, entity_id, action, old, new, history_id=None):
    return VersionHistory.objects.create(
        version_history_id=history_id or uuid.uuid4(),
        versioned_entity_type=entity_type,
        versioned_entity_id=entity_id,
        version_number=str(
            VersionHistory.objects.filter(
                versioned_entity_type=entity_type,
                versioned_entity_id=entity_id,
            ).count() + 1
        ),
        change_summary=action,
        author_user=actor,
        old_value_json=old,
        new_value_json=new,
        effective_from=timezone.localdate(),
    )


def _review_expected_body(row):
    audit_body = row.audit_log.new_value_json
    if not isinstance(audit_body, dict):
        return None
    role_codes = audit_body.get("actor_role_codes")
    if not isinstance(role_codes, list) or row.canonical_role_code not in role_codes:
        return None
    return {
        "review_action_id": str(row.pk),
        "workspace_action_id": row.workspace_action_id,
        "loan_application_id": str(row.document_checklist.loan_application_id),
        "document_checklist_id": str(row.document_checklist_id),
        "checklist_item_id": str(row.checklist_item_id) if row.checklist_item_id else None,
        "loan_document_id": str(row.loan_document_id) if row.loan_document_id else None,
        "action_type": row.action_type,
        "approval_stage": row.approval_stage,
        "reason": row.reason,
        "prior_state": row.prior_state,
        "current_state": row.current_state,
        "workflow_event_id": str(row.workflow_event_id),
        "actor_user_id": str(row.actor_user_id),
        "actor_user_name_snapshot": row.actor_user_name_snapshot,
        "actor_role_codes": role_codes,
        "actor_team_codes": row.actor_team_codes_json,
        "request_id": row.request_id,
        "audit_log_id": str(row.audit_log_id),
        "version_history_id": str(row.version_history_id),
    }


def review_action_is_current(row):
    """Reconcile one immutable review action before it can affect current truth."""
    expected_stage = None
    if row.action_type == StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION:
        if row.checklist_item_id is None or row.loan_document_id is None:
            valid_target = False
        else:
            current_document_id = selectors.latest_generated_metadata_by_type(
                application_id=row.document_checklist.loan_application_id,
                document_types={row.loan_document.document_type},
            ).get(row.loan_document.document_type)
            valid_target = (
                row.approval_stage == "checklist_item"
                and row.canonical_role_code
                in {"compliance_team_member", "company_secretary"}
                and row.checklist_item.document_checklist_id
                == row.document_checklist_id
                and _DOCUMENT_TYPE_BY_ITEM.get(row.checklist_item.item_code)
                == row.loan_document.document_type
                and current_document_id == row.loan_document_id
                and row.loan_document.loan_application_id
                == row.document_checklist.loan_application_id
            )
    else:
        expected_stage = next(
            (
                (status, stage, role)
                for status, (stage, role, _permission) in _APPROVAL_STAGE.items()
                if stage == row.approval_stage
            ),
            None,
        )
        valid_target = (
            expected_stage is not None
            and row.canonical_role_code == expected_stage[2]
            and (
                row.action_type == StaffDocumentReviewAction.TYPE_ADD_CONDITION
                and row.checklist_item_id is None
                and row.loan_document_id is None
                and row.prior_state == expected_stage[0]
                or row.action_type == StaffDocumentReviewAction.TYPE_RETURN_CORRECTION
                and row.checklist_item_id is not None
                and row.loan_document_id is not None
                and row.checklist_item.document_checklist_id == row.document_checklist_id
                and row.checklist_item.item_code == "final_checklist"
                and row.checklist_item.loan_document_id == row.loan_document_id
                and row.prior_state == row.checklist_item.completion_status
                and row.loan_document.loan_application_id
                == row.document_checklist.loan_application_id
            )
        )
    expected_current = (
        "condition_added"
        if row.action_type == StaffDocumentReviewAction.TYPE_ADD_CONDITION
        else "correction_requested"
    )
    workflow_entity = "checklist_item" if row.checklist_item_id else "document_checklist"
    workflow_entity_id = row.checklist_item_id or row.document_checklist_id
    expected_body = _review_expected_body(row)
    if expected_body is None:
        return False
    result = bool(
        valid_target
        and row.current_state == expected_current
        and row.workflow_event.workflow_name == "documentation_review"
        and row.workflow_event.entity_type == workflow_entity
        and row.workflow_event.entity_id == workflow_entity_id
        and row.workflow_event.from_state == row.prior_state
        and row.workflow_event.to_state == row.current_state
        and row.workflow_event.triggered_by_user_id == row.actor_user_id
        and row.workflow_event.trigger_reason == row.action_type
        and row.audit_log.actor_user_id == row.actor_user_id
        and row.audit_log.action == f"legal_documents.{row.action_type}"
        and row.audit_log.entity_type == workflow_entity
        and row.audit_log.entity_id == workflow_entity_id
        and row.audit_log.old_value_json == {"status": row.prior_state}
        and row.audit_log.new_value_json == expected_body
        and row.version_history.versioned_entity_type == "staff_document_review_action"
        and row.version_history.versioned_entity_id == workflow_entity_id
        and row.version_history.change_summary == f"legal_documents.{row.action_type}"
        and row.version_history.author_user_id == row.actor_user_id
        and row.version_history.old_value_json == {"status": row.prior_state}
        and row.version_history.new_value_json == expected_body
        and AuditLog.objects.filter(
            action=f"legal_documents.{row.action_type}",
            entity_type=workflow_entity,
            entity_id=workflow_entity_id,
            new_value_json__review_action_id=str(row.pk),
        ).count() == 1
        and VersionHistory.objects.filter(
            versioned_entity_type="staff_document_review_action",
            versioned_entity_id=workflow_entity_id,
            new_value_json__review_action_id=str(row.pk),
        ).count() == 1
        and AuditLog.objects.filter(
            action=f"legal_documents.{row.action_type}",
            new_value_json__workflow_event_id=str(row.workflow_event_id),
        ).count() == 1
        and VersionHistory.objects.filter(
            versioned_entity_type="staff_document_review_action",
            new_value_json__workflow_event_id=str(row.workflow_event_id),
        ).count() == 1
    )
    return result


def _signed_copy_expected_body(row):
    audit_body = row.audit_log.new_value_json
    if not isinstance(audit_body, dict):
        return None
    role_codes = audit_body.get("actor_role_codes")
    team_codes = audit_body.get("actor_team_codes")
    actor_name = audit_body.get("actor_user_name_snapshot")
    if not isinstance(role_codes, list) or not isinstance(team_codes, list) or not actor_name:
        return None
    return {
        "signed_copy_id": str(row.pk),
        "workspace_action_id": row.workspace_action_id,
        "loan_application_id": str(row.loan_application_id),
        "loan_document_id": str(row.loan_document_id),
        "document_id": str(row.document_id),
        "checksum_sha256": row.checksum_sha256,
        "remarks": row.remarks,
        "supersedes_signed_copy_id": str(row.supersedes_id) if row.supersedes_id else None,
        "resolves_review_action_id": (
            str(row.resolves_review_action_id) if row.resolves_review_action_id else None
        ),
        "audit_log_id": str(row.audit_log_id),
        "version_history_id": str(row.version_history_id),
        "actor_user_id": str(row.uploader_user_id),
        "actor_user_name_snapshot": actor_name,
        "actor_role_codes": role_codes,
        "actor_team_codes": team_codes,
        "request_id": row.request_id,
        "workflow_event_id": str(row.workflow_event_id),
    }


def _signed_copy_row_evidence_is_current(row):
    expected_body = _signed_copy_expected_body(row)
    if expected_body is None:
        return False
    expected_old = {"signed_copy_id": str(row.supersedes_id) if row.supersedes_id else None}
    upload_audits = AuditLog.objects.filter(
        action="documents.file.uploaded",
        entity_type="document_file",
        entity_id=row.document_id,
    )
    upload_audit = upload_audits.first()
    upload_body = upload_audit.new_value_json if upload_audit else None
    return bool(
        row.loan_document.loan_application_id == row.loan_application_id
        and row.document.checksum_sha256 == row.checksum_sha256
        and row.document.uploaded_by_user_id == row.uploader_user_id
        and upload_audits.count() == 1
        and upload_audit.actor_user_id == row.uploader_user_id
        and upload_audit.ip_address == row.audit_log.ip_address
        and upload_audit.user_agent == row.audit_log.user_agent
        and isinstance(upload_body, dict)
        and upload_body.get("document_id") == str(row.document_id)
        and upload_body.get("checksum_sha256") == row.checksum_sha256
        and upload_body.get("related_entity_type") == "loan_document_signed_copy"
        and upload_body.get("related_entity_id") == str(row.loan_document_id)
        and upload_body.get("supersedes_signed_copy_id")
        == (str(row.supersedes_id) if row.supersedes_id else None)
        and upload_body.get("resolves_review_action_id")
        == (str(row.resolves_review_action_id) if row.resolves_review_action_id else None)
        and upload_body.get("remarks") == row.remarks
        and upload_body.get("request_id") == row.request_id
        and upload_body.get("workspace_action_id") == row.workspace_action_id
        and upload_body.get("signed_copy_id") == str(row.pk)
        and row.workflow_event.workflow_name == "staff_signed_document_copy"
        and row.workflow_event.entity_type == "loan_document"
        and row.workflow_event.entity_id == row.loan_document_id
        and row.workflow_event.from_state
        == ("signed_copy_uploaded" if row.supersedes_id else "signed_copy_pending")
        and row.workflow_event.to_state
        == (
            "corrected_signed_copy_uploaded"
            if row.resolves_review_action_id
            else "signed_copy_uploaded"
        )
        and row.workflow_event.triggered_by_user_id == row.uploader_user_id
        and row.workflow_event.trigger_reason == "upload_signed_copy"
        and row.audit_log.actor_user_id == row.uploader_user_id
        and row.audit_log.action == "legal_documents.signed_copy_uploaded"
        and row.audit_log.entity_type == "loan_document"
        and row.audit_log.entity_id == row.loan_document_id
        and row.audit_log.old_value_json == expected_old
        and row.audit_log.new_value_json == expected_body
        and row.version_history.versioned_entity_type == "staff_signed_document_copy"
        and row.version_history.versioned_entity_id == row.loan_document_id
        and row.version_history.change_summary == "legal_documents.signed_copy_uploaded"
        and row.version_history.author_user_id == row.uploader_user_id
        and row.version_history.old_value_json == expected_old
        and row.version_history.new_value_json == expected_body
        and AuditLog.objects.filter(
            action="legal_documents.signed_copy_uploaded",
            entity_type="loan_document",
            entity_id=row.loan_document_id,
            new_value_json__signed_copy_id=str(row.pk),
        ).count() == 1
        and VersionHistory.objects.filter(
            versioned_entity_type="staff_signed_document_copy",
            versioned_entity_id=row.loan_document_id,
            new_value_json__signed_copy_id=str(row.pk),
        ).count() == 1
        and AuditLog.objects.filter(
            action="legal_documents.signed_copy_uploaded",
            new_value_json__workflow_event_id=str(row.workflow_event_id),
        ).count() == 1
        and VersionHistory.objects.filter(
            versioned_entity_type="staff_signed_document_copy",
            new_value_json__workflow_event_id=str(row.workflow_event_id),
        ).count() == 1
        and (
            row.resolves_review_action_id is None
            or (
                row.supersedes_id is not None
                and review_action_is_current(row.resolves_review_action)
                and row.resolves_review_action.action_type
                in {
                    StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION,
                    StaffDocumentReviewAction.TYPE_RETURN_CORRECTION,
                }
                and row.resolves_review_action.document_checklist.loan_application_id
                == row.loan_application_id
                and row.resolves_review_action.loan_document_id == row.loan_document_id
            )
        )
    )


def _current_signed_copy_chain(loan_document_id):
    rows = list(
        StaffSignedDocumentCopy.objects.filter(loan_document_id=loan_document_id)
        .select_related(
            "loan_document",
            "document",
            "uploader_user",
            "workflow_event",
            "audit_log",
            "version_history",
            "resolves_review_action",
        )
        .order_by("created_at", "staff_signed_document_copy_id")
    )
    if not rows:
        return []
    tails = [row for row in rows if not hasattr(row, "successor")]
    if len(tails) != 1:
        return None
    chain = []
    seen = set()
    current = tails[0]
    while current is not None and current.pk not in seen:
        chain.append(current)
        seen.add(current.pk)
        current = current.supersedes
    chain.reverse()
    if len(chain) != len(rows) or any(
        row.loan_application_id != chain[0].loan_application_id
        or row.loan_document_id != loan_document_id
        or not _signed_copy_row_evidence_is_current(row)
        for row in chain
    ):
        return None
    return chain


def signed_copy_is_current(row):
    chain = _current_signed_copy_chain(row.loan_document_id)
    return bool(chain and chain[-1].pk == row.pk)


def _review_is_resolved(row):
    if row.loan_document_id is None:
        return False
    try:
        resolved = row.resolved_by_signed_copy
    except StaffSignedDocumentCopy.DoesNotExist:
        return False
    chain = _current_signed_copy_chain(row.loan_document_id)
    latest = selectors.latest_generated_metadata_by_type(
        application_id=row.document_checklist.loan_application_id,
        document_types={row.loan_document.document_type},
    )
    resolved_index = next(
        (index for index, copy in enumerate(chain or []) if copy.pk == resolved.pk),
        None,
    )
    return bool(
        chain
        and latest.get(row.loan_document.document_type) == row.loan_document_id
        and resolved_index is not None
        and all(
            copy.resolves_review_action_id is not None
            for copy in chain[resolved_index + 1:]
        )
        and resolved.resolves_review_action_id == row.pk
        and resolved.loan_application_id == row.document_checklist.loan_application_id
        and resolved.loan_document_id == row.loan_document_id
    )


@transaction.atomic
def upload_signed_copy(*, actor, application_id, loan_document_id, remarks,
                       uploaded_file, request, metadata):
    if uploaded_file is None:
        raise ValidationError({"file": "A signed document file is required."})
    if not document_services.user_can_upload_documents(actor):
        raise AccessDenied
    LoanApplication.objects.select_for_update().filter(pk=application_id).get()
    document = (
        LoanDocument.objects.select_for_update()
        .select_related("document")
        .filter(pk=loan_document_id, loan_application_id=application_id)
        .first()
    )
    if document is None:
        raise NotFound
    checklist = DocumentChecklist.objects.select_for_update().filter(
        loan_application_id=application_id
    ).first()
    if checklist is None:
        raise NotFound
    checksum = _file_checksum(uploaded_file)
    current_rows = list(
        StaffSignedDocumentCopy.objects.select_for_update()
        .filter(loan_document=document, successor__isnull=True)[:2]
    )
    if len(current_rows) > 1:
        raise Conflict("Signed-copy predecessor chain is ambiguous.")
    current = current_rows[0] if current_rows else None
    if current is not None and not signed_copy_is_current(current):
        raise Conflict("Signed-copy predecessor evidence is not current.")
    open_reviews = list(
        StaffDocumentReviewAction.objects.select_for_update()
        .filter(
            document_checklist=checklist,
            loan_document=document,
            action_type__in=[
                StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION,
                StaffDocumentReviewAction.TYPE_RETURN_CORRECTION,
            ],
            resolved_by_signed_copy__isnull=True,
        )
        .select_related(
            "document_checklist", "checklist_item", "loan_document", "actor_user",
            "workflow_event", "audit_log", "version_history",
        )
        .order_by("created_at", "staff_document_review_action_id")[:2]
    )
    if any(not review_action_is_current(row) for row in open_reviews):
        raise Conflict("Open correction evidence is not current.")
    if len(open_reviews) > 1:
        raise Conflict("Open correction evidence is ambiguous.")
    open_review = open_reviews[0] if open_reviews else None
    resolving_review = open_review if current is not None else None
    action_id, audit_id, version_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    workspace_action_id = (
        metadata.workspace_action_id
        or getattr(request, "_workspace_action_id", uuid.uuid4().hex)
    )
    stored = document_services.store_document_upload(
        user=actor,
        request=request,
        uploaded_file=uploaded_file,
        document_category="legal",
        sensitivity_level="confidential",
        related_entity_type="loan_document_signed_copy",
        related_entity_id=document.pk,
        provenance_metadata={
            "loan_application_id": str(application_id),
            "loan_document_id": str(document.pk),
            "supersedes_signed_copy_id": str(current.pk) if current else None,
            "resolves_review_action_id": (
                str(resolving_review.pk) if resolving_review else None
            ),
            "remarks": remarks,
            "request_id": metadata.request_id,
            "workspace_action_id": workspace_action_id,
            "signed_copy_id": str(action_id),
        },
    )
    old = {"signed_copy_id": str(current.pk) if current else None}
    body = {
        "signed_copy_id": str(action_id),
        "workspace_action_id": workspace_action_id,
        "loan_application_id": str(application_id),
        "loan_document_id": str(document.pk),
        "document_id": str(stored.pk),
        "checksum_sha256": checksum,
        "remarks": remarks,
        "supersedes_signed_copy_id": str(current.pk) if current else None,
        "resolves_review_action_id": (
            str(resolving_review.pk) if resolving_review else None
        ),
        "audit_log_id": str(audit_id),
        "version_history_id": str(version_id),
        **_metadata_body(actor, metadata),
    }
    workflow = record_workflow_event(
        actor=actor,
        workflow_name="staff_signed_document_copy",
        entity_type="loan_document",
        entity_id=document.pk,
        from_state="signed_copy_uploaded" if current else "signed_copy_pending",
        to_state=(
            "corrected_signed_copy_uploaded"
            if resolving_review
            else "signed_copy_uploaded"
        ),
        trigger_reason="upload_signed_copy",
    )
    audit = AuditLog.objects.create(
        audit_log_id=audit_id,
        actor_user=actor,
        actor_type="user",
        action="legal_documents.signed_copy_uploaded",
        entity_type="loan_document",
        entity_id=document.pk,
        old_value_json=old,
        new_value_json={**body, "workflow_event_id": str(workflow.pk)},
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    history = _history(
        actor=actor,
        entity_type="staff_signed_document_copy",
        entity_id=document.pk,
        action="legal_documents.signed_copy_uploaded",
        old=old,
        new={**body, "workflow_event_id": str(workflow.pk), "audit_log_id": str(audit.pk)},
        history_id=version_id,
    )
    row = StaffSignedDocumentCopy.objects.create(
        staff_signed_document_copy_id=action_id,
        workspace_action_id=workspace_action_id,
        loan_application_id=application_id,
        loan_document=document,
        document=stored,
        uploader_user=actor,
        checksum_sha256=checksum,
        remarks=remarks,
        request_id=metadata.request_id,
        supersedes=current,
        resolves_review_action=resolving_review,
        workflow_event=workflow,
        audit_log=audit,
        version_history=history,
    )
    return serialize_signed_copy(row)


@transaction.atomic
def record_review_action(*, actor, checklist_id, action_type, reason, metadata,
                         approval_stage, canonical_role_code,
                         checklist_item_id=None, loan_document_id=None):
    application_id = DocumentChecklist.objects.filter(pk=checklist_id).values_list(
        "loan_application_id", flat=True
    ).first()
    if application_id is None:
        raise NotFound
    LoanApplication.objects.select_for_update().get(pk=application_id)
    checklist = DocumentChecklist.objects.select_for_update().filter(pk=checklist_id).first()
    item = ChecklistItem.objects.select_for_update().filter(
        pk=checklist_item_id, document_checklist=checklist
    ).first() if checklist_item_id else None
    document = LoanDocument.objects.select_for_update().filter(
        pk=loan_document_id, loan_application_id=application_id
    ).first() if loan_document_id else None
    if action_type == StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION and (
        item is None or document is None
    ):
        raise NotFound
    if action_type == StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION:
        current_document_id = selectors.latest_generated_metadata_by_type(
            application_id=application_id,
            document_types={document.document_type},
        ).get(document.document_type)
        valid_authority = (
            approval_stage == "checklist_item"
            and canonical_role_code in {"compliance_team_member", "company_secretary"}
            and _actor_can_authorise(
                actor, canonical_role_code, "documents.checklist.update"
            )
            and _DOCUMENT_TYPE_BY_ITEM.get(item.item_code) == document.document_type
            and current_document_id == document.pk
        )
    else:
        current_stage = _APPROVAL_STAGE.get(checklist.checklist_status)
        valid_authority = (
            current_stage is not None
            and (approval_stage, canonical_role_code) == current_stage[:2]
            and _actor_can_authorise(actor, current_stage[1], current_stage[2])
        )
    if not valid_authority:
        raise AccessDenied
    stage = approval_stage
    role = canonical_role_code
    existing = StaffDocumentReviewAction.objects.select_for_update().filter(
        document_checklist=checklist,
        checklist_item=item,
        loan_document=document,
        action_type=action_type,
        approval_stage=stage,
    )
    if action_type != StaffDocumentReviewAction.TYPE_ADD_CONDITION:
        existing = existing.filter(resolved_by_signed_copy__isnull=True)
    retained = existing.first()
    if retained:
        if (
            retained.workspace_action_id == metadata.workspace_action_id
            and retained.actor_user_id == actor.pk
            and retained.reason == reason
        ):
            return serialize_review_action(retained, replay=True)
        raise Conflict("Current documentation review action is immutable.")
    prior = item.completion_status if item else checklist.checklist_status
    current = "condition_added" if action_type == StaffDocumentReviewAction.TYPE_ADD_CONDITION else "correction_requested"
    action_id, audit_id, version_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    workspace_action_id = metadata.workspace_action_id or uuid.uuid4().hex
    workflow = record_workflow_event(
        actor=actor,
        workflow_name="documentation_review",
        entity_type="checklist_item" if item else "document_checklist",
        entity_id=item.pk if item else checklist.pk,
        from_state=prior,
        to_state=current,
        trigger_reason=action_type,
    )
    body = {
        "review_action_id": str(action_id),
        "workspace_action_id": workspace_action_id,
        "loan_application_id": str(application_id),
        "document_checklist_id": str(checklist.pk),
        "checklist_item_id": str(item.pk) if item else None,
        "loan_document_id": str(document.pk) if document else None,
        "action_type": action_type,
        "approval_stage": stage,
        "reason": reason,
        "prior_state": prior,
        "current_state": current,
        "workflow_event_id": str(workflow.pk),
        **_metadata_body(actor, metadata),
    }
    audit = AuditLog.objects.create(
        audit_log_id=audit_id,
        actor_user=actor,
        actor_type="user",
        action=f"legal_documents.{action_type}",
        entity_type="checklist_item" if item else "document_checklist",
        entity_id=item.pk if item else checklist.pk,
        old_value_json={"status": prior},
        new_value_json={**body, "audit_log_id": str(audit_id), "version_history_id": str(version_id)},
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    history = VersionHistory.objects.create(
        version_history_id=version_id,
        versioned_entity_type="staff_document_review_action",
        versioned_entity_id=item.pk if item else checklist.pk,
        version_number=str(StaffDocumentReviewAction.objects.filter(document_checklist=checklist).count() + 1),
        change_summary=f"legal_documents.{action_type}",
        author_user=actor,
        old_value_json={"status": prior},
        new_value_json={**body, "audit_log_id": str(audit.pk), "version_history_id": str(version_id)},
        effective_from=timezone.localdate(),
    )
    row = StaffDocumentReviewAction.objects.create(
        staff_document_review_action_id=action_id,
        workspace_action_id=workspace_action_id,
        document_checklist=checklist,
        checklist_item=item,
        loan_document=document,
        action_type=action_type,
        approval_stage=stage,
        reason=reason,
        prior_state=prior,
        current_state=current,
        actor_user=actor,
        actor_user_name_snapshot=actor.full_name,
        canonical_role_code=role,
        actor_team_codes_json=actor.team_codes(),
        request_id=metadata.request_id,
        workflow_event=workflow,
        audit_log=audit,
        version_history=history,
    )
    return serialize_review_action(row)


def current_projection(checklist):
    signed = list(
        StaffSignedDocumentCopy.objects.filter(
            loan_application_id=checklist.loan_application_id,
            successor__isnull=True,
        ).select_related("document", "uploader_user")
    )
    reviews = list(
        StaffDocumentReviewAction.objects.filter(document_checklist=checklist)
        .select_related("actor_user", "checklist_item", "loan_document")
    )
    reconciled_ids = {row.pk for row in reviews if review_action_is_current(row)}
    unresolved_ids = {
        row.pk for row in reviews
        if row.pk not in reconciled_ids
        or (
            row.action_type != StaffDocumentReviewAction.TYPE_ADD_CONDITION
            and not _review_is_resolved(row)
        )
    }
    valid_signed = [
        row for row in signed
        if signed_copy_is_current(row)
    ]
    return {
        "signed_by_document": {row.loan_document_id: row for row in valid_signed},
        "open_by_item": {
            row.checklist_item_id: row for row in reviews
            if row.pk in unresolved_ids and row.checklist_item_id
        },
        "open_reviews": [row for row in reviews if row.pk in unresolved_ids],
        "conditions": [
            row for row in reviews
            if row.action_type == StaffDocumentReviewAction.TYPE_ADD_CONDITION
            and row.pk in reconciled_ids
        ],
        "all_reviews": [row for row in reviews if row.pk in reconciled_ids],
        "snapshot_ids": [
            f"{row.pk}:{'current' if row in valid_signed else 'invalid'}"
            for row in signed
        ] + [
            f"{row.pk}:{'current' if row.pk in reconciled_ids else 'invalid'}:"
            f"{'open' if row.pk in unresolved_ids else 'resolved'}"
            for row in reviews
        ],
    }


def has_open_blocker(checklist, checklist_item=None):
    query = StaffDocumentReviewAction.objects.filter(
        document_checklist=checklist,
    ).select_related(
        "document_checklist",
        "checklist_item",
        "loan_document",
        "actor_user",
        "workflow_event",
        "audit_log",
        "version_history",
    )
    if checklist_item is not None:
        query = query.filter(checklist_item=checklist_item)
    for row in query:
        if not review_action_is_current(row):
            return True
        if (
            row.action_type != StaffDocumentReviewAction.TYPE_ADD_CONDITION
            and not _review_is_resolved(row)
        ):
            return True
    return False


def replay_workspace_action(*, actor, application_id, workspace_action_id,
                            payload, uploaded_file):
    signed = StaffSignedDocumentCopy.objects.filter(
        workspace_action_id=workspace_action_id,
        loan_application_id=application_id,
    ).first()
    if signed is not None:
        if signed.uploader_user_id != actor.pk:
            return None
        exact = (
            uploaded_file is not None
            and _file_checksum(uploaded_file) == signed.checksum_sha256
            and payload.get("remarks") == signed.remarks
            and set(payload) == {"remarks"}
        )
        if exact and signed_copy_is_current(signed):
            return serialize_signed_copy(signed, replay=True)
        if exact:
            raise Conflict("Signed-copy action evidence is no longer current.")
        raise Conflict("Signed-copy action facts are immutable.")
    review = StaffDocumentReviewAction.objects.filter(
        workspace_action_id=workspace_action_id,
        document_checklist__loan_application_id=application_id,
    ).first()
    if review is None or review.actor_user_id != actor.pk:
        return None
    field = "condition" if review.action_type == StaffDocumentReviewAction.TYPE_ADD_CONDITION else "remarks"
    if (
        set(payload) == {field}
        and payload.get(field) == review.reason
        and uploaded_file is None
        and review_action_is_current(review)
    ):
        return serialize_review_action(review, replay=True)
    raise Conflict("Documentation review action facts are immutable.")


def serialize_signed_copy(row, replay=False):
    return {
        "action_code": "upload_signed_copy",
        "signed_copy_id": str(row.pk),
        "entity_type": "loan_document",
        "entity_id": str(row.loan_document_id),
        "previous_status": "signed_copy_uploaded" if row.supersedes_id else "signed_copy_pending",
        "new_status": "signed_copy_uploaded",
        "workflow_event_id": str(row.workflow_event_id),
        "replay": replay,
        "available_actions": [],
    }


def serialize_review_action(row, replay=False):
    return {
        "action_code": row.action_type,
        "review_action_id": str(row.pk),
        "entity_type": "checklist_item" if row.checklist_item_id else "document_checklist",
        "entity_id": str(row.checklist_item_id or row.document_checklist_id),
        "previous_status": row.prior_state,
        "new_status": row.current_state,
        "workflow_event_id": str(row.workflow_event_id),
        "replay": replay,
        "available_actions": [],
    }
