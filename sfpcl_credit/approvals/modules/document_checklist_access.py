"""Single owner-facing authority boundary for document-checklist reads."""

from dataclasses import dataclass

from django.db.models import Exists, OuterRef, Q, Subquery

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.approvals.modules.read_scope import (
    evaluate_approval_case_read_scope,
    resolve_persisted_role_scope,
)
from sfpcl_credit.identity.modules import auth_service


READ_PERMISSION = "documents.checklist.read"
LEGACY_READ_PERMISSION = "applications.loan_application.read"
ROUTE_POST_SANCTION = "post_sanction"
ROUTE_PRE_SANCTION = "pre_sanction"


def scope_post_sanction_checklists(*, actor, queryset):
    """Apply the same governed object scope as detail reads to a checklist queryset."""
    permissions = set(auth_service.effective_permission_codes(actor))
    if not actor.can_authenticate() or READ_PERMISSION not in permissions:
        return queryset.none(), "FORBIDDEN"
    queryset = queryset.filter(
        loan_application__application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION
    )
    roles = set(actor.role_codes())
    if roles & {
        "compliance_team_member", "company_secretary", "credit_manager",
        "internal_auditor",
    }:
        return queryset, None
    if "senior_manager_finance" in roles:
        return queryset.filter(checklist_status="sanction_approved"), None
    if "chief_financial_controller" in roles:
        return queryset.none(), None
    if resolve_persisted_role_scope(actor):
        return queryset, None
    latest_cases = ApprovalCase.objects.filter(
        loan_application_id=OuterRef("loan_application_id")
    ).order_by("-cycle_number", "-submitted_at")
    queryset = queryset.annotate(
        latest_case_id=Subquery(latest_cases.values("pk")[:1])
    )
    attributable_latest_case = ApprovalCase.objects.filter(
        pk=OuterRef("latest_case_id")
    ).filter(
        Q(required_approver_index__user_id=actor.pk)
        | Q(actions__approver_user_id=actor.pk)
    )
    return queryset.annotate(
        actor_can_read_latest_case=Exists(attributable_latest_case)
    ).filter(actor_can_read_latest_case=True), None


@dataclass(frozen=True)
class ChecklistReadResolution:
    route: str | None
    application: LoanApplication | None
    attribution: str
    error_code: str | None = None


def resolve_read_access(*, actor, application_id):
    """Resolve compatibility route and object scope before checklist ORM access."""
    permissions = auth_service.effective_permission_codes(actor)
    legacy_read = LEGACY_READ_PERMISSION in permissions
    if (
        not actor.can_authenticate()
        or (READ_PERMISSION not in permissions and not legacy_read)
    ):
        return ChecklistReadResolution(None, None, "global_permission", "FORBIDDEN")

    application = (
        LoanApplication.objects.select_related("created_by_user", "received_by_user")
        .filter(pk=application_id)
        .first()
    )
    if application is None:
        if READ_PERMISSION in permissions and "compliance_team_member" in actor.role_codes():
            return ChecklistReadResolution(None, None, "documentation_absent_parent", "NOT_FOUND")
        if legacy_read:
            return ChecklistReadResolution(
                ROUTE_PRE_SANCTION, None, "legacy_application_route"
            )
        return ChecklistReadResolution(
            None, None, "absent_parent_nondisclosure", "OBJECT_ACCESS_DENIED"
        )
    if application.application_status != LoanApplication.STATUS_APPROVED_BY_SANCTION:
        return ChecklistReadResolution(
            ROUTE_PRE_SANCTION, application, "legacy_application_route"
        )
    if READ_PERMISSION not in permissions:
        return ChecklistReadResolution(None, application, "global_permission", "FORBIDDEN")

    case = (
        application.sanction_approval_cases.prefetch_related("actions")
        .order_by("-cycle_number", "-submitted_at")
        .first()
    )
    if case is None:
        return ChecklistReadResolution(
            None, application, "missing_approval_scope", "OBJECT_ACCESS_DENIED"
        )
    access = _evaluate_post_sanction_scope(
        actor=actor,
        application=application,
        case=case,
        actor_permissions=permissions,
    )
    if not access.allowed:
        return ChecklistReadResolution(
            None, application, access.attribution, "OBJECT_ACCESS_DENIED"
        )
    return ChecklistReadResolution(
        ROUTE_POST_SANCTION, application, access.attribution
    )


@dataclass(frozen=True)
class _PostSanctionScope:
    allowed: bool
    attribution: str


def _evaluate_post_sanction_scope(*, actor, application, case, actor_permissions):
    """Return the source-attributed application/case scope for a sanctioned package."""
    roles = set(actor.role_codes())
    if "senior_manager_finance" in roles:
        checklist = getattr(application, "legal_document_checklist", None)
        return _PostSanctionScope(
            bool(checklist and checklist.checklist_status == "sanction_approved"),
            "documentation_approved_pending_disbursement_scope",
        )
    if "chief_financial_controller" in roles:
        return _PostSanctionScope(False, "disbursement_readiness_not_yet_available")
    # Source §19.2 defines these roles' application scope as the sanctioned
    # documentation queue itself; the status predicate is their canonical row scope.
    if roles & {
        "compliance_team_member",
        "company_secretary",
        "credit_manager",
        "internal_auditor",
    }:
        return _PostSanctionScope(True, "sanctioned_documentation_application_scope")
    approval_scope = evaluate_approval_case_read_scope(
        actor=actor,
        case=case,
        actor_permissions=actor_permissions,
    )
    if approval_scope.allowed:
        return _PostSanctionScope(True, approval_scope.attribution)
    return _PostSanctionScope(False, "no_checklist_object_scope")
