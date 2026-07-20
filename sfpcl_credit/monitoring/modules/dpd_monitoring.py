from decimal import Decimal
from uuid import UUID, uuid4

from django.db import transaction
from django.db.models import Prefetch, Q
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import (
    LoanAccount,
    RepaymentSchedule,
    RepaymentScheduleAllocation,
)
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme, DpdStatus


READ_PERMISSION = "monitoring.dpd.read"
CALCULATE_PERMISSION = "monitoring.dpd.calculate"
CALCULATION_VERSION = "DPD-CALC-1"
SERVICEABLE_STATUSES = {
    "active",
    "partially_repaid",
    "overdue",
    "grace_period",
    "extended",
    "non_recoverable_under_review",
}
PORTFOLIO_LIMIT = 100


class DpdValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class DpdPermissionDenied(Exception):
    pass


class DpdNotFound(Exception):
    pass


class DpdConflict(Exception):
    pass


def calculate_for_loan(*, actor, loan_account_id, payload, request=None):
    as_of_date = _validate_as_of_payload(payload)
    _require_permission(actor, CALCULATE_PERMISSION)
    account = _scoped_accounts(actor).filter(pk=loan_account_id).first()
    if account is None:
        raise DpdNotFound
    if account.loan_account_status not in SERVICEABLE_STATUSES:
        raise DpdConflict("The loan is not active for DPD calculation.")
    return _calculate_locked(
        actor=actor,
        loan_account_id=account.pk,
        as_of_date=as_of_date,
        request=request,
    )


def get_current_for_loan(*, actor, loan_account_id):
    _require_permission(actor, READ_PERMISSION)
    account = _scoped_accounts(actor).filter(pk=loan_account_id).first()
    if account is None or account.current_dpd_status_id is None:
        raise DpdNotFound
    row = DpdStatus.objects.select_related("operational_scheme").filter(
        pk=account.current_dpd_status_id,
        loan_account=account,
    ).first()
    if row is None:
        raise DpdNotFound
    return serialize_dpd_status(row)


def calculate_portfolio(*, actor, payload, request=None):
    cleaned = _validate_portfolio_payload(payload)
    _require_permission(actor, CALCULATE_PERMISSION)
    scoped = _scoped_accounts(actor)
    if cleaned["include_all_active_loans"]:
        account_ids = list(
            scoped.filter(loan_account_status__in=SERVICEABLE_STATUSES)
            .order_by("loan_account_id")
            .values_list("loan_account_id", flat=True)[:PORTFOLIO_LIMIT]
        )
    else:
        requested = cleaned["loan_account_ids"]
        accessible = set(
            scoped.filter(pk__in=requested).values_list("loan_account_id", flat=True)
        )
        account_ids = requested

    results = []
    for account_id in account_ids:
        if not cleaned["include_all_active_loans"] and account_id not in accessible:
            results.append(
                {"loan_account_id": str(account_id), "outcome": "failed", "reason": "inaccessible"}
            )
            continue
        account_status = LoanAccount.objects.filter(pk=account_id).values_list(
            "loan_account_status", flat=True
        ).first()
        if account_status not in SERVICEABLE_STATUSES:
            results.append(
                {"loan_account_id": str(account_id), "outcome": "skipped", "reason": "not_active"}
            )
            continue
        try:
            snapshot = _calculate_locked(
                actor=actor,
                loan_account_id=account_id,
                as_of_date=cleaned["as_of_date"],
                request=request,
            )
            results.append(
                {
                    "loan_account_id": str(account_id),
                    "outcome": "calculated",
                    "dpd_status": snapshot,
                }
            )
        except (DpdConflict, LoanAccount.DoesNotExist) as exc:
            results.append(
                {"loan_account_id": str(account_id), "outcome": "failed", "reason": str(exc)}
            )
    run_id = uuid4()
    AuditLog.objects.create(
        actor_user=actor,
        action="monitoring.dpd.portfolio_calculated",
        entity_type="dpd_portfolio_run",
        entity_id=run_id,
        new_value_json={
            "as_of_date": cleaned["as_of_date"].isoformat(),
            "calculated_count": sum(row["outcome"] == "calculated" for row in results),
            "skipped_count": sum(row["outcome"] == "skipped" for row in results),
            "failed_count": sum(row["outcome"] == "failed" for row in results),
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    return {
        "run_id": str(run_id),
        "as_of_date": cleaned["as_of_date"].isoformat(),
        "calculated_count": sum(row["outcome"] == "calculated" for row in results),
        "skipped_count": sum(row["outcome"] == "skipped" for row in results),
        "failed_count": sum(row["outcome"] == "failed" for row in results),
        "results": results,
    }


@transaction.atomic
def _calculate_locked(*, actor, loan_account_id, as_of_date, request):
    account = LoanAccount.objects.select_for_update().get(pk=loan_account_id)
    retained = DpdStatus.objects.filter(
        loan_account=account, as_of_date=as_of_date
    ).first()
    if retained is not None:
        _advance_current_pointer(account=account, candidate=retained)
        return serialize_dpd_status(retained)

    calculation = _calculate_amounts(account=account, as_of_date=as_of_date)
    scheme = _effective_scheme(as_of_date)
    standard_bucket = _standard_bucket(
        calculation["days_past_due"],
        scheme,
        has_unpaid_schedule=calculation["earliest_unpaid_due_date"] is not None,
    )
    audit = AuditLog.objects.create(
        actor_user=actor,
        action="monitoring.dpd.calculated",
        entity_type="loan_account",
        entity_id=account.pk,
        new_value_json={
            "as_of_date": as_of_date.isoformat(),
            "calculation_version": CALCULATION_VERSION,
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    row = DpdStatus.objects.create(
        loan_account=account,
        as_of_date=as_of_date,
        days_past_due=calculation["days_past_due"],
        sop_bucket=_sop_bucket(calculation["earliest_unpaid_due_date"], as_of_date),
        standard_bucket=standard_bucket,
        principal_overdue_amount=calculation["principal_overdue"],
        interest_overdue_amount=calculation["interest_overdue"],
        total_overdue_amount=(
            calculation["principal_overdue"] + calculation["interest_overdue"]
        ),
        earliest_unpaid_due_date=calculation["earliest_unpaid_due_date"],
        calculation_version=CALCULATION_VERSION,
        operational_scheme=scheme,
        calculation_inputs_json=calculation["inputs"],
        calculated_by_user=actor,
        calculation_audit=audit,
    )
    _advance_current_pointer(account=account, candidate=row)
    return serialize_dpd_status(row)


def _advance_current_pointer(*, account, candidate):
    if account.current_dpd_status_id == candidate.pk:
        return
    current_date = DpdStatus.objects.filter(
        pk=account.current_dpd_status_id,
        loan_account=account,
    ).values_list("as_of_date", flat=True).first()
    if current_date is not None and current_date > candidate.as_of_date:
        return
    account.current_dpd_status_id = candidate.pk
    account.save(update_fields=["current_dpd_status_id"])


def _calculate_amounts(*, account, as_of_date):
    schedule_rows = list(
        RepaymentSchedule.objects.filter(
            loan_account=account, due_date__lte=as_of_date
        )
        .prefetch_related(
            Prefetch(
                "allocation_applications",
                queryset=RepaymentScheduleAllocation.objects.select_related(
                    "allocation__ledger_entry",
                    "allocation__reversal__ledger_entry",
                ),
            )
        )
        .order_by("due_date", "installment_number", "repayment_schedule_id")
    )
    principal = Decimal("0.00")
    interest = Decimal("0.00")
    earliest = None
    applied_allocation_ids = []
    schedule_inputs = []
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
            applied_allocation_ids.append(str(allocation.pk))
            reversal = getattr(allocation, "reversal", None)
            reversal_ledger = getattr(reversal, "ledger_entry", None) if reversal else None
            if reversal_ledger is not None and reversal_ledger.transaction_date <= as_of_date:
                paid_principal -= application.principal_applied
                paid_interest -= application.interest_applied
        principal_remaining = row.principal_due - paid_principal
        interest_remaining = row.interest_due - paid_interest
        schedule_inputs.append(
            {
                "repayment_schedule_id": str(row.pk),
                "due_date": row.due_date.isoformat(),
                "principal_due": f"{row.principal_due:.2f}",
                "interest_due": f"{row.interest_due:.2f}",
                "principal_paid_as_of": f"{paid_principal:.2f}",
                "interest_paid_as_of": f"{paid_interest:.2f}",
            }
        )
        if principal_remaining > 0 or interest_remaining > 0:
            earliest = earliest or row.due_date
            principal += max(principal_remaining, Decimal("0.00"))
            interest += max(interest_remaining, Decimal("0.00"))
    return {
        "days_past_due": (as_of_date - earliest).days if earliest else 0,
        "earliest_unpaid_due_date": earliest,
        "principal_overdue": principal,
        "interest_overdue": interest,
        "inputs": {
            "schedule_lines": schedule_inputs,
            "applied_allocation_ids": sorted(set(applied_allocation_ids)),
            "as_of_date": as_of_date.isoformat(),
        },
    }


def _sop_bucket(earliest_unpaid_due_date, as_of_date):
    if earliest_unpaid_due_date is None:
        return "current"
    first = _anniversary(earliest_unpaid_due_date, 1)
    second = _anniversary(earliest_unpaid_due_date, 2)
    third = _anniversary(earliest_unpaid_due_date, 3)
    if as_of_date < first:
        return "current"
    if as_of_date < second:
        return "one_to_two_years"
    if as_of_date <= third:
        return "two_to_three_years"
    return "more_than_three_years"


def _anniversary(value, years):
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def _effective_scheme(as_of_date):
    rows = list(
        DpdOperationalBucketScheme.objects.filter(
            status="active",
            effective_from__lte=as_of_date,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=as_of_date))
        .order_by("effective_from", "dpd_operational_bucket_scheme_id")[:2]
    )
    if len(rows) > 1:
        raise DpdConflict("Multiple operational DPD bucket schemes are effective.")
    return rows[0] if rows else None


def _standard_bucket(days_past_due, scheme, *, has_unpaid_schedule):
    if scheme is None or not has_unpaid_schedule:
        return None
    if days_past_due <= scheme.first_upper_days:
        return "0_30"
    if days_past_due <= scheme.second_upper_days:
        return "31_60"
    if days_past_due <= scheme.third_upper_days:
        return "61_90"
    return "over_90"


def _validate_as_of_payload(payload):
    if set(payload) != {"as_of_date"}:
        raise DpdValidation({"body": "Only as_of_date is accepted."})
    value = payload.get("as_of_date")
    parsed = parse_date(value) if isinstance(value, str) else None
    if parsed is None:
        raise DpdValidation({"as_of_date": "Must be an ISO date."})
    return parsed


def _validate_portfolio_payload(payload):
    allowed = {"as_of_date", "loan_account_ids", "include_all_active_loans"}
    if set(payload) != allowed:
        raise DpdValidation(
            {"body": "Use as_of_date, loan_account_ids and include_all_active_loans."}
        )
    as_of_date = _validate_as_of_payload({"as_of_date": payload.get("as_of_date")})
    raw_ids = payload.get("loan_account_ids")
    include_all = payload.get("include_all_active_loans")
    if not isinstance(raw_ids, list):
        raise DpdValidation({"loan_account_ids": "Must be a list."})
    if len(raw_ids) > PORTFOLIO_LIMIT:
        raise DpdValidation({"loan_account_ids": "Must contain at most 100 ids."})
    try:
        account_ids = [UUID(str(value)) for value in raw_ids]
    except (ValueError, TypeError, AttributeError) as exc:
        raise DpdValidation({"loan_account_ids": "Each item must be a UUID."}) from exc
    if len(set(account_ids)) != len(account_ids):
        raise DpdValidation({"loan_account_ids": "Ids must be unique."})
    if not isinstance(include_all, bool):
        raise DpdValidation({"include_all_active_loans": "Must be a boolean."})
    if include_all == bool(account_ids):
        raise DpdValidation(
            {"include_all_active_loans": "Select either all active loans or one or more ids."}
        )
    return {
        "as_of_date": as_of_date,
        "loan_account_ids": account_ids,
        "include_all_active_loans": include_all,
    }


def _require_permission(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
    ):
        raise DpdPermissionDenied


def _scoped_accounts(actor):
    try:
        return scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise DpdPermissionDenied from exc


def serialize_dpd_status(row):
    return {
        "dpd_status_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "as_of_date": row.as_of_date.isoformat(),
        "days_past_due": row.days_past_due,
        "sop_bucket": row.sop_bucket,
        "standard_bucket": row.standard_bucket,
        "principal_overdue_amount": f"{row.principal_overdue_amount:.2f}",
        "interest_overdue_amount": f"{row.interest_overdue_amount:.2f}",
        "total_overdue_amount": f"{row.total_overdue_amount:.2f}",
        "calculation_version": row.calculation_version,
        "operational_scheme_version": (
            row.operational_scheme.version if row.operational_scheme_id else None
        ),
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


__all__ = [
    "DpdConflict",
    "DpdNotFound",
    "DpdPermissionDenied",
    "DpdValidation",
    "calculate_for_loan",
    "calculate_portfolio",
    "get_current_for_loan",
    "serialize_dpd_status",
]
