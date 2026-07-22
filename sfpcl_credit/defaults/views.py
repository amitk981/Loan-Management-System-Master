from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    success_response,
)
from sfpcl_credit.defaults.modules.default_workflow import (
    DefaultConflict,
    DefaultNotFound,
    DefaultPermissionDenied,
    DefaultValidation,
    api_assess_default_case,
    api_open_default_case,
    get_default_case,
    list_default_cases,
)
from sfpcl_credit.identity.modules import http_auth


@require_http_methods(["POST"])
def default_case_open(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            api_open_default_case(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except DefaultValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Default case opening failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Default case opening failed validation.",
            {"body": exc.messages[0]},
        )
    except DefaultPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Default case opening permission is required."
        )
    except DefaultNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )
    except DefaultConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def default_case_assess(request, default_case_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            api_assess_default_case(
                actor=actor,
                default_case_id=default_case_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except DefaultValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Default assessment failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Default assessment failed validation.",
            {"body": exc.messages[0]},
        )
    except DefaultPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Default assessment permission is required."
        )
    except DefaultNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The default case was not found or is inaccessible."
        )
    except DefaultConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["GET"])
def default_case_detail(request, default_case_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            get_default_case(actor=actor, default_case_id=default_case_id), request
        )
    except DefaultPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Default case read permission is required."
        )
    except DefaultNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The default case was not found or is inaccessible."
        )


@require_http_methods(["GET"])
def default_case_list(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        rows, pagination = list_default_cases(actor=actor, query_params=request.GET)
        return list_response(rows, pagination, request)
    except DefaultValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Default case query failed validation.",
            exc.field_errors,
        )
    except DefaultPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Default case read permission is required."
        )
