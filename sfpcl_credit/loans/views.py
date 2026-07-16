from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
    DomainValidationError,
)
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.loans.modules.loan_account_lifecycle import (
    LoanAccountConflict,
    create_loan_account,
)


@require_http_methods(["POST"])
def create_from_sanction(request, loan_application_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            create_loan_account(
                actor=actor,
                application_id=loan_application_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except DomainValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan account creation failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan account creation failed validation.",
            {"body": exc.messages[0]},
        )
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request,
            403,
            "OBJECT_ACCESS_DENIED",
            "The loan application was not found or is inaccessible.",
        )
    except DomainInvalidStateError as exc:
        return error_response(request, 409, "STALE_STATE", str(exc))
    except LoanAccountConflict as exc:
        return error_response(request, 409, "LOAN_ACCOUNT_CONFLICT", str(exc))
