from dataclasses import dataclass
from django.db import transaction
from django.utils import timezone
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.modules.document_checklist_facts import resolve_approved_facts
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.models import DocumentChecklist
from sfpcl_credit.security_instruments.models import SecurityPackage
from sfpcl_credit.workflows.events import record_workflow_event
READ_PERMISSION = "security.package.read"
CREATE_PERMISSION = "security.package.create"
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
def require_actor(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
        or not {"compliance_team_member", "company_secretary"}.intersection(
            auth_service.effective_role_codes(actor)
        )
    ):
        raise AccessDenied


def require_create_actor(actor):
    require_actor(actor, CREATE_PERMISSION)


def read_package(*, actor, application_id):
    application = resolve_application(actor, application_id, READ_PERMISSION)
    package = SecurityPackage.objects.filter(loan_application=application).first()
    if package is None:
        raise NotFound
    return serialize_package(package)


def refresh_package(*, actor, application_id, metadata):
    with transaction.atomic():
        application = resolve_application(
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
        _record_creation(actor, package, metadata)
        return serialize_package(package)


def resolve_package(actor, package_id, permission, for_update=False):
    require_actor(actor, permission)
    queryset = SecurityPackage.objects
    if for_update:
        queryset = queryset.select_for_update()
    package = queryset.select_related("loan_application").filter(pk=package_id).first()
    if package is None:
        raise NotFound
    if not has_canonical_stage4_scope(package.loan_application_id):
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    return package


def resolve_application(actor, application_id, permission, for_update=False):
    require_actor(actor, permission)
    queryset = LoanApplication.objects
    if for_update:
        queryset = queryset.select_for_update()
    application = queryset.filter(pk=application_id).first()
    if application is None:
        raise NotFound
    if not has_canonical_stage4_scope(application.pk):
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    return application


def has_canonical_stage4_scope(application_id):
    if not LoanApplication.objects.filter(
        pk=application_id,
        application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
    ).exists():
        return False
    facts = resolve_approved_facts(application_id=application_id)
    if facts is None:
        return False
    checklist = DocumentChecklist.objects.filter(loan_application_id=application_id).first()
    if checklist is None:
        return False
    creation_rows = list(
        AuditLog.objects.filter(
            action="document_checklist.created",
            entity_type="document_checklist",
            entity_id=checklist.pk,
        ).order_by("created_at", "audit_log_id")[:2]
    )
    if len(creation_rows) != 1:
        return False
    creation = creation_rows[0].new_value_json or {}
    return (
        creation.get("approval_case_id") == str(facts.approval_case_id)
        and creation.get("sanction_decision_id") == str(facts.sanction_decision_id)
    )


def serialize_package(package):
    from sfpcl_credit.security_instruments.modules.power_of_attorney import serialize_poa

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


def _record_creation(actor, package, metadata):
    context = {
        **serialize_package(package),
        "actor_role_codes": auth_service.effective_role_codes(actor),
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
