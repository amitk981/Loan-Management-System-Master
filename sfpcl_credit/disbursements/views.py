from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, success_response
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
        return success_response(
            evaluate(actor=actor, loan_account_id=loan_account_id), request
        )
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
