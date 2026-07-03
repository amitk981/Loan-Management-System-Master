"""Auth service boundary: token/session/audit behavior for the auth endpoints.

Views (`sfpcl_credit/identity/views.py`) translate HTTP only and call the
functions here (`docs/source/technical-architecture.md` §13.1,
`docs/source/codebase-design.md` §6-7). All multi-entity work — credential
checks, session creation, refresh rotation, replay/revocation, and auth audit
logging — lives behind this explicit interface so it can be tested directly and
reused by later auth endpoints (e.g. 002D `GET /auth/me/`).
"""

import secrets

from django.conf import settings
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog, Permission, User, UserSession
from sfpcl_credit.identity.modules.tokens import (
    TokenError,
    access_claims,
    decode_token,
    encode_token,
    hash_token,
    refresh_claims,
)


class CredentialError(Exception):
    """Raised when login credentials are rejected.

    `outcome` distinguishes the audit reason ("invalid_credentials" vs
    "inactive_user"); both surface to the caller as a single 401 so the
    response never reveals which check failed.
    """

    def __init__(self, outcome, user=None):
        self.outcome = outcome
        self.user = user
        super().__init__(outcome)


def authenticate_user(email, password):
    user = User.objects.select_related("primary_role").filter(email__iexact=email).first()
    if not user or not user.check_password(password):
        raise CredentialError("invalid_credentials", user=None)
    if not user.can_authenticate():
        raise CredentialError("inactive_user", user=user)
    return user


def auth_payload(user, session, refresh_token):
    return {
        "token_type": "Bearer",
        "access_token": encode_token(access_claims(user, session)),
        "refresh_token": refresh_token,
        "expires_in": settings.AUTH_ACCESS_TOKEN_MINUTES * 60,
        "user": {
            "user_id": str(user.user_id),
            "full_name": user.full_name,
            "email": user.email,
            "status": user.status,
            "role_codes": user.role_codes(),
            "team_codes": user.team_codes(),
            "approval_authority_type": user.approval_authority_type or None,
        },
    }


def _store_refresh_token(session, token):
    session.refresh_token_hash = hash_token(token)
    session.last_used_at = timezone.now()
    session.save(update_fields=["refresh_token_hash", "last_used_at"])
    return token


def issue_login_tokens_and_session(user, request):
    """Create an active session for `user` and return `(session, auth_payload)`."""
    session = UserSession.objects.create(
        user=user,
        refresh_token_hash="",
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
        expires_at=timezone.now()
        + timezone.timedelta(hours=settings.AUTH_REFRESH_TOKEN_HOURS),
    )
    refresh_token = _store_refresh_token(session, encode_token(refresh_claims(session)))
    user.last_login_at = timezone.now()
    user.save(update_fields=["last_login_at"])
    return session, auth_payload(user, session, refresh_token)


def rotate_refresh_token(session):
    """Issue and persist a new refresh token, invalidating the previous one."""
    return _store_refresh_token(session, encode_token(refresh_claims(session)))


def validate_refresh_session(refresh_token):
    """Return the active session bound to `refresh_token` or raise `TokenError`.

    Rejects expired/malformed/wrong-type tokens, missing/inactive sessions,
    rotated-or-revoked tokens (hash mismatch = replay), and users who can no
    longer authenticate.
    """
    claims = decode_token(refresh_token, expected_type="refresh")
    try:
        session = UserSession.objects.select_related("user", "user__primary_role").get(
            user_session_id=claims["session_id"]
        )
    except (KeyError, UserSession.DoesNotExist) as exc:
        raise TokenError("INVALID_TOKEN", "Refresh session does not exist.") from exc

    if not session.is_active():
        raise TokenError("INVALID_TOKEN", "Refresh session is not active.")
    if not secrets.compare_digest(session.refresh_token_hash, hash_token(refresh_token)):
        raise TokenError("INVALID_TOKEN", "Refresh token has been rotated or revoked.")
    if not session.user.can_authenticate():
        session.revoke("user_status_changed")
        raise TokenError("INVALID_TOKEN", "User is not active.")
    return session


def revoke_session_for_logout(session):
    session.revoke("logout")
    return session


def validate_access_token(access_token):
    """Decode and verify an access token for callers such as 002D `/auth/me/`.

    Stateless by design: access tokens are short-lived and verified by
    signature/expiry/type only, matching 002B behavior where logout revokes the
    refresh session while an already-issued access token stands until it
    expires. Returns the decoded claims; raises `TokenError` otherwise.
    """
    return decode_token(access_token, expected_type="access")


def validate_access_session(access_token):
    """Return the active session bound to `access_token` or raise `TokenError`.

    `/auth/me/` needs current session state, not only stateless JWT validity:
    logout/session revocation and user status changes must block profile,
    permissions, and action availability.
    """
    claims = validate_access_token(access_token)
    try:
        session = UserSession.objects.select_related("user", "user__primary_role").get(
            user_session_id=claims["session_id"]
        )
    except (KeyError, UserSession.DoesNotExist) as exc:
        raise TokenError("INVALID_TOKEN", "Access session does not exist.") from exc

    if str(session.user_id) != str(claims.get("user_id", "")):
        raise TokenError("INVALID_TOKEN", "Access token user does not match session.")
    if not session.is_active():
        raise TokenError("INVALID_TOKEN", "Access session is not active.")
    if not session.user.can_authenticate():
        session.revoke("user_status_changed")
        raise TokenError("INVALID_TOKEN", "User is not active.")
    return session


def effective_permission_codes(user):
    if user.primary_role.status != "active":
        return []
    codes = Permission.objects.filter(
        role_permissions__role=user.primary_role
    ).values_list("permission_code", flat=True)
    return sorted(set(codes))


def current_user_payload(user):
    permissions = effective_permission_codes(user)
    return {
        "user_id": str(user.user_id),
        "full_name": user.full_name,
        "email": user.email,
        "status": user.status,
        "role_codes": user.role_codes(),
        "team_codes": user.team_codes(),
        "permissions": permissions,
        "available_actions": permissions,
    }


def current_user_payload_for_access_token(access_token):
    session = validate_access_session(access_token)
    return current_user_payload(session.user)


def record_auth_event(request, action, user=None, session=None, outcome=None, email=None):
    AuditLog.objects.create(
        actor_user=user,
        actor_type="user" if user else "anonymous",
        action=action,
        entity_type="user_session" if session else "auth",
        entity_id=session.user_session_id if session else None,
        new_value_json={"outcome": outcome, "email": email or (user.email if user else None)},
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
