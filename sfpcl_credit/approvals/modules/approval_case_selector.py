"""Query shaping for database-narrowed approval-case read candidates."""

from django.db.models import Q

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.approvals.modules.read_scope import resolve_persisted_role_scope
from sfpcl_credit.identity.modules.auth_service import effective_permission_codes


def select_approval_case_candidates(
    *,
    actor,
    actor_permissions=None,
):
    """Return coarse actor-scoped candidates and the persisted selector scope."""
    persisted_scope_type = resolve_persisted_role_scope(actor)
    queryset = (
        ApprovalCase.objects.select_related(
            "loan_application",
            "loan_appraisal_note",
            "appraisal_review_decision",
            "general_meeting_approval",
            "exception_register_entry",
        )
        .prefetch_related("actions")
        .filter(
            version__gte=2,
            approval_matrix_rule_id__isnull=False,
            sanction_committee_id__isnull=False,
            decision_date__isnull=False,
            amount__isnull=False,
            related_entity_id__isnull=False,
            routing_snapshot_is_coherent=True,
        )
    )
    if persisted_scope_type:
        queryset = queryset.filter(
            approval_type=ApprovalCase.TYPE_SANCTION,
            related_entity_type="loan_application",
        )
    else:
        object_scope = Q(required_approver_index__user_id=actor.pk)
        if "credit_manager" in actor.role_codes():
            object_scope |= Q(submitted_by_user=actor)
            permissions = actor_permissions or effective_permission_codes(actor)
            if "applications.loan_application.read" in permissions:
                object_scope |= (
                    Q(loan_application__current_stage="credit_assessment")
                    | Q(loan_application__created_by_user=actor)
                    | Q(loan_application__received_by_user=actor)
                )
        queryset = queryset.filter(object_scope).distinct()
    return queryset, persisted_scope_type
