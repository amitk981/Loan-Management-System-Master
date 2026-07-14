from dataclasses import dataclass
from datetime import timedelta
from typing import Callable
import uuid

from django.core.exceptions import ValidationError
from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext


CDSL_REVEAL_PERMISSION = "security.cdsl_pledge.reveal"
CDSL_REVEAL_ROLES = {"company_secretary"}
CDSL_SUCCESS_ACTION = "security.cdsl_pledge.bo_accounts_revealed"
CDSL_DENIED_ACTION = "security.cdsl_pledge.bo_accounts_reveal_denied"
CDSL_EXPIRY_SECONDS = 300
CDSL_RATE_LIMIT_COUNT = 1
CDSL_RATE_LIMIT_SECONDS = 300


class SensitiveAccessDenied(Exception):
    error_code = "SENSITIVE_FIELD_ACCESS_DENIED"


class SensitiveObjectNotFound(Exception):
    pass


class SensitiveRateLimited(Exception):
    pass


class SensitiveValueUnavailable(Exception):
    pass


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


@dataclass(frozen=True)
class SensitiveEntity:
    entity_type: str
    entity_id: uuid.UUID
    related_ids: dict
    encrypted_fields: dict[str, str | None]


def mask_value(field_name: str, encrypted_value: str | None, default_length=16):
    del field_name
    return FieldEncryption.mask(encrypted_value, default_length)


def reveal_cdsl_bo_accounts(
    *, actor, cdsl_share_pledge_id, payload, metadata: RequestMetadata,
    resolve_entity: Callable,
):
    reason = _reason(payload, actor, cdsl_share_pledge_id, metadata)
    _require_authority(actor, cdsl_share_pledge_id, reason, metadata)
    try:
        entity = resolve_entity(actor)
    except SensitiveAccessDenied:
        _audit_denial(
            actor, cdsl_share_pledge_id, reason, "object_access_denied", metadata
        )
        raise
    if entity is None:
        raise SensitiveObjectNotFound
    _require_rate_limit(actor, entity, reason, metadata)

    # BO accounts are High rather than Very High under auth-permissions §21.1, so this
    # policy records that re-authentication is not required. The interface retains the
    # decision explicitly for later Very High field adapters.
    reauthentication_required = False
    try:
        values = {
            name: (
                FieldEncryption.decrypt(f"cdsl.{name}", value)
                if value is not None else None
            )
            for name, value in entity.encrypted_fields.items()
        }
    except InvalidCiphertext as exc:
        _audit_denial(
            actor, entity.entity_id, reason, "ciphertext_unavailable", metadata
        )
        raise SensitiveValueUnavailable from exc

    expires_at = timezone.now() + timedelta(seconds=CDSL_EXPIRY_SECONDS)
    expires_at_value = expires_at.isoformat().replace("+00:00", "Z")
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=CDSL_SUCCESS_ACTION,
        entity_type=entity.entity_type,
        entity_id=entity.entity_id,
        old_value_json={},
        new_value_json={
            "cdsl_share_pledge_id": str(entity.entity_id),
            **entity.related_ids,
            "field_names": sorted(entity.encrypted_fields),
            "reason": reason,
            "outcome": "success",
            "request_id": metadata.request_id,
            "expires_at": expires_at_value,
            "reauthentication_required": reauthentication_required,
            "reauthentication_satisfied": True,
            "rate_limit_count": CDSL_RATE_LIMIT_COUNT,
            "rate_limit_window_seconds": CDSL_RATE_LIMIT_SECONDS,
            "actor_role_codes": auth_service.effective_role_codes(actor),
            "actor_team_codes": actor.team_codes(),
        },
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    return {**values, "expires_at": expires_at_value}


def _reason(payload, actor, entity_id, metadata):
    errors = {}
    if not isinstance(payload, dict):
        errors["non_field_errors"] = "A JSON object is required."
        payload = {}
    unknown = set(payload) - {"reason"}
    missing = {"reason"} - set(payload)
    errors.update({field: "Unknown field." for field in sorted(unknown)})
    errors.update({field: "This field is required." for field in sorted(missing)})
    reason = payload.get("reason")
    if "reason" not in missing:
        if not isinstance(reason, str) or not reason.strip():
            errors["reason"] = "A non-empty reason is required."
        elif len(reason.strip()) > 500:
            errors["reason"] = "Must be at most 500 characters."
    if errors:
        _audit_denial(actor, entity_id, None, "validation_failed", metadata)
        raise ValidationError(errors)
    return reason.strip()


def _require_authority(actor, entity_id, reason, metadata):
    roles = set(auth_service.effective_role_codes(actor)) if actor.can_authenticate() else set()
    permissions = (
        set(auth_service.effective_permission_codes(actor))
        if actor.can_authenticate() else set()
    )
    if CDSL_REVEAL_PERMISSION not in permissions or not roles.intersection(CDSL_REVEAL_ROLES):
        _audit_denial(actor, entity_id, reason, "missing_reveal_authority", metadata)
        raise SensitiveAccessDenied


def _require_rate_limit(actor, entity, reason, metadata):
    since = timezone.now() - timedelta(seconds=CDSL_RATE_LIMIT_SECONDS)
    count = AuditLog.objects.filter(
        actor_user=actor,
        action=CDSL_SUCCESS_ACTION,
        entity_type=entity.entity_type,
        entity_id=entity.entity_id,
        created_at__gte=since,
    ).count()
    if count >= CDSL_RATE_LIMIT_COUNT:
        _audit_denial(actor, entity.entity_id, reason, "rate_limited", metadata)
        raise SensitiveRateLimited


def _audit_denial(actor, entity_id, reason, denial_reason, metadata):
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=CDSL_DENIED_ACTION,
        entity_type="cdsl_share_pledge",
        entity_id=entity_id,
        old_value_json={},
        new_value_json={
            "cdsl_share_pledge_id": str(entity_id),
            "outcome": "denied",
            "denial_reason": denial_reason,
            "reason": reason,
            "request_id": metadata.request_id,
        },
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
