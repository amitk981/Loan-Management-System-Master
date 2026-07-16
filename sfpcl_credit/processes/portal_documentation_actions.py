"""Borrower-safe post-sanction documentation projection and actions."""
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from django.core.exceptions import ValidationError
from django.db import transaction
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.modules import document_checklist_facts
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.processes import document_checklist_actions, portal_application_scope
from sfpcl_credit.legal_documents import selectors as legal_document_selectors
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
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
class PortalDocumentContent:
    body: bytes
    file_name: str
    mime_type: str


@dataclass(frozen=True)
class PortalActionAuthority:
    reconciled_complete: bool
    upload_allowed: bool
    reupload_allowed: bool


@dataclass(frozen=True)
class PortalActionDecision:
    application: LoanApplication
    checklist: DocumentChecklist | None
    items: tuple[ChecklistItem, ...]
    completion_action_item_ids: frozenset
    current_submissions: dict
    current_issued_documents: dict
    approved: bool
def resolve_context(*, actor, application_id):
    try:
        return portal_application_scope.resolve(
            actor=actor, application_id=application_id
        )
    except portal_application_scope.PortalApplicationScopeNotFound as exc:
        raise PortalDocumentationNotFound from exc
@transaction.atomic
def get_projection(*, actor, application_id):
    context = resolve_context(actor=actor, application_id=application_id)
    decision = _resolve_locked_decision(context=context)
    application = decision.application
    base = {
        "loan_application_id": str(application.pk),
        "application_reference_number": application.application_reference_number,
        "application_status": application.application_status,
    }
    if not decision.approved:
        return {
            **base,
            "availability": "blocked",
            "unavailable_reason": "Documentation actions are available after a current sanction approval.",
            "actions": [],
        }
    checklist = decision.checklist
    if checklist is None:
        return {
            **base,
            "availability": "blocked",
            "unavailable_reason": "The post-sanction documentation checklist is not available yet.",
            "actions": [],
        }
    return {
        **base,
        "availability": "available",
        "unavailable_reason": None,
        "actions": [
            _serialize_item(
                item,
                checklist,
                decision.completion_action_item_ids,
                decision.current_submissions.get(item.item_code),
                decision.current_issued_documents.get(item.item_code),
            )
            for item in decision.items
        ],
    }


def _resolve_locked_decision(*, context):
    application = LoanApplication.objects.select_for_update().get(
        pk=context.application.pk
    )
    approved = bool(
        application.application_status == LoanApplication.STATUS_APPROVED_BY_SANCTION
        and document_checklist_facts.resolve_approved_facts(application_id=application.pk)
        is not None
    )
    if not approved:
        return PortalActionDecision(
            application=application,
            checklist=None,
            items=(),
            completion_action_item_ids=frozenset(),
            current_submissions={},
            current_issued_documents={},
            approved=False,
        )
    checklist = (
        DocumentChecklist.objects.select_for_update()
        .filter(loan_application=application)
        .first()
    )
    if checklist is None:
        return PortalActionDecision(
            application=application,
            checklist=None,
            items=(),
            completion_action_item_ids=frozenset(),
            current_submissions={},
            current_issued_documents={},
            approved=True,
        )
    items = tuple(
        ChecklistItem.objects.select_for_update()
        .filter(document_checklist=checklist)
        .order_by("display_order", "checklist_item_id")
    )
    submissions = {
        row.action_code: row
        for row in PortalDocumentationSubmission.objects.select_for_update()
        .select_related("document")
        .filter(loan_application=application, successor__isnull=True)
    }
    issued_types = {"term_sheet", "loan_agreement"}
    current_ids = legal_document_selectors.latest_generated_metadata_by_type(
        application_id=application.pk,
        document_types=issued_types,
    )
    current_documents = {
        row.document_type: row
        for row in LoanDocument.objects.select_for_update()
        .select_related("document", "document_template")
        .filter(pk__in=current_ids.values())
    }
    return PortalActionDecision(
        application=application,
        checklist=checklist,
        items=items,
        completion_action_item_ids=frozenset(
            document_checklist_actions.borrower_safe_completed_item_ids(checklist)
        ),
        current_submissions=submissions,
        current_issued_documents=current_documents,
        approved=True,
    )


def _serialize_item(
    item, checklist, completion_action_item_ids, submission, current_issued_document
):
    section, instruction = _ACTION_PRESENTATION[item.item_code]
    authority = _resolve_action_authority(
        item=item,
        completion_action_item_ids=completion_action_item_ids,
        submission=submission,
    )
    status = (
        "not_required"
        if not item.applicable_flag
        else "complete"
        if authority.reconciled_complete
        else "submitted"
        if submission
        else "pending_borrower"
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
        "upload_allowed": authority.upload_allowed,
        "reupload_allowed": authority.reupload_allowed,
        "download": _download_metadata(item, current_issued_document),
    }


def _resolve_action_authority(*, item, completion_action_item_ids, submission):
    reconciled_complete = (
        item.completion_status == ChecklistItem.STATUS_COMPLETE
        and item.pk in completion_action_item_ids
    )
    mutable = bool(
        item.item_code in UPLOAD_ACTION_CODES
        and item.required_flag
        and item.applicable_flag
        and item.completion_status == ChecklistItem.STATUS_PENDING
        and not item.applicability_blocker
        and not reconciled_complete
    )
    return PortalActionAuthority(
        reconciled_complete=reconciled_complete,
        upload_allowed=mutable and submission is None,
        reupload_allowed=mutable and submission is not None,
    )
def _download_metadata(item, document):
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
    decision = _resolve_locked_decision(context=context)
    application = decision.application
    if not decision.approved:
        raise PortalDocumentationUnavailable(
            "Documentation uploads require a current sanction approval."
        )
    item = next((row for row in decision.items if row.item_code == action_code), None)
    previous = decision.current_submissions.get(action_code)
    authority = (
        _resolve_action_authority(
            item=item,
            completion_action_item_ids=decision.completion_action_item_ids,
            submission=previous,
        )
        if item is not None
        else None
    )
    if authority is None or not (
        authority.upload_allowed or authority.reupload_allowed
    ):
        raise PortalDocumentationUnavailable(
            "This documentation action is not currently available for upload."
        )
    uploaded_file, notes = _validate_upload_request(request)
    document_version = (
        PortalDocumentationSubmission.objects.filter(
            loan_application=application, action_code=action_code
        ).count()
        + 1
    )
    document = document_services.store_document_upload(
        user=actor,
        request=request,
        uploaded_file=uploaded_file,
        document_category="legal",
        sensitivity_level="confidential",
        related_entity_type="loan_application",
        related_entity_id=application.pk,
        audit_spec=document_services.DocumentAuditSpec(
            action="portal.document.uploaded",
            actor_type="portal_account",
            metadata={
                "portal_account_id": str(context.account.pk),
                "member_id": str(context.account.member_id),
                "loan_application_id": str(application.pk),
                "action_code": action_code,
                "document_version": document_version,
                "document_category": "legal",
                "sensitivity_level": "confidential",
                "reason": "borrower_portal_submission",
                "request_id": request.headers.get("X-Request-ID"),
                "network": {
                    "ip_address": document_services.request_ip(request),
                    "user_agent": document_services.request_user_agent(request),
                },
                "outcome": "accepted",
            },
        ),
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
@transaction.atomic
def download(*, actor, application_id, action_code, request, storage=None):
    context = resolve_context(actor=actor, application_id=application_id)
    decision = _resolve_locked_decision(context=context)
    application = decision.application
    if (
        not decision.approved
        or action_code not in {"term_sheet", "loan_agreement"}
    ):
        raise PortalDocumentationNotFound
    item = next((row for row in decision.items if row.item_code == action_code), None)
    document = decision.current_issued_documents.get(action_code)
    if (
        item is None
        or not item.required_flag
        or not item.applicable_flag
        or document is None
        or document.document is None
        or document.renderer_validation_status != document.RENDERER_CURRENT_VALIDATED
    ):
        raise PortalDocumentationNotFound
    storage = storage or LocalDocumentStorage()
    scope = {
        "portal_account_id": str(context.account.pk),
        "member_id": str(context.account.member_id),
        "loan_application_id": str(application.pk),
        "action_code": action_code,
        "loan_document_id": str(document.pk),
    }
    if request.GET.get("content") != "1":
        capability = document_services.issue_download_capability(
            document=document.document,
            scope=scope,
        )
        query = urlencode({"content": "1", "token": capability["token"]})
        return {
            "download_url": (
                f"/api/v1/portal/applications/{application.pk}/documentation-actions/"
                f"{action_code}/download/?{query}"
            ),
            "expires_at": capability["expires_at"],
        }
    try:
        body = document_services.read_with_download_capability(
            document=document.document,
            scope=scope,
            token=request.GET.get("token", ""),
            storage=storage,
        )
    except ValidationError:
        raise PortalDocumentationNotFound
    document_services.record_document_audit(
        user=actor,
        request=request,
        document=document.document,
        spec=document_services.DocumentAuditSpec(
            action="portal.document.downloaded",
            actor_type="portal_account",
            metadata={
            "portal_account_id": str(context.account.pk),
            "member_id": str(context.account.member_id),
            "loan_application_id": str(application.pk),
            "action_code": action_code,
            "document_version": document.document_template.template_version,
            "document_category": document.document_category,
            "request_id": request.headers.get("X-Request-ID"),
            "sensitivity_level": document.document.sensitivity_level,
            "reason": "borrower_portal_published_document",
            "network": {
                "ip_address": document_services.request_ip(request),
                "user_agent": document_services.request_user_agent(request),
            },
            "capability_verified": True,
            "outcome": "accepted",
            },
        ),
    )
    return PortalDocumentContent(
        body=body, file_name=document.document.file_name,
        mime_type=document.document.mime_type or "application/octet-stream")
