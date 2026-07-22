from django.views.decorators.http import require_http_methods

from django.core.exceptions import ValidationError

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.closure.modules.loan_closure import (
    ClosureConflict,
    ClosureNotFound,
    ClosurePermissionDenied,
    ClosureValidation,
    NocConflict,
    NocValidation,
    ArchiveConflict,
    ArchiveValidation,
    archive,
    read_archive,
    search_archives,
    close,
    download_noc,
    evaluate_readiness,
    generate_noc,
    read_noc,
)
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.closure.modules.security_return import (
    SecurityReturnConflict,
    SecurityReturnNotFound,
    SecurityReturnPermissionDenied,
    SecurityReturnValidation,
    record_security_return,
)


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


@require_http_methods(["GET", "POST"])
def noc_issue(request, loan_closure_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET":
        try:
            return success_response(
                read_noc(
                    actor=actor,
                    loan_closure_id=loan_closure_id,
                    request=request,
                ),
                request,
            )
        except ClosurePermissionDenied:
            return error_response(
                request, 403, "FORBIDDEN", "NOC read authority is required."
            )
        except ClosureNotFound:
            return error_response(
                request,
                404,
                "NOT_FOUND",
                "The NOC was not found or is inaccessible.",
            )
    try:
        return success_response(
            generate_noc(
                actor=actor,
                loan_closure_id=loan_closure_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except NocValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "NOC issuance failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "NOC issuance failed validation.",
            {"body": exc.messages[0]},
        )
    except ClosurePermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "NOC issuance authority is required."
        )
    except ClosureNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan closure was not found or is inaccessible."
        )
    except NocConflict as exc:
        return error_response(request, 409, "NOC_ISSUANCE_CONFLICT", str(exc))


@require_http_methods(["GET"])
def noc_download(request, loan_closure_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            download_noc(
                actor=actor,
                loan_closure_id=loan_closure_id,
                request=request,
            ),
            request,
        )
    except ClosurePermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "NOC download authority is required."
        )
    except ClosureNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The NOC was not found or is inaccessible."
        )


@require_http_methods(["POST"])
def security_return_record(request, loan_closure_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            record_security_return(
                actor=actor,
                loan_closure_id=loan_closure_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except SecurityReturnValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Security return failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Security return failed validation.",
            {"body": exc.messages[0]},
        )
    except SecurityReturnPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Security-return authority is required."
        )
    except SecurityReturnNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan closure was not found or is inaccessible."
        )
    except SecurityReturnConflict as exc:
        return error_response(request, 409, "SECURITY_RETURN_CONFLICT", str(exc))


@require_http_methods(["GET", "POST"])
def archive_record(request, loan_closure_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET":
        try:
            return success_response(
                read_archive(
                    actor=actor,
                    loan_closure_id=loan_closure_id,
                    request=request,
                ),
                request,
            )
        except ClosurePermissionDenied:
            return error_response(
                request, 403, "FORBIDDEN", "Archive read authority is required."
            )
        except ClosureNotFound:
            return error_response(
                request,
                404,
                "NOT_FOUND",
                "The archive manifest was not found or is inaccessible.",
            )
    try:
        return success_response(
            archive(
                actor=actor,
                loan_closure_id=loan_closure_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key"),
                request=request,
            ),
            request,
        )
    except ArchiveValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Archive creation failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Archive creation failed validation.",
            {"body": exc.messages[0]},
        )
    except ClosurePermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Archive creation authority is required."
        )
    except ClosureNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan closure was not found or is inaccessible."
        )
    except ArchiveConflict as exc:
        return error_response(request, 409, "ARCHIVE_CONFLICT", str(exc))


@require_http_methods(["GET"])
def archive_manifest(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        items, pagination = search_archives(
            actor=actor, query_params=request.GET, request=request
        )
        return list_response(items, pagination, request)
    except ArchiveValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Archive search failed validation.",
            exc.field_errors,
        )
    except ClosurePermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Archive read authority is required."
        )
