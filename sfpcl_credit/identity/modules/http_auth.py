"""Shared HTTP authentication helpers for protected Django views."""

from sfpcl_credit.api import error_response
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.tokens import TokenError


def bearer_access_token(request):
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
    return parts[1], None


def authenticated_session(request):
    access_token, response = bearer_access_token(request)
    if response is not None:
        return None, response
    try:
        session = auth_service.validate_access_session(access_token)
    except TokenError as exc:
        return None, error_response(request, 401, exc.code, exc.message)
    return session, None


def authenticated_user(request):
    session, response = authenticated_session(request)
    if response is not None:
        return None, response
    return session.user, None


def authenticated_user_with_permissions(request):
    user, response = authenticated_user(request)
    if response is not None:
        return None, None, response
    return user, auth_service.effective_permission_codes(user), None


__all__ = [
    "authenticated_session",
    "authenticated_user",
    "authenticated_user_with_permissions",
    "bearer_access_token",
]
