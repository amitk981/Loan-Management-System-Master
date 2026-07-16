"""Replaceable adapter contract for the manual and future SAP boundary."""

from dataclasses import dataclass
import hashlib
from io import BytesIO
import json
import re
from typing import Protocol
import uuid
import zipfile


XLSX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_REFERENCE_RE = re.compile(r"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{1,128}$")


def validate_xlsx_workbook_bytes(workbook_bytes):
    """Reject lookalike ZIP prefixes and accept only the retained XLSX package shape."""
    if not isinstance(workbook_bytes, bytes) or not zipfile.is_zipfile(BytesIO(workbook_bytes)):
        raise ValueError("The retained SAP Annexure-I is not an XLSX workbook.")
    with zipfile.ZipFile(BytesIO(workbook_bytes)) as workbook:
        names = set(workbook.namelist())
    required = {"[Content_Types].xml", "xl/workbook.xml", "xl/worksheets/sheet1.xml"}
    if not required.issubset(names):
        raise ValueError("The retained SAP Annexure-I is not an XLSX workbook.")


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


class _IdempotentSapAdapter:
    """Shared local contract that every manual, fake, or future adapter must satisfy."""

    def __init__(self):
        self._deliveries_by_key = {}
        self._keys_by_request = {}

    def create_customer_profile_request(self, payload, idempotency_key):
        _validate_payload(payload, idempotency_key)
        fingerprint = _payload_fingerprint(payload)
        existing_key = self._keys_by_request.get(payload.request_id)
        if existing_key is not None and existing_key != idempotency_key:
            raise ValueError("The SAP idempotency key cannot change for this request.")
        retained = self._deliveries_by_key.get(idempotency_key)
        if retained is not None:
            retained_fingerprint, result = retained
            if retained_fingerprint != fingerprint:
                raise ValueError("The SAP delivery facts cannot change on replay.")
            return result
        result = self._perform_delivery(payload, idempotency_key)
        _validate_result(result, expected_checksum=payload.checksum_sha256)
        self._keys_by_request[payload.request_id] = idempotency_key
        self._deliveries_by_key[idempotency_key] = (fingerprint, result)
        return result

    def _perform_delivery(self, payload, idempotency_key):
        raise NotImplementedError


class ManualSapAdapter(_IdempotentSapAdapter):
    """File-first MVP adapter; accepts a verified workbook without calling SAP/email."""

    _NAMESPACE = uuid.UUID("91e33a41-9136-4d4b-97b6-25f69fcde8d7")

    def _perform_delivery(self, payload, idempotency_key):
        checksum = hashlib.sha256(payload.workbook_bytes).hexdigest()
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
        if not _valid_manual_reference(external_reference):
            raise ValueError("The SAP delivery reference is invalid.")
        return SapCustomerStatus(
            external_reference=external_reference,
            delivery_status="delivered",
        )


class FakeSapAdapter(ManualSapAdapter):
    """Deterministic test adapter satisfying the same file-acceptance contract."""

    _NAMESPACE = uuid.UUID("d6283117-8c45-4a4b-b00e-2a56a8857fd9")


class FutureSapAdapter(_IdempotentSapAdapter):
    """Future transport slot; validates SAP-owned facts before delegation."""

    def __init__(self, *, transport: SapAdapter):
        super().__init__()
        self.transport = transport

    def _perform_delivery(self, payload, idempotency_key):
        return self.transport.create_customer_profile_request(payload, idempotency_key)

    def get_customer_status(self, external_reference):
        _validate_reference(external_reference)
        status = self.transport.get_customer_status(external_reference)
        if (
            not isinstance(status, SapCustomerStatus)
            or status.external_reference != external_reference
            or status.delivery_status != "delivered"
        ):
            raise ValueError("The SAP delivery status is invalid.")
        return status


def _validate_payload(payload, idempotency_key):
    if not isinstance(payload, SapCustomerProfilePayload):
        raise ValueError("The SAP customer profile payload is invalid.")
    if not all(
        isinstance(value, uuid.UUID)
        for value in (payload.request_id, payload.assignee_user_id, payload.document_id)
    ):
        raise ValueError("The SAP customer profile identity is invalid.")
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        raise ValueError("The SAP idempotency key is invalid.")
    if (
        not isinstance(payload.file_name, str)
        or not payload.file_name.lower().endswith(".xlsx")
        or payload.mime_type != XLSX_MIME_TYPE
    ):
        raise ValueError("The SAP Annexure-I file contract is invalid.")
    validate_xlsx_workbook_bytes(payload.workbook_bytes)
    checksum = hashlib.sha256(payload.workbook_bytes).hexdigest()
    if (
        not isinstance(payload.checksum_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", payload.checksum_sha256)
        or checksum != payload.checksum_sha256
    ):
        raise ValueError("The retained SAP Annexure-I failed adapter verification.")


def _payload_fingerprint(payload):
    facts = {
        "request_id": str(payload.request_id),
        "assignee_user_id": str(payload.assignee_user_id),
        "document_id": str(payload.document_id),
        "file_name": payload.file_name,
        "mime_type": payload.mime_type,
        "checksum_sha256": payload.checksum_sha256,
    }
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _validate_result(result, *, expected_checksum):
    if (
        not isinstance(result, SapCustomerResult)
        or result.delivery_status != "delivered"
        or result.checksum_sha256 != expected_checksum
    ):
        raise ValueError("The SAP delivery result is invalid.")
    _validate_reference(result.external_reference)


def _validate_reference(external_reference):
    if not isinstance(external_reference, str) or not _REFERENCE_RE.fullmatch(
        external_reference
    ):
        raise ValueError("The SAP delivery reference is invalid.")


def _valid_manual_reference(external_reference):
    try:
        _validate_reference(external_reference)
        prefix, identity = external_reference.split(":", 1)
        return prefix == "manual" and str(uuid.UUID(identity)) == identity
    except (ValueError, AttributeError):
        return False

__all__ = [
    "FakeSapAdapter",
    "FutureSapAdapter",
    "ManualSapAdapter",
    "SapAdapter",
    "SapCustomerProfilePayload",
    "SapCustomerResult",
    "SapCustomerStatus",
    "XLSX_MIME_TYPE",
    "validate_xlsx_workbook_bytes",
]
