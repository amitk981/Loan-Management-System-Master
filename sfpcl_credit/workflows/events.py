import uuid
from datetime import datetime, time, timedelta
from math import ceil

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.approvals.modules.read_scope import has_active_audit_read_scope
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.workflows.models import WorkflowEvent


WORKFLOW_EVENT_READ_PERMISSION = "audit.workflow_event.read"

_UUID_FILTERS = {"entity_id", "actor_user_id"}
_FILTER_PARAMS = {
    "entity_type",
    "workflow_name",
    "to_state",
    "created_from",
    "created_to",
    "exception",
    "approval",
    "application_reference",
    "loan_account_reference",
} | _UUID_FILTERS
_PAGINATION_PARAMS = {"page", "page_size"}
_ALLOWED_PARAMS = _FILTER_PARAMS | _PAGINATION_PARAMS

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100


def record_workflow_event(
    *,
    actor,
    workflow_name,
    entity_type,
    entity_id,
    from_state,
    to_state,
    trigger_reason="",
    action_code="",
    metadata=None,
):
    """Persist a source §26.2 workflow event through the canonical interface.

    `action_code` and `metadata` are accepted so callers pass explicit action
    facts at the boundary, but §26.2 has no action/metadata columns. They are
    intentionally not embedded as business rules or schema drift.
    """
    return WorkflowEvent.objects.create(
        workflow_name=workflow_name,
        entity_type=entity_type,
        entity_id=entity_id,
        from_state=from_state,
        to_state=to_state,
        triggered_by_user=actor,
        trigger_reason=trigger_reason or "",
    )


def user_can_read_workflow_events(user):
    if WORKFLOW_EVENT_READ_PERMISSION not in auth_service.effective_permission_codes(user):
        return False
    if "internal_auditor" in auth_service.effective_role_codes(user):
        return has_active_audit_read_scope(user)
    return True


def serialize_workflow_event(row):
    actor = None
    if row.triggered_by_user_id is not None:
        actor = {
            "user_id": str(row.triggered_by_user_id),
            "full_name": row.triggered_by_user.full_name,
        }
    return {
        "workflow_event_id": str(row.workflow_event_id),
        "workflow_name": row.workflow_name,
        "module": row.workflow_name,
        "entity_type": row.entity_type,
        "entity_id": str(row.entity_id),
        "linked_record": {
            "entity_type": row.entity_type,
            "entity_id": str(row.entity_id),
        },
        "from_state": row.from_state,
        "to_state": row.to_state,
        "triggered_by_user": actor,
        "trigger_reason": row.trigger_reason,
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_workflow_events(*, actor, query_params):
    filters, predicates = _validated_filters(query_params)
    queryset = (
        WorkflowEvent.objects.select_related("triggered_by_user")
        .filter(**filters)
        .filter(predicates)
        .filter(_scope_predicate(actor))
        .order_by("-created_at", "-workflow_event_id")
    )

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
        serialize_workflow_event(row) for row in queryset[offset : offset + page_size]
    ]
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
    for field in ("entity_type", "workflow_name", "to_state"):
        value = query_params.get(field)
        if value:
            filters[field] = value
    for field in _UUID_FILTERS:
        raw = query_params.get(field)
        if raw:
            model_field = "triggered_by_user_id" if field == "actor_user_id" else field
            filters[model_field] = _parse_uuid(field, raw)
    predicates = Q()
    predicates &= _reference_predicate(query_params)
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

    predicate = Q(triggered_by_user=actor)
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
    predicate = Q(workflow_name__icontains=token) | Q(entity_type__icontains=token)
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
