from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET, require_POST

from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    request_ip,
    request_user_agent,
    success_response,
)
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.legal_documents.modules import document_generation


@require_GET
def loan_document_collection(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data, pagination = document_generation.list_for_application(
            actor=user,
            application_id=loan_application_id,
            query_params=request.GET,
        )
    except document_generation.LegalDocumentAccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to this loan application.",
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan document query failed validation.",
            document_generation.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)


@require_POST
def generate_loan_document(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = document_generation.generate(
            actor=user,
            application_id=loan_application_id,
            payload=parse_json_body(request),
            metadata=document_generation.RequestMetadata(
                request_id=request.headers.get("X-Request-ID"),
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            ),
        )
    except document_generation.LegalDocumentAccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to this loan application.",
        )
    except document_generation.InvalidGenerationState as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan document generation failed validation.",
            document_generation.validation_field_errors(exc),
        )
    return success_response(data, request)
