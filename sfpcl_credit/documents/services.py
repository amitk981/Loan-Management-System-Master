import uuid
from dataclasses import dataclass
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import transaction

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service


DOCUMENT_UPLOAD_PERMISSION = "documents.file.upload"
DOCUMENT_DOWNLOAD_PERMISSION = "documents.file.download"
DOCUMENT_UPLOAD_AUDIT_ACTION = "documents.file.uploaded"
DOCUMENT_DOWNLOAD_AUDIT_ACTION = "documents.file.downloaded"
ALLOWED_SENSITIVITY_LEVELS = DocumentFile.SENSITIVITY_LEVELS
GENERAL_MEETING_REFERENCE_PURPOSE = "general_meeting_evidence"
GENERAL_MEETING_WORKFLOW_SCOPE = "related_party_sanction_case"
_INACCESSIBLE_REFERENCE_MESSAGE = "Document file was not found or is inaccessible."


@dataclass(frozen=True)
class DocumentReferenceContext:
    related_entity_type: str
    related_entity_id: uuid.UUID
    related_entity_access_allowed: bool
    workflow_scope: str
    actor_role_codes: frozenset[str]
    actor_is_related_case_approver: bool


def user_can_upload_documents(user):
    return DOCUMENT_UPLOAD_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_download_documents(user):
    return DOCUMENT_DOWNLOAD_PERMISSION in auth_service.effective_permission_codes(user)


def upload_document_file(user, request, storage=None):
    cleaned = validate_upload_request(request)
    storage = storage or LocalDocumentStorage()
    uploaded_file = cleaned["file"]
    stored = storage.store(uploaded_file)
    file_name = uploaded_file.name
    file_extension = Path(file_name).suffix or None

    with transaction.atomic():
        document = DocumentFile.objects.create(
            file_name=file_name,
            file_extension=file_extension,
            mime_type=getattr(uploaded_file, "content_type", "") or None,
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=user,
            sensitivity_level=cleaned["sensitivity_level"],
        )
        AuditLog.objects.create(
            actor_user=user,
            actor_type="user",
            action=DOCUMENT_UPLOAD_AUDIT_ACTION,
            entity_type="document_file",
            entity_id=document.document_id,
            old_value_json=None,
            new_value_json={
                "document_id": str(document.document_id),
                "file_name": document.file_name,
                "file_extension": document.file_extension,
                "mime_type": document.mime_type,
                "file_size_bytes": document.file_size_bytes,
                "storage_provider": document.storage_provider,
                "storage_key": document.storage_key,
                "checksum_sha256": document.checksum_sha256,
                "sensitivity_level": document.sensitivity_level,
                "document_category": cleaned["document_category"],
                "related_entity_type": cleaned.get("related_entity_type"),
                "related_entity_id": str(cleaned["related_entity_id"])
                if cleaned.get("related_entity_id")
                else None,
            },
            ip_address=request_ip(request),
            user_agent=request_user_agent(request),
        )
    return serialize_document_file(document)


def download_document_file(user, request, document_id, storage=None):
    storage = storage or LocalDocumentStorage()
    document = DocumentFile.objects.get(document_id=document_id)
    descriptor = storage.download_descriptor(document)

    AuditLog.objects.create(
        actor_user=user,
        actor_type="user",
        action=DOCUMENT_DOWNLOAD_AUDIT_ACTION,
        entity_type="document_file",
        entity_id=document.document_id,
        old_value_json=None,
        new_value_json={
            "document_id": str(document.document_id),
            "file_name": document.file_name,
            "mime_type": document.mime_type,
            "file_size_bytes": document.file_size_bytes,
            "storage_provider": document.storage_provider,
            "sensitivity_level": document.sensitivity_level,
            "expires_at": descriptor["expires_at"],
        },
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return descriptor


def resolve_referenceable_documents(
    *,
    actor_permissions,
    document_ids_by_field,
    context,
    purpose,
):
    """Resolve document references only when immutable upload provenance proves access."""
    permissions = set(actor_permissions)
    if DOCUMENT_DOWNLOAD_PERMISSION not in permissions:
        raise ValidationError(
            {
                field: _INACCESSIBLE_REFERENCE_MESSAGE
                for field in document_ids_by_field
            }
        )
    purpose_is_allowed = purpose == GENERAL_MEETING_REFERENCE_PURPOSE
    workflow_scope_is_allowed = (
        context.workflow_scope == GENERAL_MEETING_WORKFLOW_SCOPE
    )
    legal_category_access_allowed = (
        bool(
            context.actor_role_codes
            & {"compliance_team_member", "company_secretary", "credit_manager"}
        )
        or context.actor_is_related_case_approver
    )
    documents = DocumentFile.objects.in_bulk(document_ids_by_field.values())
    upload_metadata = {}
    for audit in (
        AuditLog.objects.filter(
            action=DOCUMENT_UPLOAD_AUDIT_ACTION,
            entity_type="document_file",
            entity_id__in=document_ids_by_field.values(),
        )
        .order_by("-created_at", "-audit_log_id")
    ):
        upload_metadata.setdefault(str(audit.entity_id), audit.new_value_json or {})

    denied_fields = {}
    for field, document_id in document_ids_by_field.items():
        document = documents.get(document_id)
        metadata = upload_metadata.get(str(document_id), {})
        reference_is_allowed = (
            purpose_is_allowed
            and workflow_scope_is_allowed
            and context.related_entity_access_allowed
            and legal_category_access_allowed
            and document is not None
            and metadata.get("document_id") == str(document_id)
            and metadata.get("related_entity_type") == context.related_entity_type
            and metadata.get("related_entity_id") == str(context.related_entity_id)
            and metadata.get("document_category") == "legal"
            and document.sensitivity_level in ALLOWED_SENSITIVITY_LEVELS
            and metadata.get("sensitivity_level") == document.sensitivity_level
        )
        if not reference_is_allowed:
            denied_fields[field] = _INACCESSIBLE_REFERENCE_MESSAGE
    if denied_fields:
        raise ValidationError(denied_fields)
    return {
        field: documents[document_id]
        for field, document_id in document_ids_by_field.items()
    }


def validate_upload_request(request):
    field_errors = {}
    uploaded_file = request.FILES.get("file")
    document_category = (request.POST.get("document_category") or "").strip()
    raw_sensitivity = (request.POST.get("sensitivity_level") or "").strip()
    related_entity_type = (request.POST.get("related_entity_type") or "").strip()
    raw_related_entity_id = (request.POST.get("related_entity_id") or "").strip()

    if uploaded_file is None:
        field_errors["file"] = "This field is required."
    if not document_category:
        field_errors["document_category"] = "This field is required."
    if not raw_sensitivity:
        field_errors["sensitivity_level"] = "This field is required."

    sensitivity_level = raw_sensitivity.lower()
    if raw_sensitivity and sensitivity_level not in ALLOWED_SENSITIVITY_LEVELS:
        field_errors["sensitivity_level"] = (
            "Must be one of public, internal, confidential, restricted."
        )

    related_entity_id = None
    if raw_related_entity_id:
        try:
            related_entity_id = uuid.UUID(raw_related_entity_id)
        except ValueError:
            field_errors["related_entity_id"] = "Must be a valid UUID."

    if field_errors:
        raise ValidationError(field_errors)

    return {
        "file": uploaded_file,
        "document_category": document_category,
        "sensitivity_level": sensitivity_level,
        "related_entity_type": related_entity_type or None,
        "related_entity_id": related_entity_id,
    }


def serialize_document_file(document):
    return {
        "document_id": str(document.document_id),
        "file_name": document.file_name,
        "mime_type": document.mime_type,
        "file_size_bytes": document.file_size_bytes,
        "sensitivity_level": document.sensitivity_level,
        "uploaded_at": document.uploaded_at.isoformat().replace("+00:00", "Z"),
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


__all__ = [
    "DOCUMENT_DOWNLOAD_AUDIT_ACTION",
    "DOCUMENT_DOWNLOAD_PERMISSION",
    "DOCUMENT_UPLOAD_AUDIT_ACTION",
    "DOCUMENT_UPLOAD_PERMISSION",
    "download_document_file",
    "DocumentReferenceContext",
    "GENERAL_MEETING_REFERENCE_PURPOSE",
    "GENERAL_MEETING_WORKFLOW_SCOPE",
    "resolve_referenceable_documents",
    "upload_document_file",
    "user_can_download_documents",
    "user_can_upload_documents",
    "validation_field_errors",
]
