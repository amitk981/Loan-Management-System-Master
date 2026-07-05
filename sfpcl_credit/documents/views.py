from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from sfpcl_credit.api import error_response, success_response
from sfpcl_credit.documents import services
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.tokens import TokenError


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


@require_POST
def upload_document_file(request):
    user, response = _authenticate_session(request)
    if response is not None:
        return response
    if not services.user_can_upload_documents(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to upload document files.",
        )
    try:
        data = services.upload_document_file(user, request)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Document upload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)
