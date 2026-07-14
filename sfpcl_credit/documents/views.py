from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    request_ip,
    request_user_agent,
    success_response,
)
from sfpcl_credit.documents import selectors, services
from sfpcl_credit.documents.modules import document_templates
from sfpcl_credit.documents.modules import document_generation
from sfpcl_credit.applications.modules import application_authority
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
            rows, pagination = selectors.list_document_templates(request.GET)
            data = [document_templates.serialize(row) for row in rows]
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
            actor=user,
            metadata=_request_metadata(request),
            payload=parse_json_body(request),
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
            metadata=_request_metadata(request),
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


@require_http_methods(["GET"])
def loan_document_collection(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    application, access = application_authority.resolve_application_access(
        application_id=loan_application_id,
        actor=user,
        required_permission=document_generation.READ_PERMISSION,
        actor_permissions=permissions,
    )
    if not access.allowed:
        return error_response(
            request, 403, access.error_code or "OBJECT_ACCESS_DENIED",
            "You do not have access to this loan application."
        )
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    try:
        data, pagination = document_generation.list_for_application(
            application_id=application.pk, query_params=request.GET
        )
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "Loan document query failed validation.",
            document_generation.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)


@require_POST
def generate_loan_document(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    application, access = application_authority.resolve_application_access(
        application_id=loan_application_id,
        actor=user,
        required_permission=document_generation.GENERATE_PERMISSION,
        actor_permissions=permissions,
    )
    if not access.allowed:
        return error_response(
            request, 403, access.error_code or "OBJECT_ACCESS_DENIED",
            "You do not have access to this loan application."
        )
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    try:
        data = document_generation.generate(
            actor=user,
            application_id=application.pk,
            payload=parse_json_body(request),
            metadata=document_generation.RequestMetadata(
                request_id=request.headers.get("X-Request-ID"),
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            ),
        )
    except document_generation.InvalidGenerationState as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "Loan document generation failed validation.",
            document_generation.validation_field_errors(exc),
        )
    return success_response(data, request)


def _request_metadata(request):
    return document_templates.RequestMetadata(
        request_id=request.headers.get("X-Request-ID"),
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
