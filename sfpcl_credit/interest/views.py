from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.interest.modules.interest_engine import (
    InterestAccrualConflict,
    InterestAccrualNotFound,
    InterestAccrualPermissionDenied,
    InterestAccrualValidation,
    InterestInvoiceConflict,
    InterestInvoiceNotFound,
    InterestInvoicePermissionDenied,
    InterestInvoiceValidation,
    bulk_generate_monthly_accruals,
    create_monthly_accrual,
    generate_invoice,
    issue_invoice,
    list_invoices,
    record_accrual_sap_status,
)


@require_http_methods(["POST"])
def accrual_collection(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            create_monthly_accrual(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except (InterestAccrualValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, InterestAccrualValidation) else {"body": exc.messages[0]}
        return error_response(request, 400, "VALIDATION_ERROR", "Interest accrual generation failed validation.", fields)
    except InterestAccrualPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Interest accrual permission and loan scope are required.")
    except InterestAccrualNotFound:
        return error_response(request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible.")
    except InterestAccrualConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def accrual_bulk_generate(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            bulk_generate_monthly_accruals(
                actor=actor,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except (InterestAccrualValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, InterestAccrualValidation) else {"body": exc.messages[0]}
        return error_response(request, 400, "VALIDATION_ERROR", "Bulk interest accrual generation failed validation.", fields)
    except InterestAccrualPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Bulk interest accrual permission and loan scope are required.")


@require_http_methods(["POST"])
def accrual_mark_sap_posted(request, accrual_entry_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            record_accrual_sap_status(
                actor=actor,
                accrual_entry_id=accrual_entry_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except (InterestAccrualValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, InterestAccrualValidation) else {"body": exc.messages[0]}
        return error_response(request, 400, "VALIDATION_ERROR", "SAP accrual status capture failed validation.", fields)
    except InterestAccrualPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Interest accrual permission and loan scope are required.")
    except InterestAccrualNotFound:
        return error_response(request, 404, "NOT_FOUND", "The accrual entry was not found or is inaccessible.")
    except InterestAccrualConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


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
