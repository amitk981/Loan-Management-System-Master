"""Legal-document signature capture and mismatch resolution owner."""

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from sfpcl_credit.applications.modules import signature_identity_facts
from sfpcl_credit.applications.models import LoanApplication, Witness
from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.legal_documents.models import LoanDocument, SignatureRecord
from sfpcl_credit.legal_documents.modules import document_authority, document_checklist
from sfpcl_credit.legal_documents.request_contracts import (
    SignatureMismatchResolutionRequest,
    SignatureRecordRequest,
)
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


class SignatureMismatchUnresolved(InvalidState):
    pass


class EvidenceConflict(Exception):
    pass


class ProjectionConflict(Exception):
    pass


def all_current_signatures_resolved(*, application_id):
    """Decide current signer identity, provenance, and mismatch evidence."""
    application = LoanApplication.objects.select_related("nominee").filter(pk=application_id).first()
    if application is None:
        return False
    latest = {}
    for document_type, document_id in LoanDocument.objects.filter(
        loan_application_id=application_id
    ).order_by("document_type", "-created_at", "-loan_document_id").values_list(
        "document_type", "loan_document_id"
    ):
        latest.setdefault(document_type, document_id)
    witnesses = set(Witness.objects.filter(
        loan_application_id=application_id,
        verification_status="verified",
        shareholder_verified_flag=True,
    ).values_list("witness_id", flat=True))
    rows = list(SignatureRecord.objects.select_for_update().select_related(
        "loan_document", "mismatch_resolution_workflow_event"
    ).filter(loan_document__loan_application_id=application_id))
    return all(
        row.loan_document_id == latest.get(row.loan_document.document_type)
        and _expected_readiness_signer(row, application, witnesses)
        and _readiness_row_resolved(row)
        for row in rows
    )


def _expected_readiness_signer(row, application, witnesses):
    allowed_parties = {
        "power_of_attorney": {"borrower", "nominee"},
        "tri_party_agreement": {"borrower", "nominee"},
        "sh4": {"borrower", "witness"},
        "term_sheet": {"borrower", "nominee", "user"},
        "loan_agreement": {"borrower", "witness"},
    }.get(row.loan_document.document_type, set())
    if row.signer_party_type not in allowed_parties:
        return False
    if row.signer_party_type == "borrower":
        return row.signer_party_id == application.member_id
    if row.signer_party_type == "nominee":
        return bool(application.nominee_id and row.signer_party_id == application.nominee_id)
    if row.signer_party_type == "witness":
        return row.signer_party_id in witnesses
    if row.signer_party_type == "user" and row.loan_document.document_type == "term_sheet":
        user = User.objects.filter(pk=row.signer_party_id).first()
        case = (
            ApprovalCase.objects.filter(loan_application_id=application.pk)
            .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
            .first()
        )
        projection = case.committee_projection_json if case else {}
        eligible_ids = {
            str(projection.get("cfo_user_id") or ""),
            *{str(value) for value in projection.get("director_user_ids", []) if value},
        }
        excluded_ids = {
            str(value.get("user_id"))
            for value in (case.excluded_approvers_json if case else [])
            if isinstance(value, dict) and value.get("user_id")
        }
        return bool(
            user
            and user.can_authenticate()
            and str(row.signer_party_id) in eligible_ids - excluded_ids
        )
    return False


def _readiness_row_resolved(row):
    if row.signature_status == "signed":
        return bool(not row.signature_mismatch_flag and row.signed_at and row.captured_by_user_id and row.mismatch_resolution_type is None)
    if row.signature_status != "mismatch" or not row.signature_mismatch_flag:
        return False
    required_type = "bank_verification_letter" if row.mismatch_resolution_type == "bank_verification_letter" else "borrower_declaration"
    evidence = LoanDocument.objects.select_related("document").filter(
        loan_application_id=row.loan_document.loan_application_id,
        document_id=row.mismatch_resolution_document_id,
        document_type=required_type,
        generation_status=LoanDocument.GENERATION_GENERATED,
        renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
        renderer_validated_document_id=F("document_id"),
        renderer_validated_checksum_sha256=F("document__checksum_sha256"),
    ).first()
    audits = list(AuditLog.objects.filter(action="documents.signature.mismatch_resolved", entity_type="signature_record", entity_id=row.pk)[:2])
    histories = list(VersionHistory.objects.filter(versioned_entity_type="signature_record", versioned_entity_id=row.pk, change_summary="documents.signature.mismatch_resolved")[:2])
    workflow = row.mismatch_resolution_workflow_event
    return bool(
        row.mismatch_resolution_type and row.mismatch_resolution_document_id
        and row.mismatch_resolution_remarks and row.captured_by_user_id
        and row.verified_by_user_id and row.captured_by_user_id != row.verified_by_user_id
        and row.verified_at and evidence and len(audits) == 1 and len(histories) == 1
        and audits[0].actor_user_id == row.verified_by_user_id
        and histories[0].author_user_id == row.verified_by_user_id
        and audits[0].new_value_json == histories[0].new_value_json
        and (audits[0].new_value_json or {}).get("signature_record_id") == str(row.pk)
        and workflow and workflow.workflow_name == "loan_document_signature"
        and workflow.entity_type == "loan_document" and workflow.entity_id == row.loan_document_id
        and workflow.from_state == "mismatch" and workflow.to_state == "resolved"
        and workflow.triggered_by_user_id == row.verified_by_user_id
        and workflow.trigger_reason == "documents.signature.mismatch_resolved"
    )


def record(*, actor, loan_document_id, payload, metadata):
    require_record_actor(actor)

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
        if record is not None and document_authority.has_terminal_execution_consumption(
            loan_document
        ):
            raise InvalidState(
                "Signature evidence consumed by terminal legal execution cannot be changed."
            )
        if record is not None and record.legacy_maker_attribution:
            raise ValidationError(
                {
                    "signature_status": (
                        "Legacy signature evidence without a retained capture maker cannot be changed."
                    )
                }
            )
        if (
            record is not None
            and loan_document.document_type == "tri_party_agreement"
            and loan_document.verification_status == "verified"
        ):
            raise InvalidState(
                "A signature consumed by verified tri-party execution cannot be changed."
            )
        if record is not None:
            if cleaned["signer_name_snapshot"] != record.signer_name_snapshot:
                raise ValidationError(
                    {"signer_name_snapshot": "Must match the frozen signer name."}
                )
            cleaned = {
                **cleaned,
                "signer_party_id": record.signer_party_id,
                "signer_name_snapshot": record.signer_name_snapshot,
            }
        else:
            identity = signature_identity_facts.resolve_signer_identity(
                application=loan_document.loan_application,
                party_type=cleaned["signer_party_type"],
                party_id=cleaned["signer_party_id"],
            )
            if identity is None:
                raise ValidationError(
                    {"signer_party_id": "Signer was not found for this application."}
                )
            if cleaned["signer_name_snapshot"] != identity.name:
                raise ValidationError(
                    {"signer_name_snapshot": "Must match the canonical signer name."}
                )
            cleaned = {
                **cleaned,
                "signer_party_id": identity.party_id,
                "signer_name_snapshot": identity.name,
            }
        if (
            record is not None
            and record.signature_status == "mismatch"
            and record.signature_mismatch_flag
            and not record.mismatch_resolution_type
        ):
            raise SignatureMismatchUnresolved(
                "An unresolved signature mismatch can only be cleared through mismatch resolution."
            )
        if record is not None and record.mismatch_resolution_type:
            raise InvalidState(
                "A resolved signature cannot be changed through the capture action."
            )
        if record is not None and record.captured_by_user_id is None:
            raise ValidationError(
                {
                    "signature_status": (
                        "Legacy signature evidence without a retained capture maker cannot be changed."
                    )
                }
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
                loan_document=loan_document,
                captured_by_user=actor,
                **values,
            )
            action = "documents.signature.created"
        else:
            values["captured_by_user"] = actor
            for field, value in values.items():
                setattr(record, field, value)
            record.save(update_fields=list(values))
            action = "documents.signature.changed"
        _project_signature_fact(actor, loan_document, metadata)
        new = _snapshot(record)
        _record_evidence(actor, loan_document, record, action, old, new, metadata)
        return _serialize(record)


def require_record_actor(actor):
    document_authority.require_mutation_actor(actor=actor, permission=RECORD_PERMISSION)
    try:
        document_authority.require_compliance_preparer(actor)
    except document_authority.RoleAuthorityDenied:
        raise AccessDenied


def require_resolve_actor(actor):
    document_authority.require_mutation_actor(actor=actor, permission=RESOLVE_PERMISSION)
    try:
        document_authority.require_company_secretary(actor)
    except document_authority.RoleAuthorityDenied:
        raise AccessDenied


def resolve_mismatch(*, actor, signature_record_id, payload, metadata):
    require_resolve_actor(actor)
    cleaned = _validate_resolution(payload)
    with transaction.atomic():
        signature_record = document_authority.resolve_current_stage4_signature(
            actor=actor,
            permission=RESOLVE_PERMISSION,
            signature_record_id=signature_record_id,
            for_update=True,
        )
        loan_document = signature_record.loan_document
        if not signature_record.mismatch_resolution_type:
            if (
                signature_record.signature_status != "mismatch"
                or not signature_record.signature_mismatch_flag
            ):
                raise InvalidState("Only an unresolved mismatch signature can be resolved.")
            if signature_record.captured_by_user_id is None:
                raise ValidationError(
                    {
                        "mismatch_resolution_type": (
                            "A retained capture maker is required before mismatch resolution."
                        )
                    }
                )
            if signature_record.captured_by_user_id == actor.pk:
                raise ValidationError(
                    {
                        "mismatch_resolution_type": (
                            "The capture maker and resolver must be different users."
                        )
                    }
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
                return _resolution_action(signature_record)
            raise InvalidState("A resolved mismatch cannot be replaced through this action.")
        if signature_record.legacy_maker_attribution:
            raise ValidationError(
                {
                    "mismatch_resolution_type": (
                        "Legacy signature evidence cannot supply new resolution truth."
                    )
                }
            )

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
        workflow_event = _record_evidence(
            actor,
            loan_document,
            signature_record,
            "documents.signature.mismatch_resolved",
            old,
            new,
            metadata,
            workflow_state="resolved",
        )
        signature_record.mismatch_resolution_workflow_event = workflow_event
        signature_record.save(update_fields=["mismatch_resolution_workflow_event"])
        return _resolution_action(signature_record)


def _validate_capture(payload):
    if isinstance(payload, SignatureRecordRequest):
        return payload.as_values()
    return SignatureRecordRequest.parse(payload).as_values()


def _validate_resolution(payload):
    if isinstance(payload, SignatureMismatchResolutionRequest):
        return payload.as_values()
    return SignatureMismatchResolutionRequest.parse(payload).as_values()


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
            legal_signature_rows=selectors.signature_facts_for_application(
                application_id=loan_document.loan_application_id
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
    return record_workflow_event(
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
        "captured_by_user_id": (
            str(record.captured_by_user_id) if record.captured_by_user_id else None
        ),
        "verified_by_user_id": (
            str(record.verified_by_user_id) if record.verified_by_user_id else None
        ),
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
        "captured_by_user_id": None,
        "verified_by_user_id": None,
    }


def _serialize(record):
    return {
        "signature_record_id": str(record.pk),
        "loan_document_id": str(record.loan_document_id),
        **_snapshot(record),
    }


def _resolution_action(record):
    return {
        "entity_type": "signature_record",
        "entity_id": str(record.pk),
        "previous_status": "mismatch",
        "new_status": "resolved",
        "workflow_event_id": (
            str(record.mismatch_resolution_workflow_event_id)
            if record.mismatch_resolution_workflow_event_id
            else None
        ),
        "available_actions": [],
    }


def _iso(value):
    return value.isoformat().replace("+00:00", "Z") if value else None


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
