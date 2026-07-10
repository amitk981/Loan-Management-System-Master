from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET

from sfpcl_credit.api import error_response, success_response
from sfpcl_credit.dashboard import services
from sfpcl_credit.identity.modules import http_auth


@require_GET
def dashboard_summary(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_read_dashboard(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read dashboard summaries.",
        )
    try:
        data = services.dashboard_summary(user, request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Dashboard query failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)
