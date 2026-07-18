"""Read-only cross-owner projection for the initial Loan Account 360 view."""

from math import ceil

from django.db import transaction

from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    resolve_current_disbursement_evidence,
)
from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_post_transfer_evidence,
)
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    account_is_scoped,
    resolve_creation_truth,
    scoped_account_candidates,
)
from sfpcl_credit.sap_workflow.models import SapCustomerCode, SapCustomerProfileRequest


class LoanAccountProjectionNotFound(Exception):
    pass


class LoanAccountProjectionValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


@transaction.atomic
def list_accounts(*, actor, query_params):
    page, page_size = _pagination(query_params)
    projections = [
        projection
        for account in scoped_account_candidates(actor=actor).select_related(
            "loan_application",
            "member",
            "sanction_decision",
            "terms",
            "sap_customer_code",
        )
        if account_is_scoped(
            actor=actor, account=account, cfc_scope_resolver=_has_cfc_scope
        )
        and (projection := _project(account)) is not None
    ]
    total_count = len(projections)
    total_pages = ceil(total_count / page_size) if total_count else 1
    if page > total_pages:
        raise LoanAccountProjectionValidation({"page": "Page is out of range."})
    start = (page - 1) * page_size
    return projections[start : start + page_size], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


@transaction.atomic
def get_account(*, actor, loan_account_id):
    account = (
        scoped_account_candidates(actor=actor)
        .select_related(
            "loan_application",
            "member",
            "sanction_decision",
            "terms",
            "sap_customer_code",
        )
        .filter(pk=loan_account_id)
        .first()
    )
    projection = (
        _project(account)
        if account is not None
        and account_is_scoped(
            actor=actor, account=account, cfc_scope_resolver=_has_cfc_scope
        )
        else None
    )
    if projection is None:
        raise LoanAccountProjectionNotFound
    return projection


def _project(account):
    if resolve_creation_truth(account=account) is None:
        return None
    if account.sap_customer_code_id:
        if not _sap_is_current_for_account(account):
            return None
    activated_at = None
    if account.loan_account_status == "sanctioned":
        if any(
            value != 0
            for value in (
                account.disbursed_amount,
                account.principal_outstanding,
                account.interest_outstanding,
                account.charges_outstanding,
                account.total_outstanding,
            )
        ) or (
            account.tenure_start_date is not None
            or account.tenure_end_date is not None
        ):
            return None
    elif account.loan_account_status == "active":
        transfer = resolve_post_transfer_evidence(
            application_id=account.loan_application_id
        )
        if (
            transfer is None
            or transfer.loan_account_id != account.pk
            or transfer.loan_application_id != account.loan_application_id
            or transfer.member_id != account.member_id
            or transfer.amount != account.disbursed_amount
            or account.principal_outstanding != transfer.amount
            or account.total_outstanding != transfer.amount
            or account.interest_outstanding != 0
            or account.charges_outstanding != 0
            or account.tenure_start_date != transfer.disbursed_at.date()
        ):
            return None
        activated_at = transfer.disbursed_at
    else:
        return None
    return {
        "loan_account_id": str(account.pk),
        "loan_account_number": account.loan_account_number,
        "loan_application_id": str(account.loan_application_id),
        "application_reference_number": (
            account.loan_application.application_reference_number
        ),
        "member": {
            "member_id": str(account.member_id),
            "display_name": account.member.display_name,
        },
        "sap_customer_code": (
            account.sap_customer_code.sap_customer_code
            if account.sap_customer_code_id
            else None
        ),
        "loan_type": account.loan_type,
        "facility_type": account.terms.facility_type,
        "interest_rate_type": account.interest_rate_type,
        "current_interest_rate": _decimal(account.current_interest_rate, 4),
        "sanctioned_amount": _decimal(account.sanctioned_amount),
        "disbursed_amount": _decimal(account.disbursed_amount),
        "principal_outstanding": _decimal(account.principal_outstanding),
        "interest_outstanding": _decimal(account.interest_outstanding),
        "charges_outstanding": _decimal(account.charges_outstanding),
        "total_outstanding": _decimal(account.total_outstanding),
        "loan_account_status": account.loan_account_status,
        "tenure_start_date": _date(account.tenure_start_date),
        "tenure_end_date": _date(account.tenure_end_date),
        "repayment_date": _date(account.repayment_date),
        "tenure_months": account.sanction_decision.sanctioned_tenure_months,
        "created_at": _timestamp(account.created_at),
        "activated_at": _timestamp(activated_at),
    }


def _has_cfc_scope(account):
    if account.loan_account_status == "active":
        evidence = resolve_post_transfer_evidence(
            application_id=account.loan_application_id
        )
        return bool(evidence and evidence.loan_account_id == account.pk)
    current = resolve_current_disbursement_evidence(
        loan_account_id=account.pk,
        allowed_authorisation_statuses=("pending", "approved", "rejected"),
    )
    return bool(current and current.loan_account_id == account.pk)


def _sap_is_current_for_account(account):
    code = account.sap_customer_code
    requests = list(
        SapCustomerProfileRequest.objects.select_related(
            "assigned_to_user__primary_role"
        )
        .filter(
            loan_application_id=account.loan_application_id,
            member_id=account.member_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
            sap_customer_code_id=account.sap_customer_code_id,
        )
        .order_by("created_at", "sap_customer_profile_request_id")[:2]
    )
    if len(requests) != 1:
        return False
    request = requests[0]
    return bool(
        code.status == SapCustomerCode.STATUS_ACTIVE
        and code.member_id == account.member_id
        and request.completed_at
        and request.assigned_to_user.can_authenticate()
        and request.assigned_to_user.primary_role.status == "active"
        and request.assigned_to_user.primary_role.role_code
        == "senior_manager_finance"
    )


def _pagination(query_params):
    unknown = set(query_params) - {"page", "page_size"}
    if unknown:
        raise LoanAccountProjectionValidation(
            {key: "Unknown query parameter." for key in sorted(unknown)}
        )
    return (
        _positive_int("page", query_params.get("page"), 1),
        _positive_int("page_size", query_params.get("page_size"), 20, maximum=100),
    )


def _positive_int(name, raw, default, maximum=None):
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise LoanAccountProjectionValidation({name: "Must be a positive integer."}) from exc
    if value < 1 or maximum is not None and value > maximum:
        message = (
            f"Must be at most {maximum}."
            if maximum and value > maximum
            else "Must be a positive integer."
        )
        raise LoanAccountProjectionValidation({name: message})
    return value


def _decimal(value, places=2):
    return f"{value:.{places}f}"


def _date(value):
    return value.isoformat() if value is not None else None


def _timestamp(value):
    return value.isoformat().replace("+00:00", "Z") if value is not None else None


__all__ = [
    "LoanAccountProjectionNotFound",
    "LoanAccountProjectionValidation",
    "LoanAccountReadPermissionDenied",
    "get_account",
    "list_accounts",
]
