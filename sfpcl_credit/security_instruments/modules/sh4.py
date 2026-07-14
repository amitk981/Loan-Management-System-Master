from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from sfpcl_credit.applications.models import Witness
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import Shareholding
from sfpcl_credit.security_instruments.evidence_contract import require_coordinated
from sfpcl_credit.security_instruments.models import SH4ShareTransferForm
from sfpcl_credit.security_instruments.modules import security_package
from sfpcl_credit.security_instruments.modules.evidence_recorder import record_security_evidence
from sfpcl_credit.workflows.events import record_workflow_event


MANAGE_PERMISSION = "security.sh4.manage"
READ_PERMISSION = security_package.READ_PERMISSION
RequestMetadata = security_package.RequestMetadata
AccessDenied = security_package.AccessDenied
NotFound = security_package.NotFound
Conflict = security_package.Conflict


def require_manage_actor(actor):
    security_package.require_actor(actor, MANAGE_PERMISSION)


def read_sh4(*, actor, security_package_id, evidence_access):
    package = security_package.resolve_package(
        actor, security_package_id, READ_PERMISSION,
        evidence_access=evidence_access,
    )
    form = SH4ShareTransferForm.objects.filter(security_package=package).first()
    if form is None:
        raise NotFound
    return serialize_sh4(form)


def create_sh4(*, actor, security_package_id, values, metadata, evidence_access):
    require_manage_actor(actor)
    if "compliance_team_member" not in auth_service.effective_role_codes(actor):
        raise AccessDenied
    with transaction.atomic():
        package = security_package.resolve_package(
            actor, security_package_id, MANAGE_PERMISSION, for_update=True,
            evidence_access=evidence_access,
        )
        cleaned = _resolve_values(package, values, False, evidence_access)
        retained = SH4ShareTransferForm.objects.select_for_update().filter(
            security_package=package
        ).first()
        if retained is not None:
            if _business_snapshot(retained) == _values_snapshot(cleaned):
                return serialize_sh4(retained)
            raise Conflict("An SH-4 already exists for this security package; use PATCH.")
        _project(package, cleaned["loan_document"], evidence_access)
        form = SH4ShareTransferForm.objects.create(
            security_package=package, prepared_by_user=actor, **cleaned
        )
        _record_evidence(
            actor, form, "security.sh4.created", {}, metadata, evidence_access
        )
        return serialize_sh4(form)


def update_sh4(
    *, actor, sh4_share_transfer_form_id, values, metadata, evidence_access
):
    require_manage_actor(actor)
    with transaction.atomic():
        form = (
            SH4ShareTransferForm.objects.select_for_update()
            .select_related("security_package__loan_application")
            .filter(pk=sh4_share_transfer_form_id)
            .first()
        )
        if form is None or not security_package.has_canonical_stage4_scope(
            form.security_package.loan_application_id, evidence_access
        ):
            raise NotFound
        cleaned = _resolve_values(form.security_package, values, True, evidence_access)
        new_snapshot = _values_snapshot(cleaned)
        if _business_snapshot(form) == new_snapshot:
            if form.form_status == "held_in_custody":
                return _custody_action(form)
            return serialize_sh4(form)
        if form.form_status == "held_in_custody":
            raise Conflict("A held SH-4 is terminal and cannot be changed or downgraded.")
        taking_custody = cleaned["form_status"] == "held_in_custody"
        if taking_custody:
            _validate_custody(form, cleaned, actor, evidence_access)
        else:
            if "compliance_team_member" not in auth_service.effective_role_codes(actor):
                raise ValidationError(
                    {"form_status": "Only Compliance authority may change preparation facts."}
                )
            if cleaned["form_status"] not in {"pending", "signed"}:
                raise ValidationError({"form_status": "Unsupported preparation state."})
            _validate_signed(cleaned, evidence_access)
        old = serialize_sh4(form)
        _project(form.security_package, cleaned["loan_document"], evidence_access)
        workflow_event = None
        evidence = {}
        if taking_custody:
            evidence = _custody_evidence(
                form, cleaned, actor, metadata, evidence_access
            )
            workflow_event = record_workflow_event(
                actor=actor, workflow_name="sh4", entity_type="sh4_share_transfer_form",
                entity_id=form.pk, from_state=form.form_status, to_state="held_in_custody",
                trigger_reason="security.sh4.custodied", action_code="security.sh4.custodied",
                metadata=evidence,
            )
        for field, value in cleaned.items():
            setattr(form, field, value)
        form.prepared_by_user = form.prepared_by_user if taking_custody else actor
        form.custodian_user = actor if taking_custody else None
        form.custody_evidence_json = evidence
        form.custody_workflow_event_id = workflow_event.pk if workflow_event else None
        form.updated_at = timezone.now()
        form.save(update_fields=[
            *cleaned.keys(), "prepared_by_user", "custodian_user",
            "custody_evidence_json", "custody_workflow_event_id", "updated_at",
        ])
        if taking_custody:
            AuditLog.objects.create(
                actor_user=actor, actor_type="user", action="documents.execution.consumed",
                entity_type="loan_document", entity_id=form.loan_document_id,
                old_value_json={}, new_value_json={
                    "consumer_entity_type": "sh4_share_transfer_form",
                    "consumer_entity_id": str(form.pk),
                    "workflow_event_id": str(workflow_event.pk), **evidence,
                }, ip_address=metadata.ip_address, user_agent=metadata.user_agent,
            )
        _record_evidence(
            actor, form,
            "security.sh4.custodied" if taking_custody else "security.sh4.changed",
            old, metadata, evidence_access, record_workflow=not taking_custody,
        )
        return _custody_action(form) if taking_custody else serialize_sh4(form)


def _resolve_values(package, values, allow_custody, evidence_access):
    errors = {}
    facts = require_coordinated(evidence_access).approved_facts(
        application_id=package.loan_application_id
    )
    if facts is None or facts.holding_mode != "physical":
        errors["form_status"] = "SH-4 is applicable only to frozen physical shareholding."
    if not package.physical_share_security_required_flag:
        errors["form_status"] = "Refresh the physical security requirement before SH-4 capture."
    application = package.loan_application
    if values["member_id"] != application.member_id:
        errors["member_id"] = "Must be the sanctioned application's borrower."
    witness = Witness.objects.filter(
        loan_application=application,
        shareholder_verified_flag=True, verification_status="verified",
        verified_by_user__isnull=False, verified_at__isnull=False,
        verification_shareholding__status="active",
        verification_shareholding__member_id=F("member_id"),
        verification_folio_number=F("verification_shareholding__folio_number"),
    ).order_by("-version", "-updated_at", "-created_at", "-witness_id").first()
    if (
        witness is None
        or witness.pk != values["witness_id"]
        or witness.member_id == application.member_id
    ):
        errors["witness_id"] = "Must be this application's current verified shareholder witness."
    shareholding = Shareholding.objects.filter(
        pk=values["shareholding_id"], member_id=application.member_id,
        status="active", holding_mode="physical",
    ).first()
    if shareholding is None:
        errors["shareholding_id"] = "Must be the borrower's active physical shareholding."
    elif values["share_count"] is not None and values["share_count"] > shareholding.available_share_count:
        errors["share_count"] = "Cannot exceed the retained available physical shares."
    document, _stamp, _signatures = require_coordinated(evidence_access).sh4_evidence(
        application_id=application.pk, loan_document_id=values["loan_document_id"]
    )
    if document is None or document.renderer_validation_status != "current_validated":
        errors["loan_document_id"] = "Current rendered SH-4 document was not found for this application."
    if not allow_custody and values["form_status"] != "pending":
        errors["form_status"] = "Creation prepares pending SH-4 facts; use PATCH for later states."
    if values["form_status"] == "pending" and (
        values["signed_at"] is not None or values["custody_location"] is not None
    ):
        errors["form_status"] = "Pending SH-4 cannot carry signature or custody facts."
    if values["form_status"] == "signed" and (
        values["signed_at"] is None or values["custody_location"] is not None
    ):
        errors["form_status"] = "Signed SH-4 requires signed_at and cannot carry custody."
    if values["form_status"] == "held_in_custody" and (
        values["signed_at"] is None or values["custody_location"] is None
    ):
        errors["form_status"] = "Held SH-4 requires signed_at and custody_location."
    if errors:
        raise ValidationError(errors)
    return {
        "member_id": values["member_id"], "witness": witness,
        "shareholding": shareholding, "share_count": values["share_count"],
        "loan_document": document, "form_status": values["form_status"],
        "custody_location": values["custody_location"], "signed_at": values["signed_at"],
    }


def _validate_signed(cleaned, evidence_access):
    errors = {}
    _document, stamp, rows = require_coordinated(evidence_access).sh4_evidence(
        application_id=cleaned["loan_document"].loan_application_id,
        loan_document_id=cleaned["loan_document"].pk,
    )
    if (
        stamp is None or stamp.status != "adequate"
        or stamp.prepared_by_user_id is None or stamp.verified_by_user_id is None
        or stamp.prepared_by_user_id == stamp.verified_by_user_id
    ):
        errors["loan_document_id"] = "Signed SH-4 requires current adequate maker/checker stamp evidence."
    expected = {
        "borrower": cleaned["member_id"],
        "witness": cleaned["witness"].pk,
    }
    by_type = {row["signer_party_type"]: row for row in rows}
    if len(rows) != 2:
        errors["form_status"] = "Distinct current borrower and witness signatures are required."
    else:
        for party_type, party_id in expected.items():
            row = by_type.get(party_type)
            if (
                row is None or row["signer_party_id"] != party_id
                or not row["signer_name_snapshot"].strip()
                or row["signature_status"] != "signed"
                or row["signature_mismatch_flag"]
                or row["mismatch_resolution_type"] is not None
                or row["signed_at"] is None or row["captured_by_user_id"] is None
                or timezone.localdate(row["signed_at"]) != cleaned["signed_at"]
            ):
                errors["form_status"] = "Distinct current borrower and witness signatures are required."
    if errors:
        raise ValidationError(errors)


def _validate_custody(form, cleaned, actor, evidence_access):
    errors = {}
    if "company_secretary" not in auth_service.effective_role_codes(actor):
        errors["form_status"] = "Only Company Secretary authority may record SH-4 custody."
    retained = _business_snapshot(form)
    proposed = _values_snapshot(cleaned)
    for field in (
        "member_id", "witness_id", "shareholding_id", "share_count",
        "loan_document_id", "signed_at",
    ):
        if retained[field] != proposed[field]:
            errors[field] = "Custody must consume the exact retained signed SH-4 facts."
    if form.form_status != "signed":
        errors["form_status"] = "Custody requires the exact retained signed SH-4."
    _validate_signed(cleaned, evidence_access)
    _document, stamp, rows = require_coordinated(evidence_access).sh4_evidence(
        application_id=form.security_package.loan_application_id,
        loan_document_id=cleaned["loan_document"].pk,
    )
    maker_ids = {form.prepared_by_user_id, stamp.prepared_by_user_id}
    maker_ids.update(row["captured_by_user_id"] for row in rows)
    if actor.pk in maker_ids:
        errors["form_status"] = "The custody checker must be distinct from current material makers."
    if errors:
        raise ValidationError(errors)


def _custody_evidence(form, cleaned, actor, metadata, evidence_access):
    document, stamp, rows = require_coordinated(evidence_access).sh4_evidence(
        application_id=form.security_package.loan_application_id,
        loan_document_id=cleaned["loan_document"].pk,
    )
    return {
        "loan_application_id": str(form.security_package.loan_application_id),
        "security_package_id": str(form.security_package_id),
        "member_id": str(cleaned["member_id"]), "witness_id": str(cleaned["witness"].pk),
        "shareholding_id": str(cleaned["shareholding"].pk),
        "loan_document_id": str(document.pk),
        "renderer_contract_version": document.renderer_contract_version,
        "document_file_id": str(document.document_id),
        "document_checksum_sha256": document.document.checksum_sha256,
        "stamp_duty_record_id": str(stamp.pk),
        "stamp_prepared_by_user_id": str(stamp.prepared_by_user_id),
        "stamp_verified_by_user_id": str(stamp.verified_by_user_id),
        "signatures": sorted([{
            "signature_record_id": str(row["signature_record_id"]),
            "signer_party_type": row["signer_party_type"],
            "signer_party_id": str(row["signer_party_id"]),
            "signer_name_snapshot": row["signer_name_snapshot"],
            "captured_by_user_id": str(row["captured_by_user_id"]),
            "signed_at": row["signed_at"].isoformat().replace("+00:00", "Z"),
        } for row in rows], key=lambda row: row["signer_party_type"]),
        "sh4_prepared_by_user_id": str(form.prepared_by_user_id),
        "sh4_custodian_user_id": str(actor.pk),
        "custody_location": cleaned["custody_location"],
        "request_id": metadata.request_id, "ip_address": metadata.ip_address,
        "user_agent": metadata.user_agent,
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "actor_team_codes": actor.team_codes(),
    }


def _project(package, document, evidence_access):
    require_coordinated(evidence_access).project_checklist_item(
        application_id=package.loan_application_id,
        item_code="sh4",
        document=document,
    )


def serialize_sh4(form):
    return {
        "sh4_share_transfer_form_id": str(form.pk),
        "security_package_id": str(form.security_package_id),
        "member_id": str(form.member_id),
        "witness_id": str(form.witness_id),
        "shareholding_id": str(form.shareholding_id),
        "share_count": form.share_count,
        "loan_document_id": str(form.loan_document_id),
        "form_status": form.form_status,
        "custody_location": form.custody_location,
        "signed_at": form.signed_at.isoformat() if form.signed_at else None,
        "prepared_by_user_id": str(form.prepared_by_user_id),
        "custodian_user_id": str(form.custodian_user_id) if form.custodian_user_id else None,
        "custody_evidence": form.custody_evidence_json or None,
    }


def _values_snapshot(values):
    return {
        "member_id": str(values["member_id"]),
        "witness_id": str(values["witness"].pk),
        "shareholding_id": str(values["shareholding"].pk),
        "share_count": values["share_count"],
        "loan_document_id": str(values["loan_document"].pk),
        "form_status": values["form_status"],
        "custody_location": values["custody_location"],
        "signed_at": values["signed_at"].isoformat() if values["signed_at"] else None,
    }


def _business_snapshot(form):
    omitted = {
        "sh4_share_transfer_form_id", "security_package_id", "prepared_by_user_id",
        "custodian_user_id", "custody_evidence",
    }
    return {key: value for key, value in serialize_sh4(form).items() if key not in omitted}


def _record_evidence(
    actor, form, action, old, metadata, evidence_access, record_workflow=True
):
    _document, stamp, signatures = require_coordinated(
        evidence_access
    ).sh4_evidence(
        application_id=form.security_package.loan_application_id,
        loan_document_id=form.loan_document_id,
    )
    snapshot = {
        **serialize_sh4(form),
        "loan_application_id": str(form.security_package.loan_application_id),
        "stamp_duty_record_id": str(stamp.pk) if stamp else None,
        "stamp_prepared_by_user_id": (
            str(stamp.prepared_by_user_id) if stamp and stamp.prepared_by_user_id else None
        ),
        "stamp_verified_by_user_id": (
            str(stamp.verified_by_user_id) if stamp and stamp.verified_by_user_id else None
        ),
        "signature_record_ids": [str(row["signature_record_id"]) for row in signatures],
        "signature_party_types": [row["signer_party_type"] for row in signatures],
        "signature_capture_maker_user_ids": [
            str(row["captured_by_user_id"])
            for row in signatures if row["captured_by_user_id"]
        ],
    }
    record_security_evidence(
        actor=actor,
        entity_type="sh4_share_transfer_form",
        entity_id=form.pk,
        action=action,
        old=old,
        snapshot=snapshot,
        metadata=metadata,
        workflow_name="sh4",
        from_state=old.get("form_status"),
        to_state=form.form_status,
        record_workflow=record_workflow,
    )


def _custody_action(form):
    return {
        "entity_type": "sh4_share_transfer_form", "entity_id": str(form.pk),
        "previous_status": "signed", "new_status": "held_in_custody",
        "workflow_event_id": str(form.custody_workflow_event_id), "available_actions": [],
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
