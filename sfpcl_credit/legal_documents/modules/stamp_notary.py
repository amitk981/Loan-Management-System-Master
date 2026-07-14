import re
import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents.models import (
    LoanDocument,
    NotarisationRecord,
    StampDutyRecord,
)
from sfpcl_credit.legal_documents.modules import document_authority, document_checklist
from sfpcl_credit.workflows.events import record_workflow_event


STAMP_PERMISSION = "documents.stamp.record"
NOTARY_PERMISSION = "documents.notary.record"
STAMP_FIELDS = {
    "stamp_paper_amount", "stamp_type", "stamp_number", "stamp_purchase_date",
    "executed_date", "status", "remarks",
}
NOTARY_FIELDS = {
    "notary_name", "notary_registration_number", "notarised_date", "status",
    "evidence_document_id", "remarks",
}
_MONEY = re.compile(r"^(0|[1-9][0-9]{0,15})\.[0-9]{2}$")


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


AccessDenied = document_authority.AccessDenied
NotFound = document_authority.NotFound
ProvenanceConflict = document_authority.ProvenanceConflict


class ProjectionConflict(Exception):
    pass


def record_stamp(*, actor, loan_document_id, payload, metadata):
    document_authority.require_mutation_actor(actor=actor, permission=STAMP_PERMISSION)
    cleaned = _validate_stamp(payload, actor)
    return _record(
        actor=actor, loan_document_id=loan_document_id, cleaned=cleaned,
        metadata=metadata, kind="stamp",
    )


def record_notary(*, actor, loan_document_id, payload, metadata):
    document_authority.require_mutation_actor(actor=actor, permission=NOTARY_PERMISSION)
    cleaned = _validate_notary(payload, actor)
    return _record(
        actor=actor, loan_document_id=loan_document_id, cleaned=cleaned,
        metadata=metadata, kind="notary",
    )


def _record(*, actor, loan_document_id, cleaned, metadata, kind):
    permission = STAMP_PERMISSION if kind == "stamp" else NOTARY_PERMISSION
    with transaction.atomic():
        loan_document = document_authority.resolve_current_stage4_target(
            actor=actor,
            permission=permission,
            loan_document_id=loan_document_id,
            for_update=True,
        )

        if kind == "notary":
            cleaned = _resolve_notary_evidence(
                cleaned, loan_document.loan_application_id, actor.role_codes()
            )

        model = StampDutyRecord if kind == "stamp" else NotarisationRecord
        record = model.objects.select_for_update().filter(loan_document=loan_document).first()
        old = _snapshot(record, kind) if record else {}
        new = _snapshot_values(cleaned, kind)
        if old == new:
            return _serialize(record, kind)

        _project_checklist_status(loan_document, kind, cleaned["status"])
        verified_by = actor if cleaned["status"] in {"adequate", "completed"} else None
        values = {**cleaned, "verified_by_user": verified_by, "updated_at": timezone.now()}
        if record is None:
            record = model.objects.create(loan_document=loan_document, **values)
            action = f"documents.{kind}.created"
        else:
            for field, value in values.items():
                setattr(record, field, value)
            record.save(update_fields=[*values.keys()])
            action = f"documents.{kind}.changed"

        projection_field = "stamp_status" if kind == "stamp" else "notarisation_status"
        setattr(loan_document, projection_field, cleaned["status"])
        loan_document.save(update_fields=[projection_field])
        new = _snapshot(record, kind)
        _record_evidence(actor, loan_document, record, kind, action, old, new, metadata)
        return _serialize(record, kind)


def _validate_stamp(payload, actor):
    _exact_fields(payload, STAMP_FIELDS)
    raw_amount = payload.get("stamp_paper_amount")
    if not isinstance(raw_amount, str) or not _MONEY.fullmatch(raw_amount):
        raise ValidationError({"stamp_paper_amount": "Must be a non-negative two-decimal string."})
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation as exc:
        raise ValidationError({"stamp_paper_amount": "Must be a non-negative two-decimal string."}) from exc
    stamp_type = payload.get("stamp_type")
    status = payload.get("status")
    errors = {}
    if stamp_type not in StampDutyRecord.TYPES:
        errors["stamp_type"] = "Must be one of physical, electronic."
    if status not in StampDutyRecord.STATUSES:
        errors["status"] = "Must be one of pending, adequate, insufficient."
    executed = _date("executed_date", payload.get("executed_date"))
    purchased = _date("stamp_purchase_date", payload.get("stamp_purchase_date"))
    if purchased and executed and purchased > executed:
        errors["stamp_purchase_date"] = "Must be on or before the executed date."
    if status == "adequate":
        if executed is None:
            errors["executed_date"] = "Adequate stamp duty requires an executed date."
        if "company_secretary" not in actor.role_codes():
            errors["status"] = "Only Company Secretary authority may record adequate status."
    if errors:
        raise ValidationError(errors)
    return {
        "stamp_paper_amount": amount,
        "stamp_type": stamp_type,
        "stamp_number": _nullable_text("stamp_number", payload.get("stamp_number"), 120),
        "stamp_purchase_date": purchased,
        "executed_date": executed,
        "status": status,
        "remarks": _nullable_text("remarks", payload.get("remarks"), 4000),
    }


def _validate_notary(payload, actor):
    _exact_fields(payload, NOTARY_FIELDS)
    status = payload.get("status")
    if status not in NotarisationRecord.STATUSES:
        raise ValidationError({"status": "Must be one of pending, completed, rejected."})
    cleaned = {
        "notary_name": _nullable_text("notary_name", payload.get("notary_name"), 255),
        "notary_registration_number": _nullable_text("notary_registration_number", payload.get("notary_registration_number"), 120),
        "notarised_date": _date("notarised_date", payload.get("notarised_date")),
        "status": status,
        "evidence_document_id": payload.get("evidence_document_id"),
        "remarks": _nullable_text("remarks", payload.get("remarks"), 4000),
    }
    errors = {}
    if status == "completed":
        for field in ("notary_name", "notary_registration_number", "notarised_date", "evidence_document_id"):
            if not cleaned[field]:
                errors[field] = "Completed notarisation requires this field."
        if "company_secretary" not in actor.role_codes():
            errors["status"] = "Only Company Secretary authority may record completed status."
    if errors:
        raise ValidationError(errors)
    if cleaned["evidence_document_id"]:
        try:
            cleaned["evidence_document_id"] = uuid.UUID(str(cleaned["evidence_document_id"]))
        except (ValueError, TypeError, AttributeError):
            raise ValidationError({"evidence_document_id": "Document file was not found or is inaccessible."})
    return cleaned


def _resolve_notary_evidence(cleaned, application_id, actor_role_codes):
    document_id = cleaned.pop("evidence_document_id")
    if document_id is None:
        return {**cleaned, "evidence_document": None}
    document = document_services.resolve_legal_application_evidence_reference(
        actor_role_codes=actor_role_codes,
        application_id=application_id,
        document_id=document_id,
    )
    return {**cleaned, "evidence_document": document}


def _project_checklist_status(loan_document, kind, status):
    try:
        if kind == "stamp":
            document_checklist.project_lifecycle_status(
                loan_document=loan_document, stamp_status=status
            )
        else:
            document_checklist.project_lifecycle_status(
                loan_document=loan_document, notarisation_status=status
            )
    except document_checklist.ChecklistLifecycleProjectionConflict as exc:
        raise ProjectionConflict(str(exc)) from exc


def _record_evidence(actor, loan_document, record, kind, action, old, new, metadata):
    context = {
        "loan_document_id": str(loan_document.pk),
        "loan_application_id": str(loan_document.loan_application_id),
        "actor_role_codes": actor.role_codes(),
        "actor_team_codes": actor.team_codes(),
        "request_id": metadata.request_id,
        **new,
    }
    AuditLog.objects.create(
        actor_user=actor, actor_type="user", action=action,
        entity_type=f"{kind}_record", entity_id=record.pk,
        old_value_json=old, new_value_json=context,
        ip_address=metadata.ip_address, user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type=f"{kind}_record", versioned_entity_id=record.pk,
        version_number=str(VersionHistory.objects.filter(
            versioned_entity_type=f"{kind}_record", versioned_entity_id=record.pk
        ).count() + 1),
        change_summary=action, author_user=actor, old_value_json=old,
        new_value_json=context, effective_from=timezone.localdate(),
    )
    record_workflow_event(
        actor=actor, workflow_name=f"loan_document_{'stamping' if kind == 'stamp' else 'notarisation'}",
        entity_type="loan_document", entity_id=loan_document.pk,
        from_state=old.get("status"), to_state=new["status"],
        trigger_reason=action, action_code=action, metadata=context,
    )


def _snapshot(record, kind):
    if record is None:
        return {}
    if kind == "stamp":
        return {
            "stamp_paper_amount": f"{record.stamp_paper_amount:.2f}",
            "stamp_type": record.stamp_type,
            "stamp_number": record.stamp_number,
            "stamp_purchase_date": _iso(record.stamp_purchase_date),
            "executed_date": _iso(record.executed_date),
            "status": record.status,
            "remarks": record.remarks,
        }
    return {
        "notary_name": record.notary_name,
        "notary_registration_number": record.notary_registration_number,
        "notarised_date": _iso(record.notarised_date),
        "status": record.status,
        "evidence_document_id": str(record.evidence_document_id) if record.evidence_document_id else None,
        "evidence_document_name": record.evidence_document.file_name if record.evidence_document_id else None,
        "remarks": record.remarks,
    }


def _snapshot_values(values, kind):
    if kind == "stamp":
        return {**values, "stamp_paper_amount": f"{values['stamp_paper_amount']:.2f}",
                "stamp_purchase_date": _iso(values["stamp_purchase_date"]), "executed_date": _iso(values["executed_date"])}
    return {
        "notary_name": values["notary_name"], "notary_registration_number": values["notary_registration_number"],
        "notarised_date": _iso(values["notarised_date"]), "status": values["status"],
        "evidence_document_id": str(values["evidence_document"].pk) if values.get("evidence_document") else None,
        "evidence_document_name": values["evidence_document"].file_name if values.get("evidence_document") else None,
        "remarks": values["remarks"],
    }


def _serialize(record, kind):
    return {f"{kind}_record_id": str(record.pk), "loan_document_id": str(record.loan_document_id), **_snapshot(record, kind)}


def _exact_fields(payload, allowed):
    if not isinstance(payload, dict):
        raise ValidationError({"body": "A JSON object is required."})
    unknown = set(payload) - allowed
    if unknown:
        raise ValidationError({field: "Unknown field." for field in sorted(unknown)})
    missing = allowed - set(payload)
    if missing:
        raise ValidationError({field: "This field is required." for field in sorted(missing)})


def _date(field, value):
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
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


def _iso(value):
    return value.isoformat() if value else None


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
