from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
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
from sfpcl_credit.loans.modules.direct_repayment_posting import (
    RepaymentConflict,
    RepaymentNotFound,
    RepaymentPermissionDenied,
    RepaymentValidation,
    capture_direct_repayment,
    mark_sap_posted,
)
from sfpcl_credit.loans.modules.subsidiary_deduction_reconciliation import (
    capture_subsidiary_deduction,
    verify_treasury_reconciliation,
)
from sfpcl_credit.loans.modules.repayment_allocator import (
    RepaymentAllocator,
    RepaymentAllocationConflict,
    RepaymentAllocationNotFound,
    RepaymentAllocationPermissionDenied,
    RepaymentAllocationValidation,
)
from sfpcl_credit.loans.modules.repayment_adjustments import (
    RepaymentAdjustmentConflict,
    RepaymentAdjustmentNotFound,
    RepaymentAdjustmentPermissionDenied,
    RepaymentAdjustmentValidation,
    approve_manual_allocation,
    reverse_repayment,
)
from sfpcl_credit.loans.modules.bank_statement_matching import (
    BankStatementConflict,
    BankStatementNotFound,
    BankStatementPermissionDenied,
    BankStatementValidation,
    import_statement,
    list_statement_lines,
    manual_match_statement_line,
    record_statement_exception,
)
from sfpcl_credit.processes.loan_servicing import (
    LoanServicingReadNotFound,
    LoanServicingReadValidation,
    get_ledger,
    get_repayments,
    get_schedule,
)
from sfpcl_credit.processes.loan_ledger_statements import (
    LoanLedgerStatementDenied,
    LoanLedgerStatementNotFound,
    LoanLedgerStatementValidation,
    download_statement,
    record_download_denial,
    request_statement,
    statement_status,
)
from sfpcl_credit.processes.direct_repayment_command import execute_direct_repayment
from sfpcl_credit.processes.loan_account_360 import (
    LoanAccountProjectionNotFound,
    LoanAccountProjectionValidation,
    LoanAccountReadPermissionDenied,
    get_account,
    list_accounts,
)


@require_http_methods(["GET"])
def account_list(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data, pagination = list_accounts(actor=actor, query_params=request.GET)
        return list_response(data, pagination, request)
    except LoanAccountProjectionValidation as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "Loan account query failed validation.", exc.field_errors
        )
    except LoanAccountReadPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Loan account read permission is required.")


@require_http_methods(["GET"])
def account_detail(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            get_account(actor=actor, loan_account_id=loan_account_id), request
        )
    except LoanAccountReadPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Loan account read permission is required.")
    except LoanAccountProjectionNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )


@require_http_methods(["GET"])
def repayment_schedule(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data, pagination = get_schedule(
            actor=actor,
            loan_account_id=loan_account_id,
            query_params=request.GET,
        )
        return list_response(data, pagination, request)
    except LoanServicingReadValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Repayment schedule query failed validation.",
            exc.field_errors,
        )
    except LoanAccountReadPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Loan account read permission is required."
        )
    except LoanServicingReadNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )


@require_http_methods(["GET"])
def ledger(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data, pagination = get_ledger(
            actor=actor,
            loan_account_id=loan_account_id,
            query_params=request.GET,
        )
        return list_response(data, pagination, request)
    except LoanServicingReadValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan ledger query failed validation.",
            exc.field_errors,
        )
    except LoanAccountReadPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Loan account read permission is required."
        )
    except LoanServicingReadNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )


@require_http_methods(["POST"])
def ledger_statement_request(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            request_statement(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except LoanLedgerStatementValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Statement request failed validation.", exc.field_errors)
    except LoanLedgerStatementDenied:
        return error_response(request, 403, "FORBIDDEN", "Loan statement export permission is required.")
    except (LoanLedgerStatementNotFound, LoanServicingReadNotFound):
        return error_response(request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible.")


@require_http_methods(["GET"])
def ledger_statement_status(request, statement_job_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            statement_status(actor=actor, statement_job_id=statement_job_id), request
        )
    except LoanLedgerStatementDenied:
        return error_response(request, 403, "FORBIDDEN", "Loan statement export permission is required.")
    except (LoanLedgerStatementNotFound, LoanServicingReadNotFound):
        return error_response(request, 404, "NOT_FOUND", "The statement job was not found or is inaccessible.")


@require_http_methods(["GET"])
def ledger_statement_download(request, statement_job_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        content = download_statement(
            actor=actor,
            statement_job_id=statement_job_id,
            capability=request.GET.get("capability", ""),
            request=request,
        )
        response = HttpResponse(content.body, content_type=content.mime_type)
        response["Content-Disposition"] = f'attachment; filename="{content.file_name}"'
        return response
    except LoanLedgerStatementDenied:
        return error_response(request, 403, "FORBIDDEN", "Loan statement export permission is required.")
    except (LoanLedgerStatementNotFound, LoanServicingReadNotFound):
        record_download_denial(
            actor=actor, statement_job_id=statement_job_id, request=request
        )
        return error_response(request, 404, "NOT_FOUND", "The statement download was not found or is inaccessible.")


@require_http_methods(["GET", "POST"])
def direct_repayment(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET":
        try:
            data, pagination = get_repayments(
                actor=actor,
                loan_account_id=loan_account_id,
                query_params=request.GET,
            )
            return list_response(data, pagination, request)
        except LoanServicingReadValidation as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Repayment query failed validation.",
                exc.field_errors,
            )
        except LoanAccountReadPermissionDenied:
            return error_response(
                request, 403, "FORBIDDEN", "Loan account read permission is required."
            )
        except LoanServicingReadNotFound:
            return error_response(
                request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
            )
    try:
        payload = parse_json_body(request)
        capture = (
            capture_subsidiary_deduction
            if payload.get("repayment_source") == "subsidiary_deduction"
            else capture_direct_repayment
        )
        return success_response(
            capture(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=payload,
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except RepaymentValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Repayment capture failed validation.", exc.field_errors)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Repayment capture failed validation.", {"body": exc.messages[0]})
    except RepaymentPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Repayment capture permission is required.")
    except RepaymentNotFound:
        return error_response(request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible.")
    except RepaymentConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def repayment_mark_sap_posted(request, repayment_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            mark_sap_posted(actor=actor, repayment_id=repayment_id, payload=parse_json_body(request), request=request),
            request,
        )
    except RepaymentValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "SAP posting failed validation.", exc.field_errors)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "SAP posting failed validation.", {"body": exc.messages[0]})
    except RepaymentPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "SAP posting permission is required.")
    except RepaymentNotFound:
        return error_response(request, 404, "NOT_FOUND", "The repayment was not found or is inaccessible.")
    except RepaymentConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def direct_repayment_command(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            execute_direct_repayment(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except (RepaymentValidation, RepaymentAllocationValidation) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Direct repayment command failed validation.",
            exc.field_errors,
        )
    except (RepaymentPermissionDenied, RepaymentAllocationPermissionDenied):
        return error_response(
            request, 403, "FORBIDDEN", "Direct repayment command permission is required."
        )
    except (RepaymentNotFound, RepaymentAllocationNotFound):
        return error_response(
            request, 404, "NOT_FOUND", "The repayment or loan account was not found."
        )
    except (RepaymentConflict, RepaymentAllocationConflict) as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def subsidiary_deduction_verify(request, repayment_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            verify_treasury_reconciliation(
                actor=actor,
                repayment_id=repayment_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except RepaymentValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Subsidiary verification failed validation.",
            exc.field_errors,
        )
    except RepaymentPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Repayment allocation permission is required."
        )
    except RepaymentNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The repayment was not found or is inaccessible."
        )
    except RepaymentConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def repayment_allocate(request, repayment_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            RepaymentAllocator.allocate(
                actor=actor,
                repayment_id=repayment_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except RepaymentAllocationValidation as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "Repayment allocation failed validation.", exc.field_errors
        )
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "Repayment allocation failed validation.", {"body": exc.messages[0]}
        )
    except RepaymentAllocationPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Repayment allocation permission is required.")
    except RepaymentAllocationNotFound:
        return error_response(request, 404, "NOT_FOUND", "The repayment was not found or is inaccessible.")
    except RepaymentAllocationConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def repayment_manual_allocation_approve(request, repayment_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            approve_manual_allocation(
                actor=actor,
                repayment_id=repayment_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except RepaymentAdjustmentValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Manual allocation approval failed validation.", exc.field_errors)
    except RepaymentAdjustmentPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Elevated manual allocation approval permission is required.")
    except RepaymentAdjustmentNotFound:
        return error_response(request, 404, "NOT_FOUND", "The repayment was not found or is inaccessible.")
    except RepaymentAdjustmentConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def repayment_manual_allocate(request, repayment_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            RepaymentAllocator.allocate(
                actor=actor,
                repayment_id=repayment_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                manual=True,
                request=request,
            ),
            request,
        )
    except RepaymentAllocationValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Manual allocation failed validation.", exc.field_errors)
    except RepaymentAllocationPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Repayment allocation permission is required.")
    except RepaymentAllocationNotFound:
        return error_response(request, 404, "NOT_FOUND", "The repayment was not found or is inaccessible.")
    except RepaymentAllocationConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def repayment_reverse(request, repayment_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            reverse_repayment(
                actor=actor,
                repayment_id=repayment_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except RepaymentAdjustmentValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Repayment reversal failed validation.", exc.field_errors)
    except RepaymentAdjustmentPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Elevated financial reversal permission is required.")
    except RepaymentAdjustmentNotFound:
        return error_response(request, 404, "NOT_FOUND", "The repayment was not found or is inaccessible.")
    except RepaymentAdjustmentConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def bank_statement_import(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(import_statement(actor=actor, request=request), request)
    except BankStatementValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Bank statement import failed validation.",
            exc.field_errors,
        )
    except BankStatementPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Bank statement import permission is required."
        )
    except BankStatementConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["GET"])
def bank_statement_line_list(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data, pagination = list_statement_lines(actor=actor, query_params=request.GET)
        return list_response(data, pagination, request)
    except BankStatementValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Bank statement line query failed validation.",
            exc.field_errors,
        )
    except BankStatementPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Bank statement read permission is required."
        )


@require_http_methods(["POST"])
def bank_statement_line_match(request, bank_statement_line_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            manual_match_statement_line(
                actor=actor,
                line_id=bank_statement_line_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except BankStatementValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Bank statement match failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Bank statement match failed validation.",
            {"body": exc.messages[0]},
        )
    except BankStatementPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Bank statement match permission is required."
        )
    except BankStatementNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The statement line or repayment was not found or is inaccessible."
        )
    except BankStatementConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def bank_statement_line_exception(request, bank_statement_line_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            record_statement_exception(
                actor=actor,
                line_id=bank_statement_line_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except BankStatementValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Bank statement exception failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "Bank statement exception failed validation.", {"body": exc.messages[0]}
        )
    except BankStatementPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Bank statement match permission is required."
        )
    except BankStatementNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The statement line was not found or is inaccessible."
        )
    except BankStatementConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


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
