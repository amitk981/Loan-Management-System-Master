from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.security_instruments.evidence_contract import require_coordinated
from sfpcl_credit.security_instruments.models import BlankDatedCheque
from sfpcl_credit.security_instruments.request_contracts import BlankDatedChequeRequest
from sfpcl_credit.security_instruments.modules import security_package
from sfpcl_credit.security_instruments.modules.evidence_recorder import record_security_evidence
from sfpcl_credit.shared.encryption import FieldEncryption
from sfpcl_credit.workflows.events import record_workflow_event


MANAGE_PERMISSION = "security.blank_cheque.manage"
READ_PERMISSION = security_package.READ_PERMISSION
RequestMetadata = security_package.RequestMetadata
AccessDenied = security_package.AccessDenied
NotFound = security_package.NotFound
Conflict = security_package.Conflict


def require_manage_actor(actor):
    security_package.require_actor(actor, MANAGE_PERMISSION)


def read_cheque(*, actor, security_package_id, evidence_access):
    package = security_package.resolve_package(
        actor, security_package_id, READ_PERMISSION, evidence_access=evidence_access
    )
    cheque = BlankDatedCheque.objects.filter(security_package=package).first()
    if cheque is None:
        raise NotFound
    return serialize_cheque(cheque)


def create_cheque(*, actor, security_package_id, values, metadata, evidence_access):
    require_manage_actor(actor)
    if "compliance_team_member" not in auth_service.effective_role_codes(actor):
        raise AccessDenied
    with transaction.atomic():
        package = security_package.resolve_package(
            actor, security_package_id, MANAGE_PERMISSION, for_update=True,
            evidence_access=evidence_access,
        )
        cleaned = _resolve_values(package, values, evidence_access)
        retained = (
            BlankDatedCheque.objects.select_for_update()
            .filter(security_package=package)
            .first()
        )
        if retained is not None:
            if _matches(retained, cleaned):
                return serialize_cheque(retained)
            raise Conflict("A blank-dated cheque already exists; use PATCH.")
        if cleaned["cheque_status"] != BlankDatedCheque.STATUS_COLLECTED:
            raise ValidationError(
                {"cheque_status": "Compliance may create only collected preparation facts."}
            )
        _project(package, evidence_access)
        try:
            cheque = BlankDatedCheque.objects.create(
                security_package=package,
                prepared_by_user=actor,
                **cleaned,
            )
        except IntegrityError as exc:
            raise Conflict("This blank-dated cheque is already retained.") from exc
        _record_evidence(
            actor, cheque, "security.blank_cheque.collected", {}, metadata,
            evidence_access=evidence_access,
        )
        return serialize_cheque(cheque)


def update_cheque(
    *, actor, blank_dated_cheque_id, values, metadata, evidence_access
):
    require_manage_actor(actor)
    with transaction.atomic():
        cheque = (
            BlankDatedCheque.objects.select_for_update(of=("self",))
            .select_related("security_package__loan_application")
            .filter(pk=blank_dated_cheque_id)
            .first()
        )
        if cheque is None or not security_package.has_canonical_stage4_scope(
            cheque.security_package.loan_application_id, evidence_access
        ):
            raise NotFound
        candidate = (
            values
            if set(values) == BlankDatedChequeRequest.FIELDS
            and not isinstance(values.get("collected_at"), str)
            else BlankDatedChequeRequest.parse(
                values if set(values) == BlankDatedChequeRequest.FIELDS
                else _merge_locked_candidate(cheque, values)
            ).as_values()
        )
        cleaned = _resolve_values(
            cheque.security_package,
            candidate,
            evidence_access,
        )
        if _matches(cheque, cleaned):
            if cheque.cheque_status == BlankDatedCheque.STATUS_HELD:
                return _custody_action(cheque)
            return serialize_cheque(cheque)
        if cheque.cheque_status == BlankDatedCheque.STATUS_HELD:
            raise Conflict("Held blank-dated cheque custody is terminal in this workflow.")
        terminal = cleaned["cheque_status"] == BlankDatedCheque.STATUS_HELD
        roles = set(auth_service.effective_role_codes(actor))
        if terminal:
            if "company_secretary" not in roles:
                raise AccessDenied
            if actor.pk == cheque.prepared_by_user_id:
                raise ValidationError(
                    {"cheque_status": "Custodian must be distinct from the Compliance preparer."}
                )
            retained = _material(cheque)
            proposed = _cleaned_material(cleaned)
            if retained != proposed:
                raise ValidationError(
                    {"cheque_status": "Custody must consume the exact retained Compliance facts."}
                )
            cleaned["cheque_number_encrypted"] = cheque.cheque_number_encrypted
        elif "compliance_team_member" not in roles:
            raise AccessDenied
        old = serialize_cheque(cheque)
        _project(cheque.security_package, evidence_access)
        workflow = None
        custody_evidence = {}
        if terminal:
            custody_evidence = _custody_evidence(
                cheque, cleaned, actor, metadata, evidence_access
            )
            workflow = record_workflow_event(
                actor=actor,
                workflow_name="blank_dated_cheque",
                entity_type="blank_dated_cheque",
                entity_id=cheque.pk,
                from_state=cheque.cheque_status,
                to_state=cleaned["cheque_status"],
                trigger_reason="security.blank_cheque.held",
                action_code="security.blank_cheque.held",
                metadata=custody_evidence,
            )
        for field, value in cleaned.items():
            setattr(cheque, field, value)
        if terminal:
            cheque.custodian_user = actor
            cheque.custody_evidence_json = custody_evidence
            cheque.custody_workflow_event_id = workflow.pk
        else:
            cheque.prepared_by_user = actor
        cheque.updated_at = timezone.now()
        cheque.save()
        action = "security.blank_cheque.held" if terminal else "security.blank_cheque.changed"
        _record_evidence(
            actor, cheque, action, old, metadata, record_workflow=not terminal,
            evidence_access=evidence_access,
        )
        return _custody_action(cheque) if terminal else serialize_cheque(cheque)


def sensitive_entity_facts(cheque):
    return {
        "entity_type": "blank_dated_cheque",
        "entity_id": cheque.pk,
        "related_ids": {
            "security_package_id": str(cheque.security_package_id),
            "loan_application_id": str(cheque.security_package.loan_application_id),
            "member_id": str(cheque.member_id),
            "bank_account_id": str(cheque.bank_account_id),
            "cancelled_cheque_id": str(cheque.cancelled_cheque_id),
        },
        "encrypted_fields": {"cheque_number": cheque.cheque_number_encrypted},
    }


def _custody_action(cheque):
    return {
        "entity_type": "blank_dated_cheque",
        "entity_id": str(cheque.pk),
        "previous_status": "collected",
        "new_status": "held",
        "workflow_event_id": str(cheque.custody_workflow_event_id),
        "available_actions": [],
    }


def serialize_cheque(cheque):
    return {
        "blank_dated_cheque_id": str(cheque.pk),
        "security_package_id": str(cheque.security_package_id),
        "member_id": str(cheque.member_id),
        "bank_account_id": str(cheque.bank_account_id),
        "cancelled_cheque_id": str(cheque.cancelled_cheque_id),
        "cancelled_cheque_document_id": str(cheque.cancelled_cheque.document_id),
        "cancelled_cheque": {
            "masked_bank_account": f"{'*' * 8}{cheque.bank_account.account_number_last4}",
            "ifsc": cheque.bank_account.ifsc,
            "branch_name": cheque.bank_account.branch_name or None,
            "verification_status": cheque.cancelled_cheque.verification_status,
        },
        "cheque_number": "******",
        "document_id": str(cheque.document_id) if cheque.document_id else None,
        "cheque_status": cheque.cheque_status,
        "custody_location": cheque.custody_location,
        "collected_at": cheque.collected_at.isoformat(),
        "prepared_by_user_id": str(cheque.prepared_by_user_id),
        "custodian_user_id": (
            str(cheque.custodian_user_id) if cheque.custodian_user_id else None
        ),
        "custody_evidence": cheque.custody_evidence_json or None,
    }


def _resolve_values(package, values, evidence_access):
    errors = {}
    access = require_coordinated(evidence_access)
    fact = access.blank_cheque_bank_fact(application_id=package.loan_application_id)
    if not fact.valid:
        errors["bank_account_id"] = fact.blocker
    else:
        if values["member_id"] != fact.member_id:
            errors["member_id"] = "Must be the sanctioned borrower."
        if values["bank_account_id"] != fact.bank_account_id:
            errors["bank_account_id"] = "Must be the retained verified application bank account."
    if not package.blank_cheque_required_flag or not package.cancelled_cheque_required_flag:
        errors["bank_account_id"] = "Refresh canonical cheque requirements before capture."
    document = None
    if values["document_id"] is not None:
        document = access.blank_cheque_scan(
            application_id=package.loan_application_id,
            document_id=values["document_id"],
        )
        if document is None:
            errors["document_id"] = "Must reference an exact same-application public upload."
    if errors:
        raise ValidationError(errors)
    return {
        "member_id": fact.member_id,
        "bank_account_id": fact.bank_account_id,
        "cancelled_cheque_id": fact.cancelled_cheque_id,
        "cheque_number_encrypted": FieldEncryption.encrypt(
            "blank_cheque.cheque_number", values["cheque_number"]
        ),
        "cheque_number_hash": FieldEncryption.hash_for_lookup(
            "blank_cheque.cheque_number", values["cheque_number"]
        ),
        "document_id": document.pk if document else None,
        "cheque_status": values["cheque_status"],
        "custody_location": values["custody_location"],
        "collected_at": values["collected_at"],
    }


def _merge_locked_candidate(cheque, values):
    candidate = {
        "member_id": cheque.member_id,
        "bank_account_id": cheque.bank_account_id,
        "cheque_number": FieldEncryption.decrypt(
            "blank_cheque.cheque_number", cheque.cheque_number_encrypted
        ),
        "document_id": cheque.document_id,
        "cheque_status": cheque.cheque_status,
        "custody_location": cheque.custody_location,
        "collected_at": cheque.collected_at.isoformat(),
    }
    candidate.update(values)
    return candidate


def _project(package, evidence_access):
    require_coordinated(evidence_access).project_checklist_item(
        application_id=package.loan_application_id,
        item_code="blank_dated_cheque",
        document=None,
    )


def _matches(cheque, values):
    return _material(cheque) == _cleaned_material(values) and (
        cheque.cheque_status == values["cheque_status"]
        and cheque.custody_location == values["custody_location"]
    )


def _material(cheque):
    return {
        "member_id": cheque.member_id,
        "bank_account_id": cheque.bank_account_id,
        "cancelled_cheque_id": cheque.cancelled_cheque_id,
        "cheque_number_hash": cheque.cheque_number_hash,
        "document_id": cheque.document_id,
        "collected_at": cheque.collected_at,
    }


def _cleaned_material(values):
    return {
        key: values[key]
        for key in (
            "member_id", "bank_account_id", "cancelled_cheque_id",
            "cheque_number_hash", "document_id", "collected_at",
        )
    }


def _custody_evidence(cheque, cleaned, actor, metadata, evidence_access):
    fact = require_coordinated(evidence_access).blank_cheque_bank_fact(
        application_id=cheque.security_package.loan_application_id
    )
    return {
        **_snapshot_values(cheque, cleaned),
        "cancelled_cheque_document_id": str(fact.cancelled_cheque_document_id),
        "blank_cheque_prepared_by_user_id": str(cheque.prepared_by_user_id),
        "blank_cheque_custodian_user_id": str(actor.pk),
        "request_id": metadata.request_id,
        "ip_address": metadata.ip_address,
        "user_agent": metadata.user_agent,
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "actor_team_codes": actor.team_codes(),
    }


def _snapshot_values(cheque, values):
    return {
        "loan_application_id": str(cheque.security_package.loan_application_id),
        "security_package_id": str(cheque.security_package_id),
        "member_id": str(values["member_id"]),
        "bank_account_id": str(values["bank_account_id"]),
        "cancelled_cheque_id": str(values["cancelled_cheque_id"]),
        "cheque_number": "******",
        "document_id": str(values["document_id"]) if values["document_id"] else None,
        "cheque_status": values["cheque_status"],
        "custody_location": values["custody_location"],
        "collected_at": values["collected_at"].isoformat(),
    }


def _record_evidence(
    actor, cheque, action, old, metadata, *, evidence_access, record_workflow=True
):
    snapshot = {
        **serialize_cheque(cheque),
        "loan_application_id": str(cheque.security_package.loan_application_id),
        "cheque_hash": cheque.cheque_number_hash,
    }
    record_security_evidence(
        actor=actor,
        entity_type="blank_dated_cheque",
        entity_id=cheque.pk,
        action=action,
        old=old,
        snapshot=snapshot,
        metadata=metadata,
        workflow_name="blank_dated_cheque",
        from_state=old.get("cheque_status"),
        to_state=cheque.cheque_status,
        record_workflow=record_workflow,
    )


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
