"""Loan-owned immutable source decision for DPD calculations."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db.models import Prefetch
from django.db.models import F, Q

from sfpcl_credit.loans.models import (
    LoanAccount,
    RepaymentSchedule,
    RepaymentScheduleAllocation,
)
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)


class DpdSourcePermissionDenied(Exception):
    pass


@dataclass(frozen=True)
class DpdScheduleLineDecision:
    repayment_schedule_id: UUID
    due_date: date
    principal_due: Decimal
    interest_due: Decimal
    principal_paid_as_of: Decimal
    interest_paid_as_of: Decimal


@dataclass(frozen=True)
class DpdSourceDecision:
    loan_account_id: UUID
    loan_account_status: str
    current_dpd_status_id: UUID | None
    as_of_date: date
    schedule_lines: tuple[DpdScheduleLineDecision, ...]
    applied_allocation_ids: tuple[UUID, ...]
    applied_capitalisation_ids: tuple[UUID, ...]


def resolve_locked_dpd_source_decision(*, actor, loan_account_id, as_of_date):
    """Lock and re-authorise one loan before freezing schedule/ledger truth."""
    try:
        account = LoanAccount.objects.select_for_update().filter(
            pk=loan_account_id
        ).first()
        if account is not None and not scoped_account_candidates(actor=actor).filter(
            pk=account.pk
        ).exists():
            account = None
    except LoanAccountReadPermissionDenied as exc:
        raise DpdSourcePermissionDenied from exc
    if account is None:
        raise DpdSourcePermissionDenied

    schedule_rows = list(
        RepaymentSchedule.objects.filter(
            loan_account=account,
            due_date__lte=as_of_date,
        )
        .prefetch_related(
            Prefetch(
                "allocation_applications",
                queryset=RepaymentScheduleAllocation.objects.select_related(
                    "allocation__ledger_entry",
                    "allocation__reversal__ledger_entry",
                ),
            ),
            "interest_capitalisation_evidence__capitalisation__ledger_entry",
        )
        .order_by("due_date", "installment_number", "repayment_schedule_id")
    )
    lines = []
    allocation_ids = set()
    capitalisation_ids = set()
    for row in schedule_rows:
        paid_principal = Decimal("0.00")
        paid_interest = Decimal("0.00")
        for application in row.allocation_applications.all():
            allocation = application.allocation
            ledger_entry = getattr(allocation, "ledger_entry", None)
            if ledger_entry is None or ledger_entry.transaction_date > as_of_date:
                continue
            paid_principal += application.principal_applied
            paid_interest += application.interest_applied
            allocation_ids.add(allocation.pk)
            reversal = getattr(allocation, "reversal", None)
            reversal_ledger = (
                getattr(reversal, "ledger_entry", None) if reversal else None
            )
            if (
                reversal_ledger is not None
                and reversal_ledger.transaction_date <= as_of_date
            ):
                paid_principal -= application.principal_applied
                paid_interest -= application.interest_applied
        capitalisation_evidence = getattr(
            row, "interest_capitalisation_evidence", None
        )
        if capitalisation_evidence is not None:
            capitalisation = capitalisation_evidence.capitalisation
            ledger_entry = getattr(capitalisation, "ledger_entry", None)
            if (
                ledger_entry is not None
                and ledger_entry.transaction_date <= as_of_date
            ):
                paid_interest += capitalisation_evidence.interest_reclassified_amount
                capitalisation_ids.add(capitalisation.pk)
        lines.append(
            DpdScheduleLineDecision(
                repayment_schedule_id=row.pk,
                due_date=row.due_date,
                principal_due=row.principal_due,
                interest_due=row.interest_due,
                principal_paid_as_of=paid_principal,
                interest_paid_as_of=paid_interest,
            )
        )
    return DpdSourceDecision(
        loan_account_id=account.pk,
        loan_account_status=account.loan_account_status,
        current_dpd_status_id=account.current_dpd_status_id,
        as_of_date=as_of_date,
        schedule_lines=tuple(lines),
        applied_allocation_ids=tuple(sorted(allocation_ids, key=str)),
        applied_capitalisation_ids=tuple(sorted(capitalisation_ids, key=str)),
    )


def has_current_unpaid_schedule(*, loan_account_id):
    """Lock and answer current schedule serviceability for final delivery owners."""
    return (
        RepaymentSchedule.objects.select_for_update()
        .filter(loan_account_id=loan_account_id)
        .filter(
            Q(paid_principal__lt=F("principal_due"))
            | Q(paid_interest__lt=F("interest_due"))
            | Q(paid_charges__lt=F("charges_due"))
        )
        .exists()
    )


__all__ = [
    "DpdScheduleLineDecision",
    "DpdSourceDecision",
    "DpdSourcePermissionDenied",
    "resolve_locked_dpd_source_decision",
    "has_current_unpaid_schedule",
]
