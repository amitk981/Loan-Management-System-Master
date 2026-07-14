from dataclasses import dataclass
from django.db import transaction
from django.utils import timezone
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.security_instruments.evidence_contract import require_coordinated
from sfpcl_credit.security_instruments.models import SecurityPackage
from sfpcl_credit.security_instruments.modules.evidence_recorder import (
    record_security_evidence,
)
READ_PERMISSION = "security.package.read"
CREATE_PERMISSION = "security.package.create"
DIRECT_STAGE4_READ_ROLES = {
    "compliance_team_member",
    "company_secretary",
    "credit_manager",
}
FINANCE_STATE_SCOPED_READ_ROLES = {
    "senior_manager_finance", "chief_financial_controller"
}
APPROVAL_SCOPED_READ_ROLES = {"cfo", "director", "internal_auditor"}
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


def require_permission_actor(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
    ):
        raise AccessDenied


def require_actor(actor, permission):
    require_permission_actor(actor, permission)
    if (
        not {"compliance_team_member", "company_secretary"}.intersection(
            auth_service.effective_role_codes(actor)
        )
    ):
        raise AccessDenied


def require_create_actor(actor):
    require_actor(actor, CREATE_PERMISSION)


def read_package(*, actor, application_id, evidence_access):
    application = resolve_application(
        actor, application_id, READ_PERMISSION, evidence_access=evidence_access
    )
    package = SecurityPackage.objects.filter(loan_application=application).first()
    if package is None:
        raise NotFound
    return serialize_package(package, evidence_access)


def refresh_package(*, actor, application_id, metadata, evidence_access):
    with transaction.atomic():
        application = resolve_application(
            actor, application_id, CREATE_PERMISSION, for_update=True,
            evidence_access=evidence_access,
        )
        package = (
            SecurityPackage.objects.select_for_update()
            .filter(loan_application=application)
            .first()
        )
        facts = require_coordinated(evidence_access).approved_facts(
            application_id=application.pk
        )
        physical_required = facts is not None and facts.holding_mode == "physical"
        demat_required = facts is not None and facts.holding_mode == "demat"
        cheque_fact = require_coordinated(evidence_access).blank_cheque_bank_fact(
            application_id=application.pk
        )
        cheque_required = cheque_fact.valid
        if package is not None:
            if (
                package.physical_share_security_required_flag != physical_required
                or package.demat_pledge_required_flag != demat_required
                or package.blank_cheque_required_flag != cheque_required
                or package.cancelled_cheque_required_flag != cheque_required
            ):
                old = serialize_package(package, evidence_access)
                package.physical_share_security_required_flag = physical_required
                package.demat_pledge_required_flag = demat_required
                package.blank_cheque_required_flag = cheque_required
                package.cancelled_cheque_required_flag = cheque_required
                package.updated_at = timezone.now()
                package.save(update_fields=[
                    "physical_share_security_required_flag",
                    "demat_pledge_required_flag",
                    "blank_cheque_required_flag",
                    "cancelled_cheque_required_flag",
                    "updated_at",
                ])
                _record_change(actor, package, old, metadata, evidence_access)
            return serialize_package(package, evidence_access)
        package = SecurityPackage.objects.create(
            loan_application=application,
            physical_share_security_required_flag=physical_required,
            demat_pledge_required_flag=demat_required,
            blank_cheque_required_flag=cheque_required,
            cancelled_cheque_required_flag=cheque_required,
        )
        _record_creation(actor, package, metadata, evidence_access)
        return serialize_package(package, evidence_access)


def resolve_package(actor, package_id, permission, for_update=False, evidence_access=None):
    _require_target_authority(actor, permission)
    queryset = SecurityPackage.objects
    if for_update:
        queryset = queryset.select_for_update()
    package = queryset.select_related("loan_application").filter(pk=package_id).first()
    if package is None:
        raise NotFound
    if not has_canonical_stage4_scope(package.loan_application_id, evidence_access):
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    if permission == READ_PERMISSION and not _has_package_read_scope(
        actor, package.loan_application_id, evidence_access
    ):
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    return package


def resolve_application(
    actor, application_id, permission, for_update=False, evidence_access=None
):
    _require_target_authority(actor, permission)
    queryset = LoanApplication.objects
    if for_update:
        queryset = queryset.select_for_update()
    application = queryset.filter(pk=application_id).first()
    if application is None:
        raise NotFound
    if not has_canonical_stage4_scope(application.pk, evidence_access):
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    if permission == READ_PERMISSION and not _has_package_read_scope(
        actor, application.pk, evidence_access
    ):
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    return application


def _require_target_authority(actor, permission):
    if permission != READ_PERMISSION:
        require_actor(actor, permission)
        return
    require_permission_actor(actor, permission)
    roles = set(auth_service.effective_role_codes(actor))
    if not roles.intersection(
        DIRECT_STAGE4_READ_ROLES
        | FINANCE_STATE_SCOPED_READ_ROLES
        | APPROVAL_SCOPED_READ_ROLES
    ):
        raise AccessDenied("OBJECT_ACCESS_DENIED")


def _has_package_read_scope(actor, application_id, evidence_access):
    roles = set(auth_service.effective_role_codes(actor))
    if roles.intersection(FINANCE_STATE_SCOPED_READ_ROLES):
        return require_coordinated(evidence_access).finance_read_allowed(
            actor, application_id
        )
    if roles.intersection(DIRECT_STAGE4_READ_ROLES):
        return True
    return require_coordinated(evidence_access).approval_read_allowed(
        actor, application_id
    )


def has_canonical_stage4_scope(application_id, evidence_access):
    if not LoanApplication.objects.filter(
        pk=application_id,
        application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
    ).exists():
        return False
    return require_coordinated(evidence_access).canonical_stage4_scope(application_id)


def serialize_package(package, evidence_access):
    from sfpcl_credit.security_instruments.modules.cdsl_share_pledge import serialize_pledge
    from sfpcl_credit.security_instruments.modules.power_of_attorney import serialize_poa
    from sfpcl_credit.security_instruments.modules.sh4 import serialize_sh4
    from sfpcl_credit.security_instruments.modules.blank_dated_cheque import serialize_cheque

    poa = getattr(package, "power_of_attorney", None)
    sh4 = getattr(package, "sh4_share_transfer_form", None)
    cdsl = getattr(package, "cdsl_share_pledge", None)
    cheque = getattr(package, "blank_dated_cheque", None)
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
        "sh4_share_transfer_form": serialize_sh4(sh4) if sh4 else None,
        "cdsl_share_pledge": (
            serialize_pledge(cdsl, evidence_access) if cdsl else None
        ),
        "blank_dated_cheque": serialize_cheque(cheque) if cheque else None,
    }


def _record_creation(actor, package, metadata, evidence_access):
    record_security_evidence(
        actor=actor,
        action="security.package.created",
        entity_type="security_package",
        entity_id=package.pk,
        old={},
        snapshot=serialize_package(package, evidence_access),
        metadata=metadata,
        workflow_name="security_package",
        from_state=None,
        to_state=package.security_status,
        trigger_reason="Security package created for sanctioned application.",
    )


def _record_change(actor, package, old, metadata, evidence_access):
    record_security_evidence(
        actor=actor,
        action="security.package.requirements_changed",
        entity_type="security_package",
        entity_id=package.pk,
        old=old,
        snapshot=serialize_package(package, evidence_access),
        metadata=metadata,
        workflow_name="security_package",
        from_state=package.security_status,
        to_state=package.security_status,
    )
