import hashlib
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.configurations.modules.source_bank_governance import (
    resolve_source_bank_account,
)
from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.domain_errors import DomainObjectAccessDenied, DomainPermissionDenied
from sfpcl_credit.identity.models import AuditLog, Permission, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.workflows.events import record_workflow_event


AUTHORISE_PERMISSION = "finance.disbursement.authorise"
CFC_ROLE = "chief_financial_controller"
DECISIONS = {"approved", "rejected"}


class DisbursementAuthorisationConflict(Exception):
    code = "CONFLICT"


def _authorise(*, actor, disbursement_id, payload, request=None):
    cleaned = _validate_payload(payload)
    with transaction.atomic():
        checker = _locked_checker(actor)
        row = (
            Disbursement.objects.select_for_update(of=("self",))
            .select_related(
                "loan_account",
                "loan_account__terms",
                "cfc_task",
                "initiation_audit",
                "initiation_workflow_event",
            )
            .filter(pk=disbursement_id)
            .first()
        )
        if row is None:
            raise DomainObjectAccessDenied(None)
        _lock_related_evidence(row)
        if row.authorisation_status in DECISIONS:
            if _is_complete_terminal_replay(row, cleaned):
                return serialize_authorisation(row)
            raise DisbursementAuthorisationConflict(
                "The disbursement already has a different terminal authorisation decision."
            )
        source = resolve_source_bank_account(for_update=True)
        if not _coherent_pending_initiation(row) or not _current_source_matches(
            row, source
        ):
            raise DisbursementAuthorisationConflict(
                "The pending disbursement initiation evidence is stale or incoherent."
            )
        if row.initiated_by_user_id == checker.pk:
            raise DomainPermissionDenied(
                "The CFC checker must be different from the payment initiator."
            )

        now = timezone.now()
        request_id = _request_id(request)
        ip_address = request_ip(request) if request else ""
        user_agent = request_user_agent(request) if request else ""
        comments_digest = _sha256(cleaned["comments"])
        initiation_request_id = row.initiation_audit.new_value_json["request_id"]
        initiation_comment_digest = row.initiation_audit.new_value_json[
            "final_verification_comment_digest"
        ]
        evidence_digest = _sha256(
            initiation_request_id + row.readiness_digest + initiation_comment_digest
        )
        action_id = uuid.uuid4()
        teams = sorted(checker.team_codes())
        safe_evidence = {
            "action_id": str(action_id),
            "disbursement_id": str(row.pk),
            "loan_account_id": str(row.loan_account_id),
            "loan_application_id": str(row.loan_application_id),
            "member_id": str(row.member_id),
            "disbursement_amount": f"{row.disbursement_amount:.2f}",
            "maker_user_id": str(row.initiated_by_user_id),
            "maker_role_code": row.maker_role_code,
            "maker_team_codes": row.maker_team_codes_json,
            "checker_user_id": str(checker.pk),
            "checker_role_code": CFC_ROLE,
            "checker_team_codes": teams,
            "initiation_request_id": initiation_request_id,
            "initiation_comment_digest": initiation_comment_digest,
            "readiness_digest": row.readiness_digest,
            "authorisation_evidence_digest": evidence_digest,
            "comments_digest": comments_digest,
            "request_id": request_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "authorised_at": now.isoformat().replace("+00:00", "Z"),
            "authorisation_status": cleaned["decision"],
            "bank_transfer_status": Disbursement.TRANSFER_PENDING,
            "outcome": cleaned["decision"],
        }
        action = (
            "disbursement.authorised"
            if cleaned["decision"] == "approved"
            else "disbursement.rejected"
        )
        audit = AuditLog.objects.create(
            actor_user=checker,
            actor_type="user",
            action=action,
            entity_type="disbursement",
            entity_id=row.pk,
            old_value_json={
                "authorisation_status": Disbursement.AUTHORISATION_PENDING,
                "bank_transfer_status": Disbursement.TRANSFER_PENDING,
            },
            new_value_json=safe_evidence,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        trace = (
            f"action_id={action_id};request_id={request_id};"
            f"evidence_digest={evidence_digest};comments_digest={comments_digest}"
        )
        workflow = record_workflow_event(
            actor=checker,
            workflow_name="DisbursementAuthorisation",
            entity_type="disbursement",
            entity_id=row.pk,
            from_state=Disbursement.AUTHORISATION_PENDING,
            to_state=cleaned["decision"],
            trigger_reason=trace,
            action_code=action,
            metadata=safe_evidence,
        )
        task = row.cfc_task
        task.read_at = now
        task.read_by_user = checker
        task.read_state_version += 1
        task.action_label = cleaned["decision"].title()
        task.action_url = ""
        task.message = f"{task.message} Decision: {cleaned['decision']}."
        task.save(
            update_fields=[
                "read_at",
                "read_by_user",
                "read_state_version",
                "action_label",
                "action_url",
                "message",
                "updated_at",
            ]
        )

        row.authorisation_status = cleaned["decision"]
        row.authorised_by_user = checker
        row.authorised_at = now
        row.authorisation_comments = cleaned["comments"]
        row.checker_role_code = CFC_ROLE
        row.checker_team_codes_json = teams
        row.authorisation_action_id = action_id
        row.authorisation_evidence_digest = evidence_digest
        row.authorisation_request_id = request_id
        row.authorisation_ip_address = ip_address
        row.authorisation_user_agent = user_agent
        row.authorisation_audit = audit
        row.authorisation_workflow_event = workflow
        row.save(
            update_fields=[
                "authorisation_status",
                "authorised_by_user",
                "authorised_at",
                "authorisation_comments",
                "checker_role_code",
                "checker_team_codes_json",
                "authorisation_action_id",
                "authorisation_evidence_digest",
                "authorisation_request_id",
                "authorisation_ip_address",
                "authorisation_user_agent",
                "authorisation_audit",
                "authorisation_workflow_event",
            ]
        )
        return serialize_authorisation(row)


def serialize_authorisation(row):
    return {
        "disbursement_id": str(row.pk),
        "authorisation_status": row.authorisation_status,
        "bank_transfer_status": row.bank_transfer_status,
        "authorised_at": row.authorised_at.isoformat().replace("+00:00", "Z"),
        "next_action": (
            "record_bank_transfer" if row.authorisation_status == "approved" else "none"
        ),
    }


def _validate_payload(payload):
    allowed = {"decision", "comments"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    for field in allowed - set(payload):
        errors[field] = "This field is required."
    decision = payload.get("decision")
    if not isinstance(decision, str) or decision not in DECISIONS:
        errors["decision"] = "Must be approved or rejected."
    raw_comments = payload.get("comments")
    comments = raw_comments.strip() if isinstance(raw_comments, str) else ""
    if not comments:
        errors["comments"] = "This field is required."
    elif len(comments) > 2000:
        errors["comments"] = "Must be at most 2000 characters."
    if errors:
        raise ValidationError(errors)
    return {"decision": decision, "comments": comments}


def _lock_related_evidence(row):
    from sfpcl_credit.applications.models import LoanApplication
    from sfpcl_credit.communications.models import Notification
    from sfpcl_credit.identity.models import AuditLog
    from sfpcl_credit.loans.models import LoanAccount
    from sfpcl_credit.members.models import BankAccount, Member
    from sfpcl_credit.workflows.models import WorkflowEvent

    LoanAccount.objects.select_for_update().get(pk=row.loan_account_id)
    LoanApplication.objects.select_for_update().get(pk=row.loan_application_id)
    Member.objects.select_for_update().get(pk=row.member_id)
    list(
        BankAccount.objects.select_for_update()
        .filter(pk__in=(row.borrower_bank_account_id, row.source_bank_account_id))
        .order_by("bank_account_id")
    )
    Notification.objects.select_for_update().get(pk=row.cfc_task_id)
    AuditLog.objects.select_for_update().get(pk=row.initiation_audit_id)
    WorkflowEvent.objects.select_for_update().get(pk=row.initiation_workflow_event_id)
    if row.authorisation_audit_id:
        AuditLog.objects.select_for_update().get(pk=row.authorisation_audit_id)
    if row.authorisation_workflow_event_id:
        WorkflowEvent.objects.select_for_update().get(
            pk=row.authorisation_workflow_event_id
        )


def _locked_checker(actor):
    checker = (
        User.objects.select_for_update()
        .select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None), status=User.ACTIVE_STATUS)
        .first()
    )
    roles = set(auth_service.effective_role_codes(checker)) if checker else set()
    permission = Permission.objects.filter(permission_code=AUTHORISE_PERMISSION).first()
    permissions = (
        set(auth_service.effective_permission_codes(checker)) if checker else set()
    )
    if (
        checker is None
        or not checker.can_authenticate()
        or checker.primary_role.status != "active"
        or checker.approval_authority_type != CFC_ROLE
        or CFC_ROLE not in roles
        or permission is None
        or permission.risk_level != Permission.RISK_CRITICAL
        or AUTHORISE_PERMISSION not in permissions
    ):
        raise DomainPermissionDenied(
            "Active governed CFC disbursement authorisation authority is required."
        )
    return checker


def _coherent_pending_initiation(row):
    evidence = row.initiation_audit.new_value_json or {}
    request_id = evidence.get("request_id")
    comment_digest = evidence.get("final_verification_comment_digest")
    trace = (
        f"request_id={request_id};verification_digest={comment_digest};"
        f"amount={row.disbursement_amount:.2f}"
    )
    readiness = row.readiness_evidence_json or {}
    account = row.loan_account
    borrower_bank = row.borrower_bank_account
    source_bank = row.source_bank_account
    return bool(
        row.initiation_status == Disbursement.INITIATED
        and row.authorisation_status == Disbursement.AUTHORISATION_PENDING
        and row.bank_transfer_status == Disbursement.TRANSFER_PENDING
        and row.authorised_by_user_id is None
        and row.authorised_at is None
        and row.authorisation_action_id is None
        and row.loan_application_id == account.loan_application_id
        and row.member_id == account.member_id
        and account.loan_account_status == "sanctioned"
        and row.disbursement_amount > 0
        and row.disbursement_amount <= account.terms.loan_amount
        and row.disbursement_amount <= account.sanctioned_amount
        and all(
            value == 0
            for value in (
                account.disbursed_amount,
                account.principal_outstanding,
                account.interest_outstanding,
                account.charges_outstanding,
                account.total_outstanding,
            )
        )
        and borrower_bank.owner_party_type == "member"
        and borrower_bank.owner_party_id == row.member_id
        and borrower_bank.verification_status == "verified"
        and borrower_bank.status == "active"
        and source_bank.owner_party_type == "sfpcl"
        and request_id
        and comment_digest == _sha256(row.final_verification_comments)
        and readiness.get("check_digest") == row.readiness_digest
        and readiness.get("borrower_bank_account_id")
        == str(row.borrower_bank_account_id)
        and readiness.get("source_bank_account_id") == str(row.source_bank_account_id)
        and readiness.get("source_bank_governance_id")
        and readiness.get("source_bank_version_history_id")
        and readiness.get("source_bank_audit_log_id")
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
        and evidence.get("readiness_evidence") == readiness
        and evidence.get("idempotency_digest") == row.idempotency_key_digest
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
        and row.cfc_task.recipient_role_code == CFC_ROLE
        and row.cfc_task.sender_user_id == row.initiated_by_user_id
        and row.cfc_task.action_label == "Review disbursement"
        and row.cfc_task.action_url == f"/api/v1/disbursements/{row.pk}/authorise/"
        and row.cfc_task.read_at is None
        and row.cfc_task.read_by_user_id is None
        and trace in row.cfc_task.message
    )


def _current_source_matches(row, source):
    evidence = row.readiness_evidence_json or {}
    return bool(
        source
        and source.active
        and source.source_bank_account_id == row.source_bank_account_id
        and str(source.governance_id) == evidence.get("source_bank_governance_id")
        and str(source.version_history_id)
        == evidence.get("source_bank_version_history_id")
        and str(source.audit_log_id) == evidence.get("source_bank_audit_log_id")
    )


def _is_complete_terminal_replay(row, cleaned):
    initiation = row.initiation_audit.new_value_json or {}
    initiation_request_id = initiation.get("request_id")
    initiation_comment_digest = initiation.get("final_verification_comment_digest")
    expected_evidence_digest = _sha256(
        (initiation_request_id or "")
        + row.readiness_digest
        + (initiation_comment_digest or "")
    )
    comments_digest = _sha256(cleaned["comments"])
    expected_action = (
        "disbursement.authorised"
        if row.authorisation_status == "approved"
        else "disbursement.rejected"
    )
    expected = {
        "action_id": str(row.authorisation_action_id),
        "disbursement_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_application_id": str(row.loan_application_id),
        "member_id": str(row.member_id),
        "disbursement_amount": f"{row.disbursement_amount:.2f}",
        "maker_user_id": str(row.initiated_by_user_id),
        "maker_role_code": row.maker_role_code,
        "maker_team_codes": row.maker_team_codes_json,
        "checker_user_id": str(row.authorised_by_user_id),
        "checker_role_code": row.checker_role_code,
        "checker_team_codes": row.checker_team_codes_json,
        "initiation_request_id": initiation_request_id,
        "initiation_comment_digest": initiation_comment_digest,
        "readiness_digest": row.readiness_digest,
        "authorisation_evidence_digest": row.authorisation_evidence_digest,
        "comments_digest": comments_digest,
        "request_id": row.authorisation_request_id,
        "ip_address": row.authorisation_ip_address,
        "user_agent": row.authorisation_user_agent,
        "authorised_at": row.authorised_at.isoformat().replace("+00:00", "Z"),
        "authorisation_status": row.authorisation_status,
        "bank_transfer_status": Disbursement.TRANSFER_PENDING,
        "outcome": row.authorisation_status,
    }
    trace = (
        f"action_id={row.authorisation_action_id};"
        f"request_id={row.authorisation_request_id};"
        f"evidence_digest={row.authorisation_evidence_digest};"
        f"comments_digest={comments_digest}"
    )
    audit = row.authorisation_audit
    workflow = row.authorisation_workflow_event
    return bool(
        row.authorisation_status == cleaned["decision"]
        and row.authorisation_comments == cleaned["comments"]
        and row.bank_transfer_status == Disbursement.TRANSFER_PENDING
        and row.authorised_at
        and row.authorised_by_user_id
        and row.authorisation_action_id
        and row.authorised_by_user_id != row.initiated_by_user_id
        and row.checker_role_code == CFC_ROLE
        and isinstance(row.checker_team_codes_json, list)
        and initiation_request_id
        and initiation_comment_digest
        and row.authorisation_evidence_digest == expected_evidence_digest
        and row.authorisation_request_id
        and row.authorisation_audit_id
        and row.authorisation_workflow_event_id
        and audit.action == expected_action
        and audit.entity_type == "disbursement"
        and audit.entity_id == row.pk
        and audit.actor_user_id == row.authorised_by_user_id
        and audit.old_value_json
        == {
            "authorisation_status": Disbursement.AUTHORISATION_PENDING,
            "bank_transfer_status": Disbursement.TRANSFER_PENDING,
        }
        and audit.new_value_json == expected
        and audit.ip_address == row.authorisation_ip_address
        and audit.user_agent == row.authorisation_user_agent
        and workflow.workflow_name == "DisbursementAuthorisation"
        and workflow.entity_type == "disbursement"
        and workflow.entity_id == row.pk
        and workflow.from_state == Disbursement.AUTHORISATION_PENDING
        and workflow.to_state == row.authorisation_status
        and workflow.triggered_by_user_id == row.authorised_by_user_id
        and workflow.trigger_reason == trace
        and row.cfc_task.read_at == row.authorised_at
        and row.cfc_task.read_by_user_id == row.authorised_by_user_id
        and row.cfc_task.action_label == row.authorisation_status.title()
        and row.cfc_task.action_url == ""
        and row.cfc_task.message.endswith(f"Decision: {row.authorisation_status}.")
    )


def _request_id(request):
    supplied = request.headers.get("X-Request-ID", "").strip() if request else ""
    return (
        supplied if supplied and len(supplied) <= 255 else f"req_cfc_{uuid.uuid4().hex}"
    )


def _sha256(value):
    return hashlib.sha256(value.encode()).hexdigest()


__all__ = ["DisbursementAuthorisationConflict"]
