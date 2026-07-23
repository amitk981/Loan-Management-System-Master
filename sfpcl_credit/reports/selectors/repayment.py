from django.db.models import Sum

from sfpcl_credit.loans.models import Repayment
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import inclusive_date_range, reject_unknown
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission


PERMISSION = "finance.loan_account.read"
SOURCES = {"direct_farmer", "subsidiary_deduction"}
ALLOCATION_STATUSES = {
    "pending",
    "allocated",
    "allocated_with_exception",
    "reversed",
}
SAP_STATUSES = {"pending", "posted"}


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {
            "from_date",
            "to_date",
            "repayment_source",
            "allocation_status",
            "sap_posting_status",
            "page",
            "page_size",
        },
    )
    require_permission(actor=actor, permission=PERMISSION)
    try:
        accounts = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    queryset = Repayment.objects.select_related(
        "loan_account",
        "member",
    ).filter(loan_account__in=accounts)
    from_date, to_date = inclusive_date_range(query_params)
    if from_date:
        queryset = queryset.filter(received_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(received_date__lte=to_date)
    for field, allowed in (
        ("repayment_source", SOURCES),
        ("allocation_status", ALLOCATION_STATUSES),
        ("sap_posting_status", SAP_STATUSES),
    ):
        queryset = _controlled_filter(queryset, query_params, field, allowed)
    total = queryset.aggregate(value=Sum("amount_received"))["value"]
    rows, pagination = paginate(
        queryset.order_by("-received_date", "-created_at", "-repayment_id"),
        query_params,
    )
    pagination["totals"] = {"amount_received": f"{(total or 0):.2f}"}
    return [_serialize(row) for row in rows], pagination


def _controlled_filter(queryset, query_params, field, allowed):
    value = query_params.get(field)
    if not value:
        return queryset
    if value not in allowed:
        raise ReportValidation({field: "Unsupported value."})
    return queryset.filter(**{field: value})


def _serialize(row):
    return {
        "repayment_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_account_number": row.loan_account.loan_account_number,
        "member_id": str(row.member_id),
        "borrower_name": row.member.display_name,
        "repayment_source": row.repayment_source,
        "amount_received": f"{row.amount_received:.2f}",
        "received_date": row.received_date.isoformat(),
        "payment_method": row.payment_method,
        "bank_reference_number": row.bank_reference_number,
        "allocation_status": row.allocation_status,
        "sap_posting_status": row.sap_posting_status,
    }
