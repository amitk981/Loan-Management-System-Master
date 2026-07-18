from math import ceil
import uuid

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.models import Communication, ContentTemplate, Notification
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.communications.modules.communication_dispatcher import CommunicationDispatcher


CONTENT_TEMPLATE_READ_PERMISSION = "communications.content_template.read"
CONTENT_TEMPLATE_MANAGE_PERMISSION = "communications.content_template.manage"
COMMUNICATION_READ_PERMISSION = "communications.communication.read"
COMMUNICATION_SEND_PERMISSION = "communications.communication.send"
DISBURSEMENT_ADVICE_SEND_PERMISSION = "finance.disbursement.send_advice"
NOTIFICATION_READ_PERMISSION = "communications.notification.read"
CONTENT_TEMPLATE_ENTITY_TYPE = "content_template"
COMMUNICATION_ENTITY_TYPE = "communication"
NOTIFICATION_ENTITY_TYPE = "notification"
CONTENT_TEMPLATE_CREATED_ACTION = "communications.content_template.created"
CONTENT_TEMPLATE_UPDATED_ACTION = "communications.content_template.updated"
COMMUNICATION_CREATED_ACTION = "communications.communication.created"
NOTIFICATION_MARKED_READ_ACTION = "communications.notification.marked_read"

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
_NOTIFICATION_LIST_PARAMS = {"page", "page_size", "read_status", "severity", "category"}
_READ_STATUSES = {"all", "read", "unread"}
class StaleWriteError(Exception):
    pass


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


def user_can_manage_communication_exceptions(user):
    permissions = set(auth_service.effective_permission_codes(user))
    return bool(
        {
            COMMUNICATION_SEND_PERMISSION,
            DISBURSEMENT_ADVICE_SEND_PERMISSION,
        }
        & permissions
    )


def user_can_read_notifications(user):
    return NOTIFICATION_READ_PERMISSION in auth_service.effective_permission_codes(user)


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


def serialize_notification(row):
    return {
        "notification_id": str(row.notification_id),
        "communication_id": (
            str(row.communication_id) if row.communication_id else None
        ),
        "notification_type": row.notification_type,
        "category": row.category,
        "severity": row.severity,
        "title": row.title,
        "message": row.message,
        "related_entity_type": row.related_entity_type or None,
        "related_entity_id": (
            str(row.related_entity_id) if row.related_entity_id else None
        ),
        "action_label": row.action_label or None,
        "action_url": row.action_url or None,
        "sender": (
            {
                "user_id": str(row.sender_user.user_id),
                "full_name": row.sender_user.full_name,
            }
            if row.sender_user_id
            else None
        ),
        "recipient": _serialized_notification_recipient(row),
        "read": row.read,
        "read_at": row.read_at.isoformat() if row.read_at else None,
        "read_by_user_id": str(row.read_by_user_id) if row.read_by_user_id else None,
        "read_state_version": row.read_state_version,
        "created_at": row.created_at.isoformat(),
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


def paginated_notifications(user, query_params):
    filters = _validate_notification_list_query(query_params)
    queryset = _notification_queryset_for_user(user)
    if filters["read_status"] == "read":
        queryset = queryset.filter(read_at__isnull=False)
    elif filters["read_status"] == "unread":
        queryset = queryset.filter(read_at__isnull=True)
    if filters["severity"]:
        queryset = queryset.filter(severity=filters["severity"])
    if filters["category"]:
        queryset = queryset.filter(category=filters["category"])
    queryset = queryset.select_related("sender_user", "recipient_user", "communication")
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
        serialize_notification(row) for row in queryset[offset : offset + page_size]
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
    idempotency_key = request.headers.get("Idempotency-Key")
    with transaction.atomic():
        row = CommunicationDispatcher.create_from_template(
            actor=user,
            request=request,
            content_template_id=cleaned["content_template_id"],
            merge_data=cleaned["merge_data"],
            related_entity_type=cleaned["related_entity_type"],
            related_entity_id=cleaned["related_entity_id"],
            recipient_party_type=cleaned["recipient_party_type"],
            recipient_party_id=cleaned.get("recipient_party_id"),
            recipient_address=cleaned.get("recipient_address"),
            channel=cleaned["channel"],
            idempotency_key=idempotency_key,
        )
        row = CommunicationDispatcher.send(
            communication_id=row.pk,
            idempotency_key=idempotency_key,
            actor=user,
            request=request,
        )
    return serialize_communication(row)


def create_internal_team_communication(
    *, sender, team_code, related_entity_type, related_entity_id, subject, body,
    action_label, action_url, request_meta=None,
):
    """Persist a communication snapshot and its linked internal team notification."""
    request_meta = request_meta or {}
    row = Communication.objects.create(
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        recipient_party_type="team",
        recipient_address=team_code,
        channel=Communication.CHANNEL_EMAIL,
        subject_snapshot=subject,
        body_snapshot=body,
        sent_by_user=sender,
        delivery_status=Communication.DELIVERY_PENDING,
    )
    notification = Notification.objects.create(
        communication=row,
        notification_type="approval_case_completed",
        category="Application",
        severity=Notification.SEVERITY_INFO,
        title=subject,
        message=body,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        action_label=action_label,
        action_url=action_url,
        sender_user=sender,
        recipient_team_code=team_code,
    )
    AuditLog.objects.create(
        actor_user=sender,
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
            "recipient_party_id": None,
            "recipient_address": row.recipient_address,
            "channel": row.channel,
            "content_template_id": None,
            "sent_by_user_id": str(row.sent_by_user_id),
            "delivery_status": row.delivery_status,
        },
        ip_address=request_meta.get("ip_address", ""),
        user_agent=request_meta.get("user_agent", ""),
    )
    return row, notification


def create_internal_user_task(
    *, sender, recipient, related_entity_type, related_entity_id, subject, body,
    action_label, action_url, notification_type, category,
):
    """Persist one adapter-owned direct communication and its in-app task."""
    communication_id = uuid.uuid4()
    row = Communication.objects.create(
        communication_id=communication_id,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        recipient_party_type="user",
        recipient_party_id=recipient.pk,
        recipient_address=recipient.email,
        channel=Communication.CHANNEL_EMAIL,
        subject_snapshot=subject,
        body_snapshot=body,
        sent_by_user=sender,
        delivery_status=Communication.DELIVERY_PENDING,
        external_message_id=f"manual:{communication_id}",
    )
    task = Notification.objects.create(
        communication=row,
        notification_type=notification_type,
        category=category,
        severity=Notification.SEVERITY_INFO,
        title=subject,
        message=body,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        action_label=action_label,
        action_url=action_url,
        sender_user=sender,
        recipient_user=recipient,
    )
    return row, task


def mark_notification_read(user, request, notification_id, payload):
    expected_version = _clean_read_state_version(payload)
    with transaction.atomic():
        row = (
            _locked_notification_queryset_for_user(user)
            .select_related("sender_user", "recipient_user", "communication")
            .get(notification_id=notification_id)
        )
        if expected_version != row.read_state_version:
            raise StaleWriteError()
        old_value = {
            "read": row.read,
            "read_at": row.read_at.isoformat() if row.read_at else None,
            "read_by_user_id": str(row.read_by_user_id) if row.read_by_user_id else None,
            "read_state_version": row.read_state_version,
        }
        if not row.read:
            row.read_at = timezone.now()
            row.read_by_user = user
            row.read_state_version += 1
            row.save(
                update_fields=[
                    "read_at",
                    "read_by_user",
                    "read_state_version",
                    "updated_at",
                ]
            )
            _record_notification_marked_read_audit(
                user=user,
                request=request,
                row=row,
                old_value=old_value,
                new_value={
                    "read": row.read,
                    "read_at": row.read_at.isoformat(),
                    "read_by_user_id": str(row.read_by_user_id),
                    "read_state_version": row.read_state_version,
                },
            )
    return serialize_notification(row)


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


def _record_notification_marked_read_audit(*, user, request, row, old_value, new_value):
    AuditLog.objects.create(
        actor_user=user,
        actor_type="user",
        action=NOTIFICATION_MARKED_READ_ACTION,
        entity_type=NOTIFICATION_ENTITY_TYPE,
        entity_id=row.notification_id,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _notification_queryset_for_user(user):
    return _base_notification_queryset_for_user(user).order_by(
        "-created_at", "-notification_id"
    )


def _locked_notification_queryset_for_user(user):
    return _base_notification_queryset_for_user(user).select_for_update()


def _base_notification_queryset_for_user(user):
    return Notification.objects.filter(
        Q(recipient_user=user)
        | Q(recipient_role_code__in=user.role_codes())
        | Q(recipient_team_code__in=user.team_codes())
    )


def _serialized_notification_recipient(row):
    if row.recipient_user_id:
        return {
            "type": "user",
            "user_id": str(row.recipient_user_id),
            "full_name": row.recipient_user.full_name,
        }
    if row.recipient_role_code:
        return {"type": "role", "role_code": row.recipient_role_code}
    if row.recipient_team_code:
        return {"type": "team", "team_code": row.recipient_team_code}
    return {"type": "unknown"}


def _validate_notification_list_query(query_params):
    field_errors = {}
    unknown = set(query_params.keys()) - _NOTIFICATION_LIST_PARAMS
    for field in sorted(unknown):
        field_errors[field] = "Unknown query parameter."
    read_status = str(query_params.get("read_status", "all")).strip().lower()
    if read_status not in _READ_STATUSES:
        field_errors["read_status"] = "Must be one of all, read, unread."
    severity = _clean_optional_string(query_params.get("severity"))
    if severity and severity not in Notification.SEVERITIES:
        field_errors["severity"] = "Must be one of info, urgent, warning."
    category = _clean_optional_string(query_params.get("category"))
    if field_errors:
        raise ValidationError(field_errors)
    return {
        "read_status": read_status,
        "severity": severity,
        "category": category,
    }


def _clean_read_state_version(payload):
    if set(payload.keys()) - {"read_state_version"}:
        raise ValidationError({"read_state_version": "Only read_state_version is allowed."})
    try:
        version = int(payload.get("read_state_version"))
    except (TypeError, ValueError):
        raise ValidationError({"read_state_version": "This field is required."}) from None
    if version < 1:
        raise ValidationError({"read_state_version": "Must be a positive integer."})
    return version


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
