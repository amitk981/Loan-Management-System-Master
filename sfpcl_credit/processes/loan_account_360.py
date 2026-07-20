"""Read-only cross-owner projection for the initial Loan Account 360 view."""

from math import ceil
from uuid import UUID

from django.db import transaction
from django.db.models import F, Q

from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    filter_accounts_with_current_transfer,
)
from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    filter_accounts_with_current_initiation,
)
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    resolve_creation_truth,
    scoped_account_candidates,
    scoped_initiation_candidates,
)
from sfpcl_credit.loans.modules.loan_account_lifecycle import (
    filter_created_accounts,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    SapCustomerProfileModule,
)


class LoanAccountProjectionNotFound(Exception):
    pass


class LoanAccountProjectionValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


SERVICEABLE_STATUSES = {
    "active",
    "partially_repaid",
    "overdue",
    "grace_period",
    "extended",
}


def eligible_account_candidates(*, actor, filters):
    """Compose the canonical database-pageable Epic 009 read identity set."""
    return _eligible_account_candidates(
        actor=actor, filters=filters, candidate_owner=scoped_account_candidates
    )


def eligible_initiation_account_candidates(*, actor, filters):
    """Compose initiation candidates through their distinct mutation owner."""
    return _eligible_account_candidates(
        actor=actor, filters=filters, candidate_owner=scoped_initiation_candidates
    ).filter(_latest_sap_assignee_id=actor.pk)


def _eligible_account_candidates(*, actor, filters, candidate_owner):
    queryset = candidate_owner(actor=actor)
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

    queryset = filter_created_accounts(queryset)
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
    serviceable = Q(
        loan_account_status__in=SERVICEABLE_STATUSES,
        disbursed_amount__gt=0,
        principal_outstanding__gte=0,
        interest_outstanding__gte=0,
        charges_outstanding__gte=0,
        total_outstanding=(
            F("principal_outstanding")
            + F("interest_outstanding")
            + F("charges_outstanding")
        ),
        tenure_start_date__isnull=False,
    )
    queryset = filter_accounts_with_current_transfer(
        queryset.filter(sanctioned | serviceable)
    )
    queryset = filter_accounts_with_current_initiation(queryset)
    queryset = SapCustomerProfileModule.filter_current_account_completions(queryset)
    roles = set(auth_service.effective_role_codes(actor))
    if roles == {"senior_manager_finance"}:
        queryset = queryset.filter(_latest_sap_assignee_id=actor.pk)
    elif roles == {"chief_financial_controller"}:
        queryset = queryset.filter(
            disbursements__cfc_task__recipient_role_code="chief_financial_controller",
            disbursements__authorisation_status__in=(
                "pending",
                "approved",
                "rejected",
            ),
        )
    return queryset.distinct()


@transaction.atomic
def list_accounts(*, actor, query_params):
    page, page_size, filters = _query(query_params)
    total_count = eligible_account_candidates(actor=actor, filters=filters).count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    if page > total_pages:
        raise LoanAccountProjectionValidation({"page": "Page is out of range."})
    projections = list_account_window(
        actor=actor,
        filters=filters,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return projections, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def list_account_window(*, actor, filters, offset, limit):
    """Project one bounded canonical identity window for collection composition."""
    return _list_account_window(
        actor=actor,
        filters=filters,
        offset=offset,
        limit=limit,
        candidate_owner=eligible_account_candidates,
    )


def list_initiation_account_window(*, actor, filters, offset, limit):
    """Project one bounded initiation-owned identity window."""
    return _list_account_window(
        actor=actor,
        filters=filters,
        offset=offset,
        limit=limit,
        candidate_owner=eligible_initiation_account_candidates,
    )


def _list_account_window(*, actor, filters, offset, limit, candidate_owner):
    candidates = candidate_owner(actor=actor, filters=filters).select_related(
        "loan_application",
        "member",
        "sanction_decision",
        "terms",
        "sap_customer_code",
    )
    accounts = list(candidates[offset : offset + limit])
    projections = [_project(account, owner_selected=True) for account in accounts]
    return projections


@transaction.atomic
def get_account(*, actor, loan_account_id):
    filters = {"search": "", "status": "", "member_id": None}
    account = (
        eligible_account_candidates(actor=actor, filters=filters)
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
    projection = _project(account, owner_selected=True) if account is not None else None
    if projection is None:
        raise LoanAccountProjectionNotFound
    return projection


def _project(account, *, creation_decision=None, owner_selected=False):
    if not owner_selected and (creation_decision is False or (
        creation_decision is None and resolve_creation_truth(account=account) is None
    )):
        return None
    if account.sap_customer_code_id:
        if owner_selected:
            sap_masked = f"******{account.sap_customer_code.sap_customer_code[-4:]}"
        else:
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
    elif account.loan_account_status in SERVICEABLE_STATUSES:
        if not owner_selected:
            return None
        activated_at = account._selector_activated_at
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
            sap_masked if account.sap_customer_code_id else None
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
    if status and status not in {"sanctioned", *SERVICEABLE_STATUSES}:
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
    "list_account_window",
    "list_accounts",
]
