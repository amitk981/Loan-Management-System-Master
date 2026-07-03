from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_POST

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.tokens import TokenError
from sfpcl_credit.tracer import services


def _authenticated_user(request):
    authorization = request.headers.get("Authorization", "")
    if not authorization:
        return None, error_response(
            request, 401, "AUTH_REQUIRED", "Bearer access token is required."
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        return None, error_response(
            request, 401, "INVALID_TOKEN", "Authorization header must use Bearer token."
        )
    try:
        session = auth_service.validate_access_session(parts[1])
    except TokenError as exc:
        return None, error_response(request, 401, exc.code, exc.message)
    if services.TRACER_PERMISSION_CODE not in auth_service.effective_permission_codes(
        session.user
    ):
        return None, error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "Tracer lifecycle permission is required.",
        )
    return session.user, None


def _json(request):
    try:
        return parse_json_body(request), None
    except ValidationError as exc:
        return None, error_response(request, 400, "VALIDATION_ERROR", str(exc))


def _service_error(request, exc):
    if isinstance(exc, ValidationError):
        return error_response(request, 400, "VALIDATION_ERROR", str(exc))
    if isinstance(exc, services.TransitionError):
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    if isinstance(exc, ObjectDoesNotExist):
        return error_response(request, 404, "NOT_FOUND", "Requested tracer record was not found.")
    raise exc


@require_POST
def create_member(request):
    user, response = _authenticated_user(request)
    if response is not None:
        return response
    data, response = _json(request)
    if response is not None:
        return response
    try:
        member, _event = services.create_member(user, request, data.get("display_name"))
    except (ValidationError, services.TransitionError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(services.member_payload(member), request)


@require_POST
def create_application(request, member_id):
    user, response = _authenticated_user(request)
    if response is not None:
        return response
    data, response = _json(request)
    if response is not None:
        return response
    try:
        application, _event = services.create_application(
            user, request, member_id, data.get("amount")
        )
    except (ValidationError, services.TransitionError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(services.application_payload(application), request)


@require_POST
def sanction_application(request, application_id):
    user, response = _authenticated_user(request)
    if response is not None:
        return response
    try:
        application, previous, event = services.sanction_application(
            user, request, application_id
        )
    except (ValidationError, services.TransitionError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(
        services.action_payload(
            "loan_application",
            application.loan_application_id,
            previous,
            application.status,
            event,
        ),
        request,
    )


@require_POST
def create_loan_account(request, application_id):
    user, response = _authenticated_user(request)
    if response is not None:
        return response
    try:
        account, _event = services.create_loan_account(user, request, application_id)
    except (ValidationError, services.TransitionError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(services.loan_account_payload(account), request)


@require_POST
def mark_disbursed(request, account_id):
    user, response = _authenticated_user(request)
    if response is not None:
        return response
    try:
        account, previous, event = services.mark_disbursed(user, request, account_id)
    except (ValidationError, services.TransitionError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(
        services.action_payload(
            "loan_account", account.loan_account_id, previous, account.status, event
        ),
        request,
    )


@require_POST
def post_repayment(request, account_id):
    user, response = _authenticated_user(request)
    if response is not None:
        return response
    data, response = _json(request)
    if response is not None:
        return response
    try:
        repayment, _event = services.post_repayment(
            user, request, account_id, data.get("amount")
        )
    except (ValidationError, services.TransitionError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(services.repayment_payload(repayment), request)


@require_POST
def close_loan(request, account_id):
    user, response = _authenticated_user(request)
    if response is not None:
        return response
    try:
        account, previous, event = services.close_loan(user, request, account_id)
    except (ValidationError, services.TransitionError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(
        services.action_payload(
            "loan_account", account.loan_account_id, previous, account.status, event
        ),
        request,
    )
