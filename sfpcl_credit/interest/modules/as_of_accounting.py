"""Canonical as-of interest calculation behind the servicing owner interfaces."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from sfpcl_credit.configurations.modules.interest_rate_configuration import (
    resolve_effective_rate_periods,
)
from sfpcl_credit.loans.modules.loan_account_read import principal_periods
from sfpcl_credit.shared.money import round_monetary


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
            "gross_interest_amount": format(self.gross_interest_amount, "f"),
        }


@dataclass(frozen=True)
class AsOfInterestDecision:
    period_start: object
    period_end: object
    calculation_method: str
    day_count_basis: int
    monetary_rounding_mode: str
    monetary_precision: Decimal
    rounding_application_boundary: str
    segments: tuple[InterestSegment, ...]

    @property
    def calculation_days(self):
        return sum(segment.days for segment in self.segments)

    @property
    def gross_interest_amount(self):
        unrounded = sum(
            (segment.gross_interest_amount for segment in self.segments),
            Decimal("0.00"),
        )
        return round_monetary(
            unrounded,
            mode=self.monetary_rounding_mode,
            precision=self.monetary_precision,
            boundary=self.rounding_application_boundary,
        )

    def snapshot(self):
        return [segment.snapshot() for segment in self.segments]


def decide_interest_as_of(*, account, period_start, period_end, configuration):
    """Resolve segmented principal/rate truth or fail closed on unsupported history."""
    if configuration.calculation_method != configuration.METHOD_SIMPLE_DAILY:
        raise ValueError("The approved calculation method cannot define as-of boundaries.")
    _validate_rounding_policy(configuration)
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
        ).quantize(Decimal("0.01"))
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
        )
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
        monetary_rounding_mode=configuration.monetary_rounding_mode,
        monetary_precision=configuration.monetary_precision,
        rounding_application_boundary=configuration.rounding_application_boundary,
        segments=tuple(segments),
    )


def _validate_rounding_policy(configuration):
    round_monetary(
        Decimal("0.00"),
        mode=configuration.monetary_rounding_mode,
        precision=configuration.monetary_precision,
        boundary=configuration.rounding_application_boundary,
    )
