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
