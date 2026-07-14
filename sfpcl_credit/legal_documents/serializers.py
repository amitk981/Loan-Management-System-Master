import re
import uuid
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError

from sfpcl_credit.legal_documents.models import NotarisationRecord, StampDutyRecord


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
