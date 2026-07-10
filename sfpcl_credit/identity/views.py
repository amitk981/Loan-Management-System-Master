"""Thin auth HTTP views.

These views only parse HTTP input, call the auth service module, and translate
known errors to standard responses. All token/session/audit behavior lives in
`sfpcl_credit.identity.modules` (see 002C2). `TokenError` and `decode_token` are
re-exported for backward-compatible imports.
"""

from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET, require_POST

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import auth_service, http_auth, portal_auth_service
from sfpcl_credit.identity.modules.auth_service import CredentialError
from sfpcl_credit.identity.modules.tokens import TokenError, decode_token  # noqa: F401  (re-exported)


def _required_refresh_token(request):
    data = parse_json_body(request)
    refresh_token = data.get("refresh_token", "")
    if not refresh_token:
        raise ValidationError("Refresh token is required.")
    return refresh_token


def _missing_refresh_token_response(request, exc):
    return error_response(
        request,
        400,
        "MISSING_REQUIRED_FIELD",
        str(exc),
        {"refresh_token": "This field is required."},
    )


@require_POST
def login(request):
    try:
        data = parse_json_body(request)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", str(exc))

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return error_response(
            request,
            400,
            "MISSING_REQUIRED_FIELD",
            "Email and password are required.",
            {
                "email": "This field is required." if not email else "",
                "password": "This field is required." if not password else "",
            },
        )

    try:
        user = auth_service.authenticate_user(email, password)
    except CredentialError as exc:
        auth_service.record_auth_event(
            request, "auth.login.failed", user=exc.user, outcome=exc.outcome, email=email
        )
        return error_response(
            request, 401, "INVALID_CREDENTIALS", "Email or password is incorrect."
        )

    session, payload = auth_service.issue_login_tokens_and_session(user, request)
    auth_service.record_auth_event(
        request, "auth.login.succeeded", user=user, session=session, outcome="success"
    )
    return success_response(payload, request)


@require_POST
def refresh(request):
    try:
        session = auth_service.validate_refresh_session(_required_refresh_token(request))
    except ValidationError as exc:
        return _missing_refresh_token_response(request, exc)
    except TokenError as exc:
        return error_response(request, 401, exc.code, exc.message)

    refresh_token = auth_service.rotate_refresh_token(session)
    auth_service.record_auth_event(
        request, "auth.refresh.succeeded", user=session.user, session=session, outcome="success"
    )
    return success_response(
        auth_service.auth_payload(session.user, session, refresh_token), request
    )


@require_POST
def logout(request):
    try:
        session = auth_service.validate_refresh_session(_required_refresh_token(request))
    except ValidationError as exc:
        return _missing_refresh_token_response(request, exc)
    except TokenError as exc:
        return error_response(request, 401, exc.code, exc.message)

    auth_service.revoke_session_for_logout(session)
    auth_service.record_auth_event(
        request, "auth.logout.succeeded", user=session.user, session=session, outcome="success"
    )
    return success_response({"logged_out": True}, request)


@require_GET
def me(request):
    access_token, response = http_auth.bearer_access_token(request)
    if response is not None:
        return response
    try:
        payload = auth_service.current_user_payload_for_access_token(access_token)
    except TokenError as exc:
        return error_response(request, 401, exc.code, exc.message)
    return success_response(payload, request)


def _portal_error_response(request, exc):
    return error_response(request, exc.status, exc.code, exc.message, exc.field_errors)


@require_POST
def portal_activation_start(request):
    try:
        payload = portal_auth_service.start_activation(parse_json_body(request), request)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", str(exc))
    except portal_auth_service.PortalAuthError as exc:
        return _portal_error_response(request, exc)
    return success_response(payload, request)


@require_POST
def portal_activation_complete(request):
    try:
        payload = portal_auth_service.complete_activation(parse_json_body(request), request)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", str(exc))
    except portal_auth_service.PortalAuthError as exc:
        return _portal_error_response(request, exc)
    return success_response(payload, request)


@require_POST
def portal_login(request):
    try:
        data = parse_json_body(request)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", str(exc))
    identifier = str(data.get("identifier", "")).strip().lower()
    password = data.get("password", "")
    if not identifier or not password:
        return error_response(
            request,
            400,
            "MISSING_REQUIRED_FIELD",
            "Identifier and password are required.",
            {
                "identifier": "This field is required." if not identifier else "",
                "password": "This field is required." if not password else "",
            },
        )
    try:
        user = portal_auth_service.authenticate_portal_user(identifier, password)
    except CredentialError as exc:
        auth_service.record_auth_event(
            request,
            "portal.login.failed",
            user=exc.user,
            outcome=exc.outcome,
            email=identifier,
        )
        return error_response(
            request, 401, "INVALID_CREDENTIALS", "Identifier or password is incorrect."
        )
    session, payload = portal_auth_service.issue_portal_login(user, request)
    auth_service.record_auth_event(
        request,
        "portal.login.success",
        user=user,
        session=session,
        outcome="success",
    )
    return success_response(payload, request)


@require_POST
def portal_password_reset_start(request):
    try:
        payload = portal_auth_service.start_password_reset(parse_json_body(request), request)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", str(exc))
    except portal_auth_service.PortalAuthError as exc:
        return _portal_error_response(request, exc)
    return success_response(payload, request)


@require_POST
def portal_password_reset_complete(request):
    try:
        payload = portal_auth_service.complete_password_reset(
            parse_json_body(request), request
        )
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", str(exc))
    except portal_auth_service.PortalAuthError as exc:
        return _portal_error_response(request, exc)
    return success_response(payload, request)


@require_POST
def portal_password_change(request):
    access_token, response = http_auth.bearer_access_token(request)
    if response is not None:
        return response
    try:
        session = auth_service.validate_access_session(access_token)
        payload = portal_auth_service.change_password(
            session.user, session, parse_json_body(request), request
        )
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", str(exc))
    except TokenError as exc:
        return error_response(request, 401, exc.code, exc.message)
    except portal_auth_service.PortalAuthError as exc:
        return _portal_error_response(request, exc)
    return success_response(payload, request)
