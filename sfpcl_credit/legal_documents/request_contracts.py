import re
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from sfpcl_credit.legal_documents.models import (
    NotarisationRecord,
    SignatureRecord,
    StampDutyRecord,
)


_MONEY = re.compile(r"^(0|[1-9][0-9]{0,15})\.[0-9]{2}$")


def _exact_fields(payload, allowed):
    if not isinstance(payload, dict):
        raise ValidationError({"body": "A JSON object is required."})
    unknown = set(payload) - allowed
    if unknown:
        raise ValidationError({field: "Unknown field." for field in sorted(unknown)})
    missing = allowed - set(payload)
    if missing:
        raise ValidationError(
            {field: "This field is required." for field in sorted(missing)}
        )


def _date(field, value):
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValidationError({field: "Must be a valid ISO date."})
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError({field: "Must be a valid ISO date."}) from exc


def _nullable_text(field, value, maximum):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError({field: "Must be a string or null."})
    value = value.strip()
    if len(value) > maximum:
        raise ValidationError({field: f"Must be at most {maximum} characters."})
    return value or None


def _uuid(field, value):
    if value in (None, ""):
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValidationError(
            {field: "Document file was not found or is inaccessible."}
        ) from exc


@dataclass(frozen=True)
class StampDutyRecordRequest:
    stamp_paper_amount: Decimal
    stamp_type: str
    stamp_number: str | None
    stamp_purchase_date: date | None
    executed_date: date | None
    status: str
    remarks: str | None

    FIELDS = {
        "stamp_paper_amount",
        "stamp_type",
        "stamp_number",
        "stamp_purchase_date",
        "executed_date",
        "status",
        "remarks",
    }

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        errors = {}
        raw_amount = payload.get("stamp_paper_amount")
        if not isinstance(raw_amount, str) or not _MONEY.fullmatch(raw_amount):
            errors["stamp_paper_amount"] = "Must be a non-negative two-decimal string."
            amount = None
        else:
            try:
                amount = Decimal(raw_amount)
            except InvalidOperation:
                errors["stamp_paper_amount"] = (
                    "Must be a non-negative two-decimal string."
                )
                amount = None
        stamp_type = payload.get("stamp_type")
        if stamp_type not in StampDutyRecord.TYPES:
            errors["stamp_type"] = "Must be one of physical, electronic."
        status = payload.get("status")
        if status not in StampDutyRecord.STATUSES:
            errors["status"] = "Must be one of pending, adequate, insufficient."
        if errors:
            raise ValidationError(errors)
        return cls(
            stamp_paper_amount=amount,
            stamp_type=stamp_type,
            stamp_number=_nullable_text(
                "stamp_number", payload.get("stamp_number"), 120
            ),
            stamp_purchase_date=_date(
                "stamp_purchase_date", payload.get("stamp_purchase_date")
            ),
            executed_date=_date("executed_date", payload.get("executed_date")),
            status=status,
            remarks=_nullable_text("remarks", payload.get("remarks"), 4000),
        )

    def as_values(self):
        return asdict(self)

@dataclass(frozen=True)
class NotarisationRecordRequest:
    notary_name: str | None
    notary_registration_number: str | None
    notarised_date: date | None
    status: str
    evidence_document_id: uuid.UUID | None
    remarks: str | None

    FIELDS = {
        "notary_name",
        "notary_registration_number",
        "notarised_date",
        "status",
        "evidence_document_id",
        "remarks",
    }

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        status = payload.get("status")
        if status not in NotarisationRecord.STATUSES:
            raise ValidationError(
                {"status": "Must be one of pending, completed, rejected."}
            )
        return cls(
            notary_name=_nullable_text("notary_name", payload.get("notary_name"), 255),
            notary_registration_number=_nullable_text(
                "notary_registration_number",
                payload.get("notary_registration_number"),
                120,
            ),
            notarised_date=_date("notarised_date", payload.get("notarised_date")),
            status=status,
            evidence_document_id=_uuid(
                "evidence_document_id", payload.get("evidence_document_id")
            ),
            remarks=_nullable_text("remarks", payload.get("remarks"), 4000),
        )

    def as_values(self):
        return asdict(self)


def _aware_datetime(field, value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(
            {field: "Must be an ISO-8601 datetime with timezone or null."}
        )
    parsed = parse_datetime(value)
    if parsed is None or not timezone.is_aware(parsed):
        raise ValidationError(
            {field: "Must be an ISO-8601 datetime with timezone or null."}
        )
    return parsed


@dataclass(frozen=True)
class SignatureRecordRequest:
    signer_party_type: str
    signer_party_id: uuid.UUID | None
    signer_name_snapshot: str
    signature_method: str
    signature_status: str
    signed_at: datetime | None
    signature_mismatch_flag: bool

    FIELDS = {
        "signer_party_type",
        "signer_party_id",
        "signer_name_snapshot",
        "signature_method",
        "signature_status",
        "signed_at",
        "signature_mismatch_flag",
    }

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        errors = {}
        party_type = payload.get("signer_party_type")
        if party_type not in SignatureRecord.PARTY_TYPES:
            errors["signer_party_type"] = "Must be one of borrower, nominee, witness, user."
        method = payload.get("signature_method")
        if method not in SignatureRecord.METHODS:
            errors["signature_method"] = "Must be one of wet_ink, digital, scanned."
        status = payload.get("signature_status")
        if status not in SignatureRecord.STATUSES:
            errors["signature_status"] = "Must be one of pending, signed, mismatch."
        mismatch = payload.get("signature_mismatch_flag")
        if not isinstance(mismatch, bool):
            errors["signature_mismatch_flag"] = "Must be a boolean."
        name = payload.get("signer_name_snapshot")
        if not isinstance(name, str) or not name.strip():
            errors["signer_name_snapshot"] = "A non-empty string is required."
            name = ""
        else:
            name = name.strip()
            if len(name) > 255:
                errors["signer_name_snapshot"] = "Must be at most 255 characters."
        try:
            party_id = _uuid("signer_party_id", payload.get("signer_party_id"))
        except ValidationError:
            errors["signer_party_id"] = "Must be a valid UUID or null."
            party_id = None
        try:
            signed_at = _aware_datetime("signed_at", payload.get("signed_at"))
        except ValidationError as exc:
            errors.update({key: values[0] for key, values in exc.message_dict.items()})
            signed_at = None
        if status == "pending" and (signed_at is not None or mismatch is not False):
            errors["signature_status"] = "Pending signature cannot carry signed or mismatch facts."
        if status == "signed" and (signed_at is None or mismatch is not False):
            errors["signature_status"] = "Signed signature requires signed_at and no mismatch."
        if status == "mismatch" and mismatch is not True:
            errors["signature_mismatch_flag"] = "Mismatch status requires a true mismatch flag."
        if errors:
            raise ValidationError(errors)
        return cls(party_type, party_id, name, method, status, signed_at, mismatch)

    def as_values(self):
        return asdict(self)


@dataclass(frozen=True)
class SignatureMismatchResolutionRequest:
    mismatch_resolution_type: str
    mismatch_resolution_document_id: uuid.UUID
    remarks: str | None

    FIELDS = {
        "mismatch_resolution_type",
        "mismatch_resolution_document_id",
        "remarks",
    }

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        errors = {}
        resolution_type = payload.get("mismatch_resolution_type")
        if resolution_type not in SignatureRecord.RESOLUTION_TYPES:
            errors["mismatch_resolution_type"] = (
                "Must be one of bank_verification_letter, borrower_declaration."
            )
        try:
            document_id = _uuid(
                "mismatch_resolution_document_id",
                payload.get("mismatch_resolution_document_id"),
            )
        except ValidationError:
            errors["mismatch_resolution_document_id"] = "Must be a valid UUID."
            document_id = None
        if document_id is None and "mismatch_resolution_document_id" not in errors:
            errors["mismatch_resolution_document_id"] = "A document id is required."
        try:
            remarks = _nullable_text("remarks", payload.get("remarks"), 4000)
        except ValidationError as exc:
            errors.update({key: values[0] for key, values in exc.message_dict.items()})
            remarks = None
        if errors:
            raise ValidationError(errors)
        return cls(resolution_type, document_id, remarks)

    def as_values(self):
        return asdict(self)


@dataclass(frozen=True)
class LoanDocumentVerificationRequest:
    verification_status: str
    remarks: str | None

    FIELDS = {"verification_status", "remarks"}

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        if payload.get("verification_status") != "verified":
            raise ValidationError(
                {"verification_status": "Must be verified for this document type."}
            )
        return cls(
            verification_status="verified",
            remarks=_nullable_text("remarks", payload.get("remarks"), 4000),
        )

    def as_values(self):
        return asdict(self)
