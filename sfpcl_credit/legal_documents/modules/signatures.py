"""Legal-document signature capture and mismatch resolution owner."""

import uuid
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents.models import SignatureRecord
from sfpcl_credit.legal_documents.modules import document_authority, document_checklist
from sfpcl_credit.workflows.events import record_workflow_event


RECORD_PERMISSION = "documents.signature.record"
RESOLVE_PERMISSION = "documents.signature.resolve_mismatch"
CAPTURE_FIELDS = {
    "signer_party_type",
    "signer_party_id",
    "signer_name_snapshot",
    "signature_method",
    "signature_status",
    "signed_at",
    "signature_mismatch_flag",
}
RESOLUTION_FIELDS = {
    "mismatch_resolution_type",
    "mismatch_resolution_document_id",
    "remarks",
}


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


AccessDenied = document_authority.AccessDenied
NotFound = document_authority.NotFound
ProvenanceConflict = document_authority.ProvenanceConflict


class InvalidState(Exception):
    pass


class EvidenceConflict(Exception):
    pass


class ProjectionConflict(Exception):
    pass


def record(*, actor, loan_document_id, payload, metadata):
    document_authority.require_mutation_actor(actor=actor, permission=RECORD_PERMISSION)
    if "compliance_team_member" not in actor.role_codes():
        raise AccessDenied
    cleaned = _validate_capture(payload)
    with transaction.atomic():
        loan_document = document_authority.resolve_current_stage4_target(
            actor=actor,
            permission=RECORD_PERMISSION,
            loan_document_id=loan_document_id,
            for_update=True,
        )
        record = (
            SignatureRecord.objects.select_for_update()
            .filter(
                loan_document=loan_document,
                signer_party_type=cleaned["signer_party_type"],
                signer_party_id=cleaned["signer_party_id"],
            )
            .first()
        )
        old = _snapshot(record) if record else {}
        new = _snapshot_values(cleaned)
        old_capture = {field: old.get(field) for field in CAPTURE_FIELDS}
        new_capture = {field: new.get(field) for field in CAPTURE_FIELDS}
        if record is not None and old_capture == new_capture:
            return _serialize(record)
        if record is not None and record.mismatch_resolution_type:
            raise InvalidState(
                "A resolved signature cannot be changed through the capture action."
            )

        verification_values = (
            {"verified_by_user": actor, "verified_at": timezone.now()}
            if cleaned["signature_status"] in {"signed", "mismatch"}
            else {"verified_by_user": None, "verified_at": None}
        )
        values = {
            **cleaned,
            **verification_values,
            "mismatch_resolution_type": None,
            "mismatch_resolution_document": None,
            "mismatch_resolution_remarks": None,
            "updated_at": timezone.now(),
        }
        if record is None:
            record = SignatureRecord.objects.create(
                loan_document=loan_document, **values
            )
            action = "documents.signature.created"
        else:
            for field, value in values.items():
                setattr(record, field, value)
            record.save(update_fields=list(values))
            action = "documents.signature.changed"
        _project_signature_fact(actor, loan_document, metadata)
        new = _snapshot(record)
        _record_evidence(actor, loan_document, record, action, old, new, metadata)
        return _serialize(record)


def resolve_mismatch(*, actor, signature_record_id, payload, metadata):
    document_authority.require_mutation_actor(actor=actor, permission=RESOLVE_PERMISSION)
    if "company_secretary" not in actor.role_codes():
        raise AccessDenied
    cleaned = _validate_resolution(payload)
    with transaction.atomic():
        signature_record = (
            SignatureRecord.objects.select_for_update()
            .select_related("loan_document__loan_application", "mismatch_resolution_document")
            .filter(pk=signature_record_id)
            .first()
        )
        if signature_record is None:
            raise NotFound
        loan_document = document_authority.resolve_current_stage4_target(
            actor=actor,
            permission=RESOLVE_PERMISSION,
            loan_document_id=signature_record.loan_document_id,
            for_update=True,
        )
        evidence = _resolve_evidence(
            application_id=loan_document.loan_application_id,
            resolution_type=cleaned["mismatch_resolution_type"],
            document_id=cleaned["mismatch_resolution_document_id"],
        )
        requested = {
            "mismatch_resolution_type": cleaned["mismatch_resolution_type"],
            "mismatch_resolution_document_id": str(evidence.document_id),
            "remarks": cleaned["remarks"],
        }
        current = {
            "mismatch_resolution_type": signature_record.mismatch_resolution_type,
            "mismatch_resolution_document_id": (
                str(signature_record.mismatch_resolution_document_id)
                if signature_record.mismatch_resolution_document_id
                else None
            ),
            "remarks": signature_record.mismatch_resolution_remarks,
        }
        if signature_record.mismatch_resolution_type:
            if current == requested:
                return _serialize(signature_record)
            raise InvalidState("A resolved mismatch cannot be replaced through this action.")
        if (
            signature_record.signature_status != "mismatch"
            or not signature_record.signature_mismatch_flag
        ):
            raise InvalidState("Only an unresolved mismatch signature can be resolved.")

        old = _snapshot(signature_record)
        signature_record.mismatch_resolution_type = cleaned["mismatch_resolution_type"]
        signature_record.mismatch_resolution_document = evidence
        signature_record.mismatch_resolution_remarks = cleaned["remarks"]
        signature_record.verified_by_user = actor
        signature_record.verified_at = timezone.now()
        signature_record.updated_at = timezone.now()
        signature_record.save(
            update_fields=[
                "mismatch_resolution_type",
                "mismatch_resolution_document",
                "mismatch_resolution_remarks",
                "verified_by_user",
                "verified_at",
                "updated_at",
            ]
        )
        _project_signature_fact(actor, loan_document, metadata)
        new = _snapshot(signature_record)
        _record_evidence(
            actor,
            loan_document,
            signature_record,
            "documents.signature.mismatch_resolved",
            old,
            new,
            metadata,
            workflow_state="resolved",
        )
        return _serialize(signature_record)


def _validate_capture(payload):
    _exact_fields(payload, CAPTURE_FIELDS)
    errors = {}
    party_type = payload.get("signer_party_type")
    method = payload.get("signature_method")
    status = payload.get("signature_status")
    mismatch = payload.get("signature_mismatch_flag")
    if party_type not in SignatureRecord.PARTY_TYPES:
        errors["signer_party_type"] = "Must be one of borrower, nominee, witness, user."
    if method not in SignatureRecord.METHODS:
        errors["signature_method"] = "Must be one of wet_ink, digital, scanned."
    if status not in SignatureRecord.STATUSES:
        errors["signature_status"] = "Must be one of pending, signed, mismatch."
    if not isinstance(mismatch, bool):
        errors["signature_mismatch_flag"] = "Must be a boolean."
    signer_name = _required_text(
        "signer_name_snapshot", payload.get("signer_name_snapshot"), 255, errors
    )
    signer_id = _uuid_or_none("signer_party_id", payload.get("signer_party_id"), errors)
    signed_at = _datetime_or_none("signed_at", payload.get("signed_at"), errors)
    if status == "pending" and (signed_at is not None or mismatch is not False):
        errors["signature_status"] = "Pending signature cannot carry signed or mismatch facts."
    if status == "signed" and (signed_at is None or mismatch is not False):
        errors["signature_status"] = "Signed signature requires signed_at and no mismatch."
    if status == "mismatch" and mismatch is not True:
        errors["signature_mismatch_flag"] = "Mismatch status requires a true mismatch flag."
    if errors:
        raise ValidationError(errors)
    return {
        "signer_party_type": party_type,
        "signer_party_id": signer_id,
        "signer_name_snapshot": signer_name,
        "signature_method": method,
        "signature_status": status,
        "signed_at": signed_at,
        "signature_mismatch_flag": mismatch,
    }


def _validate_resolution(payload):
    _exact_fields(payload, RESOLUTION_FIELDS)
    errors = {}
    resolution_type = payload.get("mismatch_resolution_type")
    if resolution_type not in SignatureRecord.RESOLUTION_TYPES:
        errors["mismatch_resolution_type"] = (
            "Must be one of bank_verification_letter, borrower_declaration."
        )
    document_id = _uuid_or_none(
        "mismatch_resolution_document_id",
        payload.get("mismatch_resolution_document_id"),
        errors,
    )
    if document_id is None and "mismatch_resolution_document_id" not in errors:
        errors["mismatch_resolution_document_id"] = "A document id is required."
    remarks = _nullable_text("remarks", payload.get("remarks"), 4000, errors)
    if errors:
        raise ValidationError(errors)
    return {
        "mismatch_resolution_type": resolution_type,
        "mismatch_resolution_document_id": document_id,
        "remarks": remarks,
    }


def _resolve_evidence(*, application_id, resolution_type, document_id):
    from sfpcl_credit.legal_documents.models import LoanDocument

    required_type = (
        "bank_verification_letter"
        if resolution_type == "bank_verification_letter"
        else "borrower_declaration"
    )
    evidence_loan_document = (
        LoanDocument.objects.select_related("document")
        .filter(
            loan_application_id=application_id,
            document_id=document_id,
            document_type=required_type,
        )
        .first()
    )
    if (
        evidence_loan_document is None
        or evidence_loan_document.renderer_validation_status
        != LoanDocument.RENDERER_CURRENT_VALIDATED
    ):
        raise EvidenceConflict(
            "Resolution evidence was not found with retained legal provenance for this application."
        )
    if resolution_type == "borrower_declaration":
        stamp = getattr(evidence_loan_document, "stamp_duty_record", None)
        if stamp is None or stamp.status != "adequate":
            raise EvidenceConflict(
                "Borrower declaration resolution requires adequate non-judicial stamp evidence."
            )
    try:
        return document_services.resolve_generated_legal_evidence_reference(
            document_id=evidence_loan_document.document_id,
            expected_checksum_sha256=(
                evidence_loan_document.renderer_validated_checksum_sha256
            ),
        )
    except ValidationError as exc:
        raise EvidenceConflict(
            "Resolution evidence was not found with retained legal provenance for this application."
        ) from exc


def _project_signature_fact(actor, loan_document, metadata):
    try:
        document_checklist.project_signature_mismatch(
            application=loan_document.loan_application,
            legal_signature_rows=SignatureRecord.objects.filter(
                loan_document__loan_application=loan_document.loan_application
            ).values(
                "signature_status",
                "verified_by_user_id",
                "verified_at",
                "mismatch_resolution_type",
            ),
            actor=actor,
            request_meta={
                "request_id": metadata.request_id,
                "ip_address": metadata.ip_address,
                "user_agent": metadata.user_agent,
            },
        )
    except document_checklist.ChecklistApplicabilityConflict as exc:
        raise ProjectionConflict(str(exc)) from exc


def _record_evidence(
    actor, loan_document, record, action, old, new, metadata, workflow_state=None
):
    context = {
        "loan_document_id": str(loan_document.pk),
        "loan_application_id": str(loan_document.loan_application_id),
        "signature_record_id": str(record.pk),
        "actor_role_codes": actor.role_codes(),
        "actor_team_codes": actor.team_codes(),
        "request_id": metadata.request_id,
        **new,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="signature_record",
        entity_id=record.pk,
        old_value_json=old,
        new_value_json=context,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type="signature_record",
        versioned_entity_id=record.pk,
        version_number=str(
            VersionHistory.objects.filter(
                versioned_entity_type="signature_record",
                versioned_entity_id=record.pk,
            ).count()
            + 1
        ),
        change_summary=action,
        author_user=actor,
        old_value_json=old,
        new_value_json=context,
        effective_from=timezone.localdate(),
    )
    record_workflow_event(
        actor=actor,
        workflow_name="loan_document_signature",
        entity_type="loan_document",
        entity_id=loan_document.pk,
        from_state=old.get("signature_status"),
        to_state=workflow_state or new["signature_status"],
        trigger_reason=action,
        action_code=action,
        metadata=context,
    )


def _snapshot(record):
    return {
        "signer_party_type": record.signer_party_type,
        "signer_party_id": str(record.signer_party_id) if record.signer_party_id else None,
        "signer_name_snapshot": record.signer_name_snapshot,
        "signature_method": record.signature_method,
        "signature_status": record.signature_status,
        "signed_at": _iso(record.signed_at),
        "signature_mismatch_flag": record.signature_mismatch_flag,
        "mismatch_resolution_type": record.mismatch_resolution_type,
        "mismatch_resolution_document_id": (
            str(record.mismatch_resolution_document_id)
            if record.mismatch_resolution_document_id
            else None
        ),
        "mismatch_resolution_document_name": (
            record.mismatch_resolution_document.file_name
            if record.mismatch_resolution_document_id
            else None
        ),
        "remarks": record.mismatch_resolution_remarks,
    }


def _snapshot_values(values):
    return {
        "signer_party_type": values["signer_party_type"],
        "signer_party_id": str(values["signer_party_id"]) if values["signer_party_id"] else None,
        "signer_name_snapshot": values["signer_name_snapshot"],
        "signature_method": values["signature_method"],
        "signature_status": values["signature_status"],
        "signed_at": _iso(values["signed_at"]),
        "signature_mismatch_flag": values["signature_mismatch_flag"],
        "mismatch_resolution_type": None,
        "mismatch_resolution_document_id": None,
        "mismatch_resolution_document_name": None,
        "remarks": None,
    }


def _serialize(record):
    return {
        "signature_record_id": str(record.pk),
        "loan_document_id": str(record.loan_document_id),
        **_snapshot(record),
    }


def _exact_fields(payload, allowed):
    if not isinstance(payload, dict):
        raise ValidationError({"body": "A JSON object is required."})
    unknown = set(payload) - allowed
    missing = allowed - set(payload)
    if unknown or missing:
        raise ValidationError(
            {
                **{field: "Unknown field." for field in sorted(unknown)},
                **{field: "This field is required." for field in sorted(missing)},
            }
        )


def _required_text(field, value, maximum, errors):
    if not isinstance(value, str) or not value.strip():
        errors[field] = "A non-empty string is required."
        return ""
    value = value.strip()
    if len(value) > maximum:
        errors[field] = f"Must be at most {maximum} characters."
    return value


def _nullable_text(field, value, maximum, errors):
    if value is None:
        return None
    if not isinstance(value, str):
        errors[field] = "Must be a string or null."
        return None
    value = value.strip()
    if len(value) > maximum:
        errors[field] = f"Must be at most {maximum} characters."
    return value or None


def _uuid_or_none(field, value, errors):
    if value is None:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        errors[field] = "Must be a valid UUID or null."
        return None


def _datetime_or_none(field, value, errors):
    if value is None:
        return None
    if not isinstance(value, str):
        errors[field] = "Must be an ISO-8601 datetime or null."
        return None
    parsed = parse_datetime(value)
    if parsed is None or not timezone.is_aware(parsed):
        errors[field] = "Must be an ISO-8601 datetime with timezone or null."
        return None
    return parsed


def _iso(value):
    return value.isoformat().replace("+00:00", "Z") if value else None


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
