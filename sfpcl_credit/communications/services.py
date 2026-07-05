from math import ceil

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.models import ContentTemplate
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service


CONTENT_TEMPLATE_READ_PERMISSION = "communications.content_template.read"
CONTENT_TEMPLATE_MANAGE_PERMISSION = "communications.content_template.manage"
CONTENT_TEMPLATE_ENTITY_TYPE = "content_template"
CONTENT_TEMPLATE_CREATED_ACTION = "communications.content_template.created"
CONTENT_TEMPLATE_UPDATED_ACTION = "communications.content_template.updated"

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_PAGINATION_PARAMS = {"page", "page_size"}
_REQUIRED_CREATE_FIELDS = {
    "template_code",
    "template_name",
    "template_type",
    "audience",
    "body_template",
    "approval_status",
    "template_version",
    "effective_from",
}
_OPTIONAL_FIELDS = {
    "language_code",
    "subject_template",
    "variables",
    "effective_to",
}
_STRING_FIELDS = {
    "template_code",
    "template_name",
    "template_type",
    "language_code",
    "audience",
    "subject_template",
    "body_template",
    "template_version",
}
_DATE_FIELDS = {"effective_from", "effective_to"}
_CONTENT_TEMPLATE_FIELDS = (
    "template_code",
    "template_name",
    "template_type",
    "language_code",
    "audience",
    "subject_template",
    "body_template",
    "variables",
    "approval_status",
    "template_version",
    "effective_from",
    "effective_to",
)


def user_can_read_content_templates(user):
    permissions = auth_service.effective_permission_codes(user)
    return (
        CONTENT_TEMPLATE_READ_PERMISSION in permissions
        or CONTENT_TEMPLATE_MANAGE_PERMISSION in permissions
    )


def user_can_manage_content_templates(user):
    return CONTENT_TEMPLATE_MANAGE_PERMISSION in auth_service.effective_permission_codes(
        user
    )


def serialize_content_template(row):
    return {
        "content_template_id": str(row.content_template_id),
        "template_code": row.template_code,
        "template_name": row.template_name,
        "template_type": row.template_type,
        "language_code": row.language_code,
        "audience": row.audience,
        "subject_template": row.subject_template,
        "body_template": row.body_template,
        "variables": row.variables_json or [],
        "approval_status": row.approval_status,
        "template_version": row.template_version,
        "effective_from": row.effective_from.isoformat(),
        "effective_to": row.effective_to.isoformat() if row.effective_to else None,
    }


def paginated_content_templates(query_params):
    unknown = set(query_params.keys()) - _PAGINATION_PARAMS
    if unknown:
        raise ValidationError(
            {param: "Unknown query parameter." for param in sorted(unknown)}
        )
    queryset = ContentTemplate.objects.order_by("template_code")
    page = _positive_int(query_params.get("page"), 1)
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE),
        _MAX_PAGE_SIZE,
    )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = [
        serialize_content_template(row) for row in queryset[offset : offset + page_size]
    ]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def create_content_template(user, request, payload):
    cleaned = _validate_content_template_payload(payload, partial=False)
    cleaned["variables_json"] = cleaned.pop("variables", [])
    with transaction.atomic():
        try:
            row = ContentTemplate.objects.create(**cleaned)
        except IntegrityError as exc:
            raise ValidationError(
                {"template_code": "Content template code must be unique."}
            ) from exc
        _record_content_template_audit(
            user=user,
            request=request,
            action=CONTENT_TEMPLATE_CREATED_ACTION,
            row=row,
            old_value=None,
            new_value=serialize_content_template(row),
        )
    return serialize_content_template(row)


def update_content_template(user, request, content_template_id, payload):
    row = ContentTemplate.objects.get(content_template_id=content_template_id)
    old_value = serialize_content_template(row)
    cleaned = _validate_content_template_payload(payload, partial=True, existing=row)
    if "variables" in cleaned:
        cleaned["variables_json"] = cleaned.pop("variables")
    for field, value in cleaned.items():
        setattr(row, field, value)
    with transaction.atomic():
        try:
            row.save(update_fields=list(cleaned.keys()))
        except IntegrityError as exc:
            raise ValidationError(
                {"template_code": "Content template code must be unique."}
            ) from exc
        _record_content_template_audit(
            user=user,
            request=request,
            action=CONTENT_TEMPLATE_UPDATED_ACTION,
            row=row,
            old_value=old_value,
            new_value=serialize_content_template(row),
        )
    return serialize_content_template(row)


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


def _validate_content_template_payload(payload, *, partial, existing=None):
    field_errors = {}
    unknown = set(payload.keys()) - set(_CONTENT_TEMPLATE_FIELDS)
    for field in sorted(unknown):
        field_errors[field] = "Unknown field."
    if not partial:
        for field in sorted(_REQUIRED_CREATE_FIELDS):
            if field not in payload or payload.get(field) in ("", None):
                field_errors[field] = "This field is required."

    cleaned = {}
    for field in _CONTENT_TEMPLATE_FIELDS:
        if field not in payload:
            continue
        value = payload[field]
        if value is None and field in _OPTIONAL_FIELDS:
            cleaned[field] = None
            continue
        if field in _STRING_FIELDS:
            cleaned[field] = _clean_string(field, value, field_errors)
        elif field in _DATE_FIELDS:
            cleaned[field] = _clean_date(field, value, field_errors)
        elif field == "variables":
            cleaned[field] = _clean_variables(value, field_errors)
        elif field == "approval_status":
            cleaned[field] = _clean_approval_status(value, field_errors)

    effective_from = cleaned.get(
        "effective_from", existing.effective_from if existing is not None else None
    )
    effective_to = cleaned.get(
        "effective_to", existing.effective_to if existing is not None else None
    )
    if effective_from and effective_to and effective_to < effective_from:
        field_errors["effective_to"] = "Must be on or after effective_from."

    if field_errors:
        raise ValidationError(field_errors)
    return cleaned


def _clean_string(field, value, field_errors):
    if value is None:
        field_errors[field] = "This field is required."
        return value
    cleaned = str(value).strip()
    if not cleaned and field not in _OPTIONAL_FIELDS:
        field_errors[field] = "This field is required."
    return cleaned or None


def _clean_date(field, value, field_errors):
    if value in ("", None):
        if field not in _OPTIONAL_FIELDS:
            field_errors[field] = "This field is required."
        return None
    parsed = parse_date(str(value))
    if parsed is None:
        field_errors[field] = "Must be a valid ISO date."
    return parsed


def _clean_variables(value, field_errors):
    if value in ("", None):
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        field_errors["variables"] = "Must be a JSON array of strings."
        return []
    cleaned = [item.strip() for item in value]
    if any(not item for item in cleaned):
        field_errors["variables"] = "Must be a JSON array of non-empty strings."
    return cleaned


def _clean_approval_status(value, field_errors):
    status = str(value).strip().lower()
    if status not in ContentTemplate.APPROVAL_STATUSES:
        field_errors["approval_status"] = "Must be one of draft, approved."
    return status


def _record_content_template_audit(*, user, request, action, row, old_value, new_value):
    AuditLog.objects.create(
        actor_user=user,
        actor_type="user",
        action=action,
        entity_type=CONTENT_TEMPLATE_ENTITY_TYPE,
        entity_id=row.content_template_id,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default
