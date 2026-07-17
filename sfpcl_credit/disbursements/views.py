from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.disbursements.modules.disbursement_initiation import (
    DisbursementConflict,
    DisbursementReadinessStale,
    initiate,
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
        data.pop("_evidence", None)
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
        data = initiate(
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
        return error_response(request, 409, "DISBURSEMENT_NOT_READY", str(exc))
    except DisbursementConflict as exc:
        return error_response(request, 409, "DISBURSEMENT_CONFLICT", str(exc))
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
