from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_GET, require_POST

from sfpcl_credit.api import error_response, success_response
from sfpcl_credit.documents import services
from sfpcl_credit.identity.modules import http_auth


@require_POST
def upload_document_file(request):
    user, response = http_auth.authenticated_user(request)
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


@require_GET
def download_document_file(request, document_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_download_documents(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to download document files.",
        )
    try:
        data = services.download_document_file(user, request, document_id)
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested document file was not found."
        )
    return success_response(data, request)
