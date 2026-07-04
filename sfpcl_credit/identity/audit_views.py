"""Thin audit-log read view (003A).

Translates HTTP only: validates the bearer session (401), enforces the canonical
`audit.audit_log.read` permission (403), delegates query parsing/validation/
pagination to `identity.modules.audit_log`, and formats the standard list
envelope. All audit-query behavior lives behind the service module (002C2
boundary pattern). The endpoint is read-only and writes no audit row.
"""

from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET

from sfpcl_credit.api import error_response, list_response
from sfpcl_credit.identity.modules import audit_log, auth_service
from sfpcl_credit.identity.modules.tokens import TokenError


def _authenticate_session(request):
    """Validate the bearer session only (401 cases); no permission enforcement."""
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
def audit_log_list(request):
    user, response = _authenticate_session(request)
    if response is not None:
        return response
    if not audit_log.user_can_read_audit_logs(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to read audit logs.",
        )
    try:
        data, pagination = audit_log.paginated_audit_logs(request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Audit log query failed validation.",
            audit_log.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)
