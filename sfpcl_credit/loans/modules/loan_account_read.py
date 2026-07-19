"""Loan-owned authority and immutable creation truth for ordinary account reads."""

from django.db.models import F, Q

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.loans.modules.loan_account_lifecycle import (
    resolve_loan_account_creation,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    SapCustomerProfileModule,
)


READ_PERMISSION = "finance.loan_account.read"


class LoanAccountReadPermissionDenied(Exception):
    pass


def scoped_account_candidates(*, actor):
    """Return the canonical account candidate set after effective authority checks."""
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or READ_PERMISSION not in permissions
        or not roles.intersection(
            {
                "accounts_head",
                "cfo",
                "credit_manager",
                "senior_manager_finance",
                "chief_financial_controller",
                "company_secretary",
                "internal_auditor",
            }
        )
    ):
        raise LoanAccountReadPermissionDenied
    portfolio_scope = bool(roles.intersection({"accounts_head", "cfo"}))
    if "internal_auditor" in roles and ApprovalCaseReadScopeGrant.objects.filter(
        role__role_code="internal_auditor",
        scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
    ).exists():
        portfolio_scope = True
    if portfolio_scope:
        return LoanAccount.objects.order_by("-created_at", "loan_account_id")
    scope = Q(pk__in=[])
    if "credit_manager" in roles:
        scope |= Q(
            loan_account_status__in={
                "active",
                "partially_repaid",
                "overdue",
                "grace_period",
                "extended",
                "non_recoverable_under_review",
            }
        )
    if "senior_manager_finance" in roles:
        scope |= Q(
            loan_application__sap_customer_profile_requests__assigned_to_user=actor,
            loan_application__sap_customer_profile_requests__member_id=F("member_id"),
            loan_application__sap_customer_profile_requests__assigned_to_user__status="active",
            loan_application__sap_customer_profile_requests__assigned_to_user__primary_role__status="active",
            loan_application__sap_customer_profile_requests__assigned_to_user__primary_role__role_code="senior_manager_finance",
        )
    if "chief_financial_controller" in roles:
        scope |= Q(
            disbursements__cfc_task__recipient_role_code="chief_financial_controller",
            disbursements__authorisation_status__in=("pending", "approved", "rejected"),
        )
    if "company_secretary" in roles:
        scope |= Q(
            loan_application__application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION
        )
    return (
        LoanAccount.objects.filter(scope)
        .distinct()
        .order_by("-created_at", "loan_account_id")
    )


def scoped_initiation_candidates(*, actor):
    """Return exact Senior Finance initiation candidates without widening public reads."""
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or "senior_manager_finance" not in roles
        or "finance.disbursement.initiate" not in permissions
    ):
        raise LoanAccountReadPermissionDenied
    return (
        LoanAccount.objects.filter(
            loan_application__sap_customer_profile_requests__assigned_to_user=actor,
            loan_application__sap_customer_profile_requests__member_id=F("member_id"),
            loan_application__sap_customer_profile_requests__assigned_to_user__status="active",
            loan_application__sap_customer_profile_requests__assigned_to_user__primary_role__status="active",
            loan_application__sap_customer_profile_requests__assigned_to_user__primary_role__role_code="senior_manager_finance",
        )
        .distinct()
        .order_by("-created_at", "loan_account_id")
    )


def account_is_scoped(*, actor, account, cfc_scope_resolver):
    """Apply the source role's persisted portfolio/account scope to one candidate."""
    roles = set(auth_service.effective_role_codes(actor))
    if roles.intersection({"accounts_head", "cfo"}):
        return True
    if "credit_manager" in roles and account.loan_account_status in {
        "active",
        "partially_repaid",
        "overdue",
        "grace_period",
        "extended",
        "non_recoverable_under_review",
    }:
        return True
    if (
        "senior_manager_finance" in roles
        and SapCustomerProfileModule.is_current_finance_assignee(
            application_id=account.loan_application_id,
            member_id=account.member_id,
            actor_id=actor.pk,
        )
    ):
        return True
    if "chief_financial_controller" in roles and cfc_scope_resolver(account):
        return True
    if (
        "company_secretary" in roles
        and account.loan_application.application_status
        == LoanApplication.STATUS_APPROVED_BY_SANCTION
    ):
        return True
    return bool(
        "internal_auditor" in roles
        and ApprovalCaseReadScopeGrant.objects.filter(
            role__role_code="internal_auditor",
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        ).exists()
    )


def resolve_creation_truth(*, account):
    """Resolve immutable terms on top of the lifecycle owner's singular 009C ledger."""
    decision = resolve_loan_account_creation(loan_account_id=account.pk)
    if (
        decision is None
        or account.loan_application.member_id != account.member_id
        or account.sanction_decision.loan_application_id != account.loan_application_id
        or account.terms.loan_account_id != account.pk
        or account.sanctioned_amount != account.sanction_decision.sanctioned_amount
        or account.sanctioned_amount != account.terms.loan_amount
        or account.loan_type != account.terms.facility_type
        or account.interest_rate_type != account.terms.interest_rate_type
        or account.current_interest_rate != account.terms.rate_of_interest
        or account.repayment_date != account.terms.repayment_date
    ):
        return None
    return decision


__all__ = [
    "LoanAccountReadPermissionDenied",
    "account_is_scoped",
    "resolve_creation_truth",
    "scoped_account_candidates",
    "scoped_initiation_candidates",
]
