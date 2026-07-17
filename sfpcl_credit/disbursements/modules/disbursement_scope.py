import hashlib

from sfpcl_credit.disbursements.models import Disbursement


def has_cfc_scope(*, actor_id, loan_account_id):
    rows = list(
        Disbursement.objects.select_related(
            "cfc_task", "initiation_audit", "initiation_workflow_event"
        )
        .filter(
            loan_account_id=loan_account_id,
            initiation_status=Disbursement.INITIATED,
            authorisation_status=Disbursement.AUTHORISATION_PENDING,
            bank_transfer_status=Disbursement.TRANSFER_PENDING,
        )
        .order_by("disbursement_id")[:2]
    )
    if len(rows) != 1:
        return False
    row = rows[0]
    evidence = row.initiation_audit.new_value_json or {}
    request_id = evidence.get("request_id")
    comment_digest = evidence.get("final_verification_comment_digest")
    trace = (
        f"request_id={request_id};verification_digest={comment_digest};"
        f"amount={row.disbursement_amount:.2f}"
    )
    expected_comment_digest = hashlib.sha256(
        row.final_verification_comments.encode()
    ).hexdigest()
    return bool(
        request_id
        and comment_digest
        and len(comment_digest) == 64
        and evidence.get("disbursement_id") == str(row.pk)
        and evidence.get("loan_account_id") == str(row.loan_account_id)
        and evidence.get("loan_application_id") == str(row.loan_application_id)
        and evidence.get("member_id") == str(row.member_id)
        and evidence.get("disbursement_amount") == f"{row.disbursement_amount:.2f}"
        and evidence.get("borrower_bank_account_id")
        == str(row.borrower_bank_account_id)
        and evidence.get("source_bank_account_id") == str(row.source_bank_account_id)
        and evidence.get("maker_user_id") == str(row.initiated_by_user_id)
        and evidence.get("maker_role_codes") == [row.maker_role_code]
        and evidence.get("maker_team_codes") == row.maker_team_codes_json
        and evidence.get("readiness_digest") == row.readiness_digest
        and evidence.get("readiness_evidence") == row.readiness_evidence_json
        and evidence.get("idempotency_digest") == row.idempotency_key_digest
        and comment_digest == expected_comment_digest
        and row.initiation_audit.action == "disbursement.initiated"
        and row.initiation_audit.entity_type == "disbursement"
        and row.initiation_audit.entity_id == row.pk
        and row.initiation_audit.actor_user_id == row.initiated_by_user_id
        and row.initiation_workflow_event.workflow_name == "DisbursementInitiated"
        and row.initiation_workflow_event.entity_type == "disbursement"
        and row.initiation_workflow_event.entity_id == row.pk
        and row.initiation_workflow_event.from_state is None
        and row.initiation_workflow_event.to_state == Disbursement.INITIATED
        and row.initiation_workflow_event.triggered_by_user_id
        == row.initiated_by_user_id
        and row.initiation_workflow_event.trigger_reason == trace
        and row.cfc_task.notification_type == "disbursement_authorisation"
        and row.cfc_task.category == "Finance"
        and row.cfc_task.severity == row.cfc_task.SEVERITY_URGENT
        and row.cfc_task.related_entity_type == "disbursement"
        and row.cfc_task.related_entity_id == row.pk
        and row.cfc_task.recipient_role_code == "chief_financial_controller"
        and row.cfc_task.sender_user_id == row.initiated_by_user_id
        and row.cfc_task.action_label == "Review disbursement"
        and row.cfc_task.action_url
        == f"/api/v1/disbursements/{row.pk}/authorise/"
        and trace in row.cfc_task.message
    )
