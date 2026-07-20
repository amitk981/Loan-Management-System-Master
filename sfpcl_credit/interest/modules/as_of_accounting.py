"""Canonical as-of interest calculation behind the servicing owner interfaces."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from sfpcl_credit.configurations.modules.interest_rate_configuration import (
    resolve_effective_rate_periods,
)
from sfpcl_credit.loans.modules.loan_account_read import principal_periods


MONEY = Decimal("0.01")


@dataclass(frozen=True)
class InterestSegment:
    period_start: object
    period_end: object
    days: int
    principal_amount: Decimal
    effective_rate: Decimal
    rate_config_id: object
    rate_version_number: str
    gross_interest_amount: Decimal

    def snapshot(self):
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "days": self.days,
            "principal_amount": f"{self.principal_amount:.2f}",
            "effective_rate": f"{self.effective_rate:.4f}",
            "rate_version_number": self.rate_version_number,
            "gross_interest_amount": f"{self.gross_interest_amount:.2f}",
        }


@dataclass(frozen=True)
class AsOfInterestDecision:
    period_start: object
    period_end: object
    calculation_method: str
    day_count_basis: int
    segments: tuple[InterestSegment, ...]

    @property
    def calculation_days(self):
        return sum(segment.days for segment in self.segments)

    @property
    def gross_interest_amount(self):
        return sum(
            (segment.gross_interest_amount for segment in self.segments),
            Decimal("0.00"),
        ).quantize(MONEY)

    def snapshot(self):
        return [segment.snapshot() for segment in self.segments]


def decide_interest_as_of(*, account, period_start, period_end, configuration):
    """Resolve segmented principal/rate truth or fail closed on unsupported history."""
    if configuration.calculation_method != configuration.METHOD_SIMPLE_DAILY:
        raise ValueError("The approved calculation method cannot define as-of boundaries.")
    principals = principal_periods(
        account=account,
        period_start=period_start,
        period_end=period_end,
    )
    rates = resolve_effective_rate_periods(period_start, period_end)
    boundary_dates = {period_start, period_end + timedelta(days=1)}
    boundary_dates.update(period.period_start for period in principals)
    boundary_dates.update(period.period_end + timedelta(days=1) for period in principals)
    boundary_dates.update(rate.effective_from for rate in rates)
    boundary_dates.update(rate.effective_to + timedelta(days=1) for rate in rates)
    ordered = sorted(boundary_dates)
    segments = []
    for start, next_start in zip(ordered, ordered[1:]):
        end = next_start - timedelta(days=1)
        principal = next(
            period.principal_amount
            for period in principals
            if period.period_start <= start <= period.period_end
        ).quantize(MONEY)
        rate = next(
            decision
            for decision in rates
            if decision.effective_from <= start <= decision.effective_to
        )
        days = (end - start).days + 1
        amount = (
            principal
            * rate.effective_rate
            * Decimal(days)
            / (Decimal("100") * Decimal(configuration.day_count_basis))
        ).quantize(MONEY, rounding=ROUND_HALF_UP)
        segments.append(
            InterestSegment(
                period_start=start,
                period_end=end,
                days=days,
                principal_amount=principal,
                effective_rate=rate.effective_rate,
                rate_config_id=rate.interest_rate_config_id,
                rate_version_number=rate.version_number,
                gross_interest_amount=amount,
            )
        )
    return AsOfInterestDecision(
        period_start=period_start,
        period_end=period_end,
        calculation_method=configuration.calculation_method,
        day_count_basis=configuration.day_count_basis,
        segments=tuple(segments),
    )
