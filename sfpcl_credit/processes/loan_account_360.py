"""Read-only cross-owner projection for the initial Loan Account 360 view."""

from math import ceil
from uuid import UUID

from django.db import transaction
from django.db.models import F, Q

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
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import get_account_customer_code


class LoanAccountProjectionNotFound(Exception):
    pass


class LoanAccountProjectionValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


@transaction.atomic
def list_accounts(*, actor, query_params):
    page, page_size, filters = _query(query_params)
    candidates = _apply_filters(
        scoped_account_candidates(actor=actor).select_related(
            "loan_application",
            "member",
            "sanction_decision",
            "terms",
            "sap_customer_code",
        ),
        filters,
    )
    candidates = _database_coherent_candidates(candidates)
    projections = [
        projection
        for account in candidates
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
    sap_decision = None
    if account.sap_customer_code_id:
        sap_decision = _sap_is_current_for_account(account)
        if sap_decision is None:
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
            sap_decision.customer_code_masked if sap_decision else None
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
    decision = get_account_customer_code(
        application_id=account.loan_application_id,
        member_id=account.member_id,
        customer_code_id=account.sap_customer_code_id,
    )
    return (
        decision
        if (
        decision
        and decision.customer_code_id == account.sap_customer_code_id
        and decision.member_id == account.member_id
        and decision.loan_application_id == account.loan_application_id
        )
        else None
    )


def _query(query_params):
    allowed = {
        "page",
        "page_size",
        "search",
        "loan_account_status",
        "member_id",
        "dpd_bucket",
    }
    unknown = set(query_params) - allowed
    if unknown:
        raise LoanAccountProjectionValidation(
            {key: "Unknown query parameter." for key in sorted(unknown)}
        )
    search = str(query_params.get("search", "")).strip()
    if len(search) > 120:
        raise LoanAccountProjectionValidation(
            {"search": "Must be at most 120 characters."}
        )
    status = str(query_params.get("loan_account_status", "")).strip()
    if status and status not in {"sanctioned", "active"}:
        raise LoanAccountProjectionValidation(
            {"loan_account_status": "Select a current Epic 009 loan account status."}
        )
    member_id = None
    raw_member_id = query_params.get("member_id")
    if raw_member_id not in (None, ""):
        try:
            member_id = UUID(str(raw_member_id))
        except (TypeError, ValueError, AttributeError) as exc:
            raise LoanAccountProjectionValidation(
                {"member_id": "Must be a valid UUID."}
            ) from exc
    if str(query_params.get("dpd_bucket", "")).strip():
        raise LoanAccountProjectionValidation(
            {
                "dpd_bucket": (
                    "DPD filtering is owned by Epic 010 and is not available yet."
                )
            }
        )
    return (
        _positive_int("page", query_params.get("page"), 1),
        _positive_int("page_size", query_params.get("page_size"), 20, maximum=100),
        {"search": search, "status": status, "member_id": member_id},
    )


def _apply_filters(queryset, filters):
    search = filters["search"]
    if search:
        queryset = queryset.filter(
            Q(loan_account_number__icontains=search)
            | Q(loan_application__application_reference_number__icontains=search)
            | Q(member__legal_name__icontains=search)
            | Q(member__folio_number__icontains=search)
        )
    if filters["status"]:
        queryset = queryset.filter(loan_account_status=filters["status"])
    if filters["member_id"]:
        queryset = queryset.filter(member_id=filters["member_id"])
    return queryset


def _database_coherent_candidates(queryset):
    """Exclude relational/state drift before count and database pagination."""
    queryset = queryset.filter(
        loan_application__member_id=F("member_id"),
        sanction_decision__loan_application_id=F("loan_application_id"),
        terms__loan_amount=F("sanctioned_amount"),
        terms__facility_type=F("loan_type"),
        terms__interest_rate_type=F("interest_rate_type"),
        terms__rate_of_interest=F("current_interest_rate"),
        terms__repayment_date=F("repayment_date"),
    )
    sanctioned = Q(
        loan_account_status="sanctioned",
        disbursed_amount=0,
        principal_outstanding=0,
        interest_outstanding=0,
        charges_outstanding=0,
        total_outstanding=0,
        tenure_start_date__isnull=True,
        tenure_end_date__isnull=True,
    )
    active = Q(
        loan_account_status="active",
        disbursed_amount__gt=0,
        principal_outstanding=F("disbursed_amount"),
        total_outstanding=F("disbursed_amount"),
        interest_outstanding=0,
        charges_outstanding=0,
        tenure_start_date__isnull=False,
        disbursements__bank_transfer_status="successful",
        disbursements__disbursement_amount=F("disbursed_amount"),
        disbursements__loan_application_id=F("loan_application_id"),
        disbursements__member_id=F("member_id"),
        disbursements__register_update__isnull=False,
        disbursements__initial_payment_sap_posting__posting_status="pending",
    )
    return queryset.filter(sanctioned | active).distinct()


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
