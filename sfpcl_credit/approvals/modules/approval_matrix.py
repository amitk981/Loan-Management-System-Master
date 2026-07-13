from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import UUID

from django.db.models import Q

from sfpcl_credit.approvals.models import ApprovalMatrixRule


class ApprovalMatrixResolutionError(Exception):
    code = "APPROVAL_MATRIX_RESOLUTION_ERROR"


class NoEffectiveApprovalRule(ApprovalMatrixResolutionError):
    code = "NO_EFFECTIVE_APPROVAL_RULE"


class AmbiguousApprovalRule(ApprovalMatrixResolutionError):
    code = "AMBIGUOUS_APPROVAL_RULE"


class InvalidApprovalFacts(ApprovalMatrixResolutionError):
    code = "INVALID_APPROVAL_FACTS"


@dataclass(frozen=True)
class ApprovalMatrixProjection:
    approval_matrix_rule_id: UUID
    version_number: str
    decision_type: str
    amount: Decimal
    amount_min: Decimal | None
    amount_max: Decimal | None
    condition_code: str | None
    decision_date: date
    required_approver_roles: tuple[str, ...]
    required_director_count: int
    joint_approval_required: bool
    register_required: str | None


def resolve_approval_matrix(*, decision_type, amount, condition_code, decision_date):
    if not isinstance(decision_date, date) or not isinstance(decision_type, str) or not decision_type.strip():
        raise InvalidApprovalFacts("Decision type and decision date are required.")
    try:
        amount = Decimal(amount)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise InvalidApprovalFacts("Amount must be a finite decimal.") from exc
    if not amount.is_finite() or amount < 0:
        raise InvalidApprovalFacts("Amount must be a finite non-negative decimal.")
    condition_code = condition_code or None
    matches = list(
        ApprovalMatrixRule.objects.filter(
            decision_type=decision_type.strip(),
            condition_code=condition_code,
            status__in=(
                ApprovalMatrixRule.STATUS_ACTIVE,
                ApprovalMatrixRule.STATUS_SUPERSEDED,
            ),
            effective_from__lte=decision_date,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=decision_date))
        .filter(Q(amount_min__isnull=True) | Q(amount_min__lte=amount))
        .filter(Q(amount_max__isnull=True) | Q(amount_max__gte=amount))
    )
    if not matches:
        raise NoEffectiveApprovalRule("No effective approval matrix rule matches the supplied facts.")
    if len(matches) != 1:
        raise AmbiguousApprovalRule("More than one approval matrix rule matches the supplied facts.")
    rule = matches[0]
    return ApprovalMatrixProjection(
        approval_matrix_rule_id=rule.pk,
        version_number=rule.version_number,
        decision_type=rule.decision_type,
        amount=amount,
        amount_min=rule.amount_min,
        amount_max=rule.amount_max,
        condition_code=rule.condition_code,
        decision_date=decision_date,
        required_approver_roles=tuple(rule.required_approver_roles_json),
        required_director_count=rule.required_director_count,
        joint_approval_required=rule.joint_approval_required_flag,
        register_required=rule.register_required,
    )
