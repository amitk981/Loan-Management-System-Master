from dataclasses import dataclass
import re

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    LoanDocument,
    PowerOfAttorney,
    SecurityPackage,
)
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.workflows.events import record_workflow_event


READ_PERMISSION = "security.package.read"
CREATE_PERMISSION = "security.package.create"
MANAGE_PERMISSION = "security.poa.manage"


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


class AccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"):
        self.error_code = error_code


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


def require_manage_actor(actor):
    _require_actor(actor, MANAGE_PERMISSION)


def _require_actor(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
        or not {"compliance_team_member", "company_secretary"}.intersection(
            actor.role_codes()
        )
    ):
        raise AccessDenied


def read_package(*, actor, application_id):
    application = _resolve_application(actor, application_id, READ_PERMISSION)
    package = SecurityPackage.objects.filter(loan_application=application).first()
    if package is None:
        raise NotFound
    return serialize_package(package)


def refresh_package(*, actor, application_id, metadata):
    with transaction.atomic():
        application = _resolve_application(
            actor, application_id, CREATE_PERMISSION, for_update=True
        )
        package = (
            SecurityPackage.objects.select_for_update()
            .filter(loan_application=application)
            .first()
        )
        if package is not None:
            return serialize_package(package)
        package = SecurityPackage.objects.create(loan_application=application)
        _record_package_creation(actor, package, metadata)
        return serialize_package(package)


def read_poa(*, actor, security_package_id):
    package = _resolve_package(actor, security_package_id, READ_PERMISSION)
    poa = PowerOfAttorney.objects.filter(security_package=package).first()
    if poa is None:
        raise NotFound
    return serialize_poa(poa)


def create_poa(*, actor, security_package_id, values, metadata):
    with transaction.atomic():
        package = _resolve_package(
            actor, security_package_id, MANAGE_PERMISSION, for_update=True
        )
        cleaned = _resolve_poa_values(package, values, actor, allow_activation=False)
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
        _project_poa(package, cleaned["loan_document"], cleaned)
        poa = PowerOfAttorney.objects.create(
            security_package=package,
            prepared_by_user=actor,
            verified_by_user=None,
            **cleaned,
        )
        _record_poa_evidence(actor, poa, "security.poa.created", {}, metadata)
        return serialize_poa(poa)


def update_poa(*, actor, power_of_attorney_id, values, metadata):
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
        cleaned = _resolve_poa_values(package, values, actor, allow_activation=True)
        new_snapshot = _values_snapshot(cleaned)
        if _business_snapshot(poa) == new_snapshot:
            return serialize_poa(poa)
        activating = cleaned["status"] == "active"
        if activating:
            _validate_activation(poa, cleaned, actor)
        elif "compliance_team_member" not in actor.role_codes():
            raise _validation_error(
                {"status": "Only Compliance authority may change draft preparation facts."}
            )
        old = serialize_poa(poa)
        _project_poa(package, cleaned["loan_document"], cleaned)
        for field, value in cleaned.items():
            setattr(poa, field, value)
        poa.verified_by_user = actor if activating else None
        poa.updated_at = timezone.now()
        poa.save(update_fields=[*cleaned.keys(), "verified_by_user", "updated_at"])
        _record_poa_evidence(actor, poa, "security.poa.changed", old, metadata)
        return serialize_poa(poa)


def _resolve_package(actor, package_id, permission, for_update=False):
    _require_actor(actor, permission)
    queryset = SecurityPackage.objects
    if for_update:
        queryset = queryset.select_for_update()
    package = (
        queryset.select_related("loan_application").filter(pk=package_id).first()
    )
    if package is None:
        raise NotFound
    if (
        package.loan_application.application_status
        != LoanApplication.STATUS_APPROVED_BY_SANCTION
    ):
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    return package


def _resolve_poa_values(package, values, actor, allow_activation):
    from django.core.exceptions import ValidationError

    application = package.loan_application
    errors = {}
    if values["borrower_member_id"] != application.member_id:
        errors["borrower_member_id"] = "Must be the sanctioned application's borrower."
    if application.nominee_id is None or values["nominee_id"] != application.nominee_id:
        errors["nominee_id"] = "Must be the sanctioned application's selected nominee."
    attorney = (
        User.objects.select_related("primary_role")
        .filter(
            pk=values["attorney_user_id"],
            status=User.ACTIVE_STATUS,
            primary_role__role_code="company_secretary",
            primary_role__status="active",
        )
        .first()
    )
    if attorney is None:
        errors["attorney_user_id"] = "Must identify an active Company Secretary."
    words = " ".join(values["purpose_summary"].lower().split())
    explicit_authority = re.search(
        r"\bauthori[sz](?:e|es|ed) (?:the )?company secretary to initiate "
        r"(?:the )?sale of shares (?:on|upon) default\b",
        words,
    )
    negated = re.search(r"\b(?:not|never|prohibit(?:s|ed)?)\b", words)
    if explicit_authority is None or negated is not None:
        errors["purpose_summary"] = (
            "Must explicitly authorise the Company Secretary to initiate share sale on default."
        )
    document, stamp, notary = selectors.poa_evidence_for_update(
        application_id=application.pk,
        loan_document_id=values["loan_document_id"],
        stamp_duty_record_id=values["stamp_duty_record_id"],
        notarisation_record_id=values["notarisation_record_id"],
    )
    if (
        document is None
        or document.renderer_validation_status
        != LoanDocument.RENDERER_CURRENT_VALIDATED
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


def _validate_activation(poa, cleaned, actor):
    errors = {}
    if "company_secretary" not in actor.role_codes():
        errors["status"] = "Only Company Secretary authority may activate a Power of Attorney."
    if cleaned["attorney_user"].pk != actor.pk:
        errors["attorney_user_id"] = (
            "The activating Company Secretary must be the retained attorney."
        )
    if poa.prepared_by_user_id == actor.pk:
        errors["status"] = "The preparer and activating verifier must be different users."
    if cleaned["execution_status"] != "executed" or cleaned["effective_from"] is None:
        errors["execution_status"] = (
            "Active Power of Attorney requires executed status and effective_from."
        )
    stamp = cleaned["stamp_duty_record"]
    if (
        stamp.status != "adequate"
        or stamp.prepared_by_user_id is None
        or stamp.verified_by_user_id is None
        or stamp.prepared_by_user_id == stamp.verified_by_user_id
    ):
        errors["stamp_duty_record_id"] = (
            "Activation requires current adequate maker/checker stamp evidence."
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
    rows = selectors.execution_signature_facts_for_document(
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


def _project_poa(package, document, values):
    item = (
        ChecklistItem.objects.select_for_update()
        .filter(
            document_checklist__loan_application_id=package.loan_application_id,
            item_code="poa",
            applicable_flag=True,
            required_flag=True,
        )
        .first()
    )
    if item is None:
        raise Conflict("The required Power of Attorney checklist item was not found.")
    item.loan_document = document
    item.poa_execution_status = values["execution_status"]
    item.poa_status = values["status"]
    item.save(update_fields=["loan_document", "poa_execution_status", "poa_status"])


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
    }
    return {key: value for key, value in serialize_poa(poa).items() if key not in omitted}


def _resolve_application(actor, application_id, permission, for_update=False):
    _require_actor(actor, permission)
    queryset = LoanApplication.objects
    if for_update:
        queryset = queryset.select_for_update()
    application = queryset.filter(pk=application_id).first()
    if application is None:
        raise NotFound
    if application.application_status != LoanApplication.STATUS_APPROVED_BY_SANCTION:
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    return application


def serialize_package(package):
    poa = getattr(package, "power_of_attorney", None)
    return {
        "security_package_id": str(package.pk),
        "loan_application_id": str(package.loan_application_id),
        "loan_account_id": str(package.loan_account_id) if package.loan_account_id else None,
        "security_status": package.security_status,
        "physical_share_security_required_flag": package.physical_share_security_required_flag,
        "demat_pledge_required_flag": package.demat_pledge_required_flag,
        "poa_required_flag": package.poa_required_flag,
        "blank_cheque_required_flag": package.blank_cheque_required_flag,
        "cancelled_cheque_required_flag": package.cancelled_cheque_required_flag,
        "security_ready_flag": False,
        "power_of_attorney": serialize_poa(poa) if poa else None,
    }


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
    }


def _record_poa_evidence(actor, poa, action, old, metadata):
    context = {
        **serialize_poa(poa),
        "actor_role_codes": actor.role_codes(),
        "actor_team_codes": actor.team_codes(),
        "request_id": metadata.request_id,
        "ip_address": metadata.ip_address,
        "user_agent": metadata.user_agent,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="power_of_attorney",
        entity_id=poa.pk,
        old_value_json=old,
        new_value_json=context,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type="power_of_attorney",
        versioned_entity_id=poa.pk,
        version_number=str(
            VersionHistory.objects.filter(
                versioned_entity_type="power_of_attorney",
                versioned_entity_id=poa.pk,
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
        workflow_name="power_of_attorney",
        entity_type="power_of_attorney",
        entity_id=poa.pk,
        from_state=old.get("status"),
        to_state=poa.status,
        trigger_reason=action,
        action_code=action,
        metadata=context,
    )


def _record_package_creation(actor, package, metadata):
    context = {
        **serialize_package(package),
        "actor_role_codes": actor.role_codes(),
        "actor_team_codes": actor.team_codes(),
        "request_id": metadata.request_id,
        "ip_address": metadata.ip_address,
        "user_agent": metadata.user_agent,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="security.package.created",
        entity_type="security_package",
        entity_id=package.pk,
        old_value_json={},
        new_value_json=context,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type="security_package",
        versioned_entity_id=package.pk,
        version_number="1",
        change_summary="security.package.created",
        author_user=actor,
        old_value_json={},
        new_value_json=context,
        effective_from=timezone.localdate(),
    )
    record_workflow_event(
        actor=actor,
        workflow_name="security_package",
        entity_type="security_package",
        entity_id=package.pk,
        from_state=None,
        to_state=package.security_status,
        trigger_reason="Security package created for sanctioned application.",
        action_code="security.package.created",
        metadata=context,
    )


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}
