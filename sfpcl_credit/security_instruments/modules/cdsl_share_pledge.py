from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import Shareholding
from sfpcl_credit.members.protected_identity import (
    identity_hash,
    mask_protected_identity,
    reveal_sealed_protected_identity,
    sealed_protected_identity_token,
)
from sfpcl_credit.security_instruments.models import CDSLSharePledge
from sfpcl_credit.security_instruments.evidence_contract import require_coordinated
from sfpcl_credit.security_instruments.modules import security_package
from sfpcl_credit.security_instruments.modules.evidence_recorder import record_security_evidence
from sfpcl_credit.workflows.events import record_workflow_event


MANAGE_PERMISSION = "security.cdsl_pledge.manage"
REVEAL_PERMISSION = "security.cdsl_pledge.reveal"
READ_PERMISSION = security_package.READ_PERMISSION
SFPCL_ENTITY_NAME = "Sahyadri Farmers Producer Company Limited"
RequestMetadata = security_package.RequestMetadata
AccessDenied = security_package.AccessDenied
NotFound = security_package.NotFound
Conflict = security_package.Conflict
def require_manage_actor(actor):
    security_package.require_actor(actor, MANAGE_PERMISSION)
def read_pledge(*, actor, security_package_id, evidence_access):
    package = security_package.resolve_package(
        actor, security_package_id, READ_PERMISSION,
        evidence_access=evidence_access,
    )
    pledge = CDSLSharePledge.objects.filter(security_package=package).first()
    if pledge is None:
        raise NotFound
    return serialize_pledge(pledge)
def require_reveal_actor(actor, cdsl_share_pledge_id, metadata):
    if (
        not actor.can_authenticate()
        or REVEAL_PERMISSION not in auth_service.effective_permission_codes(actor)
        or "company_secretary" not in auth_service.effective_role_codes(actor)
    ):
        _record_reveal_denial(
            actor, cdsl_share_pledge_id, "missing_reveal_authority", metadata
        )
        raise AccessDenied("SENSITIVE_FIELD_ACCESS_DENIED")
def reveal_bo_accounts(
    *, actor, cdsl_share_pledge_id, reason, metadata, evidence_access
):
    require_reveal_actor(actor, cdsl_share_pledge_id, metadata)
    pledge = (
        CDSLSharePledge.objects.select_related("security_package")
        .filter(pk=cdsl_share_pledge_id)
        .first()
    )
    if pledge is None:
        raise NotFound
    try:
        security_package.resolve_package(
            actor, pledge.security_package_id, READ_PERMISSION,
            evidence_access=evidence_access,
        )
    except AccessDenied:
        _record_reveal_denial(actor, pledge.pk, "object_access_denied", metadata)
        raise
    try:
        pledgor_value = reveal_sealed_protected_identity(
            pledge.pledgor_bo_account_encrypted
        )
        pledgee_value = (
            reveal_sealed_protected_identity(pledge.pledgee_bo_account_encrypted)
            if pledge.pledgee_bo_account_encrypted else None
        )
    except ValueError as exc:
        raise Conflict("The retained BO account token cannot be revealed safely.") from exc
    expires_at = timezone.now() + timedelta(minutes=5)
    expires_at_value = expires_at.isoformat().replace("+00:00", "Z")
    AuditLog.objects.create(
        actor_user=actor, actor_type="user",
        action="security.cdsl_pledge.bo_accounts_revealed",
        entity_type="cdsl_share_pledge", entity_id=pledge.pk,
        old_value_json={}, new_value_json={
            "cdsl_share_pledge_id": str(pledge.pk),
            "security_package_id": str(pledge.security_package_id),
            "loan_application_id": str(pledge.security_package.loan_application_id),
            "field_names": ["pledgor_bo_account", "pledgee_bo_account"],
            "reason": reason, "outcome": "success",
            "request_id": metadata.request_id, "expires_at": expires_at_value,
            "actor_role_codes": auth_service.effective_role_codes(actor),
            "actor_team_codes": actor.team_codes(),
        }, ip_address=metadata.ip_address, user_agent=metadata.user_agent,
    )
    return {
        "cdsl_share_pledge_id": str(pledge.pk),
        "pledgor_bo_account": pledgor_value,
        "pledgee_bo_account": pledgee_value,
        "expires_at": expires_at_value,
    }
def _record_reveal_denial(actor, pledge_id, denial_reason, metadata):
    AuditLog.objects.create(
        actor_user=actor, actor_type="user",
        action="security.cdsl_pledge.bo_accounts_reveal_denied",
        entity_type="cdsl_share_pledge", entity_id=pledge_id,
        old_value_json={}, new_value_json={
            "cdsl_share_pledge_id": str(pledge_id),
            "outcome": "denied", "denial_reason": denial_reason,
            "request_id": metadata.request_id,
        }, ip_address=metadata.ip_address, user_agent=metadata.user_agent,
    )
def create_pledge(
    *, actor, security_package_id, values, metadata, evidence_access
):
    require_manage_actor(actor)
    if "compliance_team_member" not in auth_service.effective_role_codes(actor):
        raise AccessDenied
    with transaction.atomic():
        package = security_package.resolve_package(
            actor, security_package_id, MANAGE_PERMISSION, for_update=True,
            evidence_access=evidence_access,
        )
        cleaned = _resolve_values(package, values, evidence_access)
        retained = CDSLSharePledge.objects.select_for_update().filter(
            security_package=package
        ).first()
        if retained is not None:
            if _matches(retained, cleaned):
                return serialize_pledge(retained)
            raise Conflict(
                "A CDSL pledge already exists for this security package; use PATCH."
            )
        if cleaned["pledge_acceptance_status"] != "pending":
            raise ValidationError(
                {"pledge_acceptance_status": "Compliance may create only pending acceptance facts."}
            )
        if cleaned["pledge_status"] != "pending":
            raise ValidationError(
                {"pledge_status": "Compliance may create only pending pledge facts."}
            )
        if (
            cleaned["prf_status"] == "submitted"
            and not cleaned["pledge_sequence_number"]
        ):
            raise ValidationError(
                {"pledge_sequence_number": "Submitted PRF requires a PSN."}
            )
        if (
            cleaned["prf_status"] == "prepared"
            and cleaned["pledge_sequence_number"] is not None
        ):
            raise ValidationError(
                {"pledge_sequence_number": "Prepared PRF cannot carry a PSN yet."}
            )
        _project(package, cleaned["evidence_loan_document"], evidence_access)
        evidence_document = cleaned.pop("evidence_loan_document").document
        pledge = CDSLSharePledge.objects.create(
            security_package=package,
            prepared_by_user=actor,
            evidence_document=evidence_document,
            **cleaned,
        )
        _record_evidence(actor, pledge, "security.cdsl_pledge.created", {}, metadata)
        return serialize_pledge(pledge)
def update_pledge(
    *, actor, cdsl_share_pledge_id, values, metadata, evidence_access
):
    require_manage_actor(actor)
    with transaction.atomic():
        pledge = (
            CDSLSharePledge.objects.select_for_update(of=("self",))
            .select_related("security_package__loan_application", "evidence_document")
            .filter(pk=cdsl_share_pledge_id)
            .first()
        )
        if pledge is None or not security_package.has_canonical_stage4_scope(
            pledge.security_package.loan_application_id, evidence_access
        ):
            raise NotFound
        cleaned = _resolve_values(pledge.security_package, values, evidence_access)
        if _matches(pledge, cleaned):
            if pledge.pledge_acceptance_status in {"accepted", "rejected"}:
                return _acceptance_action(pledge)
            return serialize_pledge(pledge)
        if pledge.pledge_acceptance_status in {"accepted", "rejected"}:
            raise Conflict(
                "A checked CDSL pledge is terminal and cannot be changed or downgraded."
            )
        terminal = cleaned["pledge_acceptance_status"] in {"accepted", "rejected"}
        if terminal:
            _validate_checker(pledge, cleaned, actor)
        else:
            _validate_preparation(pledge, cleaned, actor)
        old = serialize_pledge(pledge)
        _project(
            pledge.security_package,
            cleaned["evidence_loan_document"],
            evidence_access,
        )
        evidence_loan_document = cleaned["evidence_loan_document"]
        evidence_document = (
            evidence_loan_document.document if evidence_loan_document else None
        )
        workflow_event = None
        acceptance_evidence = {}
        if terminal:
            acceptance_evidence = _acceptance_evidence(
                pledge, cleaned, evidence_document, actor, metadata
            )
            workflow_event = record_workflow_event(
                actor=actor, workflow_name="cdsl_share_pledge",
                entity_type="cdsl_share_pledge", entity_id=pledge.pk,
                from_state=pledge.pledge_status, to_state=cleaned["pledge_status"],
                trigger_reason=f"security.cdsl_pledge.{cleaned['pledge_acceptance_status']}",
                action_code=f"security.cdsl_pledge.{cleaned['pledge_acceptance_status']}",
                metadata=acceptance_evidence,
            )
        cleaned.pop("evidence_loan_document")
        for field, value in cleaned.items():
            setattr(pledge, field, value)
        pledge.evidence_document = evidence_document
        pledge.prepared_by_user = pledge.prepared_by_user if terminal else actor
        pledge.verified_by_user = actor if terminal else None
        pledge.acceptance_evidence_json = acceptance_evidence
        pledge.acceptance_workflow_event_id = workflow_event.pk if workflow_event else None
        pledge.created_at_cdsl = timezone.now() if cleaned["pledge_status"] == "created" else None
        pledge.updated_at = timezone.now()
        pledge.save()
        action = f"security.cdsl_pledge.{cleaned['pledge_acceptance_status']}" if terminal else "security.cdsl_pledge.changed"
        if terminal and evidence_document is not None:
            AuditLog.objects.create(
                actor_user=actor, actor_type="user", action="documents.execution.consumed",
                entity_type="loan_document",
                entity_id=acceptance_evidence["loan_document_id"],
                old_value_json={}, new_value_json={
                    "consumer_entity_type": "cdsl_share_pledge",
                    "consumer_entity_id": str(pledge.pk),
                    "workflow_event_id": str(workflow_event.pk),
                    **acceptance_evidence,
                }, ip_address=metadata.ip_address, user_agent=metadata.user_agent,
            )
        _record_evidence(
            actor, pledge, action, old, metadata, record_workflow=not terminal
        )
        return _acceptance_action(pledge) if terminal else serialize_pledge(pledge)
def _validate_preparation(pledge, cleaned, actor):
    errors = {}
    if "compliance_team_member" not in auth_service.effective_role_codes(actor):
        errors["pledge_acceptance_status"] = (
            "Only Compliance authority may change preparation facts."
        )
    if cleaned["pledge_acceptance_status"] != "pending" or cleaned["pledge_status"] != "pending":
        errors["pledge_acceptance_status"] = "Preparation must remain pending."
    if pledge.prf_status == "submitted" and cleaned["prf_status"] != "submitted":
        errors["prf_status"] = "A submitted PRF cannot return to prepared."
    if cleaned["prf_status"] == "submitted" and not cleaned["pledge_sequence_number"]:
        errors["pledge_sequence_number"] = "Submitted PRF requires a PSN."
    if errors:
        raise ValidationError(errors)
def _validate_checker(pledge, cleaned, actor):
    errors = {}
    if "company_secretary" not in auth_service.effective_role_codes(actor):
        errors["pledge_acceptance_status"] = (
            "Only Company Secretary authority may verify acceptance."
        )
    if actor.pk == pledge.prepared_by_user_id:
        errors["pledge_acceptance_status"] = (
            "The acceptance checker must be distinct from the current preparer."
        )
    retained_material = {
        "pledgor_member_id": pledge.pledgor_member_id,
        "pledgee_entity_name": pledge.pledgee_entity_name,
        "pledgor_bo_account_hash": pledge.pledgor_bo_account_hash,
        "pledgee_bo_account_hash": pledge.pledgee_bo_account_hash,
        "pledgor_dp_name": pledge.pledgor_dp_name,
        "pledgee_dp_name": pledge.pledgee_dp_name,
        "prf_status": pledge.prf_status,
        "pledge_sequence_number": pledge.pledge_sequence_number,
        "pledged_share_count": pledge.pledged_share_count,
        "agreement_number": pledge.agreement_number,
        "evidence_document_id": pledge.evidence_document_id,
    }
    proposed_material = {
        "pledgor_member_id": cleaned["pledgor_member_id"],
        "pledgee_entity_name": cleaned["pledgee_entity_name"],
        "pledgor_bo_account_hash": cleaned["pledgor_bo_account_hash"],
        "pledgee_bo_account_hash": cleaned["pledgee_bo_account_hash"],
        "pledgor_dp_name": cleaned["pledgor_dp_name"],
        "pledgee_dp_name": cleaned["pledgee_dp_name"],
        "prf_status": cleaned["prf_status"],
        "pledge_sequence_number": cleaned["pledge_sequence_number"],
        "pledged_share_count": cleaned["pledged_share_count"],
        "agreement_number": cleaned["agreement_number"],
        "evidence_document_id": (
            cleaned["evidence_loan_document"].document_id
            if cleaned["evidence_loan_document"] else None
        ),
    }
    for field, retained in retained_material.items():
        if proposed_material[field] != retained:
            public_field = field.removesuffix("_hash")
            errors[public_field] = (
                "Acceptance must consume the exact retained Compliance preparation facts."
            )
    required = {
        "pledge_sequence_number": cleaned["pledge_sequence_number"],
        "pledgor_dp_name": cleaned["pledgor_dp_name"],
        "pledgee_dp_name": cleaned["pledgee_dp_name"],
        "pledgee_bo_account": cleaned["pledgee_bo_account_encrypted"],
        "evidence_document_id": cleaned["evidence_loan_document"],
    }
    for field, value in required.items():
        if value is None:
            errors[field] = "Required before acceptance verification."
    if cleaned["prf_status"] != "submitted":
        errors["prf_status"] = "Acceptance verification requires submitted PRF facts."
    if cleaned["pledge_acceptance_status"] == "accepted":
        if cleaned["pledge_status"] != "created":
            errors["pledge_status"] = "Accepted pledge must be created."
        if cleaned["pledged_share_count"] is None:
            errors["pledged_share_count"] = "Accepted pledge requires a positive share count."
        if not cleaned["agreement_number"]:
            errors["agreement_number"] = "Accepted pledge requires the loan agreement reference."
    elif cleaned["pledge_status"] != "pending":
        errors["pledge_status"] = "Rejected acceptance cannot create a pledge."
    if errors:
        raise ValidationError(errors)
def _acceptance_evidence(pledge, cleaned, evidence_document, actor, metadata):
    document = cleaned["evidence_loan_document"]
    return {
        "loan_application_id": str(pledge.security_package.loan_application_id),
        "security_package_id": str(pledge.security_package_id),
        "pledgor_member_id": str(cleaned["pledgor_member_id"]),
        "pledgor_bo_account": mask_protected_identity(
            cleaned["pledgor_bo_account_encrypted"], 16
        ),
        "pledgee_bo_account": mask_protected_identity(
            cleaned["pledgee_bo_account_encrypted"], 16
        ),
        "pledgor_dp_name": cleaned["pledgor_dp_name"],
        "pledgee_dp_name": cleaned["pledgee_dp_name"],
        "pledge_sequence_number": cleaned["pledge_sequence_number"],
        "agreement_number": cleaned["agreement_number"],
        "pledged_share_count": cleaned["pledged_share_count"],
        "future_shares_pledged_flag": True,
        "loan_document_id": str(document.pk),
        "document_file_id": str(evidence_document.pk),
        "renderer_contract_version": document.renderer_contract_version,
        "document_checksum_sha256": evidence_document.checksum_sha256,
        "cdsl_prepared_by_user_id": str(pledge.prepared_by_user_id),
        "cdsl_verified_by_user_id": str(actor.pk),
        "request_id": metadata.request_id,
        "ip_address": metadata.ip_address,
        "user_agent": metadata.user_agent,
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "actor_team_codes": actor.team_codes(),
    }
def _acceptance_action(pledge):
    return {
        "entity_type": "cdsl_share_pledge",
        "entity_id": str(pledge.pk),
        "previous_status": "pending",
        "new_status": pledge.pledge_status if pledge.pledge_status == "created" else "rejected",
        "workflow_event_id": str(pledge.acceptance_workflow_event_id),
        "available_actions": [],
    }
def _resolve_values(package, values, evidence_access):
    errors = {}
    facts = require_coordinated(evidence_access).approved_facts(
        application_id=package.loan_application_id
    )
    if facts is None or facts.holding_mode != "demat":
        errors["pledge_status"] = (
            "CDSL pledge is applicable only to frozen demat shareholding."
        )
    if not package.demat_pledge_required_flag:
        errors["pledge_status"] = (
            "Refresh the demat pledge requirement before CDSL capture."
        )
    if values["pledgor_member_id"] != package.loan_application.member_id:
        errors["pledgor_member_id"] = (
            "Must be the sanctioned application's borrower."
        )
    holdings = Shareholding.objects.select_for_update().filter(
        member_id=package.loan_application.member_id,
        holding_mode="demat",
        status="active",
        demat_account_id__isnull=False,
    )
    available_shares = sum(holding.available_share_count for holding in holdings)
    if not holdings.exists():
        errors["pledgor_member_id"] = (
            "The sanctioned borrower must have active demat shareholding."
        )
    share_count = values["pledged_share_count"]
    if share_count is not None and share_count > available_shares:
        errors["pledged_share_count"] = (
            "Cannot exceed the borrower's retained available demat shares."
        )
    if values["pledgee_entity_name"] != SFPCL_ENTITY_NAME:
        errors["pledgee_entity_name"] = "Pledgee must be SFPCL."
    pledgor_hash = identity_hash(values["pledgor_bo_account"])
    pledgee_hash = (
        identity_hash(values["pledgee_bo_account"])
        if values["pledgee_bo_account"] else None
    )
    if pledgee_hash and pledgee_hash == pledgor_hash:
        errors["pledgee_bo_account"] = (
            "Pledgor and pledgee BO accounts must be distinct."
        )
    evidence = None
    if values["evidence_document_id"] is not None:
        evidence = require_coordinated(evidence_access).cdsl_evidence(
            application_id=package.loan_application_id,
            evidence_document_id=values["evidence_document_id"],
        )
        if evidence is None:
            errors["evidence_document_id"] = (
                "Must reference current CDSL evidence for this application."
            )
    if values["pledge_status"] == "created" and values["pledge_acceptance_status"] != "accepted":
        errors["pledge_status"] = "Created pledge requires accepted evidence."
    if errors:
        raise ValidationError(errors)
    return {
        "pledgor_member_id": values["pledgor_member_id"],
        "pledgee_entity_name": values["pledgee_entity_name"],
        "pledgor_bo_account_encrypted": sealed_protected_identity_token(
            values["pledgor_bo_account"], 16
        ),
        "pledgor_bo_account_hash": pledgor_hash,
        "pledgee_bo_account_encrypted": (
            sealed_protected_identity_token(values["pledgee_bo_account"], 16)
            if values["pledgee_bo_account"] else None
        ),
        "pledgee_bo_account_hash": pledgee_hash,
        "pledgor_dp_name": values["pledgor_dp_name"],
        "pledgee_dp_name": values["pledgee_dp_name"],
        "prf_status": values["prf_status"],
        "pledge_sequence_number": values["pledge_sequence_number"],
        "pledge_acceptance_status": values["pledge_acceptance_status"],
        "pledged_share_count": values["pledged_share_count"],
        "agreement_number": values["agreement_number"],
        "pledge_status": values["pledge_status"],
        "evidence_loan_document": evidence,
    }
def _project(package, evidence_document, evidence_access):
    require_coordinated(evidence_access).project_checklist_item(
        application_id=package.loan_application_id,
        item_code="cdsl_pledge",
        document=evidence_document,
    )
def serialize_pledge(pledge):
    return {
        "cdsl_share_pledge_id": str(pledge.pk),
        "security_package_id": str(pledge.security_package_id),
        "pledgor_member_id": str(pledge.pledgor_member_id),
        "pledgee_entity_name": pledge.pledgee_entity_name,
        "pledgor_bo_account": mask_protected_identity(
            pledge.pledgor_bo_account_encrypted, 16
        ),
        "pledgee_bo_account": mask_protected_identity(
            pledge.pledgee_bo_account_encrypted, 16
        ),
        "pledgor_dp_name": pledge.pledgor_dp_name,
        "pledgee_dp_name": pledge.pledgee_dp_name,
        "prf_status": pledge.prf_status,
        "pledge_sequence_number": pledge.pledge_sequence_number,
        "pledge_acceptance_status": pledge.pledge_acceptance_status,
        "pledged_share_count": pledge.pledged_share_count,
        "agreement_number": pledge.agreement_number,
        "pledge_status": pledge.pledge_status,
        "future_shares_pledged_flag": pledge.future_shares_pledged_flag,
        "evidence_document_id": (
            str(pledge.evidence_document_id) if pledge.evidence_document_id else None
        ),
        "created_at_cdsl": (
            pledge.created_at_cdsl.isoformat().replace("+00:00", "Z")
            if pledge.created_at_cdsl else None
        ),
        "prepared_by_user_id": str(pledge.prepared_by_user_id),
        "verified_by_user_id": (
            str(pledge.verified_by_user_id) if pledge.verified_by_user_id else None
        ),
        "acceptance_evidence": pledge.acceptance_evidence_json or None,
    }
def _matches(pledge, values):
    evidence = values["evidence_loan_document"]
    return (
        pledge.pledgor_member_id == values["pledgor_member_id"]
        and pledge.pledgee_entity_name == values["pledgee_entity_name"]
        and pledge.pledgor_bo_account_hash == values["pledgor_bo_account_hash"]
        and pledge.pledgee_bo_account_hash == values["pledgee_bo_account_hash"]
        and pledge.pledgor_dp_name == values["pledgor_dp_name"]
        and pledge.pledgee_dp_name == values["pledgee_dp_name"]
        and pledge.prf_status == values["prf_status"]
        and pledge.pledge_sequence_number == values["pledge_sequence_number"]
        and pledge.pledge_acceptance_status == values["pledge_acceptance_status"]
        and pledge.pledged_share_count == values["pledged_share_count"]
        and pledge.agreement_number == values["agreement_number"]
        and pledge.pledge_status == values["pledge_status"]
        and pledge.evidence_document_id == (evidence.document_id if evidence else None)
    )
def _record_evidence(actor, pledge, action, old, metadata, record_workflow=True):
    snapshot = {
        **serialize_pledge(pledge),
        "loan_application_id": str(pledge.security_package.loan_application_id),
    }
    record_security_evidence(
        actor=actor,
        entity_type="cdsl_share_pledge",
        entity_id=pledge.pk,
        action=action,
        old=old,
        snapshot=snapshot,
        metadata=metadata,
        workflow_name="cdsl_share_pledge",
        from_state=old.get("pledge_status"),
        to_state=pledge.pledge_status,
        record_workflow=record_workflow,
    )
def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
