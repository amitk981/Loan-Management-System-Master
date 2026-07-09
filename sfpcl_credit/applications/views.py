from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, request_ip, request_user_agent, success_response
from sfpcl_credit.applications import services
from sfpcl_credit.identity.modules import http_auth


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
    user, response = http_auth.authenticated_user(request)
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
    return success_response(services.serialize_application(application), request)
