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


@dataclass(frozen=True)
class CDSLSharePledgeRequest:
    pledgor_member_id: uuid.UUID
    pledgee_entity_name: str
    pledgor_bo_account: str
    pledgee_bo_account: str | None
    pledgor_dp_name: str | None
    pledgee_dp_name: str | None
    prf_status: str
    pledge_sequence_number: str | None
    pledge_acceptance_status: str
    pledged_share_count: int | None
    agreement_number: str | None
    pledge_status: str
    evidence_document_id: uuid.UUID | None

    FIELDS = {
        "pledgor_member_id", "pledgee_entity_name", "pledgor_bo_account",
        "pledgee_bo_account", "pledgor_dp_name", "pledgee_dp_name", "prf_status",
        "pledge_sequence_number", "pledge_acceptance_status", "pledged_share_count",
        "agreement_number", "pledge_status", "evidence_document_id",
    }

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        errors = {}
        try:
            pledgor_member_id = uuid.UUID(str(payload.get("pledgor_member_id")))
        except (TypeError, ValueError, AttributeError):
            errors["pledgor_member_id"] = "A valid accessible UUID is required."
            pledgor_member_id = uuid.UUID(int=0)
        evidence_document_id = payload.get("evidence_document_id")
        if evidence_document_id is not None:
            try:
                evidence_document_id = uuid.UUID(str(evidence_document_id))
            except (TypeError, ValueError, AttributeError):
                errors["evidence_document_id"] = "A valid accessible UUID or null is required."
                evidence_document_id = None

        entity = _bounded_text(payload.get("pledgee_entity_name"), "pledgee_entity_name", 255, errors)
        pledgor_account = _bo_account(payload.get("pledgor_bo_account"), "pledgor_bo_account", errors)
        pledgee_account = _bo_account(
            payload.get("pledgee_bo_account"), "pledgee_bo_account", errors, nullable=True
        )
        if pledgor_account and pledgee_account and pledgor_account == pledgee_account:
            errors["pledgee_bo_account"] = "Pledgor and pledgee BO accounts must be distinct."
        pledgor_dp = _bounded_text(
            payload.get("pledgor_dp_name"), "pledgor_dp_name", 255, errors, nullable=True
        )
        pledgee_dp = _bounded_text(
            payload.get("pledgee_dp_name"), "pledgee_dp_name", 255, errors, nullable=True
        )
        psn = _bounded_text(
            payload.get("pledge_sequence_number"), "pledge_sequence_number", 120,
            errors, nullable=True,
        )
        agreement = _bounded_text(
            payload.get("agreement_number"), "agreement_number", 120, errors,
            nullable=True,
        )
        prf_status = payload.get("prf_status")
        if prf_status not in {"prepared", "submitted"}:
            errors["prf_status"] = "Must be one of prepared, submitted."
        acceptance = payload.get("pledge_acceptance_status")
        if acceptance not in {"pending", "accepted", "rejected"}:
            errors["pledge_acceptance_status"] = (
                "Must be one of pending, accepted, rejected."
            )
        pledge_status = payload.get("pledge_status")
        if pledge_status not in {"pending", "created"}:
            errors["pledge_status"] = (
                "Must be one of pending, created; invocation and unpledge belong to 011I."
            )
        share_count = payload.get("pledged_share_count")
        if share_count is not None and (
            isinstance(share_count, bool) or not isinstance(share_count, int)
            or share_count < 1
        ):
            errors["pledged_share_count"] = "Must be a positive integer or null."
        if errors:
            raise ValidationError(errors)
        return cls(
            pledgor_member_id=pledgor_member_id,
            pledgee_entity_name=entity,
            pledgor_bo_account=pledgor_account,
            pledgee_bo_account=pledgee_account,
            pledgor_dp_name=pledgor_dp,
            pledgee_dp_name=pledgee_dp,
            prf_status=prf_status,
            pledge_sequence_number=psn,
            pledge_acceptance_status=acceptance,
            pledged_share_count=share_count,
            agreement_number=agreement,
            pledge_status=pledge_status,
            evidence_document_id=evidence_document_id,
        )

    def as_values(self):
        return asdict(self)
def _bounded_text(value, field, maximum, errors, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value.strip():
        errors[field] = "Must be non-empty text." if not nullable else "Must be non-empty text or null."
        return None if nullable else ""
    value = value.strip()
    if len(value) > maximum:
        errors[field] = f"Must be at most {maximum} characters."
    return value
def _bo_account(value, field, errors, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str) or len(value) != 16 or not value.isdigit():
        errors[field] = "Must be exactly 16 digits." if not nullable else "Must be exactly 16 digits or null."
        return None if nullable else ""
    return value
@dataclass(frozen=True)
class CDSLBOAccountRevealRequest:
    reason: str

    FIELDS = {"reason"}

    @classmethod
    def parse(cls, payload):
        _exact_fields(payload, cls.FIELDS)
        errors = {}
        reason = _bounded_text(payload.get("reason"), "reason", 500, errors)
        if errors:
            raise ValidationError(errors)
        return cls(reason=reason)
