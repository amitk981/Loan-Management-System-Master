import uuid
from math import ceil

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service


READ_PERMISSION = "documents.template.read"
MANAGE_PERMISSION = "documents.template.manage"
ENTITY_TYPE = "document_template"
CREATE_ACTION = "documents.template.created"
SUCCESSOR_ACTION = "documents.template.successor_created"
_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
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
_LIST_PARAMS = {
    "page",
    "page_size",
    "document_type",
    "borrower_type",
    "approval_status",
}


def can_read(user):
    return READ_PERMISSION in auth_service.effective_permission_codes(user)


def can_manage(user):
    return MANAGE_PERMISSION in auth_service.effective_permission_codes(user)


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


def create(*, actor, request, payload):
    cleaned = _validate_payload(payload)
    _resolve_template_file(actor, cleaned)
    with transaction.atomic():
        replay = _exact_match(cleaned, supersedes=None)
        if replay is not None:
            return serialize(replay)
        _validate_unique_and_effective(cleaned)
        template = DocumentTemplate.objects.create(**cleaned)
        _record_evidence(
            actor=actor,
            request=request,
            action=CREATE_ACTION,
            template=template,
            old_value={},
        )
        return serialize(template)


def create_successor(*, actor, request, document_template_id, payload):
    cleaned = _validate_payload(payload)
    _resolve_template_file(actor, cleaned)
    with transaction.atomic():
        source = (
            DocumentTemplate.objects.select_for_update(of=("self",))
            .select_related("template_file")
            .get(document_template_id=document_template_id)
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
            request=request,
            action=SUCCESSOR_ACTION,
            template=template,
            old_value=serialize(source),
        )
        return serialize(template)


def list_templates(query_params):
    unknown = set(query_params.keys()) - _LIST_PARAMS
    if unknown:
        raise ValidationError(
            {key: "Unknown query parameter." for key in sorted(unknown)}
        )
    queryset = DocumentTemplate.objects.select_related("template_file")
    for field in ("document_type", "approval_status"):
        value = query_params.get(field)
        if value:
            if (
                field == "approval_status"
                and value not in DocumentTemplate.APPROVAL_STATUSES
            ):
                raise ValidationError(
                    {"approval_status": "Must be one of draft, approved, retired."}
                )
            queryset = queryset.filter(**{field: value})
    if "borrower_type" in query_params:
        value = query_params.get("borrower_type")
        if value in ("", "null"):
            queryset = queryset.filter(borrower_type__isnull=True)
        elif value not in DocumentTemplate.BORROWER_TYPES:
            raise ValidationError(
                {"borrower_type": "Must be individual_farmer, fpc, fpo, or null."}
            )
        else:
            queryset = queryset.filter(borrower_type=value)
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(
        _positive_int("page_size", query_params.get("page_size"), _DEFAULT_PAGE_SIZE),
        _MAX_PAGE_SIZE,
    )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    rows = [serialize(row) for row in queryset[offset : offset + page_size]]
    return rows, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


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
    template_file = DocumentFile.objects.filter(document_id=template_file_id).first()
    if "documents.file.download" not in permissions or template_file is None:
        raise ValidationError(
            {"template_file_id": "Document file was not found or is inaccessible."}
        )
    cleaned["template_file"] = template_file


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


def _exact_match(cleaned, *, supersedes):
    return (
        DocumentTemplate.objects.select_related("template_file")
        .filter(supersedes=supersedes, **cleaned)
        .first()
    )


def _record_evidence(*, actor, request, action, template, old_value):
    new_value = {
        **serialize(template),
        "supersedes_document_template_id": (
            str(template.supersedes_id) if template.supersedes_id else None
        ),
        "request_id": request.headers.get("X-Request-ID"),
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type=ENTITY_TYPE,
        entity_id=template.document_template_id,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
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


def _positive_int(field, value, default):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Must be a positive integer."}) from exc
    if parsed <= 0:
        raise ValidationError({field: "Must be a positive integer."})
    return parsed
