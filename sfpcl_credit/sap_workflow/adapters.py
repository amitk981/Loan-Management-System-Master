"""Replaceable adapter contract for the manual and future SAP boundary."""

from dataclasses import dataclass
import hashlib
from typing import Protocol
import uuid


@dataclass(frozen=True)
class SapCustomerProfilePayload:
    request_id: uuid.UUID
    assignee_user_id: uuid.UUID
    document_id: uuid.UUID
    file_name: str
    mime_type: str
    workbook_bytes: bytes
    checksum_sha256: str


@dataclass(frozen=True)
class SapCustomerResult:
    external_reference: str
    delivery_status: str
    checksum_sha256: str


@dataclass(frozen=True)
class SapCustomerStatus:
    external_reference: str
    delivery_status: str


class SapAdapter(Protocol):
    def create_customer_profile_request(
        self, payload: SapCustomerProfilePayload, idempotency_key: str
    ) -> SapCustomerResult: ...

    def get_customer_status(self, external_reference: str) -> SapCustomerStatus: ...


class ManualSapAdapter:
    """File-first MVP adapter; accepts a verified workbook without calling SAP/email."""

    _NAMESPACE = uuid.UUID("91e33a41-9136-4d4b-97b6-25f69fcde8d7")

    def create_customer_profile_request(self, payload, idempotency_key):
        checksum = hashlib.sha256(payload.workbook_bytes).hexdigest()
        if checksum != payload.checksum_sha256 or not payload.workbook_bytes.startswith(b"PK"):
            raise ValueError("The retained SAP Annexure-I failed adapter verification.")
        identity = uuid.uuid5(
            self._NAMESPACE,
            f"{idempotency_key}:{payload.document_id}:{payload.assignee_user_id}:{checksum}",
        )
        return SapCustomerResult(
            external_reference=f"manual:{identity}",
            delivery_status="delivered",
            checksum_sha256=checksum,
        )

    def get_customer_status(self, external_reference):
        if not str(external_reference).startswith("manual:"):
            raise ValueError("The SAP delivery reference is invalid.")
        return SapCustomerStatus(
            external_reference=external_reference,
            delivery_status="delivered",
        )


class FakeSapAdapter(ManualSapAdapter):
    """Deterministic test adapter satisfying the same file-acceptance contract."""

    _NAMESPACE = uuid.UUID("d6283117-8c45-4a4b-b00e-2a56a8857fd9")


class FutureSapAdapter:
    """Future transport slot; validates SAP-owned facts before delegation."""

    def __init__(self, *, transport: SapAdapter):
        self.transport = transport

    def create_customer_profile_request(self, payload, idempotency_key):
        ManualSapAdapter().create_customer_profile_request(payload, idempotency_key)
        return self.transport.create_customer_profile_request(payload, idempotency_key)

    def get_customer_status(self, external_reference):
        return self.transport.get_customer_status(external_reference)

__all__ = [
    "FakeSapAdapter",
    "FutureSapAdapter",
    "ManualSapAdapter",
    "SapAdapter",
    "SapCustomerProfilePayload",
    "SapCustomerResult",
    "SapCustomerStatus",
]
