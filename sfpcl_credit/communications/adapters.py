"""Replaceable channel adapters used by governed borrower communications."""

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Protocol
import uuid

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils import timezone


_REFERENCE_RE = re.compile(r"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{1,128}$")


@dataclass(frozen=True)
class EmailDeliveryPayload:
    communication_id: uuid.UUID
    recipient_email: str
    subject: str
    body_text: str
    related_entity_type: str
    related_entity_id: uuid.UUID


@dataclass(frozen=True)
class SmsDeliveryPayload:
    communication_id: uuid.UUID
    recipient_mobile: str
    template_code: str
    message: str
    related_entity_type: str
    related_entity_id: uuid.UUID


@dataclass(frozen=True)
class EmailDeliveryResult:
    external_message_id: str
    delivery_status: str
    accepted_at: object


class EmailDeliveryAdapter(Protocol):
    def send_email(
        self, payload: EmailDeliveryPayload, idempotency_key: str
    ) -> EmailDeliveryResult: ...


class SmsDeliveryAdapter(Protocol):
    def send_sms(
        self, payload: SmsDeliveryPayload, idempotency_key: str
    ) -> EmailDeliveryResult: ...


class ManualEmailDeliveryAdapter:
    """No-provider adapter: never fabricates external acceptance."""

    _NAMESPACE = uuid.UUID("49d745c9-b464-4a4a-a51c-75691409f572")

    def send_email(self, payload, idempotency_key):
        _validate_payload(payload, idempotency_key)
        raise ValueError("No external email provider is configured.")


class FakeEmailDeliveryAdapter(ManualEmailDeliveryAdapter):
    """Deterministic test adapter satisfying the production acceptance contract."""

    _NAMESPACE = uuid.UUID("6d961c69-61d4-40f3-95e0-d45666922321")

    def send_email(self, payload, idempotency_key):
        _validate_payload(payload, idempotency_key)
        identity = uuid.uuid5(self._NAMESPACE, idempotency_key)
        return EmailDeliveryResult(
            external_message_id=f"fake:{identity}",
            delivery_status="sent",
            accepted_at=timezone.now(),
        )


class FutureEmailDeliveryAdapter:
    """Future provider adapter preserving caller-owned idempotency identity."""

    def __init__(self, *, transport):
        self.transport = transport

    def send_email(self, payload, idempotency_key):
        _validate_payload(payload, idempotency_key)
        return self.transport.send_email(payload, idempotency_key)


class ManualSmsDeliveryAdapter:
    """No-provider SMS adapter: never fabricates external acceptance."""

    def send_sms(self, payload, idempotency_key):
        _validate_sms_payload(payload, idempotency_key)
        raise ValueError("No external SMS provider is configured.")


class FakeSmsDeliveryAdapter(ManualSmsDeliveryAdapter):
    """Deterministic test SMS adapter satisfying the production seam."""

    _NAMESPACE = uuid.UUID("04725d33-7f9a-4b16-bb0e-6ab0add4901b")

    def send_sms(self, payload, idempotency_key):
        _validate_sms_payload(payload, idempotency_key)
        identity = uuid.uuid5(self._NAMESPACE, idempotency_key)
        return EmailDeliveryResult(
            external_message_id=f"fake:{identity}",
            delivery_status="sent",
            accepted_at=timezone.now(),
        )


class FutureSmsDeliveryAdapter:
    """Future SMS provider adapter preserving caller idempotency."""

    def __init__(self, *, transport):
        self.transport = transport

    def send_sms(self, payload, idempotency_key):
        _validate_sms_payload(payload, idempotency_key)
        return self.transport.send_sms(payload, idempotency_key)


def validate_delivery_result(result):
    if (
        not isinstance(result, EmailDeliveryResult)
        or result.delivery_status != "sent"
        or not isinstance(result.external_message_id, str)
        or not _REFERENCE_RE.fullmatch(result.external_message_id)
        or result.accepted_at is None
        or timezone.is_naive(result.accepted_at)
    ):
        raise ValueError("Email delivery result was not accepted.")


def _validate_payload(payload, idempotency_key):
    if (
        not isinstance(payload, EmailDeliveryPayload)
        or not isinstance(payload.communication_id, uuid.UUID)
        or not isinstance(payload.related_entity_id, uuid.UUID)
        or not payload.related_entity_type
        or not payload.recipient_email
        or not payload.subject
        or not payload.body_text
        or not isinstance(idempotency_key, str)
        or not idempotency_key
    ):
        raise ValueError("Email delivery payload is invalid.")


def _validate_sms_payload(payload, idempotency_key):
    if (
        not isinstance(payload, SmsDeliveryPayload)
        or not isinstance(payload.communication_id, uuid.UUID)
        or not isinstance(payload.related_entity_id, uuid.UUID)
        or not payload.related_entity_type
        or not payload.recipient_mobile
        or not payload.template_code
        or not payload.message
        or not isinstance(idempotency_key, str)
        or not idempotency_key
    ):
        raise ValueError("SMS delivery payload is invalid.")


def delivery_payload_digest(payload):
    facts = {
        "communication_id": str(payload.communication_id),
        "recipient_email": payload.recipient_email,
        "subject": payload.subject,
        "body_text": payload.body_text,
        "related_entity_type": payload.related_entity_type,
        "related_entity_id": str(payload.related_entity_id),
    }
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def configured_email_delivery_adapter():
    try:
        adapter_class = import_string(settings.COMMUNICATION_EMAIL_ADAPTER)
        adapter = adapter_class()
    except Exception:
        return ManualEmailDeliveryAdapter()
    if not callable(getattr(adapter, "send_email", None)):
        return ManualEmailDeliveryAdapter()
    return adapter


def configured_sms_delivery_adapter():
    try:
        adapter_class = import_string(settings.COMMUNICATION_SMS_ADAPTER)
        adapter = adapter_class()
    except Exception:
        return ManualSmsDeliveryAdapter()
    if not callable(getattr(adapter, "send_sms", None)):
        return ManualSmsDeliveryAdapter()
    return adapter


__all__ = [
    "EmailDeliveryAdapter",
    "EmailDeliveryPayload",
    "EmailDeliveryResult",
    "FakeEmailDeliveryAdapter",
    "FakeSmsDeliveryAdapter",
    "FutureEmailDeliveryAdapter",
    "FutureSmsDeliveryAdapter",
    "ManualEmailDeliveryAdapter",
    "ManualSmsDeliveryAdapter",
    "SmsDeliveryAdapter",
    "SmsDeliveryPayload",
    "delivery_payload_digest",
    "configured_email_delivery_adapter",
    "configured_sms_delivery_adapter",
    "validate_delivery_result",
]
