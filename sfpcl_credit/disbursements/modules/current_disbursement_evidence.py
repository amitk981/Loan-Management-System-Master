"""One locked decision for current initiation, CFC scope, and transfer consumers."""

from dataclasses import dataclass
import hashlib
import json

from django.db.models import BooleanField, F, Func, IntegerField, JSONField, Value
from django.db.models.fields.json import KeyTextTransform, KeyTransform
from django.db.models.functions import Cast, Coalesce, NullIf, SHA256

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.loans.modules.loan_account_lifecycle import filter_created_accounts


class _JsonObjectKeyCount(Func):
    output_field = IntegerField()
    arity = 1

    def as_sqlite(self, compiler, connection, **extra_context):
        sql, params = compiler.compile(self.source_expressions[0])
        return f"(SELECT COUNT(*) FROM JSON_EACH({sql}))", params

    def as_postgresql(self, compiler, connection, **extra_context):
        sql, params = compiler.compile(self.source_expressions[0])
        return (
            f"CASE WHEN JSONB_TYPEOF({sql}) = 'object' "
            f"THEN (SELECT COUNT(*) FROM JSONB_OBJECT_KEYS({sql})) ELSE -1 END",
            (*params, *params),
        )


class _JsonValuesEqual(Func):
    output_field = BooleanField()
    arity = 2

    def as_sqlite(self, compiler, connection, **extra_context):
        left_sql, left_params = compiler.compile(self.source_expressions[0])
        right_sql, right_params = compiler.compile(self.source_expressions[1])
        return (
            "NOT EXISTS ("
            f"SELECT fullkey, type, atom FROM JSON_TREE({left_sql}) "
            "EXCEPT "
            f"SELECT fullkey, type, atom FROM JSON_TREE({right_sql})"
            ") AND NOT EXISTS ("
            f"SELECT fullkey, type, atom FROM JSON_TREE({right_sql}) "
            "EXCEPT "
            f"SELECT fullkey, type, atom FROM JSON_TREE({left_sql})"
            ")",
            (
                *left_params,
                *right_params,
                *right_params,
                *left_params,
            ),
        )

    def as_postgresql(self, compiler, connection, **extra_context):
        left_sql, left_params = compiler.compile(self.source_expressions[0])
        right_sql, right_params = compiler.compile(self.source_expressions[1])
        return f"{left_sql} = {right_sql}", (*left_params, *right_params)


@dataclass(frozen=True)
class CurrentDisbursementEvidence:
    disbursement_id: object
    loan_account_id: object
    loan_application_id: object
    member_id: object
    borrower_bank_decision_id: object
    source_bank_governance_id: object
    loan_creation_status_history_id: object
    loan_creation_audit_id: object
    loan_creation_workflow_event_id: object
    authorisation_status: str
    authorisation_action_id: object | None
    authorisation_audit_id: object | None
    authorisation_workflow_event_id: object | None
    authorisation_evidence_digest: str | None
    authorised_by_user_id: object | None
    authorised_at: object | None
    initiated_at: object


def filter_current_pending_disbursements(queryset):
    """Filter the database-pageable identity set for the pending CFC decision."""
    return queryset.annotate(
        _current_comment_digest=SHA256("final_verification_comments"),
        _audit_comment_digest=KeyTextTransform(
            "final_verification_comment_digest",
            "initiation_audit__new_value_json",
        ),
        _audit_maker_role_code=KeyTextTransform(
            "0",
            KeyTransform("maker_role_codes", "initiation_audit__new_value_json"),
        ),
        _audit_readiness_digest=KeyTextTransform(
            "readiness_digest", "initiation_audit__new_value_json"
        ),
        _audit_idempotency_digest=KeyTextTransform(
            "idempotency_digest", "initiation_audit__new_value_json"
        ),
        _audit_workflow_trace=KeyTextTransform(
            "workflow_trace", "initiation_audit__new_value_json"
        ),
        _audit_cfc_action_url=KeyTextTransform(
            "cfc_action_url", "initiation_audit__new_value_json"
        ),
        _audit_cfc_task_message=KeyTextTransform(
            "cfc_task_message", "initiation_audit__new_value_json"
        ),
        _initiation_evidence_key_count=_JsonObjectKeyCount(
            "initiation_audit__new_value_json"
        ),
        _readiness_evidence_matches=_JsonValuesEqual(
            "initiation_audit__new_value_json__readiness_evidence",
            "readiness_evidence_json",
        ),
        _initiation_manifest_matches=_JsonValuesEqual(
            "initiation_audit__new_value_json",
            "initiation_audit__old_value_json__selector_manifest",
        ),
        _canonical_manifest_matches=_JsonValuesEqual(
            "initiation_audit__new_value_json",
            Cast(
                Coalesce(
                    NullIf(
                        "initiation_audit__selector_manifest_json", Value("")
                    ),
                    Value("{}"),
                ),
                JSONField(),
            ),
        ),
        _canonical_manifest_digest=SHA256(
            "initiation_audit__selector_manifest_json"
        ),
        _initiation_retained_key_count=_JsonObjectKeyCount(
            "initiation_audit__old_value_json"
        ),
    ).filter(
        loan_account_id__in=filter_created_accounts(
            LoanAccount.objects.all()
        ).values("loan_account_id"),
        initiation_status=Disbursement.INITIATED,
        initiation_audit__action="disbursement.initiated",
        initiation_audit__entity_type="disbursement",
        initiation_audit__entity_id=F("pk"),
        initiation_audit__actor_user_id=F("initiated_by_user_id"),
        initiation_audit__actor_type="user",
        _initiation_retained_key_count=2,
        _initiation_manifest_matches=True,
        _canonical_manifest_matches=True,
        _canonical_manifest_digest=F(
            "initiation_audit__selector_manifest_sha256"
        ),
        _initiation_evidence_key_count=27,
        _audit_comment_digest=F("_current_comment_digest"),
        initiation_audit__new_value_json__maker_team_codes=F(
            "maker_team_codes_json"
        ),
        _audit_maker_role_code=F("maker_role_code"),
        initiation_audit__new_value_json__maker_role_codes__1__isnull=True,
        _audit_readiness_digest=F("readiness_digest"),
        _readiness_evidence_matches=True,
        _audit_idempotency_digest=F("idempotency_key_digest"),
        initiation_audit__new_value_json__cfc_assignment_role_code=(
            "chief_financial_controller"
        ),
        initiation_audit__new_value_json__initiation_status=Disbursement.INITIATED,
        initiation_audit__new_value_json__authorisation_status=(
            Disbursement.AUTHORISATION_PENDING
        ),
        initiation_audit__new_value_json__bank_transfer_status=(
            Disbursement.TRANSFER_PENDING
        ),
        initiation_audit__new_value_json__payment_method=(
            Disbursement.PAYMENT_METHOD_MANUAL
        ),
        initiation_audit__new_value_json__outcome="initiated",
        initiation_workflow_event__workflow_name="DisbursementInitiated",
        initiation_workflow_event__entity_type="disbursement",
        initiation_workflow_event__entity_id=F("pk"),
        initiation_workflow_event__from_state__isnull=True,
        initiation_workflow_event__to_state=Disbursement.INITIATED,
        initiation_workflow_event__triggered_by_user_id=F("initiated_by_user_id"),
        initiation_workflow_event__trigger_reason=F("_audit_workflow_trace"),
        cfc_task__notification_type="disbursement_authorisation",
        cfc_task__category="Finance",
        cfc_task__related_entity_type="disbursement",
        cfc_task__related_entity_id=F("pk"),
        cfc_task__recipient_role_code="chief_financial_controller",
        cfc_task__sender_user_id=F("initiated_by_user_id"),
        cfc_task__severity="urgent",
        cfc_task__title="Disbursement awaiting CFC authorisation",
        cfc_task__action_label="Review disbursement",
        cfc_task__action_url=F("_audit_cfc_action_url"),
        cfc_task__message=F("_audit_cfc_task_message"),
        cfc_task__read_at__isnull=True,
        cfc_task__read_by_user_id__isnull=True,
        borrower_bank_account__status="active",
        borrower_bank_account__verification_status="verified",
        borrower_bank_account__owner_party_type="member",
        borrower_bank_account__owner_party_id=F("member_id"),
        borrower_bank_account__cancelled_cheque_id=F(
            "loan_application__cancelled_cheque_id"
        ),
        borrower_bank_account__cancelled_cheque__loan_application_id=F(
            "loan_application_id"
        ),
        borrower_bank_account__cancelled_cheque__member_id=F("member_id"),
        borrower_bank_account__cancelled_cheque__verification_status="verified",
        borrower_bank_account__cancelled_cheque__account_number_hash=F(
            "borrower_bank_account__account_number_hash"
        ),
        borrower_bank_account__cancelled_cheque__ifsc=F(
            "borrower_bank_account__ifsc"
        ),
        source_bank_account__status="active",
        source_bank_account__verification_status="verified",
        source_bank_account__owner_party_type="sfpcl",
        source_bank_account__source_bank_governance_records__status="active",
        bank_transfer_status=Disbursement.TRANSFER_PENDING,
        bank_reference_number__isnull=True,
        disbursed_at__isnull=True,
        disbursement_advice_communication_id__isnull=True,
        loan_register_updated_flag=False,
        loan_account__loan_account_status="sanctioned",
        loan_account__disbursed_amount=0,
        loan_account__principal_outstanding=0,
        loan_account__interest_outstanding=0,
        loan_account__charges_outstanding=0,
        loan_account__total_outstanding=0,
    )


def resolve_current_disbursement_evidence(
    *, disbursement_id=None, loan_account_id=None, for_update=False,
    allowed_authorisation_statuses=(Disbursement.AUTHORISATION_PENDING,),
):
    """Return a safe identity manifest only when every frozen owner still agrees."""
    queryset = Disbursement.objects.select_related(
        "loan_account",
        "loan_account__terms",
        "borrower_bank_account",
        "source_bank_account",
        "cfc_task",
        "initiation_audit",
        "initiation_workflow_event",
    )
    if for_update:
        queryset = queryset.select_for_update(of=("self",))
    if disbursement_id is not None:
        queryset = queryset.filter(pk=disbursement_id)
    elif loan_account_id is not None:
        queryset = queryset.filter(loan_account_id=loan_account_id)
    else:
        raise ValueError("A disbursement or loan-account identity is required.")
    rows = list(queryset.order_by("disbursement_id")[:2])
    if len(rows) != 1:
        return None
    row = rows[0]
    if row.authorisation_status not in allowed_authorisation_statuses:
        return None

    from sfpcl_credit.applications.modules.document_checklist_facts import (
        reconcile_authorisation_bank_fact,
    )
    from sfpcl_credit.configurations.modules.source_bank_governance import (
        resolve_source_bank_account,
    )
    from sfpcl_credit.loans.modules.loan_account_lifecycle import (
        resolve_disbursement_account,
    )

    readiness = row.readiness_evidence_json or {}
    bank = reconcile_authorisation_bank_fact(
        application_id=row.loan_application_id, frozen_evidence=readiness
    )
    source = resolve_source_bank_account(for_update=for_update)
    account = resolve_disbursement_account(loan_account_id=row.loan_account_id)
    if not bank.valid or source is None or account is None:
        return None
    if not _frozen_owners_match(row, readiness, bank, source, account):
        return None
    if not _initiation_ledger_is_coherent(row):
        return None
    if not _aggregate_has_no_later_truth(row, account):
        return None
    if row.authorisation_status == "approved":
        from sfpcl_credit.disbursements.modules.disbursement_authorisation import (
            is_current_terminal_authorisation,
        )

        if not is_current_terminal_authorisation(
            row,
            {
                "decision": "approved",
                "comments": row.authorisation_comments or "",
            },
        ):
            return None
    return CurrentDisbursementEvidence(
        disbursement_id=row.pk,
        loan_account_id=row.loan_account_id,
        loan_application_id=row.loan_application_id,
        member_id=row.member_id,
        borrower_bank_decision_id=bank.bank_verification_decision_id,
        source_bank_governance_id=source.governance_id,
        loan_creation_status_history_id=account.creation_status_history_id,
        loan_creation_audit_id=account.creation_audit_id,
        loan_creation_workflow_event_id=account.creation_workflow_event_id,
        authorisation_status=row.authorisation_status,
        authorisation_action_id=row.authorisation_action_id,
        authorisation_audit_id=row.authorisation_audit_id,
        authorisation_workflow_event_id=row.authorisation_workflow_event_id,
        authorisation_evidence_digest=row.authorisation_evidence_digest,
        authorised_by_user_id=row.authorised_by_user_id,
        authorised_at=row.authorised_at,
        initiated_at=row.initiated_at,
    )


def _frozen_owners_match(row, evidence, bank, source, account):
    return bool(
        row.loan_application_id == account.loan_application_id
        and row.member_id == account.member_id
        and row.borrower_bank_account_id == bank.bank_account_id
        and row.source_bank_account_id == source.source_bank_account_id
        and evidence.get("check_digest") == row.readiness_digest
        and evidence.get("loan_creation_status_history_id")
        == str(account.creation_status_history_id)
        and evidence.get("loan_creation_audit_id") == str(account.creation_audit_id)
        and evidence.get("loan_creation_workflow_event_id")
        == str(account.creation_workflow_event_id)
        and evidence.get("source_bank_governance_id") == str(source.governance_id)
        and evidence.get("source_bank_version_history_id")
        == str(source.version_history_id)
        and evidence.get("source_bank_audit_log_id") == str(source.audit_log_id)
        and evidence.get("source_bank_request_id") == source.request_id
        and evidence.get("source_bank_facts_digest") == source.source_facts_digest
    )


def _initiation_ledger_is_coherent(row):
    evidence = row.initiation_audit.new_value_json or {}
    retained = row.initiation_audit.old_value_json or {}
    request_id = evidence.get("request_id")
    comment_digest = evidence.get("final_verification_comment_digest")
    trace = (
        f"request_id={request_id};verification_digest={comment_digest};"
        f"amount={row.disbursement_amount:.2f}"
    )
    task = row.cfc_task
    pending_task = row.authorisation_status == Disbursement.AUTHORISATION_PENDING
    return bool(
        row.initiation_status == Disbursement.INITIATED
        and retained.get("selector_manifest") == evidence
        and row.initiation_audit.selector_manifest_json
        == json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        and row.initiation_audit.selector_manifest_sha256
        == hashlib.sha256(
            row.initiation_audit.selector_manifest_json.encode()
        ).hexdigest()
        and retained.get("selector_manifest_sha256")
        == hashlib.sha256(
            json.dumps(
                evidence, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        and request_id
        and comment_digest == hashlib.sha256(
            row.final_verification_comments.encode()
        ).hexdigest()
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
        and evidence.get("workflow_trace") == trace
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
        and task.notification_type == "disbursement_authorisation"
        and task.category == "Finance"
        and task.severity == task.SEVERITY_URGENT
        and task.related_entity_type == "disbursement"
        and task.related_entity_id == row.pk
        and task.recipient_role_code == "chief_financial_controller"
        and task.sender_user_id == row.initiated_by_user_id
        and trace in task.message
        and (
            not pending_task
            or (
                task.action_label == "Review disbursement"
                and evidence.get("cfc_action_url") == task.action_url
                and evidence.get("cfc_task_message") == task.message
                and task.action_url
                == f"/api/v1/disbursements/{row.pk}/authorise/"
                and task.read_at is None
                and task.read_by_user_id is None
            )
        )
    )


def _aggregate_has_no_later_truth(row, account):
    return bool(
        row.bank_transfer_status == Disbursement.TRANSFER_PENDING
        and row.bank_reference_number is None
        and row.disbursed_at is None
        and row.disbursement_advice_communication_id is None
        and not row.loan_register_updated_flag
        and account.loan_account_status == "sanctioned"
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
    )


__all__ = [
    "CurrentDisbursementEvidence",
    "filter_current_pending_disbursements",
    "resolve_current_disbursement_evidence",
]
