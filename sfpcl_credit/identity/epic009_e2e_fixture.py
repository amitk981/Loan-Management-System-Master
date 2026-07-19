"""Reusable guarded fixture builder for the Epic 009 browser contract.

The management command consumes this single public builder instead of knowing the setup shape of
the backend regression suite.  The retained contract fixture remains the source of the unusually
deep documentation/security evidence until those owners expose a general synthetic-data factory.
"""

from sfpcl_credit.identity.models import Permission, RolePermission


def build_ready_epic009_fixture(*, password, finance_email, credit_email, cfc_email,
                                borrower_email):
    """Build and return the current owner-backed pre-initiation browser facts."""
    from sfpcl_credit.tests.test_final_documentation_approval_api import (
        FinalDocumentationApprovalApiTests,
    )

    owner = FinalDocumentationApprovalApiTests(
        "test_disbursement_readiness_real_owners_reach_a126_then_all_pass"
    )
    owner.setUp()
    finance = owner.finance
    credit = owner.credit
    _make_browser_actor(finance, finance_email, password)
    _make_browser_actor(credit, credit_email, password)
    ready = owner._real_owner_initiation_fixture(stop_before_initiation=True)
    ready["account"].member.email = borrower_email
    ready["account"].member.save(update_fields=["email"])
    _grant(
        finance,
        "finance.loan_account.read",
        "communications.notification.read",
        "finance.disbursement.mark_success",
        "finance.disbursement.send_advice",
    )
    advice_permission = Permission.objects.get(
        permission_code="finance.disbursement.send_advice"
    )
    advice_permission.risk_level = Permission.RISK_HIGH
    advice_permission.save(update_fields=["risk_level"])
    _grant(credit, "finance.loan_account.read", "communications.notification.read")

    cfc = owner.fixture._user(
        "chief_financial_controller", "Epic 009 Browser CFC"
    )
    _make_browser_actor(cfc, cfc_email, password)
    cfc.approval_authority_type = "chief_financial_controller"
    cfc.save(update_fields=["approval_authority_type"])
    _grant(
        cfc,
        "finance.disbursement.authorise",
        "finance.disbursement.mark_success",
        "finance.loan_account.read",
        "communications.notification.read",
    )
    return {
        "ready": ready,
        "finance": finance,
        "credit": credit,
        "cfc": cfc,
    }


def _make_browser_actor(user, email, password):
    user.email = email
    user.status = "active"
    user.set_password(password)
    user.save(update_fields=["email", "status", "password_hash"])


def _grant(user, *permission_codes):
    for code in permission_codes:
        permission, _ = Permission.objects.get_or_create(
            permission_code=code,
            defaults={"permission_name": code, "risk_level": Permission.RISK_CRITICAL},
        )
        RolePermission.objects.get_or_create(
            role=user.primary_role, permission=permission
        )


__all__ = ["build_ready_epic009_fixture"]
