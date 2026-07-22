"""Query shaping for database-narrowed approval-case read candidates."""

from math import ceil

from django.db.models import Q

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.approvals.modules.read_scope import resolve_persisted_role_scope
from sfpcl_credit.identity.modules.auth_service import effective_permission_codes


def select_approval_case_candidates(
    *,
    actor,
    actor_permissions=None,
    approval_type=None,
    current_status=None,
    assigned_to_me=False,
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
            Q(
                version__gte=2,
                approval_matrix_rule_id__isnull=False,
                sanction_committee_id__isnull=False,
                decision_date__isnull=False,
                amount__isnull=False,
                related_entity_id__isnull=False,
                routing_snapshot_is_coherent=True,
            )
            | Q(
                approval_type=ApprovalCase.TYPE_RECOVERY,
                related_entity_type="non_payment_note",
                sanction_committee_id__isnull=False,
                decision_date__isnull=False,
                amount__isnull=False,
                related_entity_id__isnull=False,
            )
        )
    )
    if persisted_scope_type:
        if persisted_scope_type != "audit_readonly":
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
    if approval_type:
        queryset = queryset.filter(approval_type=approval_type)
    if current_status:
        queryset = queryset.filter(current_status=current_status)
    if assigned_to_me:
        queryset = queryset.filter(
            current_status=ApprovalCase.STATUS_PENDING,
            required_approver_index__user_id=actor.pk,
        )
    return (
        queryset.order_by("-submitted_at", "-approval_case_id"),
        persisted_scope_type,
    )


def paginate_approval_case_candidates(queryset, *, page, page_size):
    """Count, normalize, and slice an already canonically readable queryset."""
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    return list(queryset[offset : offset + page_size]), {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
