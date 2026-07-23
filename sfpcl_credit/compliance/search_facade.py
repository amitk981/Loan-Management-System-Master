"""Privacy-minimised global-search projections owned by compliance."""

from sfpcl_credit.compliance.models import KYCReview
from sfpcl_credit.compliance.modules import compliance_control_tracker
from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker
from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
    NbfcPrincipalBusinessTestModule,
)
from sfpcl_credit.compliance.modules.section186_tracker import (
    Section186TrackerModule,
)
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.models import AuditLog


def search_compliance_records(*, actor, search, member_ids):
    """Return safe S02 cards without searching restricted compliance content."""
    permissions = set(auth_service.effective_permission_codes(actor))
    can_open = "compliance.task.read" in permissions
    cards = []
    matching_controls = (
        list(compliance_control_tracker.search_controls(actor=actor, search=search))
        if "compliance.control.read" in permissions
        else []
    )
    control_ids = {row.pk for row in matching_controls}

    if "compliance.control.read" in permissions:
        cards.extend(_control_card(row, can_open=can_open) for row in matching_controls)
    if "compliance.task.read" in permissions:
        tasks = compliance_control_tracker.search_tasks(
            actor=actor, search=search, control_ids=control_ids
        )
        cards.extend(_task_card(row, can_open=can_open) for row in tasks)
    if permissions.intersection(
        {"compliance.evidence.submit", "compliance.evidence.review"}
    ):
        evidence = compliance_control_tracker.search_evidence(
            actor=actor, search=search
        )
        cards.extend(_evidence_card(row) for row in evidence)
    if "compliance.section186.read" in permissions:
        sections = Section186TrackerModule.search(actor=actor, search=search)
        cards.extend(_section186_card(row, can_open=can_open) for row in sections)
    if "compliance.nbfc_test.read" in permissions:
        nbfc_tests = NbfcPrincipalBusinessTestModule.search(
            actor=actor, search=search
        )
        cards.extend(_nbfc_card(row, can_open=can_open) for row in nbfc_tests)
    if permissions.intersection(
        {"compliance.kyc_review.manage", "compliance.task.read"}
    ):
        kyc_reviews = KYCReviewTracker.search_reviews(
            actor=actor, search=search, member_ids=member_ids
        )
        cards.extend(_kyc_review_card(row, can_open=can_open) for row in kyc_reviews)
    if permissions.intersection(
        {"compliance.money_lending_review.manage", "compliance.task.read"}
    ):
        money_reviews = compliance_control_tracker.search_money_lending_reviews(
            actor=actor, search=search
        )
        cards.extend(_money_lending_card(row, can_open=can_open) for row in money_reviews)
    return cards


def _control_card(row, *, can_open):
    from sfpcl_credit.processes.global_search import build_result_card

    updated_at, updated_by = _last_update(
        row.pk, "compliance_control", row.updated_at, None
    )
    return build_result_card(
        row_id=row.pk,
        result_type="compliance_record",
        title=row.control_name,
        identifier=row.control_code,
        status=row.status,
        risk_status=None,
        amount=None,
        owner=row.owner_user.full_name,
        updated_at=updated_at,
        updated_by=updated_by,
        quick_actions=_open_actions(row.pk, can_open),
    )


def _task_card(row, *, can_open):
    from sfpcl_credit.processes.global_search import build_result_card

    updated_at, updated_by = _last_update(
        row.pk, "compliance_task", row.updated_at, None
    )
    return build_result_card(
        row_id=row.pk,
        result_type="compliance_record",
        title=f"{row.control.control_name} task",
        identifier=f"{row.control.control_code} · {row.task_period}",
        status=row.task_status,
        risk_status=None,
        amount=None,
        owner=row.assigned_to_user.full_name,
        updated_at=updated_at,
        updated_by=updated_by,
        quick_actions=_open_actions(row.pk, can_open),
    )


def _evidence_card(row):
    from sfpcl_credit.processes.global_search import build_result_card

    updated_by = row.reviewed_by_user or row.submitted_by_user
    return build_result_card(
        row_id=row.pk,
        result_type="compliance_record",
        title=f"{row.task.control.control_name} evidence",
        identifier=f"{row.task.control.control_code} · {row.task.task_period}",
        status=row.review_status,
        risk_status=None,
        amount=None,
        owner=row.submitted_by_user.full_name,
        updated_at=row.reviewed_at or row.submitted_at,
        updated_by=updated_by.full_name,
        quick_actions=[],
    )


def _section186_card(row, *, can_open):
    from sfpcl_credit.processes.global_search import build_result_card

    updated_by = row.reviewer_user if row.reviewed_at else row.prepared_by_user
    return build_result_card(
        row_id=row.pk,
        result_type="compliance_record",
        title="Section 186 quarterly limit",
        identifier=f"Section 186 · {row.financial_year} {row.quarter}",
        status=row.review_decision or "draft",
        risk_status=(
            "within_limit"
            if row.within_limit_flag
            else "special_resolution_required"
        ),
        amount=row.applicable_limit_amount,
        owner=row.reviewer_user.full_name,
        updated_at=row.reviewed_at or row.prepared_at,
        updated_by=updated_by.full_name,
        quick_actions=_open_actions(row.pk, can_open),
    )


def _nbfc_card(row, *, can_open):
    from sfpcl_credit.processes.global_search import build_result_card

    updated_by = row.reviewer_user if row.reviewed_at else row.prepared_by_user
    if row.registration_triggered_flag:
        risk_status = "registration_triggered"
    elif row.early_warning_flag:
        risk_status = "warning"
    else:
        risk_status = "clear"
    return build_result_card(
        row_id=row.pk,
        result_type="compliance_record",
        title="NBFC principal-business test",
        identifier=f"NBFC test · {row.financial_year} {row.quarter}",
        status=row.review_decision or "draft",
        risk_status=risk_status,
        amount=None,
        owner=row.reviewer_user.full_name,
        updated_at=row.reviewed_at or row.prepared_at,
        updated_by=updated_by.full_name,
        quick_actions=_open_actions(row.pk, can_open),
    )


def _kyc_review_card(row, *, can_open):
    from sfpcl_credit.processes.global_search import build_result_card

    review_label = "Re-KYC" if row.review_type == KYCReview.TYPE_REKYC else "KYC"
    updated_at, updated_by = _last_update(
        row.pk, "kyc_review", row.updated_at, None
    )
    return build_result_card(
        row_id=row.pk,
        result_type="compliance_record",
        title=f"{row.member.display_name} {review_label} review",
        identifier=f"{review_label} · {row.member.member_number}",
        status=row.status,
        risk_status=row.completeness_snapshot_json.get("risk_rating"),
        amount=None,
        owner=row.task.assigned_to_user.full_name,
        updated_at=updated_at,
        updated_by=updated_by,
        quick_actions=_open_actions(row.pk, can_open),
    )


def _money_lending_card(row, *, can_open):
    from sfpcl_credit.processes.global_search import build_result_card

    return build_result_card(
        row_id=row.pk,
        result_type="compliance_record",
        title="Money-lending law review",
        identifier=f"Money lending · {row.financial_year} · {row.state}",
        status=row.applicability,
        risk_status=None,
        amount=None,
        owner=row.reviewed_by_user.full_name,
        updated_at=row.reviewed_at,
        updated_by=row.reviewed_by_user.full_name,
        quick_actions=_open_actions(row.pk, can_open),
    )


def _open_actions(entity_id, allowed):
    if not allowed:
        return []
    return [{"label": "Open", "page": "compliance", "entity_id": str(entity_id)}]


def _last_update(entity_id, entity_type, fallback_at, fallback_user):
    event = (
        AuditLog.objects.select_related("actor_user")
        .filter(entity_id=entity_id, entity_type=entity_type)
        .order_by("-created_at", "-audit_log_id")
        .first()
    )
    if event is None:
        return (
            fallback_at,
            fallback_user.full_name if fallback_user is not None else None,
        )
    return (
        event.created_at,
        event.actor_user.full_name if event.actor_user_id else "System",
    )


__all__ = ["search_compliance_records"]
