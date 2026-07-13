"""Public read boundary for immutable approval-case routing snapshots."""

from datetime import timezone as datetime_timezone
from decimal import Decimal, InvalidOperation
from math import ceil
from uuid import UUID

from django.core.exceptions import ValidationError
from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCase, ExceptionRegisterEntry
from sfpcl_credit.approvals.modules.approval_case_selector import (
    select_approval_case_candidates,
)
from sfpcl_credit.approvals.modules.read_scope import (
    evaluate_approval_case_read_scope,
)
from sfpcl_credit.approvals.modules.conflict_of_interest import ConflictOfInterestModule
from sfpcl_credit.domain_errors import DomainObjectAccessDenied
from sfpcl_credit.identity.modules.auth_service import effective_permission_codes
from sfpcl_credit.identity.modules.object_permissions import ObjectAccessResult


_LIST_PARAMS = {"page", "page_size", "current_status", "approval_type", "assigned_to_me"}


def select_readable_approval_cases(*, actor, actor_permissions=None):
    """Return canonical frozen-valid, attributable cases before consumer filters."""
    queryset, persisted_scope_type = select_approval_case_candidates(
        actor=actor,
        actor_permissions=actor_permissions,
    )
    scoped_ids = [
        case.pk
        for case in queryset.iterator(chunk_size=100)
        if approval_case_is_readable(
            actor=actor,
            case=case,
            persisted_scope_type=persisted_scope_type,
            persisted_scope_resolved=True,
            actor_permissions=actor_permissions,
        )
    ]
    return (
        queryset.filter(pk__in=scoped_ids).order_by(
            "-submitted_at", "-approval_case_id"
        ),
        persisted_scope_type,
    )


def approval_case_is_readable(
    *,
    actor,
    case,
    persisted_scope_type=None,
    persisted_scope_resolved=False,
    actor_permissions=None,
):
    """Apply the single canonical frozen-valid and attributable read decision."""
    return is_routable_approval_case(case) and can_read_approval_case(
        actor=actor,
        case=case,
        persisted_scope_type=persisted_scope_type,
        persisted_scope_resolved=persisted_scope_resolved,
        actor_permissions=actor_permissions,
    ).allowed


def list_approval_cases(*, actor, query_params):
    unknown = set(query_params.keys()) - _LIST_PARAMS
    if unknown:
        raise ValidationError(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(_positive_int("page_size", query_params.get("page_size"), 20), 100)
    assigned_to_me = _boolean("assigned_to_me", query_params.get("assigned_to_me"))
    actor_permissions = effective_permission_codes(actor)
    queryset, _ = select_readable_approval_cases(
        actor=actor,
        actor_permissions=actor_permissions,
    )
    current_status = query_params.get("current_status")
    approval_type = query_params.get("approval_type")
    if current_status:
        queryset = queryset.filter(current_status=current_status)
    if approval_type:
        queryset = queryset.filter(approval_type=approval_type)
    if assigned_to_me:
        queryset = queryset.filter(
            current_status=ApprovalCase.STATUS_PENDING,
            required_approver_index__user_id=actor.pk,
        )
        actor_id = str(actor.pk)
        scoped_ids = [
            case.pk
            for case in queryset.iterator(chunk_size=100)
            if is_pending_approval_case_actor(case=case, actor_id=actor_id)
        ]
        queryset = queryset.filter(pk__in=scoped_ids)
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    cases = list(queryset[offset : offset + page_size])
    return [
        serialize_case_detail(case, actor, actor_permissions) for case in cases
    ], {
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
            "appraisal_review_decision",
            "general_meeting_approval",
            "exception_register_entry",
        )
        .prefetch_related("actions")
        .filter(pk=case_id)
        .first()
    )
    if case is None:
        raise ApprovalCase.DoesNotExist
    if not approval_case_is_readable(
        actor=actor, case=case, actor_permissions=actor_permissions
    ):
        if not is_routable_approval_case(case):
            raise ApprovalCase.DoesNotExist
        raise DomainObjectAccessDenied(
            ObjectAccessResult(
                allowed=False,
                reason="approval_case_not_assigned",
                error_code="OBJECT_ACCESS_DENIED",
                required_permission="approvals.case.read",
            )
        )
    return serialize_case_detail(case, actor, set(actor_permissions))


def can_read_approval_case(
    *,
    actor,
    case,
    persisted_scope_type=None,
    persisted_scope_resolved=False,
    actor_permissions=None,
):
    """Return whether the attributable read-scope decision authorises this case."""
    return evaluate_approval_case_read_scope(
        actor=actor,
        case=case,
        persisted_scope_type=persisted_scope_type,
        persisted_scope_resolved=persisted_scope_resolved,
        actor_permissions=actor_permissions,
    )


def serialize_case_summary(case):
    return {
        "approval_case_id": str(case.pk),
        "cycle_number": case.cycle_number,
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
    from sfpcl_credit.approvals.modules import general_meeting

    action_by_user = {
        str(action.approver_user_id): action for action in case.actions.all()
    }
    available_actions = _available_actions(
        case, actor, actor_permissions, action_by_user
    )
    if case.general_meeting_evidence_required:
        available_actions.append(
            general_meeting.record_action_availability(
                case=case, actor=actor, actor_permissions=actor_permissions
            )
        )
    snapshot = {
        **serialize_case_snapshot(case),
        "review_facts": case.appraisal_facts_json,
        "workbench_summary": _workbench_summary(case),
        "available_actions": available_actions,
    }
    return snapshot


def serialize_case_snapshot(case):
    """Serialize the canonical immutable routed-case projection."""
    from sfpcl_credit.approvals.modules import general_meeting

    return {
        **serialize_case_summary(case),
        "approval_matrix_rule_id": str(case.approval_matrix_rule_id),
        "approval_matrix_rule_version": case.approval_matrix_rule_version,
        "sanction_committee_id": str(case.sanction_committee_id),
        "sanction_committee_version": case.sanction_committee_version,
        **serialize_case_authority(case),
        "excluded_approvers": case.excluded_approvers_json,
        "general_meeting_evidence_required": case.general_meeting_evidence_required,
        "general_meeting_approval": general_meeting.serialize_for_case(case),
        "conflict_block_reason": case.conflict_block_reason or None,
        "reason_for_approval": case.reason_for_approval,
        "exception_condition_code": case.exception_condition_code or None,
        "exception_reason": case.exception_reason or None,
        "matrix_projection": case.matrix_projection_json,
        "committee_projection": case.committee_projection_json,
        "loan_limit_provenance": case.loan_limit_provenance_json,
    }


def _workbench_summary(case):
    facts = case.appraisal_facts_json
    borrower = facts["borrower"]
    amounts = facts["loan_amounts"]
    risk = facts["risk"]
    return {
        "borrower_name": borrower["name"],
        "member_type": borrower["member_type"],
        "requested_amount": amounts["requested_amount"],
        "recommended_amount": amounts["recommended_amount"],
        "eligible_amount": amounts["eligible_amount"],
        "approval_path": _approval_path(case),
        "exception_flag": bool(case.exception_condition_code),
        "related_party_flag": bool(
            case.general_meeting_evidence_required or case.excluded_approvers_json
        ),
        "risk_rating": risk["overall_risk_rating"],
        "submitted_at": _utc_time(case.submitted_at),
        "current_decision_status": _current_decision_status(case),
        "pending_age": _pending_age(case),
    }


def _approval_path(case):
    projection = case.matrix_projection_json
    roles = projection.get("required_approver_roles", [])
    parts = []
    if "cfo" in roles:
        parts.append("CFO")
    director_count = projection.get("required_director_count", 0)
    if isinstance(director_count, int) and director_count > 0:
        parts.append(
            "one Director" if director_count == 1
            else f"{director_count} Directors"
        )
    summary = " + ".join(parts) or "Approval path unavailable"
    if case.general_meeting_evidence_required:
        summary += " — special approval"
    elif case.exception_condition_code:
        summary += " — exception route"
    return summary


def _current_decision_status(case):
    if case.current_status == ApprovalCase.STATUS_PENDING and any(
        action.decision == "approved"
        for action in case.actions.all()
    ):
        return "partially_approved"
    return case.current_status


def _pending_age(case):
    if case.current_status != ApprovalCase.STATUS_PENDING:
        return None
    elapsed_seconds = max(0, int((timezone.now() - case.submitted_at).total_seconds()))
    days, remainder = divmod(elapsed_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    if days:
        display = f"{days}d {hours}h"
    elif hours:
        display = f"{hours}h {minutes}m"
    else:
        display = f"{minutes}m"
    return {
        "label": "Elapsed pending time",
        "elapsed_seconds": elapsed_seconds,
        "display": display,
    }


def _utc_time(value):
    return value.astimezone(datetime_timezone.utc).isoformat().replace("+00:00", "Z")


def serialize_case_authority(case):
    """Project immutable route, executable replacements, and every action together."""
    actions = list(case.actions.all())
    action_by_user = {str(action.approver_user_id): action for action in actions}
    effective = ConflictOfInterestModule.effective_approvers(case)
    user_ids = {
        str(item["user_id"])
        for item in effective
        if isinstance(item, dict) and item.get("user_id")
    } | {str(action.approver_user_id) for action in actions}
    from sfpcl_credit.identity.models import User

    users = {str(pk): user for pk, user in User.objects.in_bulk(user_ids).items()}
    required_approvers = []
    replacement_by_user = {}
    for item in effective:
        user_id = str(item["user_id"])
        action = action_by_user.get(user_id)
        row = {
            "role_code": item["role_code"],
            "user_id": user_id,
            "full_name": users[user_id].full_name,
            "decision": action.decision if action else None,
            "acted_at": _action_time(action),
        }
        if item.get("replacement_for_user_id"):
            row["replacement_for_user_id"] = str(
                item["replacement_for_user_id"]
            )
            replacement_by_user[user_id] = row["replacement_for_user_id"]
        required_approvers.append(row)
    approval_actions = []
    for action in actions:
        user_id = str(action.approver_user_id)
        row = {
            "approval_action_id": str(action.pk),
            "role_code": action.approver_role_code,
            "user_id": user_id,
            "full_name": users[user_id].full_name,
            "decision": action.decision,
            "comments": action.comments,
            "acted_at": _action_time(action),
        }
        if user_id in replacement_by_user:
            row["replacement_for_user_id"] = replacement_by_user[user_id]
        approval_actions.append(row)
    return {
        "route_approvers": case.required_approvers_json,
        "required_approvers": required_approvers,
        "approval_actions": approval_actions,
    }


def _action_time(action):
    if action is None:
        return None
    return action.acted_at.isoformat().replace("+00:00", "Z")


def _available_actions(case, actor, actor_permissions, action_by_user):
    actor_id = str(actor.pk)
    conflict_reason = ConflictOfInterestModule.conflict_reason(
        case=case, actor_id=actor_id
    )
    pending_assignment = is_pending_approval_case_actor(
        case=case, actor_id=actor_id
    )
    action_specs = (
        ("approve", "Approve", "approvals.case.approve"),
        ("reject", "Reject", "approvals.case.reject"),
        ("return", "Return for Clarification", "approvals.case.return"),
        ("abstain", "Abstain for Conflict", "approvals.case.approve"),
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
        elif conflict_reason:
            reason = "This user is marked as conflicted for the approval case and cannot approve it."
        elif permission not in actor_permissions:
            reason = "Required permission is not granted."
        elif not pending_assignment:
            reason = "You are not a pending approver for this case."
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


def approval_case_action_availability(
    *, case, actor, actor_permissions, action_code
):
    """Return the canonical §44 decision consumed by detail and writes."""
    action_by_user = {
        str(action.approver_user_id): action for action in case.actions.all()
    }
    return next(
        action for action in _available_actions(
            case, actor, set(actor_permissions), action_by_user
        )
        if action["action_code"] == action_code
    )


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
        and _exception_route_is_coherent(case, matrix)
        and isinstance(committee, dict)
        and committee.get("sanction_committee_id") == str(case.sanction_committee_id)
        and committee.get("version_number") == case.sanction_committee_version
        and committee.get("decision_date") == case.decision_date.isoformat()
        and _approver_snapshot_is_coherent(required, matrix, committee)
        and _exclusion_snapshot_is_coherent(case.excluded_approvers_json, committee)
        and _conflict_authority_state_is_coherent(case)
        and _loan_limit_provenance_is_complete(case)
        and _review_snapshot_is_complete(case)
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
            )
        )
        and isinstance(roles, list)
        and roles == ["cfo", "director"]
        and isinstance(director_count, int)
        and director_count in (1, 2)
        and matrix.get("joint_approval_required") is True
        and isinstance(matrix.get("register_required"), str)
        and bool(matrix["register_required"].strip())
    )


def _exception_route_is_coherent(case, matrix):
    condition = matrix.get("condition_code") or ""
    if not condition:
        return True
    try:
        entry = case.exception_register_entry
    except ExceptionRegisterEntry.DoesNotExist:
        return False
    provenance = case.loan_limit_provenance_json
    try:
        final_eligible_amount = Decimal(
            str(provenance["final_eligible_loan_amount"])
        )
    except (KeyError, InvalidOperation, TypeError, ValueError):
        return False
    amount_exceeds_limit = case.amount > final_eligible_amount
    expected_type = (
        ExceptionRegisterEntry.TYPE_EXCEEDS_LOAN_LIMIT
        if case.exception_required_flag
        else None
    )
    return (
        condition == "exceeds_permissible_limit"
        and matrix.get("register_required") == "exception_register"
        and matrix.get("required_director_count") == 2
        and entry.approval_case_id == case.pk
        and entry.loan_application_id == case.loan_application_id
        and entry.business_reason == case.exception_reason
        and (entry.risk_assessment is None or bool(entry.risk_assessment.strip()))
        and amount_exceeds_limit == case.exception_required_flag
        and (
            entry.exception_type == expected_type
            if expected_type
            else entry.exception_type
            in {
                ExceptionRegisterEntry.TYPE_STAGE_BYPASS,
                ExceptionRegisterEntry.TYPE_WAIVER,
            }
        )
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


def _exclusion_snapshot_is_coherent(exclusions, committee):
    committee_ids = {
        str(committee.get("cfo_user_id") or ""),
        *(
            str(user_id)
            for user_id in committee.get("director_user_ids", [])
            if user_id
        ),
    } - {""}
    seen = set()
    for item in exclusions:
        if not isinstance(item, dict):
            return False
        user_id = str(item.get("user_id") or "")
        if (
            not user_id
            or user_id not in committee_ids
            or user_id in seen
            or not isinstance(item.get("reason"), str)
            or not item["reason"].strip()
            or not isinstance(item.get("conflict_code"), str)
            or not item["conflict_code"].strip()
        ):
            return False
        seen.add(user_id)
    return True


def _conflict_authority_state_is_coherent(case):
    satisfiable = ConflictOfInterestModule.authority_is_satisfiable(case)
    if case.current_status == ApprovalCase.STATUS_BLOCKED_CONFLICT:
        return (
            not satisfiable
            and case.closed_at is not None
            and case.conflict_block_reason
            == ConflictOfInterestModule.authority_gap_reason(case)
        )
    return satisfiable and not case.conflict_block_reason


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
    """Validate approval-owned frozen provenance without consulting live credit rows."""
    provenance = case.loan_limit_provenance_json
    required = (
        "loan_limit_assessment_id",
        "loan_application_id",
        "final_eligible_loan_amount",
        "exception_required_flag",
        "calculation_rule_version",
        "policy_config_id",
        "policy_name",
        "calculated_at",
    )
    condition_requires_exception = bool(case.exception_condition_code)
    complete = (
        isinstance(provenance, dict)
        and all(provenance.get(key) not in (None, "") for key in required)
        and str(provenance["loan_application_id"]) == str(case.loan_application_id)
        and isinstance(provenance["exception_required_flag"], bool)
        and provenance["exception_required_flag"] == case.exception_required_flag
        and (not provenance["exception_required_flag"] or condition_requires_exception)
    )
    if not complete:
        return False
    try:
        final_eligible_amount = Decimal(
            str(provenance["final_eligible_loan_amount"])
        )
        calculated_at = timezone.datetime.fromisoformat(
            str(provenance["calculated_at"]).replace("Z", "+00:00")
        )
    except (InvalidOperation, TypeError, ValueError):
        return False
    return final_eligible_amount >= Decimal("0.00") and calculated_at is not None


def _review_snapshot_is_complete(case):
    """Validate mandatory approval-owned review facts without live credit reads."""
    facts = case.appraisal_facts_json
    if not isinstance(facts, dict) or not facts:
        return False
    required_sections = {
        "snapshot_schema_version",
        "snapshot_provenance",
        "maker_checker",
        "borrower",
        "eligibility",
        "loan_amounts",
        "purpose",
        "compliance_checks",
        "borrowing_history",
        "risk",
        "documentation_completeness",
        "source_references",
    }
    if not required_sections.issubset(facts):
        return False

    provenance = facts.get("snapshot_provenance")
    if (
        facts.get("snapshot_schema_version") != "approval-review-v2"
        or not isinstance(provenance, dict)
        or provenance.get("owner") != "credit"
        or provenance.get("review_decision_id") in (None, "")
    ):
        return False

    maker = facts.get("maker_checker")
    borrower = facts.get("borrower")
    amounts = facts.get("loan_amounts")
    purpose = facts.get("purpose")
    compliance = facts.get("compliance_checks")
    risk = facts.get("risk")
    documentation = facts.get("documentation_completeness")
    references = facts.get("source_references")
    eligibility = facts.get("eligibility")
    mappings = (maker, borrower, amounts, purpose, compliance, risk, documentation, references)
    if not all(isinstance(item, dict) for item in mappings):
        return False
    if not isinstance(eligibility, dict) or not eligibility:
        return False

    required_keys = (
        (
            maker,
            {
                "application_created_by_user_id",
                "application_received_by_user_id",
                "application_submitted_by_user_id",
                "appraisal_prepared_by_user_id",
                "appraisal_reviewed_by_user_id",
            },
        ),
        (borrower, {"name", "member_type"}),
        (amounts, {"requested_amount", "eligible_amount", "recommended_amount"}),
        (purpose, {"category", "description"}),
        (
            compliance,
            {
                "member_active_check",
                "default_check",
                "terms_acceptance_check",
                "purpose_check",
            },
        ),
        (
            risk,
            {
                "risk_assessment_id",
                "market_risk_rating",
                "operational_risk_rating",
                "borrower_risk_rating",
                "overall_risk_rating",
                "risk_mitigation_notes",
            },
        ),
        (documentation, {"status", "document_check"}),
        (references, {"application", "appraisal", "eligibility", "loan_limit"}),
    )
    if any(not keys.issubset(mapping) for mapping, keys in required_keys):
        return False
    def is_uuid_string(value, *, nullable=False):
        if nullable and value is None:
            return True
        if not isinstance(value, str) or not value:
            return False
        try:
            UUID(value)
        except (TypeError, ValueError):
            return False
        return True

    if not all(
        is_uuid_string(maker.get(key), nullable=key in {
            "application_created_by_user_id",
            "application_submitted_by_user_id",
        })
        for key in maker
    ):
        return False
    if any(
        not isinstance(borrower.get(key), str) or not borrower.get(key).strip()
        for key in ("name", "member_type")
    ):
        return False
    if any(
        maker.get(key) in (None, "")
        for key in (
            "application_received_by_user_id",
            "appraisal_prepared_by_user_id",
            "appraisal_reviewed_by_user_id",
        )
    ):
        return False
    if case.appraisal_review_decision_id is None:
        return False
    if str(maker["appraisal_reviewed_by_user_id"]) != str(
        case.appraisal_review_decision.reviewer_user_id
    ):
        return False
    if str(provenance["review_decision_id"]) != str(
        case.appraisal_review_decision_id
    ):
        return False
    if not is_uuid_string(provenance["review_decision_id"]):
        return False
    if not isinstance(facts.get("borrowing_history"), str):
        return False
    if not all(
        isinstance(purpose.get(key), (str, type(None)))
        for key in ("category", "description")
    ):
        return False
    if not all(
        isinstance(compliance.get(key), (str, type(None)))
        for key in (
            "member_active_check",
            "default_check",
            "terms_acceptance_check",
            "purpose_check",
        )
    ):
        return False
    if not isinstance(risk.get("risk_mitigation_notes"), str):
        return False
    if not isinstance(documentation.get("document_check"), str):
        return False
    eligibility_keys = {
        "eligibility_assessment_id",
        "loan_application_id",
        "member_active_check",
        "default_check",
        "document_check",
        "terms_acceptance_check",
        "purpose_check",
        "nominee_check",
        "overall_result",
        "assessment_notes",
        "active_member_snapshot",
        "assessed_by_user_id",
        "assessed_at",
    }
    if not eligibility_keys.issubset(eligibility):
        return False
    if (
        not isinstance(eligibility.get("overall_result"), str)
        or str(eligibility.get("loan_application_id")) != str(case.loan_application_id)
        or not is_uuid_string(eligibility.get("loan_application_id"))
        or not is_uuid_string(eligibility.get("eligibility_assessment_id"))
        or not is_uuid_string(eligibility.get("assessed_by_user_id"))
        or not isinstance(eligibility.get("active_member_snapshot"), dict)
        or not isinstance(eligibility.get("assessment_notes"), str)
    ):
        return False
    if not all(
        isinstance(eligibility.get(key), str)
        for key in (
            "member_active_check",
            "default_check",
            "document_check",
            "terms_acceptance_check",
            "purpose_check",
            "nominee_check",
        )
    ):
        return False
    try:
        assessed_at = timezone.datetime.fromisoformat(
            eligibility.get("assessed_at", "").replace("Z", "+00:00")
        )
    except (AttributeError, TypeError, ValueError):
        return False
    if assessed_at.tzinfo is None:
        return False
    if any(
        compliance[key] != eligibility[key]
        for key in (
            "member_active_check",
            "default_check",
            "terms_acceptance_check",
            "purpose_check",
        )
    ) or documentation["document_check"] != eligibility["document_check"]:
        return False
    try:
        requested_amount = amounts.get("requested_amount")
        if requested_amount is not None and Decimal(str(requested_amount)) < 0:
            return False
        if Decimal(str(amounts.get("eligible_amount"))) < 0:
            return False
        if Decimal(str(amounts.get("recommended_amount"))) < 0:
            return False
    except (InvalidOperation, TypeError, ValueError):
        return False
    if (
        not is_uuid_string(risk.get("risk_assessment_id"))
        or any(
            not isinstance(risk.get(key), str) or not risk.get(key)
            for key in (
                "market_risk_rating",
                "operational_risk_rating",
                "borrower_risk_rating",
                "overall_risk_rating",
            )
        )
    ):
        return False
    if not isinstance(documentation.get("status"), str) or not documentation.get(
        "status"
    ):
        return False

    application_id = str(case.loan_application_id)
    expected_references = {
        "application": f"/api/v1/loan-applications/{application_id}/",
        "appraisal": f"/api/v1/loan-applications/{application_id}/appraisal-note/",
        "eligibility": f"/api/v1/loan-applications/{application_id}/eligibility-assessment/",
        "loan_limit": f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/",
    }
    return (
        references == expected_references
        and _same_amount(amounts.get("recommended_amount"), case.amount)
        and _same_amount(
            amounts.get("eligible_amount"),
            case.loan_limit_provenance_json.get("final_eligible_loan_amount"),
        )
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
        for item in ConflictOfInterestModule.effective_approvers(case)
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
