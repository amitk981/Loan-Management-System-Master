"""Public read boundary for immutable approval-case routing snapshots."""

from decimal import Decimal, InvalidOperation
from math import ceil

from django.core.exceptions import ValidationError
from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.domain_errors import DomainObjectAccessDenied
from sfpcl_credit.identity.modules.object_permissions import ObjectAccessResult


_LIST_PARAMS = {"page", "page_size", "current_status", "approval_type", "assigned_to_me"}


def list_approval_cases(*, actor, query_params):
    unknown = set(query_params.keys()) - _LIST_PARAMS
    if unknown:
        raise ValidationError(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(_positive_int("page_size", query_params.get("page_size"), 20), 100)
    assigned_to_me = _boolean("assigned_to_me", query_params.get("assigned_to_me"))
    queryset = (
        ApprovalCase.objects.select_related("loan_application", "loan_appraisal_note")
        .prefetch_related("actions")
        .filter(
            version__gte=2,
            approval_matrix_rule_id__isnull=False,
            sanction_committee_id__isnull=False,
            decision_date__isnull=False,
            amount__isnull=False,
            related_entity_id__isnull=False,
        )
        .order_by("-submitted_at", "-approval_case_id")
    )
    if query_params.get("current_status"):
        queryset = queryset.filter(current_status=query_params["current_status"])
    if query_params.get("approval_type"):
        queryset = queryset.filter(approval_type=query_params["approval_type"])
    cases = [
        case for case in queryset
        if (
            is_routable_approval_case(case)
            and can_read_approval_case(actor=actor, case=case)
        )
    ]
    if assigned_to_me:
        actor_id = str(actor.pk)
        cases = [
            case
            for case in cases
            if is_pending_approval_case_actor(case=case, actor_id=actor_id)
        ]
    total_count = len(cases)
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    return [serialize_case_snapshot(case) for case in cases[offset : offset + page_size]], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def get_approval_case(*, actor, case_id, actor_permissions):
    case = (
        ApprovalCase.objects.select_related(
            "loan_application",
            "loan_appraisal_note__risk_assessment",
        )
        .prefetch_related("actions")
        .filter(pk=case_id)
        .first()
    )
    if case is None or not is_routable_approval_case(case):
        raise ApprovalCase.DoesNotExist
    if not can_read_approval_case(actor=actor, case=case):
        raise DomainObjectAccessDenied(
            ObjectAccessResult(
                allowed=False,
                reason="approval_case_not_assigned",
                error_code="OBJECT_ACCESS_DENIED",
                required_permission="approvals.case.read",
            )
        )
    return serialize_case_detail(case, actor, set(actor_permissions))


def can_read_approval_case(*, actor, case):
    """Return whether the immutable case snapshot gives this actor object scope."""
    actor_id = str(actor.pk)
    return any(
        isinstance(item, dict) and str(item.get("user_id")) == actor_id
        for item in case.required_approvers_json
    )


def serialize_case_summary(case):
    return {
        "approval_case_id": str(case.pk),
        "approval_type": case.approval_type,
        "related_entity_type": case.related_entity_type,
        "related_entity_id": str(case.related_entity_id),
        "loan_application_id": str(case.loan_application_id),
        "application_reference_number": case.loan_application.application_reference_number,
        "amount": f"{case.amount:.2f}",
        "current_status": case.current_status,
        "decision_date": case.decision_date.isoformat(),
        "version": case.version,
    }


def serialize_case_detail(case, actor, actor_permissions):
    action_by_user = {
        str(action.approver_user_id): action for action in case.actions.all()
    }
    required_approvers = []
    for item in case.required_approvers_json:
        action = action_by_user.get(str(item["user_id"]))
        required_approvers.append(
            {
                **item,
                "decision": action.decision if action else None,
                "acted_at": (
                    action.acted_at.isoformat().replace("+00:00", "Z")
                    if action
                    else None
                ),
            }
        )
    snapshot = {
        **serialize_case_snapshot(case),
        "required_approvers": required_approvers,
        "review_facts": _review_facts(case),
        "available_actions": _available_actions(
            case, actor, actor_permissions, action_by_user
        ),
    }
    return snapshot


def serialize_case_snapshot(case):
    """Serialize the canonical immutable routed-case projection."""
    return {
        **serialize_case_summary(case),
        "approval_matrix_rule_id": str(case.approval_matrix_rule_id),
        "approval_matrix_rule_version": case.approval_matrix_rule_version,
        "sanction_committee_id": str(case.sanction_committee_id),
        "sanction_committee_version": case.sanction_committee_version,
        "required_approvers": case.required_approvers_json,
        "excluded_approvers": case.excluded_approvers_json,
        "reason_for_approval": case.reason_for_approval,
        "exception_condition_code": case.exception_condition_code or None,
        "matrix_projection": case.matrix_projection_json,
        "committee_projection": case.committee_projection_json,
        "loan_limit_provenance": case.loan_limit_provenance_json,
    }


def _review_facts(case):
    application = case.loan_application
    note = case.loan_appraisal_note
    risk = note.risk_assessment
    eligibility = note.eligibility_snapshot_json
    loan_limit = note.loan_limit_snapshot_json
    return {
        "eligibility": eligibility,
        "loan_amounts": {
            "requested_amount": (
                f"{application.required_loan_amount:.2f}"
                if application.required_loan_amount is not None
                else None
            ),
            "eligible_amount": loan_limit.get("final_eligible_loan_amount"),
            "recommended_amount": f"{note.recommended_amount:.2f}",
        },
        "purpose": {
            "category": application.purpose_category or None,
            "description": application.declared_purpose or None,
        },
        "compliance_checks": {
            key: eligibility.get(key)
            for key in (
                "member_active_check",
                "default_check",
                "terms_acceptance_check",
                "purpose_check",
            )
        },
        "borrowing_history": note.borrower_summary,
        "risk": {
            "risk_assessment_id": str(risk.pk),
            "market_risk_rating": risk.market_risk_rating,
            "operational_risk_rating": risk.operational_risk_rating,
            "borrower_risk_rating": risk.borrower_risk_rating,
            "overall_risk_rating": risk.overall_risk_rating,
            "risk_mitigation_notes": risk.risk_mitigation_notes,
        },
        "documentation_completeness": {
            "status": application.completeness_status,
            "document_check": eligibility.get("document_check"),
        },
        "source_references": {
            "application": f"/api/v1/loan-applications/{application.pk}/",
            "appraisal": f"/api/v1/loan-applications/{application.pk}/appraisal-note/",
            "eligibility": f"/api/v1/loan-applications/{application.pk}/eligibility-assessment/",
            "loan_limit": f"/api/v1/loan-applications/{application.pk}/loan-limit-assessment/",
        },
    }


def _available_actions(case, actor, actor_permissions, action_by_user):
    actor_id = str(actor.pk)
    pending_assignment = is_pending_approval_case_actor(
        case=case, actor_id=actor_id
    )
    action_specs = (
        ("approve", "Approve", "approvals.case.approve"),
        ("reject", "Reject", "approvals.case.reject"),
        ("return", "Return for Clarification", "approvals.case.return"),
    )
    actions = []
    for action_code, label, permission in action_specs:
        enabled = (
            case.current_status == ApprovalCase.STATUS_PENDING
            and pending_assignment
            and permission in actor_permissions
        )
        if case.current_status != ApprovalCase.STATUS_PENDING:
            reason = "Approval case is not pending."
        elif actor_id in action_by_user:
            reason = "You have already acted on this approval case."
        elif not pending_assignment:
            reason = "You are not a pending approver for this case."
        elif permission not in actor_permissions:
            reason = "Required permission is not granted."
        else:
            reason = None
        actions.append(
            {
                "action_code": action_code,
                "label": label,
                "enabled": enabled,
                "disabled_reason": reason,
                "required_permission": permission,
            }
        )
    return actions


def is_routable_approval_case(case):
    """Validate the complete immutable authority and credit snapshot."""
    required = case.required_approvers_json
    matrix = case.matrix_projection_json
    committee = case.committee_projection_json
    return (
        case.version >= 2
        and case.approval_matrix_rule_id is not None
        and bool(case.approval_matrix_rule_version)
        and case.sanction_committee_id is not None
        and bool(case.sanction_committee_version)
        and case.decision_date is not None
        and case.amount is not None
        and bool(case.related_entity_type)
        and case.related_entity_id is not None
        and isinstance(required, list)
        and bool(required)
        and isinstance(case.excluded_approvers_json, list)
        and all(
            isinstance(item, dict)
            and item.get("role_code")
            and item.get("user_id")
            and item.get("full_name")
            for item in required
        )
        and isinstance(matrix, dict)
        and matrix.get("approval_matrix_rule_id") == str(case.approval_matrix_rule_id)
        and matrix.get("version_number") == case.approval_matrix_rule_version
        and matrix.get("decision_date") == case.decision_date.isoformat()
        and _matrix_projection_is_coherent(case, matrix)
        and isinstance(committee, dict)
        and committee.get("sanction_committee_id") == str(case.sanction_committee_id)
        and committee.get("version_number") == case.sanction_committee_version
        and committee.get("decision_date") == case.decision_date.isoformat()
        and _approver_snapshot_is_coherent(required, matrix, committee)
        and _loan_limit_provenance_is_complete(case)
    )


def _matrix_projection_is_coherent(case, matrix):
    condition = matrix.get("condition_code") or ""
    roles = matrix.get("required_approver_roles")
    director_count = matrix.get("required_director_count")
    return (
        case.approval_type == ApprovalCase.TYPE_SANCTION
        and case.related_entity_type == "loan_application"
        and str(case.related_entity_id) == str(case.loan_application_id)
        and matrix.get("decision_type") == "loan_sanction"
        and _same_amount(matrix.get("amount"), case.amount)
        and _amount_inside_projection(case.amount, matrix)
        and condition == (case.exception_condition_code or "")
        and condition in ("", "exceeds_permissible_limit")
        and (
            (not condition and not case.exception_reason)
            or (
                condition
                and bool(case.exception_reason.strip())
                and case.exception_reason == case.reason_for_approval
            )
        )
        and isinstance(roles, list)
        and roles == ["cfo", "director"]
        and isinstance(director_count, int)
        and director_count in (1, 2)
        and matrix.get("joint_approval_required") is True
        and isinstance(matrix.get("register_required"), str)
        and bool(matrix["register_required"].strip())
        and case.loan_appraisal_note.reviewed_at is not None
        and case.decision_date
        == timezone.localdate(case.loan_appraisal_note.reviewed_at)
        and case.amount == case.loan_appraisal_note.recommended_amount
    )


def _approver_snapshot_is_coherent(required, matrix, committee):
    cfo_id = str(committee.get("cfo_user_id") or "")
    director_ids = committee.get("director_user_ids")
    if (
        not cfo_id
        or not isinstance(director_ids, list)
        or len(director_ids) != 2
        or any(not item for item in director_ids)
    ):
        return False
    director_ids = [str(item) for item in director_ids]
    committee_ids = [cfo_id, *director_ids]
    if len(set(committee_ids)) != 3:
        return False
    expected = [("cfo", cfo_id)] + [
        ("director", user_id)
        for user_id in director_ids[: matrix["required_director_count"]]
    ]
    if len(required) != len(expected):
        return False
    actual = []
    for item in required:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("full_name"), str)
            or not item["full_name"].strip()
        ):
            return False
        actual.append((item.get("role_code"), str(item.get("user_id") or "")))
    return actual == expected and len({user_id for _, user_id in actual}) == len(actual)


def _same_amount(first, second):
    try:
        return Decimal(str(first)) == Decimal(str(second))
    except (InvalidOperation, TypeError, ValueError):
        return False


def _amount_inside_projection(amount, matrix):
    try:
        amount = Decimal(str(amount))
        minimum = Decimal(str(matrix["amount_min"]))
        maximum = (
            Decimal(str(matrix["amount_max"]))
            if matrix.get("amount_max") is not None
            else None
        )
    except (KeyError, InvalidOperation, TypeError, ValueError):
        return False
    return amount >= minimum and (maximum is None or amount <= maximum)


def _loan_limit_provenance_is_complete(case):
    provenance = case.loan_limit_provenance_json
    required = (
        "loan_limit_assessment_id",
        "loan_application_id",
        "exception_required_flag",
        "calculation_rule_version",
        "policy_config_id",
        "policy_name",
        "calculated_at",
    )
    snapshot = case.loan_appraisal_note.loan_limit_snapshot_json
    condition_requires_exception = bool(case.exception_condition_code)
    return (
        isinstance(provenance, dict)
        and all(provenance.get(key) not in (None, "") for key in required)
        and str(provenance["loan_limit_assessment_id"])
        == str(case.loan_appraisal_note.loan_limit_assessment_id_snapshot)
        and str(provenance["loan_application_id"]) == str(case.loan_application_id)
        and isinstance(provenance["exception_required_flag"], bool)
        and provenance["exception_required_flag"] == case.exception_required_flag
        and (not provenance["exception_required_flag"] or condition_requires_exception)
        and isinstance(snapshot, dict)
        and all(provenance.get(key) == snapshot.get(key) for key in required)
    )


def is_pending_approval_case_actor(*, case, actor_id):
    """Return whether an in-scope actor still owns a pending decision slot."""
    if case.current_status != ApprovalCase.STATUS_PENDING:
        return False
    excluded_ids = {
        str(item.get("user_id") if isinstance(item, dict) else item)
        for item in case.excluded_approvers_json
        if (isinstance(item, dict) and item.get("user_id")) or not isinstance(item, dict)
    }
    acted_ids = {str(action.approver_user_id) for action in case.actions.all()}
    return actor_id not in excluded_ids and actor_id not in acted_ids and any(
        str(item.get("user_id")) == actor_id
        for item in case.required_approvers_json
        if isinstance(item, dict)
    )


def _positive_int(field, value, default):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Must be a positive integer."}) from exc
    if parsed < 1:
        raise ValidationError({field: "Must be a positive integer."})
    return parsed


def _boolean(field, value):
    if value in (None, "", "false"):
        return False
    if value == "true":
        return True
    raise ValidationError({field: "Must be true or false."})
