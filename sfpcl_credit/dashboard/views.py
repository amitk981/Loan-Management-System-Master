from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET

from sfpcl_credit.api import error_response, success_response
from sfpcl_credit.dashboard import services
from sfpcl_credit.identity.modules import auth_service, http_auth


@require_GET
def dashboard_summary(request, expected_context=None):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    permission_codes = auth_service.effective_permission_codes(user)
    if not services.user_can_read_dashboard(user, permission_codes):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read dashboard summaries.",
        )
    try:
        data = services.dashboard_summary(
            user,
            request.GET,
            expected_context=expected_context,
            permission_codes=permission_codes,
        )
    except services.DashboardPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read this dashboard.",
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Dashboard query failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)
