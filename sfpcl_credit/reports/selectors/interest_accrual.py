import re

from django.db.models import Sum

from sfpcl_credit.interest.models import AccrualEntry
from sfpcl_credit.interest.modules.interest_engine import serialize_accrual
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import reject_unknown
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission


PERMISSION = "finance.loan_account.read"
MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {"accrual_month", "sap_posting_status", "page", "page_size"},
    )
    require_permission(actor=actor, permission=PERMISSION)
    try:
        accounts = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    queryset = AccrualEntry.objects.filter(loan_account__in=accounts)
    month = query_params.get("accrual_month")
    if month:
        if MONTH_PATTERN.fullmatch(month) is None:
            raise ReportValidation({"accrual_month": "Use YYYY-MM."})
        queryset = queryset.filter(accrual_month=month)
    status = query_params.get("sap_posting_status")
    if status:
        if status not in AccrualEntry.STATUSES:
            raise ReportValidation(
                {"sap_posting_status": "Unsupported SAP posting status."}
            )
        queryset = queryset.filter(posted_status=status)
    total = queryset.aggregate(value=Sum("interest_accrued_amount"))["value"]
    rows, pagination = paginate(
        queryset.order_by("-accrual_month", "-accrual_entry_id"),
        query_params,
    )
    pagination["totals"] = {
        "interest_accrued_amount": f"{(total or 0):.2f}",
    }
    return [serialize_accrual(row) for row in rows], pagination
