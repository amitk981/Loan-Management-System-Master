from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.configurations.modules.configuration_resolver import (
    ConfigurationResolutionError,
    resolve_effective_loan_policy,
)
from sfpcl_credit.credit.modules.loan_limit_calculator import calculate_limit_amounts
from sfpcl_credit.members.models import (
    ActiveMemberStatus,
    IndividualMemberProfile,
    LandHolding,
    Shareholding,
)
from sfpcl_credit.members.modules.active_member_status import ActiveMemberStatusModule


def project_borrower_limit(*, member, requested_amount=None):
    """Return the credit-owned, portal-safe borrower limit projection."""
    requested = _optional_money(requested_amount, "requested_amount")
    unavailable = _unavailable(requested)
    today = timezone.localdate()
    authority = ActiveMemberStatus.objects.filter(
        active_member_status_id=member.active_member_status_id,
        member=member,
        status__in=("active", "relaxation"),
        effective_from__lte=today,
        effective_to__isnull=True,
    ).first()
    if authority is None:
        return unavailable
    calculation_date = parse_date(authority.evidence_snapshot.get("calculated_as_of_date", ""))
    if calculation_date is None or calculation_date > today:
        return unavailable
    current_result = ActiveMemberStatusModule().calculate(
        member_id=member.member_id,
        as_of_date=calculation_date,
    )
    if (
        str(authority.result_id) != current_result.result_id
        or authority.evidence_snapshot != current_result.to_snapshot()
        or current_result.member_active_check not in {"pass", "relaxation"}
        or not current_result.qualification_route
    ):
        return unavailable
    shareholdings = list(Shareholding.objects.filter(
        member=member,
        status="active",
        valuation_effective_date__lte=today,
        valuation_per_share__gt=0,
        number_of_shares__gt=0,
    )[:2])
    verified_land = list(LandHolding.objects.filter(member=member, verification_status="verified"))
    profile = IndividualMemberProfile.objects.filter(member=member).first()
    if len(shareholdings) != 1 or not verified_land or profile is None:
        return unavailable
    land_area = sum((row.area_acres for row in verified_land), Decimal("0.00"))
    if profile.land_area_under_cultivation_acres is None or profile.land_area_under_cultivation_acres != land_area:
        return unavailable
    try:
        policy = resolve_effective_loan_policy(calculation_date=calculation_date)
    except ConfigurationResolutionError:
        return unavailable
    share_limit, land_limit, final_limit = calculate_limit_amounts(
        number_of_shares=shareholdings[0].number_of_shares,
        valuation_per_share=shareholdings[0].valuation_per_share,
        land_area=land_area,
        policy=policy,
    )
    within_limit = requested <= final_limit if requested is not None else None
    return {
        "status": "available",
        "unavailable_reason": None,
        "shareholding_based_limit_amount": _money(share_limit),
        "land_based_limit_amount": _money(land_limit),
        "final_eligible_loan_amount": _money(final_limit),
        "requested_amount": _money(requested),
        "amount_within_limit_flag": within_limit,
        "exception_required_flag": not within_limit if within_limit is not None else None,
        "calculated_as_of_date": current_result.calculated_as_of_date,
        "calculation_rule_version": policy.policy_version,
    }


def _unavailable(requested):
    return {
        "status": "unavailable",
        "unavailable_reason": "verified_active_member_authority_not_available",
        "shareholding_based_limit_amount": None,
        "land_based_limit_amount": None,
        "final_eligible_loan_amount": None,
        "requested_amount": _money(requested),
        "amount_within_limit_flag": None,
        "exception_required_flag": None,
        "calculated_as_of_date": None,
        "calculation_rule_version": None,
    }


def _optional_money(value, field):
    if value in (None, ""):
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError({field: "Enter a valid amount."}) from exc
    if not parsed.is_finite() or parsed <= 0:
        raise ValidationError({field: "Amount must be greater than zero."})
    return parsed.quantize(Decimal("0.01"))


def _money(value):
    return f"{value:.2f}" if value is not None else None
