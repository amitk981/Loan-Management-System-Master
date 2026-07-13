"""Explicit approval-owned coherence and attributable-reader projection."""

import uuid

from django.db import transaction

from sfpcl_credit.approvals.models import (
    ApprovalCase,
    ApprovalCaseRequiredApprover,
)
from sfpcl_credit.approvals.modules.conflict_of_interest import (
    ConflictOfInterestModule,
)


@transaction.atomic
def refresh_approval_case_projection(case):
    """Synchronize one saved case's coherence flag and exact reader actors."""
    if case.pk is None:
        raise ValueError("Approval case must be saved before projection refresh.")

    from sfpcl_credit.approvals.modules.approval_case_engine import (
        is_routable_approval_case,
    )

    coherent = is_routable_approval_case(case)
    ApprovalCase.objects.filter(pk=case.pk).update(
        routing_snapshot_is_coherent=coherent
    )
    case.routing_snapshot_is_coherent = coherent

    actor_ids = set()
    if isinstance(case.required_approvers_json, list):
        actor_ids.update(_valid_user_ids(case.required_approvers_json))
    actor_ids.update(_valid_user_ids(ConflictOfInterestModule.effective_approvers(case)))
    actor_ids.update(
        case.actions.values_list("approver_user_id", flat=True)
    )
    ApprovalCaseRequiredApprover.objects.filter(approval_case=case).exclude(
        user_id__in=actor_ids
    ).delete()
    ApprovalCaseRequiredApprover.objects.bulk_create(
        [
            ApprovalCaseRequiredApprover(approval_case=case, user_id=user_id)
            for user_id in sorted(actor_ids, key=str)
        ],
        ignore_conflicts=True,
    )
    return coherent


def _valid_user_ids(items):
    user_ids = set()
    for item in items:
        try:
            user_ids.add(uuid.UUID(str(item.get("user_id"))))
        except (AttributeError, TypeError, ValueError):
            continue
    return user_ids
