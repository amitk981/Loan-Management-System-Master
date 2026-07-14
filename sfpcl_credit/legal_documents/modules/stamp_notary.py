from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents.models import (
    NotarisationRecord,
    StampDutyRecord,
)
from sfpcl_credit.legal_documents.modules import document_authority, document_checklist
from sfpcl_credit.legal_documents.request_contracts import (
    NotarisationRecordRequest,
    StampDutyRecordRequest,
)
from sfpcl_credit.workflows.events import record_workflow_event


STAMP_PERMISSION = "documents.stamp.record"
NOTARY_PERMISSION = "documents.notary.record"


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
    require_stamp_actor(actor)
    cleaned = _validate_stamp(payload, actor)
    return _record(
        actor=actor,
        loan_document_id=loan_document_id,
        cleaned=cleaned,
        metadata=metadata,
        kind="stamp",
    )


def record_notary(*, actor, loan_document_id, payload, metadata):
    require_notary_actor(actor)
    cleaned = _validate_notary(payload, actor)
    return _record(
        actor=actor,
        loan_document_id=loan_document_id,
        cleaned=cleaned,
        metadata=metadata,
        kind="notary",
    )


def require_stamp_actor(actor):
    document_authority.require_mutation_actor(actor=actor, permission=STAMP_PERMISSION)


def require_notary_actor(actor):
    document_authority.require_mutation_actor(actor=actor, permission=NOTARY_PERMISSION)


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
        record = (
            model.objects.select_for_update()
            .filter(loan_document=loan_document)
            .first()
        )
        old = _snapshot(record, kind) if record else {}
        new = _snapshot_values(cleaned, kind)
        if _business_facts(old) == new:
            return _serialize(record, kind)
        if record is not None and record.legacy_maker_attribution:
            raise ValidationError(
                {
                    "status": (
                        "Legacy evidence without truthful maker attribution cannot be changed."
                    )
                }
            )

        verification_statuses = (
            {"adequate", "insufficient"}
            if kind == "stamp"
            else {"completed", "rejected"}
        )
        is_verification = cleaned["status"] in verification_statuses
        if is_verification:
            if record is None or record.prepared_by_user_id is None:
                raise ValidationError(
                    {
                        "status": "A retained Compliance preparation is required before verification."
                    }
                )
            if record.prepared_by_user_id == actor.pk:
                raise ValidationError(
                    {"status": "The preparer and verifier must be different users."}
                )
        elif record is not None and record.status in verification_statuses:
            raise ValidationError(
                {"status": "Compliance cannot replace or erase a verification outcome."}
            )

        _project_checklist_status(loan_document, kind, cleaned["status"])
        verified_by = actor if is_verification else None
        values = {
            **cleaned,
            "verified_by_user": verified_by,
            "updated_at": timezone.now(),
        }
        if record is None:
            record = model.objects.create(
                loan_document=loan_document,
                prepared_by_user=actor,
                **values,
            )
            action = f"documents.{kind}.created"
        else:
            if not is_verification:
                values["prepared_by_user"] = actor
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
    request = (
        payload
        if isinstance(payload, StampDutyRecordRequest)
        else StampDutyRecordRequest.parse(payload)
    )
    cleaned = request.as_values()
    status = cleaned["status"]
    errors = {}
    executed = cleaned["executed_date"]
    purchased = cleaned["stamp_purchase_date"]
    if purchased and executed and purchased > executed:
        errors["stamp_purchase_date"] = "Must be on or before the executed date."
    if status == "adequate":
        if executed is None:
            errors["executed_date"] = "Adequate stamp duty requires an executed date."
    if status in {"adequate", "insufficient"}:
        try:
            document_authority.require_company_secretary(actor)
        except document_authority.RoleAuthorityDenied:
            errors["status"] = (
                "Only Company Secretary authority may record a verification outcome."
            )
    else:
        try:
            document_authority.require_compliance_preparer(actor)
        except document_authority.RoleAuthorityDenied:
            errors["status"] = "Only Compliance authority may prepare pending facts."
    if errors:
        raise ValidationError(errors)
    return cleaned


def _validate_notary(payload, actor):
    request = (
        payload
        if isinstance(payload, NotarisationRecordRequest)
        else NotarisationRecordRequest.parse(payload)
    )
    cleaned = request.as_values()
    status = cleaned["status"]
    errors = {}
    if status == "completed":
        for field in (
            "notary_name",
            "notary_registration_number",
            "notarised_date",
            "evidence_document_id",
        ):
            if not cleaned[field]:
                errors[field] = "Completed notarisation requires this field."
    if status in {"completed", "rejected"}:
        try:
            document_authority.require_company_secretary(actor)
        except document_authority.RoleAuthorityDenied:
            errors["status"] = (
                "Only Company Secretary authority may record a verification outcome."
            )
    else:
        try:
            document_authority.require_compliance_preparer(actor)
        except document_authority.RoleAuthorityDenied:
            errors["status"] = "Only Compliance authority may prepare pending facts."
    if errors:
        raise ValidationError(errors)
    return cleaned


def _resolve_notary_evidence(cleaned, application_id, actor_role_codes):
    document_id = cleaned.pop("evidence_document_id")
    if document_id is None:
        return {**cleaned, "evidence_document": None}
    try:
        provenance = document_services.resolve_immutable_upload_provenance(
            document_id=document_id
        )
    except ValidationError as exc:
        raise ValidationError(
            {"evidence_document_id": "Document file was not found or is inaccessible."}
        ) from exc
    legal_reference_allowed = (
        bool(set(actor_role_codes) & {"compliance_team_member", "company_secretary"})
        and provenance.document_category == "legal"
        and provenance.related_entity_type == "application"
        and provenance.related_entity_id == application_id
    )
    if not legal_reference_allowed:
        raise ValidationError(
            {"evidence_document_id": "Document file was not found or is inaccessible."}
        )
    return {**cleaned, "evidence_document": provenance.document}


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
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type=f"{kind}_record",
        entity_id=record.pk,
        old_value_json=old,
        new_value_json=context,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type=f"{kind}_record",
        versioned_entity_id=record.pk,
        version_number=str(
            VersionHistory.objects.filter(
                versioned_entity_type=f"{kind}_record", versioned_entity_id=record.pk
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
        workflow_name=f"loan_document_{'stamping' if kind == 'stamp' else 'notarisation'}",
        entity_type="loan_document",
        entity_id=loan_document.pk,
        from_state=old.get("status"),
        to_state=new["status"],
        trigger_reason=action,
        action_code=action,
        metadata=context,
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
            "prepared_by_user_id": str(record.prepared_by_user_id)
            if record.prepared_by_user_id
            else None,
            "verified_by_user_id": str(record.verified_by_user_id)
            if record.verified_by_user_id
            else None,
        }
    return {
        "notary_name": record.notary_name,
        "notary_registration_number": record.notary_registration_number,
        "notarised_date": _iso(record.notarised_date),
        "status": record.status,
        "evidence_document_id": str(record.evidence_document_id)
        if record.evidence_document_id
        else None,
        "evidence_document_name": record.evidence_document.file_name
        if record.evidence_document_id
        else None,
        "remarks": record.remarks,
        "prepared_by_user_id": str(record.prepared_by_user_id)
        if record.prepared_by_user_id
        else None,
        "verified_by_user_id": str(record.verified_by_user_id)
        if record.verified_by_user_id
        else None,
    }


def _snapshot_values(values, kind):
    if kind == "stamp":
        return {
            **values,
            "stamp_paper_amount": f"{values['stamp_paper_amount']:.2f}",
            "stamp_purchase_date": _iso(values["stamp_purchase_date"]),
            "executed_date": _iso(values["executed_date"]),
        }
    return {
        "notary_name": values["notary_name"],
        "notary_registration_number": values["notary_registration_number"],
        "notarised_date": _iso(values["notarised_date"]),
        "status": values["status"],
        "evidence_document_id": str(values["evidence_document"].pk)
        if values.get("evidence_document")
        else None,
        "evidence_document_name": values["evidence_document"].file_name
        if values.get("evidence_document")
        else None,
        "remarks": values["remarks"],
    }


def _business_facts(snapshot):
    return {
        key: value
        for key, value in snapshot.items()
        if key not in {"prepared_by_user_id", "verified_by_user_id"}
    }


def _serialize(record, kind):
    return {
        f"{kind}_record_id": str(record.pk),
        "loan_document_id": str(record.loan_document_id),
        **_snapshot(record, kind),
    }


def _iso(value):
    return value.isoformat() if value else None


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
