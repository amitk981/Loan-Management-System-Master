from dataclasses import asdict, dataclass
from datetime import date
import uuid

from django.core.exceptions import ValidationError


def _exact_fields(payload, fields):
    if not isinstance(payload, dict):
        raise ValidationError({"non_field_errors": "A JSON object is required."})
    unknown = set(payload) - fields
    missing = fields - set(payload)
    errors = {field: "Unknown field." for field in sorted(unknown)}
    errors.update({field: "This field is required." for field in sorted(missing)})
    if errors:
        raise ValidationError(errors)


@dataclass(frozen=True)
class PowerOfAttorneyRequest:
    borrower_member_id: uuid.UUID
    nominee_id: uuid.UUID
    attorney_user_id: uuid.UUID
    purpose_summary: str
    loan_document_id: uuid.UUID
    stamp_duty_record_id: uuid.UUID
    notarisation_record_id: uuid.UUID
    execution_status: str
    effective_from: date | None
    status: str

    FIELDS = {
        "borrower_member_id", "nominee_id", "attorney_user_id", "purpose_summary",
        "loan_document_id", "stamp_duty_record_id", "notarisation_record_id",
        "execution_status", "effective_from", "status",
    }

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        errors, ids = {}, {}
        for field in (
            "borrower_member_id", "nominee_id", "attorney_user_id", "loan_document_id",
            "stamp_duty_record_id", "notarisation_record_id",
        ):
            try:
                ids[field] = uuid.UUID(str(payload.get(field)))
            except (TypeError, ValueError, AttributeError):
                errors[field] = "A valid accessible UUID is required."
        purpose = payload.get("purpose_summary")
        if not isinstance(purpose, str) or not purpose.strip():
            errors["purpose_summary"] = "A non-empty purpose is required."
            purpose = ""
        else:
            purpose = purpose.strip()
            if len(purpose) > 4000:
                errors["purpose_summary"] = "Must be at most 4000 characters."
        execution = payload.get("execution_status")
        if execution not in {"pending", "executed"}:
            errors["execution_status"] = "Must be one of pending, executed."
        status = payload.get("status")
        if status not in {"draft", "active"}:
            errors["status"] = "Must be one of draft, active."
        effective = payload.get("effective_from")
        if effective is not None:
            try:
                effective = date.fromisoformat(effective)
            except (TypeError, ValueError):
                errors["effective_from"] = "Must be a valid ISO date or null."
                effective = None
        if errors:
            raise ValidationError(errors)
        return cls(
            **ids,
            purpose_summary=purpose,
            execution_status=execution,
            effective_from=effective,
            status=status,
        )

    def as_values(self):
        return asdict(self)


@dataclass(frozen=True)
class SH4ShareTransferFormRequest:
    member_id: uuid.UUID
    witness_id: uuid.UUID
    shareholding_id: uuid.UUID
    share_count: int | None
    loan_document_id: uuid.UUID
    form_status: str
    custody_location: str | None
    signed_at: date | None

    FIELDS = {
        "member_id", "witness_id", "shareholding_id", "share_count",
        "loan_document_id", "form_status", "custody_location", "signed_at",
    }

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        errors, ids = {}, {}
        for field in ("member_id", "witness_id", "shareholding_id", "loan_document_id"):
            try:
                ids[field] = uuid.UUID(str(payload.get(field)))
            except (TypeError, ValueError, AttributeError):
                errors[field] = "A valid accessible UUID is required."
        share_count = payload.get("share_count")
        if share_count is not None and (
            isinstance(share_count, bool) or not isinstance(share_count, int) or share_count < 1
        ):
            errors["share_count"] = "Must be a positive integer or null."
        status = payload.get("form_status")
        if status not in {"pending", "signed", "held_in_custody"}:
            errors["form_status"] = (
                "Must be one of pending, signed, held_in_custody; invocation and return "
                "belong to later approved workflows."
            )
        location = payload.get("custody_location")
        if location is not None:
            if not isinstance(location, str):
                errors["custody_location"] = "Must be text or null."
            else:
                location = location.strip()
                if not location or len(location) > 255:
                    errors["custody_location"] = "Must be non-empty and at most 255 characters."
        signed_at = payload.get("signed_at")
        if signed_at is not None:
            try:
                signed_at = date.fromisoformat(signed_at)
            except (TypeError, ValueError):
                errors["signed_at"] = "Must be a valid ISO date or null."
                signed_at = None
        if errors:
            raise ValidationError(errors)
        return cls(
            **ids, share_count=share_count, form_status=status,
            custody_location=location, signed_at=signed_at,
        )

    def as_values(self):
        return asdict(self)
