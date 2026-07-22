from django.views.decorators.http import require_http_methods

from django.core.exceptions import ValidationError

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.closure.modules.loan_closure import (
    ClosureConflict,
    ClosureNotFound,
    ClosurePermissionDenied,
    ClosureValidation,
    close,
    evaluate_readiness,
)
from sfpcl_credit.identity.modules import http_auth


@require_http_methods(["GET"])
def closure_readiness(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            evaluate_readiness(actor=actor, loan_account_id=loan_account_id), request
        )
    except ClosurePermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Closure readiness permission is required."
        )
    except ClosureNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )


@require_http_methods(["POST"])
def loan_close(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            close(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except ClosureValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan closure failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan closure failed validation.",
            {"body": exc.messages[0]},
        )
    except ClosurePermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Loan closure authority is required."
        )
    except ClosureNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )
    except ClosureConflict as exc:
        return error_response(request, 409, "LOAN_NOT_FULLY_REPAID", str(exc))
