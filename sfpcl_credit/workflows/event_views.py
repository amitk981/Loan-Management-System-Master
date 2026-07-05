from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET

from sfpcl_credit.api import error_response, list_response
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.tokens import TokenError
from sfpcl_credit.workflows import events


def _authenticate_session(request):
    authorization = request.headers.get("Authorization", "")
    if not authorization:
        return None, error_response(
            request, 401, "AUTH_REQUIRED", "Bearer access token is required."
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        return None, error_response(
            request, 401, "INVALID_TOKEN", "Authorization header must use Bearer token."
        )
    try:
        session = auth_service.validate_access_session(parts[1])
    except TokenError as exc:
        return None, error_response(request, 401, exc.code, exc.message)
    return session.user, None


@require_GET
def workflow_event_list(request):
    user, response = _authenticate_session(request)
    if response is not None:
        return response
    if not events.user_can_read_workflow_events(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
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
