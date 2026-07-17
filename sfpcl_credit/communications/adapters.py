"""Replaceable outbound email adapter used by governed borrower communications."""

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Protocol
import uuid

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
class EmailDeliveryResult:
    external_message_id: str
    delivery_status: str
    accepted_at: object


class EmailDeliveryAdapter(Protocol):
    def send_email(
        self, payload: EmailDeliveryPayload, idempotency_key: str
    ) -> EmailDeliveryResult: ...


class ManualEmailDeliveryAdapter:
    """MVP adapter: records deterministic provider acceptance without network I/O."""

    _NAMESPACE = uuid.UUID("49d745c9-b464-4a4a-a51c-75691409f572")

    def send_email(self, payload, idempotency_key):
        _validate_payload(payload, idempotency_key)
        identity = uuid.uuid5(self._NAMESPACE, idempotency_key)
        return EmailDeliveryResult(
            external_message_id=f"manual:{identity}",
            delivery_status="sent",
            accepted_at=timezone.now(),
        )


class FakeEmailDeliveryAdapter(ManualEmailDeliveryAdapter):
    """Deterministic test adapter satisfying the production acceptance contract."""

    _NAMESPACE = uuid.UUID("6d961c69-61d4-40f3-95e0-d45666922321")


class FutureEmailDeliveryAdapter:
    """Future provider adapter preserving caller-owned idempotency identity."""

    def __init__(self, *, transport):
        self.transport = transport

    def send_email(self, payload, idempotency_key):
        _validate_payload(payload, idempotency_key)
        return self.transport.send_email(payload, idempotency_key)


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
        or payload.related_entity_type != "disbursement"
        or not payload.recipient_email
        or not payload.subject
        or not payload.body_text
        or not isinstance(idempotency_key, str)
        or not idempotency_key
    ):
        raise ValueError("Email delivery payload is invalid.")


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


__all__ = [
    "EmailDeliveryAdapter",
    "EmailDeliveryPayload",
    "EmailDeliveryResult",
    "FakeEmailDeliveryAdapter",
    "FutureEmailDeliveryAdapter",
    "ManualEmailDeliveryAdapter",
    "delivery_payload_digest",
    "validate_delivery_result",
]
