from django.db.models import Q

from sfpcl_credit.configurations.models import LoanPolicyConfig


class ConfigurationResolutionError(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__("Configuration resolution failed validation.")


def resolve_effective_loan_policy(*, calculation_date, for_update=False):
    queryset = LoanPolicyConfig.objects
    if for_update:
        queryset = queryset.select_for_update()
    policies = list(
        queryset.filter(
            status=LoanPolicyConfig.STATUS_ACTIVE,
            effective_from__lte=calculation_date,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=calculation_date))
        .order_by("-effective_from", "-loan_policy_config_id")[:2]
    )
    if len(policies) != 1:
        raise ConfigurationResolutionError(
            {
                "loan_policy_config": (
                    "Exactly one active loan policy must apply on calculation_date."
                )
            }
        )
    policy = policies[0]
    if not policy.board_approval_reference:
        raise ConfigurationResolutionError(
            {
                "loan_policy_config": (
                    "Active loan-limit policy requires Board approval metadata."
                )
            }
        )
    if policy.default_scale_of_finance_per_acre_amount <= 0:
        raise ConfigurationResolutionError(
            {"loan_policy_config": "Scale of finance must be greater than zero."}
        )
    configured_rules = [
        value
        for value in (policy.share_limit_percentage, policy.per_share_cap_amount)
        if value is not None
    ]
    if not configured_rules or any(value <= 0 for value in configured_rules):
        raise ConfigurationResolutionError(
            {
                "loan_policy_config": (
                    "Configure a positive share percentage or per-share cap before calculation."
                )
            }
        )
    return policy
