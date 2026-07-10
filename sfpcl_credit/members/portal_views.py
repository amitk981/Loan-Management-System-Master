from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET, require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, request_ip, request_user_agent, success_response
from sfpcl_credit.applications import services as application_services
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.members import portal_services
from sfpcl_credit.workflows.guard import InvalidStateTransition


def _portal_member_or_response(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return None, None, response
    member = portal_services.portal_member_for_user(user)
    if member is None:
        return None, None, error_response(
            request,
            403,
            "FORBIDDEN",
            portal_services.PORTAL_PERMISSION_ERROR,
        )
    return member, user, None


@require_GET
def portal_dashboard(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.dashboard_summary(member), request)


@require_GET
def portal_profile(request):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.profile(member, user), request)


@require_GET
def portal_produce_supply(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.produce_supply(member), request)


@require_http_methods(["GET", "POST"])
def portal_applications(request):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    if request.method == "GET":
        return success_response(portal_services.list_applications(member), request)
    try:
        body = parse_json_body(request)
        data = portal_services.create_application(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except portal_services.PortalObjectAccessError as exc:
        return _portal_object_access_denied(request, exc)
    except (application_services.LoanApplicationValidationError, ValidationError) as exc:
        return _portal_application_validation_error(request, exc)
    return success_response(data, request)


@require_http_methods(["GET", "PATCH"])
def portal_application_detail(request, loan_application_id):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        application = portal_services.get_application_for_member(member, loan_application_id)
    except portal_services.PortalObjectAccessError as exc:
        return _portal_object_access_denied(request, exc)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    if request.method == "GET":
        return success_response(portal_services.application_detail(application), request)
    try:
        body = parse_json_body(request)
        data = portal_services.update_application(
            application,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except portal_services.PortalObjectAccessError as exc:
        return _portal_object_access_denied(request, exc)
    except (application_services.LoanApplicationValidationError, ValidationError) as exc:
        return _portal_application_validation_error(request, exc)
    return success_response(data, request)


@require_http_methods(["POST"])
def portal_application_submit(request, loan_application_id):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        application = portal_services.get_application_for_member(member, loan_application_id)
    except portal_services.PortalObjectAccessError as exc:
        return _portal_object_access_denied(request, exc)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    try:
        parse_json_body(request)
        data = portal_services.submit_application(
            application,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except (application_services.LoanApplicationValidationError, ValidationError) as exc:
        return _portal_application_validation_error(request, exc)
    except (application_services.LoanApplicationInvalidStateError, InvalidStateTransition) as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(data, request)


def _portal_object_access_denied(request, exc):
    return error_response(request, 403, "OBJECT_ACCESS_DENIED", str(exc))


def _portal_application_validation_error(request, exc):
    return error_response(
        request,
        400,
        "VALIDATION_ERROR",
        "Portal application payload failed validation.",
        application_services.validation_field_errors(exc),
    )
