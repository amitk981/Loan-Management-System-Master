import re
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.security_instruments.evidence_contract import require_coordinated
from sfpcl_credit.security_instruments.models import PowerOfAttorney
from sfpcl_credit.security_instruments.modules import security_package
from sfpcl_credit.security_instruments.modules.evidence_recorder import record_security_evidence
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.models import WorkflowEvent


MANAGE_PERMISSION = "security.poa.manage"
READ_PERMISSION = security_package.READ_PERMISSION
RequestMetadata = security_package.RequestMetadata
AccessDenied = security_package.AccessDenied
NotFound = security_package.NotFound
Conflict = security_package.Conflict


def require_manage_actor(actor):
    security_package.require_actor(actor, MANAGE_PERMISSION)


def read_poa(*, actor, security_package_id, evidence_access):
    package = security_package.resolve_package(
        actor, security_package_id, READ_PERMISSION,
        evidence_access=evidence_access,
    )
    poa = PowerOfAttorney.objects.filter(security_package=package).first()
    if poa is None:
        raise NotFound
    return ordinary_poa_projection(poa)


def checklist_terminal_evidence(*, application_id, document, evidence_access):
    require_coordinated(evidence_access)
    poa = (
        PowerOfAttorney.objects.select_for_update(of=("self",))
        .select_related(
            "security_package__loan_application", "stamp_duty_record",
            "notarisation_record",
        )
        .filter(security_package__loan_application_id=application_id)
        .first()
    )
    activation = poa.activation_evidence_json if poa else {}
    workflow_valid = bool(
        poa
        and poa.activation_workflow_event_id
        and WorkflowEvent.objects.filter(
            pk=poa.activation_workflow_event_id,
            workflow_name="power_of_attorney",
            entity_type="power_of_attorney",
            entity_id=poa.pk,
            to_state="active",
            triggered_by_user_id=poa.verified_by_user_id,
            trigger_reason="security.poa.activated",
        ).exists()
    )
    if (
        poa is None
        or poa.status != PowerOfAttorney.STATUS_ACTIVE
        or poa.execution_status != PowerOfAttorney.EXECUTION_EXECUTED
        or poa.borrower_member_id != poa.security_package.loan_application.member_id
        or poa.nominee_id != poa.security_package.loan_application.nominee_id
        or poa.loan_document_id != document.pk
        or poa.stamp_duty_record.stamp_paper_amount != Decimal("500.00")
        or poa.stamp_duty_record.status != "adequate"
        or poa.notarisation_record.status != "completed"
        or poa.legacy_activation_evidence
        or not workflow_valid
        or activation.get("loan_document_id") != str(document.pk)
        or activation.get("document_file_id") != str(document.document_id)
        or activation.get("document_checksum_sha256")
        != document.renderer_validated_checksum_sha256
        or activation.get("stamp_duty_record_id") != str(poa.stamp_duty_record_id)
        or activation.get("notarisation_record_id") != str(poa.notarisation_record_id)
        or activation.get("poa_prepared_by_user_id") != str(poa.prepared_by_user_id)
        or activation.get("poa_verified_by_user_id") != str(poa.verified_by_user_id)
    ):
        return None
    return {
        "security_package_id": str(poa.security_package_id),
        "power_of_attorney_id": str(poa.pk),
        "borrower_member_id": str(poa.borrower_member_id),
        "nominee_id": str(poa.nominee_id),
        "attorney_user_id": str(poa.attorney_user_id),
        "loan_document_id": str(poa.loan_document_id),
        "stamp_duty_record_id": str(poa.stamp_duty_record_id),
        "notarisation_record_id": str(poa.notarisation_record_id),
        "prepared_by_user_id": str(poa.prepared_by_user_id),
        "verified_by_user_id": str(poa.verified_by_user_id),
        "activation_workflow_event_id": str(poa.activation_workflow_event_id),
        "status": poa.status,
        "execution_status": poa.execution_status,
    }


def create_poa(*, actor, security_package_id, values, metadata, evidence_access):
    require_manage_actor(actor)
    if "compliance_team_member" not in auth_service.effective_role_codes(actor):
        raise AccessDenied
    with transaction.atomic():
        package = security_package.resolve_package(
            actor, security_package_id, MANAGE_PERMISSION, for_update=True,
            evidence_access=evidence_access,
        )
        cleaned = _resolve_poa_values(
            package, values, actor, False, evidence_access
        )
        retained = (
            PowerOfAttorney.objects.select_for_update()
            .filter(security_package=package)
            .first()
        )
        if retained is not None:
            if _business_snapshot(retained) == _values_snapshot(cleaned):
                return serialize_poa(retained)
            raise Conflict(
                "A Power of Attorney already exists for this security package; use PATCH."
            )
        _project_poa(package, cleaned["loan_document"], cleaned, evidence_access)
        poa = PowerOfAttorney.objects.create(
            security_package=package,
            prepared_by_user=actor,
            verified_by_user=None,
            **cleaned,
        )
        _record_poa_evidence(actor, poa, "security.poa.created", {}, metadata)
        return serialize_poa(poa)


def update_poa(
    *, actor, power_of_attorney_id, values, metadata, evidence_access
):
    require_manage_actor(actor)
    with transaction.atomic():
        poa = (
            PowerOfAttorney.objects.select_for_update()
            .select_related("security_package__loan_application")
            .filter(
                pk=power_of_attorney_id,
                security_package__loan_application__application_status=(
                    LoanApplication.STATUS_APPROVED_BY_SANCTION
                ),
            )
            .first()
        )
        if poa is None:
            raise NotFound
        package = poa.security_package
        if not security_package.has_canonical_stage4_scope(
            package.loan_application_id, evidence_access
        ):
            raise NotFound
        cleaned = _resolve_poa_values(package, values, actor, True, evidence_access)
        new_snapshot = _values_snapshot(cleaned)
        if _business_snapshot(poa) == new_snapshot:
            if poa.status == "active":
                if poa.legacy_activation_evidence:
                    raise Conflict(
                        "Legacy active Power of Attorney lacks a durable activation action identity."
                    )
                return _activation_action(poa)
            return serialize_poa(poa)
        if poa.status == "active":
            raise Conflict("An active Power of Attorney is terminal and cannot be changed or downgraded.")
        activating = cleaned["status"] == "active"
        if activating:
            _validate_activation(poa, cleaned, actor, evidence_access)
        elif "compliance_team_member" not in auth_service.effective_role_codes(actor):
            raise _validation_error(
                {"status": "Only Compliance authority may change draft preparation facts."}
            )
        old = serialize_poa(poa)
        _project_poa(package, cleaned["loan_document"], cleaned, evidence_access)
        workflow_event = None
        if activating:
            evidence = _activation_evidence(
                poa, cleaned, actor, metadata, evidence_access
            )
            workflow_event = record_workflow_event(
                actor=actor,
                workflow_name="power_of_attorney",
                entity_type="power_of_attorney",
                entity_id=poa.pk,
                from_state=poa.status,
                to_state="active",
                trigger_reason="security.poa.activated",
                action_code="security.poa.activated",
                metadata=evidence,
            )
        for field, value in cleaned.items():
            setattr(poa, field, value)
        poa.verified_by_user = actor if activating else None
        poa.prepared_by_user = poa.prepared_by_user if activating else actor
        poa.activation_evidence_json = evidence if activating else {}
        poa.activation_workflow_event_id = workflow_event.pk if workflow_event else None
        poa.legacy_activation_evidence = False
        poa.updated_at = timezone.now()
        poa.save(update_fields=[
            *cleaned.keys(), "verified_by_user", "prepared_by_user",
            "activation_evidence_json", "activation_workflow_event_id", "updated_at",
            "legacy_activation_evidence",
        ])
        if activating:
            document = cleaned["loan_document"]
            document.execution_status = "executed"
            document.verification_status = "verified"
            document.save(update_fields=["execution_status", "verification_status"])
            AuditLog.objects.create(
                actor_user=actor,
                actor_type="user",
                action="documents.execution.consumed",
                entity_type="loan_document",
                entity_id=document.pk,
                old_value_json={},
                new_value_json={
                    "consumer_entity_type": "power_of_attorney",
                    "consumer_entity_id": str(poa.pk),
                    "workflow_event_id": str(workflow_event.pk),
                    **evidence,
                },
                ip_address=metadata.ip_address,
                user_agent=metadata.user_agent,
            )
        _record_poa_evidence(
            actor, poa,
            "security.poa.activated" if activating else "security.poa.changed",
            old, metadata, record_workflow=not activating,
        )
        return _activation_action(poa) if activating else serialize_poa(poa)


def _resolve_poa_values(package, values, actor, allow_activation, evidence_access):
    from django.core.exceptions import ValidationError

    application = package.loan_application
    errors = {}
    if values["borrower_member_id"] != application.member_id:
        errors["borrower_member_id"] = "Must be the sanctioned application's borrower."
    if application.nominee_id is None or values["nominee_id"] != application.nominee_id:
        errors["nominee_id"] = "Must be the sanctioned application's selected nominee."
    attorney = User.objects.select_related("primary_role").filter(
        pk=values["attorney_user_id"], status=User.ACTIVE_STATUS
    ).first()
    if attorney is None or "company_secretary" not in auth_service.effective_role_codes(attorney):
        errors["attorney_user_id"] = "Must identify an active Company Secretary."
    words = " ".join(values["purpose_summary"].lower().split())
    explicit_authority = re.search(
        r"\bauthori[sz](?:e|es|ed) (?:the )?company secretary to initiate "
        r"(?:the )?sale of shares (?:on|upon) default\b",
        words,
    )
    authority_negated = re.search(
        r"\b(?:do|does|shall|must|may) not authori[sz](?:e|es|ed) "
        r"(?:the )?company secretary to initiate (?:the )?sale of shares "
        r"(?:on|upon) default\b",
        words,
    )
    if explicit_authority is None or authority_negated is not None:
        errors["purpose_summary"] = (
            "Must explicitly authorise the Company Secretary to initiate share sale on default."
        )
    document, stamp, notary = require_coordinated(evidence_access).poa_evidence(
        application_id=application.pk,
        loan_document_id=values["loan_document_id"],
        stamp_duty_record_id=values["stamp_duty_record_id"],
        notarisation_record_id=values["notarisation_record_id"],
    )
    if (
        document is None
        or document.renderer_validation_status
        != "current_validated"
    ):
        errors["loan_document_id"] = (
            "Current rendered PoA document was not found for this application."
        )
    if stamp is None:
        errors["stamp_duty_record_id"] = (
            "Stamp record was not found for the PoA document."
        )
    if notary is None:
        errors["notarisation_record_id"] = (
            "Notarisation record was not found for the PoA document."
        )
    if not allow_activation and (
        values["status"] != "draft" or values["execution_status"] != "pending"
    ):
        errors["status"] = (
            "Creation prepares a draft; activation requires Company Secretary PATCH verification."
        )
    if not allow_activation and values["effective_from"] is not None:
        errors["effective_from"] = "Draft preparation cannot set an effective date."
    if errors:
        raise ValidationError(errors)
    return {
        "borrower_member_id": values["borrower_member_id"],
        "nominee_id": values["nominee_id"],
        "attorney_user": attorney,
        "purpose_summary": values["purpose_summary"],
        "loan_document": document,
        "stamp_duty_record": stamp,
        "notarisation_record": notary,
        "execution_status": values["execution_status"],
        "effective_from": values["effective_from"],
        "status": values["status"],
    }


def _validate_activation(poa, cleaned, actor, evidence_access):
    errors = {}
    if "company_secretary" not in auth_service.effective_role_codes(actor):
        errors["status"] = "Only Company Secretary authority may activate a Power of Attorney."
    if cleaned["attorney_user"].pk != actor.pk:
        errors["attorney_user_id"] = (
            "The activating Company Secretary must be the retained attorney."
        )
    if poa.prepared_by_user_id == actor.pk:
        errors["status"] = "The preparer and activating verifier must be different users."
    retained_preparation = _business_snapshot(poa)
    proposed_preparation = _values_snapshot(cleaned)
    for field in (
        "borrower_member_id", "nominee_id", "attorney_user_id", "purpose_summary",
        "loan_document_id", "stamp_duty_record_id", "notarisation_record_id",
    ):
        if retained_preparation[field] != proposed_preparation[field]:
            errors[field] = "Activation must verify the exact retained draft preparation."
    if cleaned["execution_status"] != "executed" or cleaned["effective_from"] is None:
        errors["execution_status"] = (
            "Active Power of Attorney requires executed status and effective_from."
        )
    stamp = cleaned["stamp_duty_record"]
    if (
        stamp.status != "adequate"
        or stamp.stamp_paper_amount != Decimal("500.00")
        or stamp.prepared_by_user_id is None
        or stamp.verified_by_user_id is None
        or stamp.prepared_by_user_id == stamp.verified_by_user_id
    ):
        errors["stamp_duty_record_id"] = (
            "Activation requires current adequate maker/checker stamp evidence "
            "on exact ₹500.00 stamp paper."
        )
    notary = cleaned["notarisation_record"]
    if (
        notary.status != "completed"
        or notary.prepared_by_user_id is None
        or notary.verified_by_user_id is None
        or notary.prepared_by_user_id == notary.verified_by_user_id
    ):
        errors["notarisation_record_id"] = (
            "Activation requires current completed maker/checker notarisation evidence."
        )
    rows = require_coordinated(evidence_access).execution_signatures(
        application_id=poa.security_package.loan_application_id,
        loan_document_id=cleaned["loan_document"].pk,
        for_update=True,
    )
    expected = {
        "borrower": (
            cleaned["borrower_member_id"],
            None,
        ),
        "nominee": (
            cleaned["nominee_id"],
            None,
        ),
    }
    if len(rows) != 2:
        errors["execution_status"] = "Distinct current borrower and nominee signatures are required."
    else:
        by_type = {row["signer_party_type"]: row for row in rows}
        for party_type, (party_id, _name) in expected.items():
            row = by_type.get(party_type)
            if (
                row is None
                or row["signer_party_id"] != party_id
                or not row["signer_name_snapshot"].strip()
                or row["signature_status"] != "signed"
                or row["signature_mismatch_flag"]
                or row["mismatch_resolution_type"] is not None
                or row["signed_at"] is None
                or row["captured_by_user_id"] is None
            ):
                errors["execution_status"] = (
                    "Distinct current borrower and nominee signatures are required."
                )
    if errors:
        raise _validation_error(errors)


def _validation_error(errors):
    from django.core.exceptions import ValidationError

    return ValidationError(errors)


def _project_poa(package, document, values, evidence_access):
    require_coordinated(evidence_access).project_checklist_item(
        application_id=package.loan_application_id,
        item_code="poa",
        document=document,
        updates={
            "poa_execution_status": values["execution_status"],
            "poa_status": values["status"],
        },
    )


def _values_snapshot(values):
    return {
        "borrower_member_id": str(values["borrower_member_id"]),
        "nominee_id": str(values["nominee_id"]),
        "attorney_user_id": str(values["attorney_user"].pk),
        "purpose_summary": values["purpose_summary"],
        "loan_document_id": str(values["loan_document"].pk),
        "stamp_duty_record_id": str(values["stamp_duty_record"].pk),
        "notarisation_record_id": str(values["notarisation_record"].pk),
        "execution_status": values["execution_status"],
        "effective_from": (
            values["effective_from"].isoformat() if values["effective_from"] else None
        ),
        "status": values["status"],
    }


def _business_snapshot(poa):
    omitted = {
        "power_of_attorney_id",
        "security_package_id",
        "prepared_by_user_id",
        "verified_by_user_id",
        "activation_evidence",
        "legacy_activation_evidence",
    }
    return {key: value for key, value in serialize_poa(poa).items() if key not in omitted}


def serialize_poa(poa):
    return {
        "power_of_attorney_id": str(poa.pk),
        "security_package_id": str(poa.security_package_id),
        "borrower_member_id": str(poa.borrower_member_id),
        "nominee_id": str(poa.nominee_id),
        "attorney_user_id": str(poa.attorney_user_id),
        "purpose_summary": poa.purpose_summary,
        "loan_document_id": str(poa.loan_document_id),
        "stamp_duty_record_id": str(poa.stamp_duty_record_id),
        "notarisation_record_id": str(poa.notarisation_record_id),
        "execution_status": poa.execution_status,
        "effective_from": poa.effective_from.isoformat() if poa.effective_from else None,
        "status": poa.status,
        "prepared_by_user_id": str(poa.prepared_by_user_id),
        "verified_by_user_id": str(poa.verified_by_user_id) if poa.verified_by_user_id else None,
        "activation_evidence": poa.activation_evidence_json or None,
        "legacy_activation_evidence": poa.legacy_activation_evidence,
    }


def ordinary_poa_projection(poa):
    return {
        "power_of_attorney_id": str(poa.pk),
        "security_package_id": str(poa.security_package_id),
        "borrower_member_id": str(poa.borrower_member_id),
        "nominee_id": str(poa.nominee_id),
        "attorney_user_id": str(poa.attorney_user_id),
        "purpose_summary": poa.purpose_summary,
        "execution_status": poa.execution_status,
        "effective_from": poa.effective_from.isoformat() if poa.effective_from else None,
        "status": poa.status,
    }


def _record_poa_evidence(actor, poa, action, old, metadata, record_workflow=True):
    record_security_evidence(
        actor=actor,
        action=action,
        entity_type="power_of_attorney",
        entity_id=poa.pk,
        old=old,
        snapshot=serialize_poa(poa),
        metadata=metadata,
        workflow_name="power_of_attorney",
        from_state=old.get("status"),
        to_state=poa.status,
        record_workflow=record_workflow,
    )


def _activation_evidence(poa, cleaned, actor, metadata, evidence_access):
    document = cleaned["loan_document"]
    signatures = require_coordinated(evidence_access).execution_signatures(
        application_id=poa.security_package.loan_application_id,
        loan_document_id=document.pk,
        for_update=True,
    )
    return {
        "loan_document_id": str(document.pk),
        "renderer_contract_version": document.renderer_contract_version,
        "document_file_id": str(document.document_id),
        "document_checksum_sha256": document.document.checksum_sha256,
        "stamp_duty_record_id": str(cleaned["stamp_duty_record"].pk),
        "stamp_prepared_by_user_id": str(cleaned["stamp_duty_record"].prepared_by_user_id),
        "stamp_verified_by_user_id": str(cleaned["stamp_duty_record"].verified_by_user_id),
        "notarisation_record_id": str(cleaned["notarisation_record"].pk),
        "notary_prepared_by_user_id": str(cleaned["notarisation_record"].prepared_by_user_id),
        "notary_verified_by_user_id": str(cleaned["notarisation_record"].verified_by_user_id),
        "signatures": sorted(
            [
                {
                    "signature_record_id": str(row["signature_record_id"]),
                    "signer_party_type": row["signer_party_type"],
                    "signer_party_id": str(row["signer_party_id"]),
                    "signer_name_snapshot": row["signer_name_snapshot"],
                    "captured_by_user_id": str(row["captured_by_user_id"]),
                    "signed_at": row["signed_at"].isoformat(),
                }
                for row in signatures
            ],
            key=lambda row: row["signer_party_type"],
        ),
        "poa_prepared_by_user_id": str(poa.prepared_by_user_id),
        "poa_verified_by_user_id": str(actor.pk),
        "request_id": metadata.request_id,
        "ip_address": metadata.ip_address,
        "user_agent": metadata.user_agent,
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "actor_team_codes": actor.team_codes(),
    }


def _activation_action(poa):
    return {
        "entity_type": "power_of_attorney",
        "entity_id": str(poa.pk),
        "previous_status": "draft",
        "new_status": "active",
        "workflow_event_id": str(poa.activation_workflow_event_id),
        "available_actions": [],
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
