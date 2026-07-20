from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.monitoring.modules.dpd_monitoring import (
    DpdConflict,
    DpdNotFound,
    DpdPermissionDenied,
    DpdValidation,
    calculate_for_loan,
    calculate_portfolio,
    get_current_for_loan,
)


@require_http_methods(["GET"])
def dpd_status(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            get_current_for_loan(actor=actor, loan_account_id=loan_account_id), request
        )
    except DpdPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "DPD read permission and loan scope are required."
        )
    except DpdNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The DPD status was not found or is inaccessible."
        )


@require_http_methods(["POST"])
def dpd_calculate(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            calculate_for_loan(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except (DpdValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, DpdValidation) else {"body": exc.messages[0]}
        return error_response(
            request, 400, "VALIDATION_ERROR", "DPD calculation failed validation.", fields
        )
    except DpdPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "DPD calculation permission and loan scope are required."
        )
    except DpdNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )
    except DpdConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def dpd_bulk_calculate(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            calculate_portfolio(
                actor=actor,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except (DpdValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, DpdValidation) else {"body": exc.messages[0]}
        return error_response(
            request, 400, "VALIDATION_ERROR", "Bulk DPD calculation failed validation.", fields
        )
    except DpdPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "DPD calculation permission and loan scope are required."
        )
