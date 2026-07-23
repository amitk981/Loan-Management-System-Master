from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.reports.errors import ReportPermissionDenied
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import reject_unknown


# Source §40.3 defines no report-specific permission. Slice 012A therefore maps
# this read to the existing owning readiness permission and canonical account scope.
PERMISSION = "finance.disbursement.readiness"


def select(*, actor, query_params):
    reject_unknown(query_params, {"page", "page_size"})
    permissions = set(auth_service.effective_permission_codes(actor))
    if not actor.can_authenticate() or PERMISSION not in permissions:
        raise ReportPermissionDenied
    try:
        accounts = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    queryset = (
        Disbursement.objects.select_related(
            "loan_account__member",
            "initiated_by_user",
            "authorised_by_user",
        )
        .filter(
            loan_account__in=accounts,
            authorisation_status__in={"pending", "approved"},
            bank_transfer_status__in={"pending", "processing"},
        )
    )
    rows, pagination = paginate(
        queryset.order_by("-initiated_at", "-disbursement_id"),
        query_params,
    )
    return [_serialize(row) for row in rows], pagination


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
        "initiation_status": row.initiation_status,
        "authorisation_status": row.authorisation_status,
        "bank_transfer_status": row.bank_transfer_status,
        "initiated_by_user_id": str(row.initiated_by_user_id),
        "initiated_by_name": row.initiated_by_user.full_name,
        "initiated_at": _timestamp(row.initiated_at),
        "authorised_by_user_id": (
            str(row.authorised_by_user_id)
            if row.authorised_by_user_id
            else None
        ),
        "authorised_at": (
            _timestamp(row.authorised_at) if row.authorised_at else None
        ),
    }


def _timestamp(value):
    return value.isoformat().replace("+00:00", "Z")
