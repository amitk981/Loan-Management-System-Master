from django.db.models import OuterRef, Subquery

from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.monitoring.models import DpdStatus
from sfpcl_credit.reports.errors import (
    ReportPermissionDenied,
    ReportValidation,
)
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import as_of_date, reject_unknown


PERMISSION = "reports.dpd.read"
OWNER_PERMISSION = "monitoring.dpd.read"
SOP_BUCKETS = {
    "current",
    "one_to_two_years",
    "two_to_three_years",
    "more_than_three_years",
}


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {"as_of_date", "sop_bucket", "page", "page_size"},
    )
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or PERMISSION not in permissions
        or OWNER_PERMISSION not in permissions
    ):
        raise ReportPermissionDenied
    try:
        scoped_accounts = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    cutoff = as_of_date(query_params)
    latest_id = (
        DpdStatus.objects.filter(
            loan_account_id=OuterRef("loan_account_id"),
            as_of_date__lte=cutoff,
        )
        .order_by("-as_of_date", "-created_at", "-dpd_status_id")
        .values("dpd_status_id")[:1]
    )
    queryset = (
        DpdStatus.objects.select_related("loan_account__member")
        .filter(
            loan_account__in=scoped_accounts,
            dpd_status_id=Subquery(latest_id),
        )
    )
    bucket = query_params.get("sop_bucket")
    if bucket:
        if bucket not in SOP_BUCKETS:
            raise ReportValidation({"sop_bucket": "Unsupported SOP bucket."})
        queryset = queryset.filter(sop_bucket=bucket)
    rows, pagination = paginate(
        queryset.order_by(
            "-days_past_due",
            "loan_account__loan_account_number",
            "dpd_status_id",
        ),
        query_params,
    )
    return [_serialize(row) for row in rows], pagination


def _serialize(row):
    account = row.loan_account
    return {
        "dpd_status_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_account_number": account.loan_account_number,
        "member_id": str(account.member_id),
        "borrower_name": account.member.display_name,
        "as_of_date": row.as_of_date.isoformat(),
        "days_past_due": row.days_past_due,
        "sop_bucket": row.sop_bucket,
        "standard_bucket": row.standard_bucket,
        "principal_overdue_amount": f"{row.principal_overdue_amount:.2f}",
        "interest_overdue_amount": f"{row.interest_overdue_amount:.2f}",
        "total_overdue_amount": f"{row.total_overdue_amount:.2f}",
        "earliest_unpaid_due_date": (
            row.earliest_unpaid_due_date.isoformat()
            if row.earliest_unpaid_due_date
            else None
        ),
        "loan_account_status": account.loan_account_status,
        "principal_outstanding": f"{account.principal_outstanding:.2f}",
    }
