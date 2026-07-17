from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.disbursements.modules.disbursement_workflow import (
    DisbursementAuthorisationConflict,
    DisbursementConflict,
    DisbursementReadinessStale,
    DisbursementWorkflow,
)
from sfpcl_credit.disbursements.modules.disbursement_readiness import evaluate
from sfpcl_credit.domain_errors import DomainObjectAccessDenied, DomainPermissionDenied
from sfpcl_credit.identity.modules import http_auth


@require_http_methods(["GET"])
def readiness(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.GET:
        fields = {field: "Unknown query parameter." for field in sorted(request.GET)}
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Disbursement readiness query failed validation.",
            fields,
        )
    try:
        data = evaluate(actor=actor, loan_account_id=loan_account_id)
        return success_response(data, request)
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request,
            403,
            "OBJECT_ACCESS_DENIED",
            "The loan account was not found or is inaccessible.",
        )
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "Invalid readiness request.", exc.message_dict
        )


@require_http_methods(["POST"])
def initiate_disbursement(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.GET:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Disbursement initiation failed validation.",
            {field: "Unknown query parameter." for field in sorted(request.GET)},
        )
    try:
        payload = parse_json_body(request)
        data = DisbursementWorkflow.initiate(
            actor=actor,
            loan_account_id=loan_account_id,
            payload=payload,
            idempotency_key=request.headers.get("Idempotency-Key"),
            request=request,
        )
        return success_response(data, request)
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request,
            403,
            "OBJECT_ACCESS_DENIED",
            "The loan account was not found or is inaccessible.",
        )
    except DisbursementReadinessStale as exc:
        return error_response(request, 409, exc.code, str(exc))
    except DisbursementConflict as exc:
        return error_response(request, 409, exc.code, str(exc))
    except ValidationError as exc:
        fields = exc.message_dict if hasattr(exc, "message_dict") else {
            "non_field_errors": exc.messages[0]
        }
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Disbursement initiation failed validation.",
            fields,
        )


@require_http_methods(["POST"])
def authorise_disbursement(request, disbursement_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.GET:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Disbursement authorisation failed validation.",
            {field: "Unknown query parameter." for field in sorted(request.GET)},
        )
    try:
        data = DisbursementWorkflow.authorise(
            actor=actor,
            disbursement_id=disbursement_id,
            payload=parse_json_body(request),
            request=request,
        )
        return success_response(data, request)
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request,
            403,
            "OBJECT_ACCESS_DENIED",
            "The disbursement was not found or is inaccessible.",
        )
    except DisbursementAuthorisationConflict as exc:
        return error_response(request, 409, exc.code, str(exc))
    except ValidationError as exc:
        fields = exc.message_dict if hasattr(exc, "message_dict") else {
            "non_field_errors": exc.messages[0]
        }
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Disbursement authorisation failed validation.",
            fields,
        )
