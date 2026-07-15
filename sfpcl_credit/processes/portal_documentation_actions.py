"""Borrower-safe post-sanction documentation projection and actions."""
from dataclasses import dataclass
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.modules import document_checklist_facts
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog, PortalAccount
from sfpcl_credit.legal_documents.modules import checklist_actions
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    PortalDocumentationSubmission,
)
UPLOAD_ACTION_CODES = frozenset(
    {
        "cancelled_cheque",
        "poa",
        "tri_party_agreement",
        "sh4",
        "term_sheet",
        "loan_agreement",
        "bank_verification_letter",
    }
)
_ACTION_PRESENTATION = {
    "witness_pan_aadhaar": ("Identity", "Witness PAN and Aadhaar are verified internally."),
    "cancelled_cheque": ("Bank", "Upload a clear cancelled-cheque copy for internal bank verification."),
    "blank_dated_cheque": ("Security", "Submit the original physically; only custody status is shown here."),
    "poa": ("Legal", "Upload the signed Power of Attorney for internal stamp, notary, and signature review."),
    "tri_party_agreement": ("Legal", "Upload the signed agreement when subsidiary repayment applies."),
    "sh4": ("Security", "Upload the signed SH-4 and submit the original physically."),
    "cdsl_pledge": ("Security", "SFPCL will update the pledge status after depository processing."),
    "term_sheet": ("Sanction", "Download the current Term Sheet, sign it, and upload the signed copy."),
    "loan_agreement": ("Legal", "Download the current Loan Agreement, sign it, and upload the signed copy."),
    "bank_verification_letter": ("Bank", "Upload the requested bank letter or borrower declaration."),
    "final_checklist": ("Approval", "Final verification and approval are completed only by SFPCL."),
}
class PortalDocumentationNotFound(Exception):
    pass
class PortalDocumentationUnavailable(Exception):
    pass
@dataclass(frozen=True)
class PortalDocumentationContext:
    account: PortalAccount
    application: LoanApplication
@dataclass(frozen=True)
class PortalDocumentContent:
    body: bytes
    file_name: str
    mime_type: str
def resolve_context(*, actor, application_id):
    account = (
        PortalAccount.objects.select_related("member")
        .filter(
            user=actor,
            status=PortalAccount.STATUS_ACTIVE,
            member__is_deleted=False,
        )
        .first()
    )
    application = (
        LoanApplication.objects.select_related("member")
        .filter(pk=application_id, member_id=account.member_id if account else None)
        .first()
    )
    if account is None or application is None:
        raise PortalDocumentationNotFound
    return PortalDocumentationContext(account=account, application=application)
def get_projection(*, actor, application_id):
    context = resolve_context(actor=actor, application_id=application_id)
    application = context.application
    base = {
        "loan_application_id": str(application.pk),
        "application_reference_number": application.application_reference_number,
        "application_status": application.application_status,
    }
    approved_facts = document_checklist_facts.resolve_approved_facts(
        application_id=application.pk
    )
    if (
        application.application_status != LoanApplication.STATUS_APPROVED_BY_SANCTION
        or approved_facts is None
    ):
        return {
            **base,
            "availability": "blocked",
            "unavailable_reason": "Documentation actions are available after a current sanction approval.",
            "actions": [],
        }
    checklist = (
        DocumentChecklist.objects.prefetch_related("items__loan_document__document")
        .filter(loan_application=application)
        .first()
    )
    if checklist is None:
        return {
            **base,
            "availability": "blocked",
            "unavailable_reason": "The post-sanction documentation checklist is not available yet.",
            "actions": [],
        }
    completion_action_item_ids = checklist_actions.borrower_safe_completed_item_ids(checklist)
    current_submissions = {
        row.action_code: row
        for row in PortalDocumentationSubmission.objects.filter(
            loan_application=application,
            successor__isnull=True,
        ).select_related("document")
    }
    return {
        **base,
        "availability": "available",
        "unavailable_reason": None,
        "actions": [
            _serialize_item(
                item,
                checklist,
                completion_action_item_ids,
                current_submissions.get(item.item_code),
            )
            for item in checklist.items.order_by("display_order", "checklist_item_id")
        ],
    }
def _serialize_item(item, checklist, completion_action_item_ids, submission):
    section, instruction = _ACTION_PRESENTATION[item.item_code]
    reconciled_complete = (
        item.completion_status == ChecklistItem.STATUS_COMPLETE
        and item.pk in completion_action_item_ids
    )
    status = (
        "not_required"
        if not item.applicable_flag
        else "complete"
        if reconciled_complete
        else "submitted"
        if submission
        else "pending_borrower"
    )
    upload_allowed = bool(
        item.required_flag
        and item.applicable_flag
        and not reconciled_complete
        and item.item_code in UPLOAD_ACTION_CODES
        and submission is None
    )
    return {
        "action_code": item.item_code,
        "label": item.item_label,
        "section": section,
        "required": item.required_flag,
        "applicable": item.applicable_flag,
        "status": status,
        "updated_date": (
            submission.created_at.date().isoformat()
            if submission
            else checklist.updated_at.date().isoformat()
        ),
        "instruction": instruction,
        "note": (
            "This requirement is currently blocked pending canonical applicability facts."
            if item.applicability_blocker
            else None
        ),
        "upload_allowed": upload_allowed,
        "reupload_allowed": bool(
            item.required_flag and item.applicable_flag and submission and not reconciled_complete),
        "download": _download_metadata(item),
    }
def _download_metadata(item):
    document = item.loan_document
    if (
        item.item_code not in {"term_sheet", "loan_agreement"}
        or document is None
        or document.document is None
        or document.renderer_validation_status != document.RENDERER_CURRENT_VALIDATED
    ):
        return None
    return {
        "file_name": document.document.file_name,
        "mime_type": document.document.mime_type,
        "action_url": (
            f"/api/v1/portal/applications/{item.document_checklist.loan_application_id}/"
            f"documentation-actions/{item.item_code}/download/"
        ),
    }
@transaction.atomic
def upload(*, actor, application_id, action_code, request):
    context = resolve_context(actor=actor, application_id=application_id)
    application = LoanApplication.objects.select_for_update().get(pk=context.application.pk)
    if (
        application.application_status != LoanApplication.STATUS_APPROVED_BY_SANCTION
        or document_checklist_facts.resolve_approved_facts(application_id=application.pk) is None
    ):
        raise PortalDocumentationUnavailable(
            "Documentation uploads require a current sanction approval."
        )
    checklist = DocumentChecklist.objects.select_for_update().filter(
        loan_application=application
    ).first()
    item = (
        ChecklistItem.objects.select_for_update()
        .filter(document_checklist=checklist, item_code=action_code)
        .first()
        if checklist
        else None
    )
    if (
        action_code not in UPLOAD_ACTION_CODES
        or item is None
        or not item.required_flag
        or not item.applicable_flag
    ):
        raise PortalDocumentationUnavailable(
            "This documentation action is not currently available for upload."
        )
    uploaded_file, notes = _validate_upload_request(request)
    previous = (
        PortalDocumentationSubmission.objects.select_for_update()
        .filter(
            loan_application=application,
            action_code=action_code,
            successor__isnull=True,
        )
        .order_by("-created_at", "-portal_documentation_submission_id")
        .first()
    )
    document = document_services.store_document_upload(
        user=actor,
        request=request,
        uploaded_file=uploaded_file,
        document_category="legal",
        sensitivity_level="confidential",
        related_entity_type="loan_application",
        related_entity_id=application.pk,
        provenance_metadata={
            "portal_account_id": str(context.account.pk),
            "member_id": str(context.account.member_id),
            "portal_action_code": action_code,
        },
    )
    submission = PortalDocumentationSubmission.objects.create(
        loan_application=application,
        action_code=action_code,
        document=document,
        portal_account=context.account,
        uploader_member=context.account.member,
        notes=notes,
        supersedes=previous,
    )
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="portal_account",
        action="portal.documentation.uploaded",
        entity_type="portal_documentation_submission",
        entity_id=submission.pk,
        old_value_json=(
            {"prior_document_id": str(previous.document_id)} if previous else None
        ),
        new_value_json={
            "portal_account_id": str(context.account.pk),
            "member_id": str(context.account.member_id),
            "loan_application_id": str(application.pk),
            "action_code": action_code,
            "document_id": str(document.pk),
            "document_category": "legal",
            "checksum_sha256": document.checksum_sha256,
            "prior_current_document_id": str(previous.document_id) if previous else None,
            "request_id": request.headers.get("X-Request-ID"),
            "outcome": "accepted",
        },
        ip_address=document_services.request_ip(request),
        user_agent=document_services.request_user_agent(request),
    )
    return {
        "action_code": action_code,
        "status": "submitted",
        "document": {
            "document_id": str(document.pk),
            "file_name": document.file_name,
            "mime_type": document.mime_type,
            "file_size_bytes": document.file_size_bytes,
            "checksum_sha256": document.checksum_sha256,
            "uploaded_at": document.uploaded_at.isoformat().replace("+00:00", "Z"),
        },
    }
def _validate_upload_request(request):
    field_errors = {}
    post_fields = set(request.POST.keys())
    file_fields = set(request.FILES.keys())
    unknown = sorted((post_fields - {"notes"}) | (file_fields - {"file"}))
    if unknown:
        field_errors["unknown_fields"] = f"Unknown fields: {', '.join(unknown)}."
    uploaded_file = request.FILES.get("file")
    if uploaded_file is None:
        field_errors["file"] = "Exactly one file is required."
    elif uploaded_file.size <= 0:
        field_errors["file"] = "File must not be empty."
    elif uploaded_file.size > 5 * 1024 * 1024:
        field_errors["file"] = "File must not exceed 5 MiB."
    if len(request.FILES.getlist("file")) != 1:
        field_errors["file"] = "Exactly one file is required."
    notes = (request.POST.get("notes") or "").strip() or None
    if notes and len(notes) > 4000:
        field_errors["notes"] = "Must not exceed 4000 characters."
    if uploaded_file is not None:
        extension = Path(uploaded_file.name).suffix.lower()
        allowed = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        if extension not in allowed or uploaded_file.content_type != allowed.get(extension):
            field_errors["file"] = "File extension and MIME type must be PDF, JPG, or PNG."
    if field_errors:
        raise ValidationError(field_errors)
    return uploaded_file, notes
def download(*, actor, application_id, action_code, request, storage=None):
    context = resolve_context(actor=actor, application_id=application_id)
    application = context.application
    if (
        application.application_status != LoanApplication.STATUS_APPROVED_BY_SANCTION
        or document_checklist_facts.resolve_approved_facts(application_id=application.pk) is None
        or action_code not in {"term_sheet", "loan_agreement"}
    ):
        raise PortalDocumentationNotFound
    item = (
        ChecklistItem.objects.select_related("loan_document__document")
        .filter(
            document_checklist__loan_application=application,
            item_code=action_code,
            required_flag=True,
            applicable_flag=True,
        )
        .first()
    )
    document = item.loan_document if item else None
    if (
        document is None
        or document.document is None
        or document.renderer_validation_status != document.RENDERER_CURRENT_VALIDATED
    ):
        raise PortalDocumentationNotFound
    storage = storage or LocalDocumentStorage()
    if request.GET.get("content") != "1":
        descriptor = storage.download_descriptor(document.document)
        expires_at = descriptor["expires_at"]
        return {
            "download_url": (
                f"/api/v1/portal/applications/{application.pk}/documentation-actions/"
                f"{action_code}/download/?content=1&expires_at={expires_at}"
            ),
            "expires_at": expires_at,
        }
    expires_at = parse_datetime(request.GET.get("expires_at", ""))
    if expires_at is None or expires_at <= timezone.now():
        raise PortalDocumentationNotFound
    body = storage.read_verified(document.document)
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="portal_account",
        action="portal.documentation.downloaded",
        entity_type="document_file",
        entity_id=document.document_id,
        old_value_json=None,
        new_value_json={
            "portal_account_id": str(context.account.pk),
            "member_id": str(context.account.member_id),
            "loan_application_id": str(application.pk),
            "action_code": action_code,
            "document_id": str(document.document_id),
            "document_category": document.document_category,
            "checksum_sha256": document.document.checksum_sha256,
            "request_id": request.headers.get("X-Request-ID"),
            "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
            "outcome": "accepted",
        },
        ip_address=document_services.request_ip(request),
        user_agent=document_services.request_user_agent(request),
    )
    return PortalDocumentContent(
        body=body, file_name=document.document.file_name,
        mime_type=document.document.mime_type or "application/octet-stream")
