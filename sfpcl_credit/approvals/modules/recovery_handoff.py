"""Approval-owned persistence adapter for frozen recovery submissions."""

from django.db.models import Max
from django.utils import timezone

from sfpcl_credit.approvals.models import (
    ApprovalCase,
    ApprovalCaseRequiredApprover,
)
from sfpcl_credit.approvals.modules.sanction_committee import (
    SanctionCommitteeResolutionError,
    resolve_sanction_committee,
)
from sfpcl_credit.approvals.modules.approval_matrix import (
    ApprovalMatrixResolutionError,
    resolve_approval_matrix,
)
from sfpcl_credit.approvals.modules.conflict_of_interest import (
    ConflictOfInterestModule,
)
from sfpcl_credit.identity.models import User
from sfpcl_credit.workflows.events import record_workflow_event


class RecoveryApprovalRouteUnavailable(Exception):
    pass


def create_or_reuse_recovery_case(*, note, actor, submitted_at):
    existing = ApprovalCase.objects.filter(
        approval_type=ApprovalCase.TYPE_RECOVERY,
        related_entity_type="non_payment_note",
        related_entity_id=note.pk,
        current_status=ApprovalCase.STATUS_PENDING,
    ).first()
    if existing is not None:
        return existing
    account = note.loan_account
    source_case = (
        ApprovalCase.objects.select_related(
            "loan_appraisal_note", "appraisal_review_decision"
        )
        .filter(loan_application_id=account.loan_application_id)
        .order_by("-cycle_number", "-submitted_at")
        .first()
    )
    if source_case is None:
        raise RecoveryApprovalRouteUnavailable(
            "The loan has no retained approval case to own the recovery route."
        )
    try:
        committee = resolve_sanction_committee(timezone.localdate())
    except SanctionCommitteeResolutionError as exc:
        raise RecoveryApprovalRouteUnavailable(
            "No unambiguous Sanction Committee is configured for submission."
        ) from exc
    try:
        matrix = resolve_approval_matrix(
            decision_type="recovery",
            amount=note.outstanding_principal_amount + note.outstanding_interest_amount,
            condition_code=note.recommended_recovery_action,
            decision_date=timezone.localdate(),
        )
    except ApprovalMatrixResolutionError as exc:
        raise RecoveryApprovalRouteUnavailable(
            "No unambiguous approval matrix route is configured for the recommended recovery action."
        ) from exc
    if not matrix.joint_approval_required:
        raise RecoveryApprovalRouteUnavailable(
            "Recovery routes must require a complete distinct authority chain."
        )
    if "director" in matrix.required_approver_roles and not (
        1 <= matrix.required_director_count <= 2
    ):
        raise RecoveryApprovalRouteUnavailable(
            "The configured recovery route has an unsupported Director count."
        )
    users = User.objects.in_bulk(
        [committee.cfo_user_id, committee.director_1_user_id, committee.director_2_user_id]
    )
    approver_facts = []
    for role_code in matrix.required_approver_roles:
        if role_code == "cfo":
            user_ids = [committee.cfo_user_id]
        elif role_code == "director":
            user_ids = [committee.director_1_user_id, committee.director_2_user_id][
                : matrix.required_director_count
            ]
        else:
            raise RecoveryApprovalRouteUnavailable(
                "The configured recovery route contains an unsupported login authority."
            )
        approver_facts.extend((role_code, user_id) for user_id in user_ids)
    if not approver_facts or len({user_id for _, user_id in approver_facts}) != len(
        approver_facts
    ):
        raise RecoveryApprovalRouteUnavailable(
            "The configured recovery route must resolve to distinct approval authorities."
        )
    if len(users) != 3:
        raise RecoveryApprovalRouteUnavailable(
            "The configured Sanction Committee contains an unavailable user."
        )
    required_approvers = [
        {
            "role_code": role_code,
            "user_id": str(user_id),
            "full_name": users[user_id].full_name,
        }
        for role_code, user_id in approver_facts
    ]
    next_cycle = (
        ApprovalCase.objects.filter(loan_application_id=account.loan_application_id)
        .aggregate(value=Max("cycle_number"))["value"]
        or 0
    ) + 1
    case = ApprovalCase.objects.create(
        loan_application_id=account.loan_application_id,
        loan_appraisal_note=source_case.loan_appraisal_note,
        appraisal_review_decision=source_case.appraisal_review_decision,
        appraisal_revision=source_case.appraisal_revision,
        appraisal_facts_json={
            "snapshot_schema_version": "non-payment-note-v1",
            "maker_checker": {
                "appraisal_prepared_by_user_id": str(note.prepared_by_user_id),
                "application_submitted_by_user_id": str(actor.pk),
            },
            "non_payment_note": {
                "non_payment_note_id": str(note.pk),
                "default_case_id": str(note.default_case_id),
                "loan_account_id": str(note.loan_account_id),
                "reason_for_non_payment": note.reason_for_non_payment,
                "intentionality_assessment": note.intentionality_assessment,
                "outstanding_principal_amount": f"{note.outstanding_principal_amount:.2f}",
                "outstanding_interest_amount": f"{note.outstanding_interest_amount:.2f}",
                "recommended_recovery_action": note.recommended_recovery_action,
                "evidence_document_ids": list(note.evidence_document_ids_json),
                "case_facts": dict(note.frozen_case_facts_json),
            },
        },
        cycle_number=next_cycle,
        approval_type=ApprovalCase.TYPE_RECOVERY,
        current_status=ApprovalCase.STATUS_PENDING,
        submission_remarks="Formal Non-Payment Note submitted for recovery decision.",
        submitted_by_user=actor,
        submitted_at=submitted_at,
        approval_matrix_rule_id=matrix.approval_matrix_rule_id,
        approval_matrix_rule_version=matrix.version_number,
        sanction_committee_id=committee.sanction_committee_id,
        sanction_committee_version=committee.version_number,
        required_approvers_json=required_approvers,
        excluded_approvers_json=[],
        committee_projection_json={
            "sanction_committee_id": str(committee.sanction_committee_id),
            "version_number": committee.version_number,
            "decision_date": timezone.localdate().isoformat(),
            "cfo_user_id": str(committee.cfo_user_id),
            "director_user_ids": [
                str(committee.director_1_user_id),
                str(committee.director_2_user_id),
            ],
        },
        matrix_projection_json={
            "approval_matrix_rule_id": str(matrix.approval_matrix_rule_id),
            "version_number": matrix.version_number,
            "decision_type": matrix.decision_type,
            "amount": f"{matrix.amount:.2f}",
            "amount_min": (
                f"{matrix.amount_min:.2f}" if matrix.amount_min is not None else None
            ),
            "amount_max": (
                f"{matrix.amount_max:.2f}" if matrix.amount_max is not None else None
            ),
            "condition_code": matrix.condition_code,
            "decision_date": matrix.decision_date.isoformat(),
            "required_approver_roles": list(matrix.required_approver_roles),
            "required_director_count": matrix.required_director_count,
            "joint_approval_required": matrix.joint_approval_required,
            "register_required": matrix.register_required,
        },
        amount=note.outstanding_principal_amount + note.outstanding_interest_amount,
        related_entity_type="non_payment_note",
        related_entity_id=note.pk,
        reason_for_approval=note.recommended_recovery_action,
        decision_date=timezone.localdate(),
        version=2,
    )
    conflict_assessment = ConflictOfInterestModule().evaluate_for_case(case)
    case.excluded_approvers_json = list(conflict_assessment.exclusions)
    if not ConflictOfInterestModule.authority_is_satisfiable(case):
        case.delete()
        raise RecoveryApprovalRouteUnavailable(
            "The configured recovery authority is insufficient after conflict exclusions."
        )
    case.save(update_fields=["excluded_approvers_json"])
    ApprovalCaseRequiredApprover.objects.bulk_create(
        [
            ApprovalCaseRequiredApprover(approval_case=case, user_id=user_id)
            for _, user_id in approver_facts
        ]
    )
    event = record_workflow_event(
        actor=actor,
        workflow_name="recovery_approval_submission",
        entity_type="non_payment_note",
        entity_id=note.pk,
        from_state="draft",
        to_state="submitted",
        trigger_reason=note.reason_for_non_payment,
        action_code="non_payment_note.submitted",
        metadata={"approval_case_id": str(case.pk)},
    )
    case.workflow_event = event
    case.save(update_fields=["workflow_event"])
    return case
