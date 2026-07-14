from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.documents import services
from sfpcl_credit.documents.modules import document_templates
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
            "FORBIDDEN",
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
            "FORBIDDEN",
            "You do not have permission to download document files.",
        )
    try:
        data = services.download_document_file(user, request, document_id)
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested document file was not found."
        )
    return success_response(data, request)


@require_http_methods(["GET", "POST"])
def document_template_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET":
        if not document_templates.can_read(user):
            return error_response(
                request, 403, "FORBIDDEN", "You do not have permission to read document templates."
            )
        try:
            data, pagination = document_templates.list_templates(request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Document template query failed validation.",
                document_templates.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    if not document_templates.can_manage(user):
        return error_response(
            request, 403, "FORBIDDEN", "You do not have permission to manage document templates."
        )
    try:
        data = document_templates.create(
            actor=user, request=request, payload=parse_json_body(request)
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Document template failed validation.",
            document_templates.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["PATCH"])
def document_template_detail(request, document_template_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not document_templates.can_manage(user):
        return error_response(
            request, 403, "FORBIDDEN", "You do not have permission to manage document templates."
        )
    try:
        data = document_templates.create_successor(
            actor=user,
            request=request,
            document_template_id=document_template_id,
            payload=parse_json_body(request),
        )
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested document template was not found."
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Document template successor failed validation.",
            document_templates.validation_field_errors(exc),
        )
    return success_response(data, request)
