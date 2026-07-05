import uuid
from math import ceil

from django.core.exceptions import ValidationError

from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.workflows.models import WorkflowEvent


WORKFLOW_EVENT_READ_PERMISSION = "audit.workflow_event.read"

_UUID_FILTERS = {"entity_id"}
_FILTER_PARAMS = {"entity_type"} | _UUID_FILTERS
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
    return WORKFLOW_EVENT_READ_PERMISSION in auth_service.effective_permission_codes(user)


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
        "entity_type": row.entity_type,
        "entity_id": str(row.entity_id),
        "from_state": row.from_state,
        "to_state": row.to_state,
        "triggered_by_user": actor,
        "trigger_reason": row.trigger_reason,
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_workflow_events(query_params):
    filters = _validated_filters(query_params)
    queryset = (
        WorkflowEvent.objects.select_related("triggered_by_user")
        .filter(**filters)
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
