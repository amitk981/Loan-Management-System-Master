"""Database-narrowed, fully validated selection for approval-case reads."""

from django.db.models import Q

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.approvals.modules.read_scope import resolve_persisted_role_scope
from sfpcl_credit.identity.modules.auth_service import effective_permission_codes


def select_approval_case_candidates(
    *,
    actor,
    current_status=None,
    approval_type=None,
    assigned_to_me=False,
    actor_permissions=None,
):
    """Return frozen-valid actor-scoped cases and the persisted selector scope."""
    persisted_scope_type = resolve_persisted_role_scope(actor)
    queryset = (
        ApprovalCase.objects.select_related(
            "loan_application",
            "loan_appraisal_note",
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
    if current_status:
        queryset = queryset.filter(current_status=current_status)
    if approval_type:
        queryset = queryset.filter(approval_type=approval_type)
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
    if assigned_to_me:
        queryset = queryset.filter(
            current_status=ApprovalCase.STATUS_PENDING,
            required_approver_index__user_id=actor.pk,
        )
    # The stored flag and reader index narrow the database scan; neither is authority.
    # Materialize the canonical frozen-valid/read-scope decision before any caller
    # computes counts, normalizes pages, applies register filters, or serializes rows.
    from sfpcl_credit.approvals.modules import approval_case_engine

    scoped_ids = [
        case.pk
        for case in queryset.iterator(chunk_size=100)
        if approval_case_engine.is_routable_approval_case(case)
        and approval_case_engine.can_read_approval_case(
            actor=actor,
            case=case,
            persisted_scope_type=persisted_scope_type,
            persisted_scope_resolved=True,
            actor_permissions=actor_permissions,
        ).allowed
    ]
    queryset = queryset.filter(pk__in=scoped_ids)
    return queryset.order_by("-submitted_at", "-approval_case_id"), persisted_scope_type
