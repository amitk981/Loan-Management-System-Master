from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_GET, require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import admin_users, auth_service
from sfpcl_credit.identity.modules.tokens import TokenError


def _authenticated_admin(request):
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
    if not admin_users.has_manage_users_permission(session.user):
        return None, error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "User management permission is required.",
        )
    return session.user, None


def _json(request):
    try:
        return parse_json_body(request), None
    except ValidationError as exc:
        return None, error_response(request, 400, "VALIDATION_ERROR", str(exc))


def _service_error(request, exc):
    if isinstance(exc, ValidationError):
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Admin user request failed validation.",
            admin_users.validation_field_errors(exc),
        )
    if isinstance(exc, ObjectDoesNotExist):
        return error_response(
            request, 404, "NOT_FOUND", "Requested admin user record was not found."
        )
    raise exc


@require_GET
def user_list(request):
    _actor, response = _authenticated_admin(request)
    if response is not None:
        return response
    data, pagination = admin_users.paginated_users(
        request.GET.get("page"),
        request.GET.get("page_size"),
    )
    return list_response(data, pagination, request)


@require_GET
def user_detail(request, user_id):
    _actor, response = _authenticated_admin(request)
    if response is not None:
        return response
    try:
        user = admin_users.get_user(user_id)
    except ObjectDoesNotExist as exc:
        return _service_error(request, exc)
    return success_response(admin_users.admin_user_payload(user), request)


@require_http_methods(["POST"])
def assign_role(request, user_id):
    actor, response = _authenticated_admin(request)
    if response is not None:
        return response
    data, response = _json(request)
    if response is not None:
        return response
    try:
        payload = admin_users.assign_role(actor, request, user_id, data.get("role_code"))
    except (ValidationError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(payload, request)


@require_http_methods(["POST"])
def add_team(request, user_id):
    actor, response = _authenticated_admin(request)
    if response is not None:
        return response
    data, response = _json(request)
    if response is not None:
        return response
    try:
        payload = admin_users.add_team(actor, request, user_id, data.get("team_code"))
    except (ValidationError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(payload, request)


@require_http_methods(["DELETE"])
def remove_team(request, user_id, team_code):
    actor, response = _authenticated_admin(request)
    if response is not None:
        return response
    try:
        payload = admin_users.remove_team(actor, request, user_id, team_code)
    except (ValidationError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(payload, request)


@require_http_methods(["PATCH"])
def set_status(request, user_id):
    actor, response = _authenticated_admin(request)
    if response is not None:
        return response
    data, response = _json(request)
    if response is not None:
        return response
    try:
        payload = admin_users.set_status(actor, request, user_id, data.get("status"))
    except (ValidationError, ObjectDoesNotExist) as exc:
        return _service_error(request, exc)
    return success_response(payload, request)
