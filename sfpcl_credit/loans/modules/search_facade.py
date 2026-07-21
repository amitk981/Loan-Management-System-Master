"""Loan-account and repayment search projections after canonical account scope."""

from django.db.models import Q

from sfpcl_credit.loans.models import Repayment
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)


READ_PERMISSION = "finance.loan_account.read"


def matching_member_ids(*, actor, permissions, query):
    if READ_PERMISSION not in permissions:
        return frozenset()
    try:
        queryset = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied:
        return frozenset()
    return frozenset(
        queryset.filter(loan_account_number_normalized=query.upper()).values_list(
            "member_id", flat=True
        )
    )


def matching_accounts(
    *, actor, permissions, query, related_member_ids, allow_direct_match, limit
):
    if READ_PERMISSION not in permissions:
        return None
    try:
        queryset = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied:
        return None
    match = Q(member_id__in=related_member_ids)
    if allow_direct_match:
        match |= (
            Q(loan_account_number_normalized=query.upper())
            | Q(member__legal_name__istartswith=query)
            | Q(member__display_name__istartswith=query)
            | Q(member__folio_number__iexact=query)
        )
    return list(
        queryset.select_related(
            "member", "loan_application", "loan_application__updated_by_user",
            "loan_application__received_by_user", "sap_customer_code", "current_dpd_status",
        )
        .filter(match)
        .distinct()
        .order_by("-created_at", "-loan_account_id")[:limit]
    )


def matching_repayments(*, permissions, account_ids, limit):
    if READ_PERMISSION not in permissions:
        return []
    return list(
        Repayment.objects.select_related("loan_account", "member", "captured_by_user")
        .filter(loan_account_id__in=account_ids)
        .order_by("-created_at", "-repayment_id")[:limit]
    )


__all__ = ["matching_accounts", "matching_member_ids", "matching_repayments"]
