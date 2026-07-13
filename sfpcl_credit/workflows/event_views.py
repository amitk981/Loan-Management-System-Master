from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET

from sfpcl_credit.api import error_response, list_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.workflows import events


@require_GET
def workflow_event_list(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not events.user_can_read_workflow_events(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read workflow events.",
        )
    try:
        data, pagination = events.paginated_workflow_events(request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Workflow event query failed validation.",
            events.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)
