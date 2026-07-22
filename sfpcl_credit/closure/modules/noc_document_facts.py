"""Immutable closure facts exposed to the governed document-generation owner."""

from sfpcl_credit.closure.models import ClosureRequirement, LoanClosure


def project_for_generation(*, application_id):
    closure = (
        LoanClosure.objects.select_related("loan_account__loan_application", "member")
        .filter(
            loan_account__loan_application_id=application_id,
            closure_type=LoanClosure.TYPE_FULL_REPAYMENT,
            closure_stage=LoanClosure.STAGE_FINANCIALLY_CLOSED,
            principal_paid_flag=True,
            interest_paid_flag=True,
            charges_paid_flag=True,
            total_outstanding_at_closure=0,
            loan_account__loan_account_status="closed",
            requirements__requirement_type=ClosureRequirement.TYPE_NOC,
            requirements__requirement_status=ClosureRequirement.STATUS_PENDING,
        )
        .first()
    )
    if closure is None:
        return None
    return {
        "borrower_name": closure.member.legal_name,
        "loan_account_number": closure.loan_account.loan_account_number,
        "application_reference": (
            closure.loan_account.loan_application.application_reference_number
        ),
        "disbursed_amount": f"{closure.loan_account.disbursed_amount:.2f}",
        "full_repayment_date": closure.closed_at.date().isoformat(),
    }


__all__ = ["project_for_generation"]
