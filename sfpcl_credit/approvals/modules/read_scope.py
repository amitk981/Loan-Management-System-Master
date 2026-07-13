"""Persisted role scopes for read-only sanction-package access."""

from dataclasses import dataclass

from sfpcl_credit.applications.modules.application_authority import (
    evaluate_application_object_access,
)
from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.approvals.modules.conflict_of_interest import ConflictOfInterestModule
from sfpcl_credit.identity.modules.auth_service import effective_permission_codes
from sfpcl_credit.identity.models import Role


SOURCE_READ_SCOPE_GRANTS = (
    ("company_secretary", ApprovalCaseReadScopeGrant.SCOPE_LEGAL_READONLY),
    ("internal_auditor", ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY),
)


@dataclass(frozen=True)
class ApprovalCaseReadScopeDecision:
    allowed: bool
    scope_type: str | None
    attribution: str


def resolve_persisted_role_scope(actor):
    if actor.primary_role.status != "active":
        return None
    return (
        ApprovalCaseReadScopeGrant.objects.filter(
            role=actor.primary_role,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        )
        .order_by("scope_type")
        .values_list("scope_type", flat=True)
        .first()
    )


def evaluate_approval_case_read_scope(
    *,
    actor,
    case,
    persisted_scope_type=None,
    persisted_scope_resolved=False,
    actor_permissions=None,
):
    """Return the exact persisted or object-owned reason an actor can read a case."""
    actor_id = str(actor.pk)
    if ConflictOfInterestModule.conflict_reason(case=case, actor_id=actor_id):
        return ApprovalCaseReadScopeDecision(
            True, "conflict_limited_readonly", "case_exclusion"
        )
    if any(
        str(item.get("user_id")) == actor_id
        for item in ConflictOfInterestModule.effective_approvers(case)
    ):
        return ApprovalCaseReadScopeDecision(True, "approval_assigned", "case_snapshot")
    if any(
        isinstance(item, dict) and str(item.get("user_id")) == actor_id
        for item in case.required_approvers_json
    ):
        return ApprovalCaseReadScopeDecision(True, "approval_assigned", "case_snapshot")

    if not persisted_scope_resolved:
        persisted_scope_type = resolve_persisted_role_scope(actor)
    if persisted_scope_type:
        return ApprovalCaseReadScopeDecision(
            True, persisted_scope_type, "persisted_role_grant"
        )

    if "credit_manager" in actor.role_codes():
        if actor.pk == case.submitted_by_user_id:
            return ApprovalCaseReadScopeDecision(
                True, "credit_owned", "case_submitter"
            )
        permissions = actor_permissions or effective_permission_codes(actor)
        application_scope = evaluate_application_object_access(
            application=case.loan_application,
            actor=actor,
            required_permission="applications.loan_application.read",
            actor_permissions=permissions,
        )
        if application_scope.allowed:
            return ApprovalCaseReadScopeDecision(
                True, "credit_owned", "application_object_scope"
            )

    return ApprovalCaseReadScopeDecision(False, None, "no_object_scope")


def seed_default_read_scope_grants():
    """Idempotently ensure only the source-named default read-scope grants."""
    for role_code, scope_type in SOURCE_READ_SCOPE_GRANTS:
        role = Role.objects.get(role_code=role_code)
        ApprovalCaseReadScopeGrant.objects.get_or_create(
            role=role,
            scope_type=scope_type,
            defaults={"status": ApprovalCaseReadScopeGrant.STATUS_ACTIVE},
        )
