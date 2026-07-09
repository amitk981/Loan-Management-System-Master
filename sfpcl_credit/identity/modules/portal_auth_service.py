import hashlib
import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.models import Communication
from sfpcl_credit.identity.models import (
    AuditLog,
    PortalAccount,
    PortalOtpChallenge,
    Role,
    User,
    UserSession,
)
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.tokens import hash_token
from sfpcl_credit.members.models import Member


BORROWER_ROLE_CODE = "borrower_portal_user"
PORTAL_ROLE = "borrower_member"
PORTAL_PERMISSION_CODES = [
    "portal.member.profile.read_own",
    "portal.loan_application.read_own",
    "portal.document.read_own",
    "portal.loan_account.read_own",
    "portal.notice.read_own",
    "portal.grievance.manage_own",
]
OTP_TTL_MINUTES = 15
MAX_OTP_ATTEMPTS = 5


class PortalAuthError(Exception):
    def __init__(self, code, message, status=400, field_errors=None):
        self.code = code
        self.message = message
        self.status = status
        self.field_errors = field_errors or {}
        super().__init__(message)


def _normalise(value):
    return str(value or "").strip()


def _normalise_contact(value):
    return _normalise(value).lower()


def _mask_contact(contact):
    contact = _normalise(contact)
    if "@" in contact:
        local, domain = contact.split("@", 1)
        return f"{local[:2]}***@{domain}"
    if len(contact) <= 4:
        return "***"
    return f"{contact[:3]}***{contact[-2:]}"


def _otp_value():
    if hasattr(settings, "PORTAL_AUTH_TEST_OTP"):
        return getattr(settings, "PORTAL_AUTH_TEST_OTP", "246810")
    return f"{secrets.randbelow(900000) + 100000:06d}"


def _otp_hash(otp):
    return hash_token(str(otp))


def _last4_matches(stored_value, provided_last4):
    provided = _normalise(provided_last4)
    if not provided:
        return True
    return _normalise(stored_value).endswith(provided)


def _password_field_errors(password, confirm_password, current_password=None):
    errors = {}
    if current_password is not None and not current_password:
        errors["current_password"] = "This field is required."
    if not password:
        errors["password"] = "This field is required."
    elif len(password) < 10:
        errors["password"] = "Password must be at least 10 characters."
    if password != confirm_password:
        errors["confirm_password"] = "Passwords must match."
    return errors


def borrower_role():
    role, _ = Role.objects.get_or_create(
        role_code=BORROWER_ROLE_CODE,
        defaults={
            "role_name": "Borrower Portal User",
            "description": "Member portal self-service user",
            "is_system_role": True,
            "status": "active",
        },
    )
    return role


def find_member_for_activation(folio_or_member_id, contact, pan_last4="", aadhaar_last4=""):
    identifier = _normalise(folio_or_member_id)
    contact_value = _normalise_contact(contact)
    if not identifier or not contact_value:
        raise PortalAuthError(
            "MISSING_REQUIRED_FIELD",
            "Member identifier and registered contact are required.",
            field_errors={
                "folio_or_member_id": "This field is required." if not identifier else "",
                "contact": "This field is required." if not contact_value else "",
            },
        )
    member = (
        Member.objects.filter(is_deleted=False)
        .filter(Q(folio_number__iexact=identifier) | Q(member_number__iexact=identifier))
        .first()
    )
    if not member:
        raise PortalAuthError("ACTIVATION_NOT_ALLOWED", "Portal activation could not be completed.")
    member_contacts = {_normalise_contact(member.email), _normalise_contact(member.mobile_number)}
    if contact_value not in member_contacts:
        raise PortalAuthError("ACTIVATION_NOT_ALLOWED", "Portal activation could not be completed.")
    if not _last4_matches(member.pan_encrypted, pan_last4) or not _last4_matches(
        member.aadhaar_encrypted, aadhaar_last4
    ):
        raise PortalAuthError("ACTIVATION_NOT_ALLOWED", "Portal activation could not be completed.")
    if PortalAccount.objects.filter(member=member, status=PortalAccount.STATUS_ACTIVE).exists():
        raise PortalAuthError("PORTAL_ACCOUNT_ACTIVE", "Portal account is already active.", status=409)
    return member


def _record_otp_delivery(member, contact, purpose):
    Communication.objects.create(
        related_entity_type="member",
        related_entity_id=member.member_id,
        recipient_party_type="member",
        recipient_party_id=member.member_id,
        recipient_address=contact,
        channel="email" if "@" in contact else "sms",
        subject_snapshot="Member portal security code",
        body_snapshot=f"Member portal {purpose} OTP issued.",
        delivery_status=Communication.DELIVERY_PENDING,
    )


def create_challenge(member, contact, purpose, portal_account=None):
    otp = _otp_value()
    challenge = PortalOtpChallenge.objects.create(
        member=member,
        portal_account=portal_account,
        purpose=purpose,
        contact=_normalise(contact),
        otp_hash=_otp_hash(otp),
        expires_at=timezone.now() + timezone.timedelta(minutes=OTP_TTL_MINUTES),
    )
    _record_otp_delivery(member, challenge.contact, purpose)
    return challenge


def start_activation(data, request):
    member = find_member_for_activation(
        data.get("folio_or_member_id"),
        data.get("contact"),
        data.get("pan_last4", ""),
        data.get("aadhaar_last4", ""),
    )
    challenge = create_challenge(
        member, data.get("contact"), PortalOtpChallenge.PURPOSE_ACTIVATION
    )
    AuditLog.objects.create(
        actor_type="portal_member",
        action="portal.auth.activation.started",
        entity_type="member",
        entity_id=member.member_id,
        new_value_json={"outcome": "otp_sent", "channel": "email" if "@" in challenge.contact else "sms"},
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return {
        "challenge_id": str(challenge.challenge_id),
        "masked_contact": _mask_contact(challenge.contact),
        "expires_at": challenge.expires_at.isoformat().replace("+00:00", "Z"),
    }


def _challenge_or_error(challenge_id, purpose):
    try:
        challenge = PortalOtpChallenge.objects.select_related(
            "member", "portal_account", "portal_account__user"
        ).get(challenge_id=challenge_id, purpose=purpose)
    except (PortalOtpChallenge.DoesNotExist, ValidationError) as exc:
        raise PortalAuthError("OTP_INVALID", "OTP challenge is invalid.") from exc
    if not challenge.is_pending():
        raise PortalAuthError("OTP_INVALID", "OTP challenge is invalid.")
    return challenge


def _verify_otp(challenge, otp):
    if not secrets.compare_digest(challenge.otp_hash, _otp_hash(otp)):
        challenge.attempt_count += 1
        if challenge.attempt_count >= MAX_OTP_ATTEMPTS:
            challenge.status = PortalOtpChallenge.STATUS_EXPIRED
        challenge.save(update_fields=["attempt_count", "status"])
        raise PortalAuthError("OTP_INVALID", "OTP challenge is invalid.")
    challenge.status = PortalOtpChallenge.STATUS_USED
    challenge.used_at = timezone.now()
    challenge.save(update_fields=["status", "used_at"])


def _portal_email(member):
    return member.email or f"portal+{member.member_id}@sfpcl.local"


@transaction.atomic
def complete_activation(data, request):
    challenge = _challenge_or_error(
        data.get("challenge_id"), PortalOtpChallenge.PURPOSE_ACTIVATION
    )
    errors = _password_field_errors(data.get("password", ""), data.get("confirm_password", ""))
    if errors:
        raise PortalAuthError("VALIDATION_ERROR", "Password failed validation.", field_errors=errors)
    if PortalAccount.objects.filter(member=challenge.member, status=PortalAccount.STATUS_ACTIVE).exists():
        raise PortalAuthError("PORTAL_ACCOUNT_ACTIVE", "Portal account is already active.", status=409)

    _verify_otp(challenge, data.get("otp", ""))
    user, _ = User.objects.get_or_create(
        email=_portal_email(challenge.member),
        defaults={
            "full_name": challenge.member.display_name,
            "mobile_number": challenge.member.mobile_number,
            "status": User.ACTIVE_STATUS,
            "primary_role": borrower_role(),
        },
    )
    user.full_name = challenge.member.display_name
    user.mobile_number = challenge.member.mobile_number
    user.status = User.ACTIVE_STATUS
    user.primary_role = borrower_role()
    user.set_password(data["password"])
    user.updated_at = timezone.now()
    user.save(
        update_fields=[
            "full_name",
            "mobile_number",
            "status",
            "primary_role",
            "password_hash",
            "updated_at",
        ]
    )
    account, _ = PortalAccount.objects.get_or_create(
        member=challenge.member,
        defaults={"user": user, "status": PortalAccount.STATUS_ACTIVE},
    )
    account.user = user
    account.status = PortalAccount.STATUS_ACTIVE
    account.activated_at = timezone.now()
    account.updated_at = timezone.now()
    account.save(update_fields=["user", "status", "activated_at", "updated_at"])
    AuditLog.objects.create(
        actor_user=user,
        actor_type="portal_member",
        action="portal.account.activated",
        entity_type="member",
        entity_id=challenge.member_id,
        new_value_json={"outcome": "success"},
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return {"portal_account": serialize_portal_account(account)}


def serialize_portal_account(account):
    return {
        "portal_account_id": str(account.portal_account_id),
        "member_id": str(account.member_id),
        "status": account.status,
        "member_display_name": account.member.display_name,
        "masked_mobile_number": _mask_contact(account.member.mobile_number),
        "masked_email": _mask_contact(account.member.email),
        "otp_login_enabled": account.otp_login_enabled,
    }


def portal_user_payload(user):
    payload = auth_service.current_user_payload(user)
    account = getattr(user, "portal_account", None)
    if account:
        payload.update(
            {
                "member_id": str(account.member_id),
                "portal_account_id": str(account.portal_account_id),
                "portal_role": PORTAL_ROLE,
                "member_display_name": account.member.display_name,
                "permissions": PORTAL_PERMISSION_CODES,
                "available_actions": PORTAL_PERMISSION_CODES,
            }
        )
    return payload


def portal_auth_payload(user, session, refresh_token):
    payload = auth_service.auth_payload(user, session, refresh_token)
    payload["user"] = portal_user_payload(user)
    return payload


def authenticate_portal_user(identifier, password):
    identifier = _normalise_contact(identifier)
    account = (
        PortalAccount.objects.select_related("user", "user__primary_role", "member")
        .filter(Q(user__email__iexact=identifier) | Q(member__email__iexact=identifier) | Q(member__mobile_number__iexact=identifier))
        .first()
    )
    if not account or not account.user.check_password(password) or not account.can_authenticate():
        raise auth_service.CredentialError("invalid_credentials", user=account.user if account else None)
    return account.user


def issue_portal_login(user, request):
    session, _payload = auth_service.issue_login_tokens_and_session(user, request)
    refresh_token = auth_service.rotate_refresh_token(session)
    return session, portal_auth_payload(user, session, refresh_token)


def start_password_reset(data, request):
    identifier = _normalise_contact(data.get("identifier"))
    account = (
        PortalAccount.objects.select_related("member", "user")
        .filter(Q(user__email__iexact=identifier) | Q(member__email__iexact=identifier) | Q(member__mobile_number__iexact=identifier))
        .first()
    )
    if account and account.status == PortalAccount.STATUS_ACTIVE:
        challenge = create_challenge(
            account.member,
            identifier,
            PortalOtpChallenge.PURPOSE_PASSWORD_RESET,
            portal_account=account,
        )
        challenge_id = str(challenge.challenge_id)
        masked_contact = _mask_contact(challenge.contact)
    else:
        challenge_id = None
        masked_contact = None
    AuditLog.objects.create(
        actor_user=account.user if account else None,
        actor_type="portal_member" if account else "anonymous",
        action="portal.auth.password_reset.started",
        entity_type="portal_account" if account else "auth",
        entity_id=account.portal_account_id if account else None,
        new_value_json={"outcome": "otp_sent" if account else "generic_response"},
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return {
        "challenge_id": challenge_id,
        "masked_contact": masked_contact,
        "message": "If a portal account exists, an OTP has been sent.",
    }


@transaction.atomic
def complete_password_reset(data, request):
    challenge = _challenge_or_error(
        data.get("challenge_id"), PortalOtpChallenge.PURPOSE_PASSWORD_RESET
    )
    if not challenge.portal_account:
        raise PortalAuthError("OTP_INVALID", "OTP challenge is invalid.")
    errors = _password_field_errors(data.get("password", ""), data.get("confirm_password", ""))
    if errors:
        raise PortalAuthError("VALIDATION_ERROR", "Password failed validation.", field_errors=errors)
    _verify_otp(challenge, data.get("otp", ""))
    user = challenge.portal_account.user
    user.set_password(data["password"])
    user.updated_at = timezone.now()
    user.save(update_fields=["password_hash", "updated_at"])
    UserSession.objects.filter(user=user, session_status=UserSession.ACTIVE).update(
        session_status=UserSession.REVOKED,
        revoked_reason="portal_password_reset",
        revoked_at=timezone.now(),
    )
    AuditLog.objects.create(
        actor_user=user,
        actor_type="portal_member",
        action="portal.auth.password_reset.completed",
        entity_type="portal_account",
        entity_id=challenge.portal_account_id,
        new_value_json={"outcome": "success"},
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return {"reset": True}


@transaction.atomic
def change_password(user, session, data, request):
    if not hasattr(user, "portal_account"):
        raise PortalAuthError("PERMISSION_DENIED", "Portal account is required.", status=403)
    errors = _password_field_errors(
        data.get("new_password", ""),
        data.get("confirm_password", ""),
        current_password=data.get("current_password", ""),
    )
    if errors:
        raise PortalAuthError("VALIDATION_ERROR", "Password failed validation.", field_errors=errors)
    if not user.check_password(data.get("current_password", "")):
        raise PortalAuthError("INVALID_CREDENTIALS", "Current password is incorrect.", status=401)
    user.set_password(data["new_password"])
    user.updated_at = timezone.now()
    user.save(update_fields=["password_hash", "updated_at"])
    UserSession.objects.filter(user=user, session_status=UserSession.ACTIVE).exclude(
        user_session_id=session.user_session_id
    ).update(
        session_status=UserSession.REVOKED,
        revoked_reason="portal_password_change",
        revoked_at=timezone.now(),
    )
    AuditLog.objects.create(
        actor_user=user,
        actor_type="portal_member",
        action="portal.password.changed",
        entity_type="portal_account",
        entity_id=user.portal_account.portal_account_id,
        new_value_json={"outcome": "success"},
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return {"password_changed": True}


def portal_scope_for_user(user):
    account = getattr(user, "portal_account", None)
    if not account:
        return None
    return {
        "member_id": str(account.member_id),
        "portal_account_id": str(account.portal_account_id),
        "portal_role": PORTAL_ROLE,
    }
