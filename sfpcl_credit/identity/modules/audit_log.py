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
from datetime import datetime, time, timedelta
from math import ceil

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.approvals.modules.read_scope import has_active_audit_read_scope
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.shared.masking import redact_sensitive_mapping


# Canonical audit-read permission from the 002C catalogue (auth-permissions §).
# Do NOT invent `reports.audit.read`; this is the only code that grants read access.
AUDIT_READ_PERMISSION = "audit.audit_log.read"

# Filters supported by §42.1. `entity_type` is a free-text match; `entity_id` and
# `actor_user_id` must be UUIDs.
_UUID_FILTERS = {"entity_id", "actor_user_id"}
_FILTER_PARAMS = {
    "entity_type",
    "created_from",
    "created_to",
    "role_code",
    "action",
    "module",
    "exception",
    "approval",
    "application_reference",
    "loan_account_reference",
} | _UUID_FILTERS
# Pagination params stay allowed alongside the filters; everything else is rejected.
_PAGINATION_PARAMS = {"page", "page_size"}
_ALLOWED_PARAMS = _FILTER_PARAMS | _PAGINATION_PARAMS

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100


def user_can_read_audit_logs(user):
    """True when the user's active role holds the canonical audit-read permission."""
    if AUDIT_READ_PERMISSION not in auth_service.effective_permission_codes(user):
        return False
    if "internal_auditor" in auth_service.effective_role_codes(user):
        return has_active_audit_read_scope(user)
    return True


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
    old_value = redact_sensitive_mapping(row.old_value_json)
    new_value = redact_sensitive_mapping(row.new_value_json)
    snapshot = row.new_value_json if isinstance(row.new_value_json, dict) else {}
    return {
        "audit_log_id": str(row.audit_log_id),
        "actor": actor,
        "actor_type": row.actor_type,
        "actor_role_codes": _string_list(snapshot.get("actor_role_codes")),
        "actor_team_codes": _string_list(snapshot.get("actor_team_codes")),
        "action": row.action,
        "module": row.action.partition(".")[0],
        "entity_type": row.entity_type,
        "entity_id": str(row.entity_id) if row.entity_id else None,
        "linked_record": {
            "entity_type": row.entity_type,
            "entity_id": str(row.entity_id) if row.entity_id else None,
        },
        "old_value": old_value,
        "new_value": new_value,
        "reason": _safe_scalar(snapshot.get("reason")),
        "outcome": _safe_scalar(snapshot.get("outcome")),
        "request_id": _safe_scalar(snapshot.get("request_id")),
        "ip_address": row.ip_address,
        "device": row.user_agent or None,
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_audit_logs(*, actor, query_params):
    """Return `(items, pagination)` for a validated audit-log query.

    Rejects unknown query parameters and invalid UUID filters with a
    `ValidationError` carrying a field-keyed message dict (mapped to the standard
    `400 VALIDATION_ERROR` envelope by the view). Results are newest-first.
    """
    filters, predicates = _validated_filters(query_params)
    queryset = (
        AuditLog.objects.select_related("actor_user")
        .filter(**filters)
        .filter(predicates)
        .filter(_scope_predicate(actor))
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
    action = query_params.get("action")
    if action:
        filters["action"] = action
    predicates = Q()
    predicates &= _reference_predicate(query_params)
    module = query_params.get("module")
    if module:
        predicates &= Q(action__startswith=f"{module}.")
    role_code = query_params.get("role_code")
    if role_code:
        predicates &= (
            Q(new_value_json__actor_role_codes__0=role_code)
            | Q(new_value_json__role_codes__0=role_code)
        )
    created_from = _date_filter(query_params, "created_from")
    created_to = _date_filter(query_params, "created_to")
    if created_from and created_to and created_from > created_to:
        raise ValidationError({"created_to": "Must be on or after created_from."})
    if created_from:
        filters["created_at__gte"] = _day_boundary(created_from)
    if created_to:
        filters["created_at__lt"] = _day_boundary(created_to + timedelta(days=1))
    predicates &= _category_predicate(query_params, "exception", "exception")
    predicates &= _category_predicate(query_params, "approval", "approv")
    return filters, predicates


def _scope_predicate(actor):
    if (
        "internal_auditor" in auth_service.effective_role_codes(actor)
        and has_active_audit_read_scope(actor)
    ):
        return Q()

    predicate = Q(actor_user=actor)
    from sfpcl_credit.loans.modules.loan_account_read import (
        LoanAccountReadPermissionDenied,
        scoped_account_candidates,
    )

    try:
        accounts = scoped_account_candidates(actor=actor)
        predicate |= Q(entity_type="loan_account", entity_id__in=accounts.values("pk"))
        predicate |= Q(
            entity_type="loan_application",
            entity_id__in=accounts.values("loan_application_id"),
        )
    except LoanAccountReadPermissionDenied:
        return predicate
    return predicate


def _date_filter(query_params, field):
    raw = query_params.get(field)
    if not raw:
        return None
    try:
        value = parse_date(raw)
    except (TypeError, ValueError):
        value = None
    if value is None:
        raise ValidationError({field: "Must be a valid ISO date."})
    return value


def _day_boundary(value):
    return timezone.make_aware(datetime.combine(value, time.min))


def _category_predicate(query_params, field, token):
    raw = query_params.get(field)
    if raw in (None, ""):
        return Q()
    if str(raw).lower() not in {"true", "false"}:
        raise ValidationError({field: "Must be true or false."})
    predicate = Q(action__icontains=token) | Q(entity_type__icontains=token)
    return predicate if str(raw).lower() == "true" else ~predicate


def _reference_predicate(query_params):
    predicate = Q()
    application_reference = query_params.get("application_reference")
    if application_reference:
        from sfpcl_credit.applications.models import LoanApplication

        predicate &= Q(
            entity_type="loan_application",
            entity_id__in=LoanApplication.objects.filter(
                application_reference_number__iexact=application_reference
            ).values("pk"),
        )
    loan_account_reference = query_params.get("loan_account_reference")
    if loan_account_reference:
        from sfpcl_credit.loans.models import LoanAccount

        predicate &= Q(
            entity_type="loan_account",
            entity_id__in=LoanAccount.objects.filter(
                loan_account_number__iexact=loan_account_reference
            ).values("pk"),
        )
    return predicate


def _string_list(value):
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _safe_scalar(value):
    return value if isinstance(value, (str, int, float, bool)) else None


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
