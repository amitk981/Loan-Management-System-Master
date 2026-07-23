from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.reports.errors import (
    ReportPermissionDenied,
    ReportValidation,
)
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import as_of_date, reject_unknown


PERMISSION = "reports.portfolio.read"
STATUSES = {
    "sanctioned",
    "active",
    "partially_repaid",
    "overdue",
    "grace_period",
    "extended",
    "non_recoverable_under_review",
    "closed",
}


def select(*, actor, query_params):
    reject_unknown(query_params, {"as_of_date", "status", "page", "page_size"})
    permissions = set(auth_service.effective_permission_codes(actor))
    if not actor.can_authenticate() or PERMISSION not in permissions:
        raise ReportPermissionDenied
    try:
        queryset = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    cutoff = as_of_date(query_params)
    queryset = queryset.select_related("member", "loan_application").filter(
        created_at__date__lte=cutoff
    )
    status = query_params.get("status")
    if status:
        if status not in STATUSES:
            raise ReportValidation({"status": "Unsupported loan account status."})
        queryset = queryset.filter(loan_account_status=status)
    rows, pagination = paginate(
        queryset.order_by("-created_at", "-loan_account_id"),
        query_params,
    )
    return [_serialize(row) for row in rows], pagination


def _serialize(row):
    return {
        "loan_account_id": str(row.pk),
        "loan_account_number": row.loan_account_number,
        "loan_application_id": str(row.loan_application_id),
        "member_id": str(row.member_id),
        "borrower_name": row.member.display_name,
        "loan_account_status": row.loan_account_status,
        "sanctioned_amount": f"{row.sanctioned_amount:.2f}",
        "disbursed_amount": f"{row.disbursed_amount:.2f}",
        "principal_outstanding": f"{row.principal_outstanding:.2f}",
        "interest_outstanding": f"{row.interest_outstanding:.2f}",
        "charges_outstanding": f"{row.charges_outstanding:.2f}",
        "total_outstanding": f"{row.total_outstanding:.2f}",
        "loan_type": row.loan_type,
        "tenure_start_date": (
            row.tenure_start_date.isoformat() if row.tenure_start_date else None
        ),
        "tenure_end_date": (
            row.tenure_end_date.isoformat() if row.tenure_end_date else None
        ),
        "repayment_date": row.repayment_date.isoformat(),
        "current_interest_rate": f"{row.current_interest_rate:.4f}",
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }
