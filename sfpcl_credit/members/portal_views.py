from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, request_ip, request_user_agent, success_response
from sfpcl_credit.applications import services as application_services
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.members import portal_services
from sfpcl_credit.processes import portal_documentation_actions as portal_documentation_process
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
    claimed_member_id = request.GET.get("member_id")
    if claimed_member_id and claimed_member_id != str(member.member_id):
        return None, None, error_response(
            request,
            403,
            "OBJECT_ACCESS_DENIED",
            "You cannot access this member.",
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


@require_GET
def portal_application_limit_projection(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        projection = portal_services.application_limit_projection(
            member,
            requested_amount=request.GET.get("requested_amount"),
        )
    except ValidationError as exc:
        return _portal_application_validation_error(request, exc)
    return success_response(projection, request)


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


@require_GET
def portal_documentation_actions(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = portal_documentation_process.get_projection(
            actor=user,
            application_id=loan_application_id,
        )
    except portal_documentation_process.PortalDocumentationNotFound:
        return error_response(
            request,
            404,
            "NOT_FOUND",
            "Loan application was not found.",
        )
    return success_response(data, request)


@require_http_methods(["POST"])
def portal_documentation_action_upload(request, loan_application_id, action_code):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = portal_documentation_process.upload(
            actor=user,
            application_id=loan_application_id,
            action_code=action_code,
            request=request,
        )
    except portal_documentation_process.PortalDocumentationNotFound:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    except portal_documentation_process.PortalDocumentationUnavailable as exc:
        return error_response(request, 409, "ACTION_UNAVAILABLE", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Portal documentation upload failed validation.",
            application_services.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_GET
def portal_documentation_action_download(request, loan_application_id, action_code):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = portal_documentation_process.download(
            actor=user,
            application_id=loan_application_id,
            action_code=action_code,
            request=request,
        )
    except portal_documentation_process.PortalDocumentationNotFound:
        return error_response(request, 404, "NOT_FOUND", "Document was not found.")
    if isinstance(data, portal_documentation_process.PortalDocumentContent):
        response = HttpResponse(data.body, content_type=data.mime_type)
        response["Content-Disposition"] = f'attachment; filename="{data.file_name}"'
        return response
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
