import base64
import hashlib
import hmac
import json
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from sfpcl_credit.identity.models import AuditLog, User, UserSession


class TokenError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(message)


def response_meta(request):
    return {
        "request_id": request.headers.get("X-Request-ID"),
        "timestamp": timezone.now().isoformat().replace("+00:00", "Z"),
        "api_version": "v1",
    }


def success_response(data, request):
    return JsonResponse({"success": True, "data": data, "meta": response_meta(request)})


def error_response(request, status, code, message, field_errors=None):
    return JsonResponse(
        {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": {},
                "field_errors": field_errors or {},
            },
            "meta": response_meta(request),
        },
        status=status,
    )


def parse_json_body(request):
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise ValidationError("Request body must be valid JSON.") from exc
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")
    return data


def b64encode(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def b64decode(raw):
    return base64.urlsafe_b64decode((raw + "=" * (-len(raw) % 4)).encode("ascii"))


def sign(message):
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"), message.encode("ascii"), hashlib.sha256
    ).digest()


def encode_token(claims):
    header = b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode("utf-8"))
    payload = b64encode(
        json.dumps(claims, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    message = f"{header}.{payload}"
    return f"{message}.{b64encode(sign(message))}"


def decode_token(token, expected_type):
    try:
        header, payload, signature = token.split(".")
    except ValueError as exc:
        raise TokenError("INVALID_TOKEN", "Token format is invalid.") from exc

    message = f"{header}.{payload}"
    if not hmac.compare_digest(signature, b64encode(sign(message))):
        raise TokenError("INVALID_TOKEN", "Token signature is invalid.")

    try:
        claims = json.loads(b64decode(payload))
    except (ValueError, json.JSONDecodeError) as exc:
        raise TokenError("INVALID_TOKEN", "Token payload is invalid.") from exc

    if claims.get("token_type") != expected_type:
        raise TokenError("INVALID_TOKEN", "Token type is invalid.")
    if int(claims.get("exp", 0)) <= int(timezone.now().timestamp()):
        code = "REFRESH_TOKEN_EXPIRED" if expected_type == "refresh" else "TOKEN_EXPIRED"
        raise TokenError(code, "Token has expired.")
    return claims


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def access_claims(user, session):
    now = timezone.now()
    exp = now + timezone.timedelta(minutes=settings.AUTH_ACCESS_TOKEN_MINUTES)
    return {
        "token_type": "access",
        "user_id": str(user.user_id),
        "session_id": str(session.user_session_id),
        "email": user.email,
        "role_codes": user.role_codes(),
        "team_codes": user.team_codes(),
        "permissions_version": user.permissions_version(),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }


def refresh_claims(session):
    now = timezone.now()
    return {
        "token_type": "refresh",
        "user_id": str(session.user_id),
        "session_id": str(session.user_session_id),
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(session.expires_at.timestamp()),
    }


def request_ip(request):
    return request.META.get("REMOTE_ADDR", "")


def request_user_agent(request):
    return request.headers.get("User-Agent", "")


def audit(request, action, user=None, session=None, outcome=None, email=None):
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


def issue_refresh_token(session):
    token = encode_token(refresh_claims(session))
    session.refresh_token_hash = hash_token(token)
    session.last_used_at = timezone.now()
    session.save(update_fields=["refresh_token_hash", "last_used_at"])
    return token


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


def active_session_for_refresh(refresh_token):
    claims = decode_token(refresh_token, expected_type="refresh")
    try:
        session = UserSession.objects.select_related("user", "user__primary_role").get(
            user_session_id=claims["session_id"]
        )
    except (KeyError, UserSession.DoesNotExist) as exc:
        raise TokenError("INVALID_TOKEN", "Refresh session does not exist.") from exc

    if not session.is_active():
        raise TokenError("INVALID_TOKEN", "Refresh session is not active.")
    if not hmac.compare_digest(session.refresh_token_hash, hash_token(refresh_token)):
        raise TokenError("INVALID_TOKEN", "Refresh token has been rotated or revoked.")
    if not session.user.can_authenticate():
        session.revoke("user_status_changed")
        raise TokenError("INVALID_TOKEN", "User is not active.")
    return session


def required_refresh_token(request):
    data = parse_json_body(request)
    refresh_token = data.get("refresh_token", "")
    if not refresh_token:
        raise ValidationError("Refresh token is required.")
    return refresh_token


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

    user = User.objects.select_related("primary_role").filter(email__iexact=email).first()
    if not user or not user.check_password(password):
        audit(request, "auth.login.failed", outcome="invalid_credentials", email=email)
        return error_response(request, 401, "INVALID_CREDENTIALS", "Email or password is incorrect.")
    if not user.can_authenticate():
        audit(request, "auth.login.failed", user=user, outcome="inactive_user")
        return error_response(request, 401, "INVALID_CREDENTIALS", "Email or password is incorrect.")

    session = UserSession.objects.create(
        user=user,
        refresh_token_hash="",
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
        expires_at=timezone.now() + timezone.timedelta(hours=settings.AUTH_REFRESH_TOKEN_HOURS),
    )
    refresh_token = issue_refresh_token(session)
    user.last_login_at = timezone.now()
    user.save(update_fields=["last_login_at"])
    audit(request, "auth.login.succeeded", user=user, session=session, outcome="success")
    return success_response(auth_payload(user, session, refresh_token), request)


@require_POST
def refresh(request):
    try:
        session = active_session_for_refresh(required_refresh_token(request))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "MISSING_REQUIRED_FIELD",
            str(exc),
            {"refresh_token": "This field is required."},
        )
    except TokenError as exc:
        return error_response(request, 401, exc.code, exc.message)

    refresh_token = issue_refresh_token(session)
    audit(request, "auth.refresh.succeeded", user=session.user, session=session, outcome="success")
    return success_response(auth_payload(session.user, session, refresh_token), request)


@require_POST
def logout(request):
    try:
        session = active_session_for_refresh(required_refresh_token(request))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "MISSING_REQUIRED_FIELD",
            str(exc),
            {"refresh_token": "This field is required."},
        )
    except TokenError as exc:
        return error_response(request, 401, exc.code, exc.message)

    session.revoke("logout")
    audit(request, "auth.logout.succeeded", user=session.user, session=session, outcome="success")
    return success_response({"logged_out": True}, request)
