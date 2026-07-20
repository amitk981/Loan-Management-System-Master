from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.interest.modules.interest_engine import (
    InterestInvoiceConflict,
    InterestInvoiceNotFound,
    InterestInvoicePermissionDenied,
    InterestInvoiceValidation,
    generate_invoice,
    issue_invoice,
    list_invoices,
)


@require_http_methods(["GET", "POST"])
def invoice_collection(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        if request.method == "GET":
            data, pagination = list_invoices(
                actor=actor,
                loan_account_id=loan_account_id,
                query_params=request.GET,
            )
            return list_response(data, pagination, request)
        return success_response(
            generate_invoice(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except (InterestInvoiceValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, InterestInvoiceValidation) else {"body": exc.messages[0]}
        return error_response(request, 400, "VALIDATION_ERROR", "Interest invoice generation failed validation.", fields)
    except InterestInvoicePermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Interest invoice permission and configured ownership are required.")
    except InterestInvoiceNotFound:
        return error_response(request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible.")
    except InterestInvoiceConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["GET"])
def invoice_list(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data, pagination = list_invoices(actor=actor, query_params=request.GET)
        return list_response(data, pagination, request)
    except InterestInvoiceValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Interest invoice query failed validation.", exc.field_errors)
    except InterestInvoicePermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Loan account read permission is required.")


@require_http_methods(["POST"])
def invoice_issue(request, interest_invoice_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            issue_invoice(
                actor=actor,
                interest_invoice_id=interest_invoice_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except (InterestInvoiceValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, InterestInvoiceValidation) else {"body": exc.messages[0]}
        return error_response(request, 400, "VALIDATION_ERROR", "Interest invoice issuance failed validation.", fields)
    except InterestInvoicePermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Interest invoice issue permission and configured ownership are required.")
    except InterestInvoiceNotFound:
        return error_response(request, 404, "NOT_FOUND", "The interest invoice was not found or is inaccessible.")
    except InterestInvoiceConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
