from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, request_ip, request_user_agent, success_response
from sfpcl_credit.applications import services
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.workflows.guard import InvalidStateTransition


@require_http_methods(["POST"])
def loan_application_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_create_applications(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to create loan applications.",
        )
    try:
        body = parse_json_body(request)
        application = services.create_draft(
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except services.LoanApplicationValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan application payload failed validation.",
            services.validation_field_errors(exc),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan application payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_application(application), request)


@require_http_methods(["GET", "PATCH"])
def loan_application_detail(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_applications(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to read loan applications.",
        )
    if request.method == "PATCH":
        if not services.user_can_update_applications(user):
            return error_response(
                request,
                403,
                "PERMISSION_DENIED",
                "You do not have permission to update loan applications.",
            )
        application = services.get_application(loan_application_id)
        if application is None:
            return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
        object_access = services.evaluate_application_object_access(
            application,
            user,
            services.APPLICATION_UPDATE_PERMISSION,
            permissions,
        )
        if not object_access.allowed:
            return _object_access_denied_response(request, object_access)
        try:
            body = parse_json_body(request)
            application = services.update_draft(
                application,
                body,
                user,
                request_ip(request),
                request_user_agent(request),
                request.headers.get("X-Request-ID"),
            )
        except services.LoanApplicationValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Loan application payload failed validation.",
                services.validation_field_errors(exc),
            )
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Loan application payload failed validation.",
                services.validation_field_errors(exc),
            )
        return success_response(services.serialize_application(application), request)

    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_READ_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    return success_response(services.serialize_application(application), request)


@require_http_methods(["POST"])
def loan_application_submit(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_submit_applications(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to submit loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_SUBMIT_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        parse_json_body(request)
        application = services.submit_application(
            application,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
            permissions,
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan application payload failed validation.",
            services.validation_field_errors(exc),
        )
    except InvalidStateTransition as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(services.serialize_application(application), request)


@require_http_methods(["POST"])
def loan_application_generate_reference(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_complete_check_applications(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to complete-check loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_COMPLETE_CHECK_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        parse_json_body(request)
        application = services.generate_reference_after_completeness_pass(
            application,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
            permissions,
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan application payload failed validation.",
            services.validation_field_errors(exc),
        )
    except InvalidStateTransition as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(services.serialize_application(application), request)


def _object_access_denied_response(request, object_access):
    return error_response(
        request,
        403,
        object_access.error_code or "OBJECT_ACCESS_DENIED",
        "You do not have access to this loan application.",
    )
