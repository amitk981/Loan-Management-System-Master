from django.db.models import Sum

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import inclusive_date_range, reject_unknown
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission


PERMISSION = "finance.disbursement.readiness"
AUTHORISATION_STATUSES = {"pending", "approved", "rejected"}
TRANSFER_STATUSES = {"pending", "processing", "successful", "failed", "reversed"}


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {
            "from_date",
            "to_date",
            "authorisation_status",
            "bank_transfer_status",
            "page",
            "page_size",
        },
    )
    require_permission(actor=actor, permission=PERMISSION)
    try:
        accounts = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    queryset = Disbursement.objects.select_related(
        "loan_account__member",
        "initiated_by_user",
        "authorised_by_user",
    ).filter(loan_account__in=accounts)
    from_date, to_date = inclusive_date_range(query_params)
    if from_date:
        queryset = queryset.filter(initiated_at__date__gte=from_date)
    if to_date:
        queryset = queryset.filter(initiated_at__date__lte=to_date)
    queryset = _controlled_filter(
        queryset,
        query_params,
        "authorisation_status",
        AUTHORISATION_STATUSES,
    )
    queryset = _controlled_filter(
        queryset,
        query_params,
        "bank_transfer_status",
        TRANSFER_STATUSES,
    )
    total = queryset.aggregate(value=Sum("disbursement_amount"))["value"]
    rows, pagination = paginate(
        queryset.order_by("-initiated_at", "-disbursement_id"),
        query_params,
    )
    pagination["totals"] = {
        "disbursement_amount": f"{(total or 0):.2f}",
    }
    return [_serialize(row) for row in rows], pagination


def _controlled_filter(queryset, query_params, field, allowed):
    value = query_params.get(field)
    if not value:
        return queryset
    if value not in allowed:
        raise ReportValidation({field: "Unsupported status."})
    return queryset.filter(**{field: value})


def _serialize(row):
    account = row.loan_account
    return {
        "disbursement_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_account_number": account.loan_account_number,
        "loan_application_id": str(row.loan_application_id),
        "member_id": str(row.member_id),
        "borrower_name": account.member.display_name,
        "disbursement_amount": f"{row.disbursement_amount:.2f}",
        "payment_method": row.payment_method,
        "initiation_status": row.initiation_status,
        "authorisation_status": row.authorisation_status,
        "bank_transfer_status": row.bank_transfer_status,
        "bank_reference_number": row.bank_reference_number,
        "initiated_at": _timestamp(row.initiated_at),
        "authorised_at": (
            _timestamp(row.authorised_at) if row.authorised_at else None
        ),
        "disbursed_at": (
            _timestamp(row.disbursed_at) if row.disbursed_at else None
        ),
    }


def _timestamp(value):
    return value.isoformat().replace("+00:00", "Z")
