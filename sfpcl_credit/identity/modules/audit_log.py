"""Audit-log read service boundary (003A).

The audit-log read endpoint (`GET /api/v1/audit-logs/`) exposes the existing
append-only `identity.AuditLog` records (`docs/source/api-contracts.md` §42.1).
All query parsing/validation, filtering, newest-first pagination, and item
serialization live here rather than in the Django view, matching the 002C2
service-boundary pattern so the behavior is unit-testable and reusable by later
audit/document slices. This module is read-only: it never writes or mutates
audit rows.
"""

import uuid
from math import ceil

from django.core.exceptions import ValidationError

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service


# Canonical audit-read permission from the 002C catalogue (auth-permissions §).
# Do NOT invent `reports.audit.read`; this is the only code that grants read access.
AUDIT_READ_PERMISSION = "audit.audit_log.read"

# Filters supported by §42.1. `entity_type` is a free-text match; `entity_id` and
# `actor_user_id` must be UUIDs.
_UUID_FILTERS = {"entity_id", "actor_user_id"}
_FILTER_PARAMS = {"entity_type"} | _UUID_FILTERS
# Pagination params stay allowed alongside the filters; everything else is rejected.
_PAGINATION_PARAMS = {"page", "page_size"}
_ALLOWED_PARAMS = _FILTER_PARAMS | _PAGINATION_PARAMS

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100


def user_can_read_audit_logs(user):
    """True when the user's active role holds the canonical audit-read permission."""
    return AUDIT_READ_PERMISSION in auth_service.effective_permission_codes(user)


def serialize_audit_log(row):
    """Map an `AuditLog` row to the §42.1 response item.

    `old_value_json`/`new_value_json` are surfaced under the contract names
    `old_value`/`new_value`. System/no-actor rows serialize as `actor: null`
    rather than fabricating a user. `user_agent` is intentionally omitted — it is
    not part of the §42.1 item shape.
    """
    actor = None
    if row.actor_user_id is not None:
        actor = {"user_id": str(row.actor_user_id), "full_name": row.actor_user.full_name}
    return {
        "audit_log_id": str(row.audit_log_id),
        "actor": actor,
        "actor_type": row.actor_type,
        "action": row.action,
        "entity_type": row.entity_type,
        "entity_id": str(row.entity_id) if row.entity_id else None,
        "old_value": row.old_value_json,
        "new_value": row.new_value_json,
        "ip_address": row.ip_address,
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_audit_logs(query_params):
    """Return `(items, pagination)` for a validated audit-log query.

    Rejects unknown query parameters and invalid UUID filters with a
    `ValidationError` carrying a field-keyed message dict (mapped to the standard
    `400 VALIDATION_ERROR` envelope by the view). Results are newest-first.
    """
    filters = _validated_filters(query_params)
    queryset = (
        AuditLog.objects.select_related("actor_user")
        .filter(**filters)
        .order_by("-created_at", "-audit_log_id")
    )

    page = _positive_int(query_params.get("page"), 1)
    page_size = min(_positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE), _MAX_PAGE_SIZE)
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size

    items = [serialize_audit_log(row) for row in queryset[offset : offset + page_size]]
    pagination = {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
    return items, pagination


def validation_field_errors(exc):
    """Flatten a `ValidationError` into `{field: message}` for the error envelope."""
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


def _validated_filters(query_params):
    unknown = set(query_params.keys()) - _ALLOWED_PARAMS
    if unknown:
        raise ValidationError(
            {param: "Unknown query parameter." for param in sorted(unknown)}
        )

    filters = {}
    entity_type = query_params.get("entity_type")
    if entity_type:
        filters["entity_type"] = entity_type
    for field in _UUID_FILTERS:
        raw = query_params.get(field)
        if raw:
            filters[field] = _parse_uuid(field, raw)
    return filters


def _parse_uuid(field, raw):
    try:
        return uuid.UUID(str(raw))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValidationError({field: "Must be a valid UUID."}) from exc


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


__all__ = [
    "AUDIT_READ_PERMISSION",
    "paginated_audit_logs",
    "serialize_audit_log",
    "user_can_read_audit_logs",
    "validation_field_errors",
]
