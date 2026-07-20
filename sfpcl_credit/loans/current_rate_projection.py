from dataclasses import dataclass
from decimal import Decimal

from django.db.models import QuerySet


class CurrentRateProjectionScopeDenied(Exception):
    pass


@dataclass(frozen=True)
class LoanRateMutation:
    loan_account_id: object
    old_interest_rate: Decimal
    current_interest_rate: Decimal
    projection_changed: bool


def publish_current_rate(*, loan_account_id, effective_rate, actor=None):
    """Lock and update the loan-owned scalar without exposing the LoanAccount model."""
    from sfpcl_credit.loans.models import LoanAccount

    if actor is not None:
        require_current_rate_scope(actor=actor, loan_account_id=loan_account_id)
    account = LoanAccount.objects.select_for_update().get(pk=loan_account_id)
    old_rate = account.current_interest_rate
    changed = old_rate != effective_rate
    if changed:
        account.current_interest_rate = effective_rate
        account.save(update_fields=["current_interest_rate"])
    return LoanRateMutation(
        loan_account_id=account.pk,
        old_interest_rate=old_rate,
        current_interest_rate=account.current_interest_rate,
        projection_changed=changed,
    )


def require_current_rate_scope(*, actor, loan_account_id):
    from sfpcl_credit.loans.modules.loan_account_read import (
        LoanAccountReadPermissionDenied,
        scoped_account_candidates,
    )

    try:
        in_scope = scoped_account_candidates(actor=actor).filter(
            pk=loan_account_id
        ).exists()
    except LoanAccountReadPermissionDenied as exc:
        raise CurrentRateProjectionScopeDenied from exc
    if not in_scope:
        raise CurrentRateProjectionScopeDenied


def current_rates_for_accounts(account_ids):
    """Return loan-owned current scalars for one bounded projection window."""
    from sfpcl_credit.loans.models import LoanAccount

    return dict(
        LoanAccount.objects.filter(pk__in=account_ids).values_list(
            "pk", "current_interest_rate"
        )
    )


def due_rate_history_account_ids(
    queryset: QuerySet, *, effective_rate, rate_config_id, limit
):
    """Select stale accounts first, then accounts lacking a retained publication."""
    stale = list(
        queryset.exclude(loan_account__current_interest_rate=effective_rate)
        .order_by("loan_account_id")
        .values_list("loan_account_id", flat=True)[:limit]
    )
    remaining = limit - len(stale)
    if remaining <= 0:
        return stale
    undecided = list(
        queryset.exclude(
            loan_account__current_rate_projection_decisions__rate_config_id=rate_config_id
        )
        .exclude(loan_account_id__in=stale)
        .order_by("loan_account_id")
        .distinct()
        .values_list("loan_account_id", flat=True)[:remaining]
    )
    return [*stale, *undecided]
