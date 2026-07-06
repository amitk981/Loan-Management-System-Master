from math import ceil
import re
import uuid

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.models import Communication, ContentTemplate
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service


CONTENT_TEMPLATE_READ_PERMISSION = "communications.content_template.read"
CONTENT_TEMPLATE_MANAGE_PERMISSION = "communications.content_template.manage"
COMMUNICATION_READ_PERMISSION = "communications.communication.read"
COMMUNICATION_SEND_PERMISSION = "communications.communication.send"
CONTENT_TEMPLATE_ENTITY_TYPE = "content_template"
COMMUNICATION_ENTITY_TYPE = "communication"
CONTENT_TEMPLATE_CREATED_ACTION = "communications.content_template.created"
CONTENT_TEMPLATE_UPDATED_ACTION = "communications.content_template.updated"
COMMUNICATION_CREATED_ACTION = "communications.communication.created"

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
_COMMUNICATION_SEND_FIELDS = {
    "related_entity_type",
    "related_entity_id",
    "recipient_party_type",
    "recipient_party_id",
    "recipient_address",
    "channel",
    "content_template_id",
    "merge_data",
}
_REQUIRED_COMMUNICATION_SEND_FIELDS = {
    "related_entity_type",
    "related_entity_id",
    "recipient_party_type",
    "channel",
    "content_template_id",
    "merge_data",
}
_COMMUNICATION_LIST_PARAMS = {
    "related_entity_type",
    "related_entity_id",
    "page",
    "page_size",
}
_TEMPLATE_VARIABLE_RE = re.compile(r"{{\s*([A-Za-z0-9_]+)\s*}}")


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


def user_can_read_communications(user):
    permissions = auth_service.effective_permission_codes(user)
    return (
        COMMUNICATION_READ_PERMISSION in permissions
        or COMMUNICATION_SEND_PERMISSION in permissions
    )


def user_can_send_communications(user):
    return COMMUNICATION_SEND_PERMISSION in auth_service.effective_permission_codes(user)


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


def serialize_communication(row):
    return {
        "communication_id": str(row.communication_id),
        "related_entity_type": row.related_entity_type,
        "related_entity_id": str(row.related_entity_id),
        "recipient_party_type": row.recipient_party_type,
        "recipient_party_id": (
            str(row.recipient_party_id) if row.recipient_party_id else None
        ),
        "recipient_address": row.recipient_address,
        "channel": row.channel,
        "content_template_id": (
            str(row.content_template_id) if row.content_template_id else None
        ),
        "subject_snapshot": row.subject_snapshot,
        "body_snapshot": row.body_snapshot,
        "sent_by_user_id": str(row.sent_by_user_id) if row.sent_by_user_id else None,
        "sent_at": row.sent_at.isoformat() if row.sent_at else None,
        "delivery_status": row.delivery_status,
        "acknowledgement_status": row.acknowledgement_status,
        "external_message_id": row.external_message_id,
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


def paginated_communications(query_params):
    filters = _validate_communication_list_query(query_params)
    queryset = Communication.objects.filter(
        related_entity_type=filters["related_entity_type"],
        related_entity_id=filters["related_entity_id"],
    ).order_by("communication_id")
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
        serialize_communication(row) for row in queryset[offset : offset + page_size]
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


def send_communication(user, request, payload):
    cleaned = _validate_send_payload(payload)
    template = _approved_effective_template(cleaned["content_template_id"])
    subject_snapshot = _render_template(
        template.subject_template, template.variables_json or [], cleaned["merge_data"]
    )
    body_snapshot = _render_template(
        template.body_template, template.variables_json or [], cleaned["merge_data"]
    )
    with transaction.atomic():
        row = Communication.objects.create(
            related_entity_type=cleaned["related_entity_type"],
            related_entity_id=cleaned["related_entity_id"],
            recipient_party_type=cleaned["recipient_party_type"],
            recipient_party_id=cleaned.get("recipient_party_id"),
            recipient_address=cleaned.get("recipient_address"),
            channel=cleaned["channel"],
            content_template=template,
            subject_snapshot=subject_snapshot,
            body_snapshot=body_snapshot,
            sent_by_user=user,
            delivery_status=Communication.DELIVERY_PENDING,
        )
        _record_communication_audit(user=user, request=request, row=row)
    return serialize_communication(row)


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


def _record_communication_audit(*, user, request, row):
    AuditLog.objects.create(
        actor_user=user,
        actor_type="user",
        action=COMMUNICATION_CREATED_ACTION,
        entity_type=COMMUNICATION_ENTITY_TYPE,
        entity_id=row.communication_id,
        old_value_json=None,
        new_value_json={
            "communication_id": str(row.communication_id),
            "related_entity_type": row.related_entity_type,
            "related_entity_id": str(row.related_entity_id),
            "recipient_party_type": row.recipient_party_type,
            "recipient_party_id": (
                str(row.recipient_party_id) if row.recipient_party_id else None
            ),
            "recipient_address": row.recipient_address,
            "channel": row.channel,
            "content_template_id": (
                str(row.content_template_id) if row.content_template_id else None
            ),
            "sent_by_user_id": str(row.sent_by_user_id) if row.sent_by_user_id else None,
            "delivery_status": row.delivery_status,
        },
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _validate_communication_list_query(query_params):
    field_errors = {}
    unknown = set(query_params.keys()) - _COMMUNICATION_LIST_PARAMS
    for field in sorted(unknown):
        field_errors[field] = "Unknown query parameter."
    related_entity_type = _clean_required_string(
        "related_entity_type", query_params.get("related_entity_type"), field_errors
    )
    related_entity_id = _clean_uuid(
        "related_entity_id", query_params.get("related_entity_id"), field_errors
    )
    if field_errors:
        raise ValidationError(field_errors)
    return {
        "related_entity_type": related_entity_type,
        "related_entity_id": related_entity_id,
    }


def _validate_send_payload(payload):
    field_errors = {}
    unknown = set(payload.keys()) - _COMMUNICATION_SEND_FIELDS
    for field in sorted(unknown):
        field_errors[field] = "Unknown field."
    for field in sorted(_REQUIRED_COMMUNICATION_SEND_FIELDS):
        if field not in payload or payload.get(field) in ("", None):
            field_errors[field] = "This field is required."

    cleaned = {
        "related_entity_type": _clean_required_string(
            "related_entity_type", payload.get("related_entity_type"), field_errors
        ),
        "related_entity_id": _clean_uuid(
            "related_entity_id", payload.get("related_entity_id"), field_errors
        ),
        "recipient_party_type": _clean_required_string(
            "recipient_party_type", payload.get("recipient_party_type"), field_errors
        ),
        "recipient_party_id": _clean_optional_uuid(
            "recipient_party_id", payload.get("recipient_party_id"), field_errors
        ),
        "recipient_address": _clean_optional_string(payload.get("recipient_address")),
        "channel": _clean_channel(payload.get("channel"), field_errors),
        "content_template_id": _clean_uuid(
            "content_template_id", payload.get("content_template_id"), field_errors
        ),
        "merge_data": _clean_merge_data(payload.get("merge_data"), field_errors),
    }
    if field_errors:
        raise ValidationError(field_errors)
    return cleaned


def _approved_effective_template(content_template_id):
    try:
        template = ContentTemplate.objects.get(content_template_id=content_template_id)
    except ContentTemplate.DoesNotExist as exc:
        raise ValidationError({"content_template_id": "Content template was not found."}) from exc
    today = timezone.localdate()
    if template.approval_status != ContentTemplate.STATUS_APPROVED:
        raise ValidationError({"content_template_id": "Content template must be approved."})
    if template.effective_from > today:
        raise ValidationError({"content_template_id": "Content template is not effective yet."})
    if template.effective_to and template.effective_to < today:
        raise ValidationError({"content_template_id": "Content template is no longer effective."})
    return template


def _render_template(template_text, declared_variables, merge_data):
    if template_text is None:
        return None
    declared = set(declared_variables)
    provided = set(merge_data.keys())
    missing = declared - provided
    extra = provided - declared
    if missing:
        raise ValidationError(
            {"merge_data": f"Missing template variables: {', '.join(sorted(missing))}."}
        )
    if extra:
        raise ValidationError(
            {"merge_data": f"Unknown template variables: {', '.join(sorted(extra))}."}
        )

    def replace(match):
        return str(merge_data[match.group(1)])

    return _TEMPLATE_VARIABLE_RE.sub(replace, template_text)


def _clean_required_string(field, value, field_errors):
    if value in ("", None):
        field_errors[field] = "This field is required."
        return None
    cleaned = str(value).strip()
    if not cleaned:
        field_errors[field] = "This field is required."
        return None
    return cleaned


def _clean_optional_string(value):
    if value in ("", None):
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _clean_uuid(field, value, field_errors):
    if value in ("", None):
        field_errors[field] = "This field is required."
        return None
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        field_errors[field] = "Must be a valid UUID."
        return None


def _clean_optional_uuid(field, value, field_errors):
    if value in ("", None):
        return None
    return _clean_uuid(field, value, field_errors)


def _clean_channel(value, field_errors):
    if value in ("", None):
        field_errors["channel"] = "This field is required."
        return None
    channel = str(value).strip().lower()
    if channel not in Communication.CHANNELS:
        field_errors["channel"] = "Must be one of courier, email, phone, sms."
    return channel


def _clean_merge_data(value, field_errors):
    if not isinstance(value, dict):
        field_errors["merge_data"] = "Must be a JSON object."
        return {}
    return value


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default
