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


def _canonical_role(actor, action_type):
    roles = set(auth_service.effective_role_codes(actor))
    if action_type == StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION:
        allowed = ("compliance_team_member", "company_secretary")
    else:
        allowed = ("company_secretary", "credit_manager", "director")
    return next((role for role in allowed if role in roles), None)


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
    current = (
        StaffSignedDocumentCopy.objects.select_for_update()
        .filter(loan_document=document, successor__isnull=True)
        .first()
    )
    open_review = (
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
        .order_by("created_at", "staff_document_review_action_id")
        .first()
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
            "resolves_review_action_id": str(open_review.pk) if open_review else None,
            "remarks": remarks,
        },
    )
    action_id, audit_id, version_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    workspace_action_id = getattr(request, "_workspace_action_id", uuid.uuid4().hex)
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
        "resolves_review_action_id": str(open_review.pk) if open_review else None,
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
        to_state="corrected_signed_copy_uploaded" if open_review else "signed_copy_uploaded",
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
        resolves_review_action=open_review,
        workflow_event=workflow,
        audit_log=audit,
        version_history=history,
    )
    return serialize_signed_copy(row)


@transaction.atomic
def record_review_action(*, actor, checklist_id, action_type, reason, metadata,
                         checklist_item_id=None, loan_document_id=None):
    role = _canonical_role(actor, action_type)
    if role is None:
        raise AccessDenied
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
    stage = (
        "checklist_item"
        if action_type == StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION
        else role
    )
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
    unresolved_ids = {
        row.pk for row in reviews
        if row.action_type != StaffDocumentReviewAction.TYPE_ADD_CONDITION
        and not hasattr(row, "resolved_by_signed_copy")
    }
    return {
        "signed_by_document": {row.loan_document_id: row for row in signed},
        "open_by_item": {
            row.checklist_item_id: row for row in reviews
            if row.pk in unresolved_ids and row.checklist_item_id
        },
        "open_reviews": [row for row in reviews if row.pk in unresolved_ids],
        "conditions": [
            row for row in reviews
            if row.action_type == StaffDocumentReviewAction.TYPE_ADD_CONDITION
        ],
        "all_reviews": reviews,
        "snapshot_ids": [str(row.pk) for row in signed + reviews],
    }


def has_open_blocker(checklist, checklist_item=None):
    query = StaffDocumentReviewAction.objects.filter(
        document_checklist=checklist,
        action_type__in=[
            StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION,
            StaffDocumentReviewAction.TYPE_RETURN_CORRECTION,
        ],
        resolved_by_signed_copy__isnull=True,
    )
    if checklist_item is not None:
        query = query.filter(checklist_item=checklist_item)
    return query.exists()


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
        if exact:
            return serialize_signed_copy(signed, replay=True)
        raise Conflict("Signed-copy action facts are immutable.")
    review = StaffDocumentReviewAction.objects.filter(
        workspace_action_id=workspace_action_id,
        document_checklist__loan_application_id=application_id,
    ).first()
    if review is None or review.actor_user_id != actor.pk:
        return None
    field = "condition" if review.action_type == StaffDocumentReviewAction.TYPE_ADD_CONDITION else "remarks"
    if set(payload) == {field} and payload.get(field) == review.reason and uploaded_file is None:
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
