import uuid
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_date

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.models import DocumentTemplate, DocumentTemplateIdentity
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service


READ_PERMISSION = "documents.template.read"
MANAGE_PERMISSION = "documents.template.manage"
ENTITY_TYPE = "document_template"
CREATE_ACTION = "documents.template.created"
SUCCESSOR_ACTION = "documents.template.successor_created"
_FIELDS = {
    "template_code",
    "template_name",
    "document_type",
    "borrower_type",
    "template_version",
    "template_file_id",
    "merge_fields",
    "approval_status",
    "effective_from",
    "effective_to",
}
_REQUIRED_FIELDS = {
    "template_code",
    "template_name",
    "document_type",
    "template_version",
    "approval_status",
    "effective_from",
}


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


def can_read(user):
    return READ_PERMISSION in auth_service.effective_permission_codes(user)


def can_manage(user):
    return MANAGE_PERMISSION in auth_service.effective_permission_codes(user)


def resolve_borrower_template_variant(member_type):
    """Resolve only governance-confirmed member-to-template variant mappings."""
    if member_type == "individual_farmer":
        return "individual_farmer"
    raise ValidationError(
        {"borrower_type": "Template borrower variant mapping requires configuration."}
    )


def serialize(template):
    return {
        "document_template_id": str(template.document_template_id),
        "template_code": template.template_code,
        "template_name": template.template_name,
        "document_type": template.document_type,
        "borrower_type": template.borrower_type,
        "template_version": template.template_version,
        "template_file_id": (
            str(template.template_file_id) if template.template_file_id else None
        ),
        "template_file_name": (
            template.template_file.file_name if template.template_file_id else None
        ),
        "merge_fields": template.merge_fields_json or [],
        "approval_status": template.approval_status,
        "effective_from": template.effective_from.isoformat(),
        "effective_to": (
            template.effective_to.isoformat() if template.effective_to else None
        ),
        "created_at": template.created_at.isoformat().replace("+00:00", "Z"),
    }


def create(*, actor, metadata, payload):
    cleaned = _validate_payload(payload)
    _resolve_template_file(actor, cleaned)
    with transaction.atomic():
        _lock_identity(cleaned)
        replay = _exact_match(cleaned, supersedes=None)
        if replay is not None:
            return serialize(replay)
        _validate_unique_and_effective(cleaned)
        template = DocumentTemplate.objects.create(**cleaned)
        _record_evidence(
            actor=actor,
            metadata=metadata,
            action=CREATE_ACTION,
            template=template,
            old_value={},
        )
        return serialize(template)


def create_successor(*, actor, metadata, document_template_id, payload):
    cleaned = _validate_payload(payload)
    _resolve_template_file(actor, cleaned)
    with transaction.atomic():
        _lock_identity(cleaned)
        source = (
            DocumentTemplate.objects.select_for_update(of=("self",))
            .select_related("template_file")
            .get(document_template_id=document_template_id)
        )
        if (
            source.document_type != cleaned["document_type"]
            or source.borrower_type != cleaned["borrower_type"]
        ):
            raise ValidationError(
                {
                    "non_field_errors": (
                        "A successor must retain its document type and borrower variant."
                    )
                }
            )
        replay = _exact_match(cleaned, supersedes=source)
        if replay is not None:
            return serialize(replay)
        if DocumentTemplate.objects.filter(supersedes=source).exists():
            raise ValidationError(
                {"non_field_errors": "This template version already has a successor."}
            )
        _validate_unique_and_effective(cleaned)
        template = DocumentTemplate.objects.create(**cleaned, supersedes=source)
        _record_evidence(
            actor=actor,
            metadata=metadata,
            action=SUCCESSOR_ACTION,
            template=template,
            old_value=serialize(source),
        )
        return serialize(template)


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


def _validate_payload(payload):
    errors = {}
    unknown = set(payload.keys()) - _FIELDS
    for field in sorted(unknown):
        errors[field] = "Unknown field."
    for field in sorted(_REQUIRED_FIELDS):
        if payload.get(field) in (None, ""):
            errors[field] = "This field is required."

    cleaned = {}
    string_limits = {
        "template_code": 120,
        "template_name": 255,
        "document_type": 100,
        "template_version": 40,
    }
    for field, max_length in string_limits.items():
        value = payload.get(field)
        if value is not None:
            value = str(value).strip()
        if field in payload and not value:
            errors[field] = "This field is required."
        elif value and len(value) > max_length:
            errors[field] = f"Must be at most {max_length} characters."
        cleaned[field] = value

    borrower_type = payload.get("borrower_type")
    if borrower_type not in (None, ""):
        borrower_type = str(borrower_type).strip().lower()
        if borrower_type not in DocumentTemplate.BORROWER_TYPES:
            errors["borrower_type"] = "Must be individual_farmer, fpc, fpo, or null."
    cleaned["borrower_type"] = borrower_type or None

    approval_status = str(payload.get("approval_status") or "").strip().lower()
    if approval_status not in DocumentTemplate.APPROVAL_STATUSES:
        errors["approval_status"] = "Must be one of draft, approved, retired."
    cleaned["approval_status"] = approval_status

    for field in ("effective_from", "effective_to"):
        value = payload.get(field)
        parsed = None if value in (None, "") else parse_date(str(value))
        if field == "effective_from" and value in (None, ""):
            errors[field] = "This field is required."
        elif value not in (None, "") and parsed is None:
            errors[field] = "Must be a valid ISO date."
        cleaned[field] = parsed
    if (
        cleaned.get("effective_from")
        and cleaned.get("effective_to")
        and cleaned["effective_to"] < cleaned["effective_from"]
    ):
        errors["effective_to"] = "Must be on or after effective_from."

    merge_fields = payload.get("merge_fields", [])
    if not isinstance(merge_fields, list) or any(
        not isinstance(value, str) for value in merge_fields
    ):
        errors["merge_fields"] = "Must be a list of unique nonblank field names."
    else:
        normalized = [value.strip() for value in merge_fields]
        if any(not value for value in normalized) or len(set(normalized)) != len(normalized):
            errors["merge_fields"] = "Must be a list of unique nonblank field names."
        cleaned["merge_fields_json"] = normalized
    if "merge_fields_json" not in cleaned:
        cleaned["merge_fields_json"] = []

    template_file_id = payload.get("template_file_id")
    if template_file_id not in (None, ""):
        try:
            template_file_id = uuid.UUID(str(template_file_id))
        except (TypeError, ValueError, AttributeError):
            errors["template_file_id"] = "Document file was not found or is inaccessible."
    cleaned["template_file_id"] = template_file_id or None
    if errors:
        raise ValidationError(errors)
    return cleaned


def _resolve_template_file(actor, cleaned):
    template_file_id = cleaned.pop("template_file_id")
    if template_file_id is None:
        cleaned["template_file"] = None
        return
    permissions = auth_service.effective_permission_codes(actor)
    cleaned["template_file"] = document_services.resolve_template_source_reference(
        actor_permissions=permissions,
        document_id=template_file_id,
    )


def _validate_unique_and_effective(cleaned):
    duplicate = DocumentTemplate.objects.filter(template_code=cleaned["template_code"])
    if duplicate.exists():
        raise ValidationError({"template_code": "Template code already exists."})
    duplicate_version = DocumentTemplate.objects.filter(
        document_type=cleaned["document_type"],
        borrower_type=cleaned["borrower_type"],
        template_version=cleaned["template_version"],
    )
    if duplicate_version.exists():
        raise ValidationError(
            {"template_version": "Template version already exists for this variant."}
        )
    if cleaned["approval_status"] != DocumentTemplate.STATUS_APPROVED:
        return
    candidates = DocumentTemplate.objects.select_for_update().filter(
        document_type=cleaned["document_type"],
        borrower_type=cleaned["borrower_type"],
        approval_status=DocumentTemplate.STATUS_APPROVED,
    )
    start = cleaned["effective_from"]
    end = cleaned["effective_to"]
    for candidate in candidates:
        if (candidate.effective_to is None or candidate.effective_to >= start) and (
            end is None or candidate.effective_from <= end
        ):
            raise ValidationError(
                {"effective_from": "Approved effective versions must not overlap."}
            )


def _lock_identity(cleaned):
    borrower_variant_key = (
        cleaned["borrower_type"] or DocumentTemplateIdentity.GLOBAL_VARIANT_KEY
    )
    identity, _ = DocumentTemplateIdentity.objects.get_or_create(
        document_type=cleaned["document_type"],
        borrower_variant_key=borrower_variant_key,
    )
    DocumentTemplateIdentity.objects.select_for_update().get(pk=identity.pk)


def _exact_match(cleaned, *, supersedes):
    return (
        DocumentTemplate.objects.select_related("template_file")
        .filter(supersedes=supersedes, **cleaned)
        .first()
    )


def _record_evidence(*, actor, metadata, action, template, old_value):
    new_value = {
        **serialize(template),
        "supersedes_document_template_id": (
            str(template.supersedes_id) if template.supersedes_id else None
        ),
        "request_id": metadata.request_id,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type=ENTITY_TYPE,
        entity_id=template.document_template_id,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type=ENTITY_TYPE,
        versioned_entity_id=template.document_template_id,
        version_number=template.template_version,
        change_summary=(
            f"Created successor template version {template.template_version}."
            if template.supersedes_id
            else f"Created template version {template.template_version}."
        ),
        author_user=actor,
        approver_user=(
            actor if template.approval_status == DocumentTemplate.STATUS_APPROVED else None
        ),
        old_value_json=old_value,
        new_value_json=new_value,
        effective_from=template.effective_from,
        effective_to=template.effective_to,
    )
