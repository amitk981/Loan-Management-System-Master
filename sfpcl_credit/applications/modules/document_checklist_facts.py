"""Application-owned cancelled-cheque facts exposed to downstream checklists."""

from dataclasses import dataclass

from sfpcl_credit.approvals.modules import document_checklist_facts as approval_facts
from sfpcl_credit.applications.models import BankVerificationDecision, LoanApplication
from sfpcl_credit.applications.modules.bank_verification import (
    decision_evidence,
    evidence_digest,
)
from sfpcl_credit.members.models import BankAccount, CancelledCheque


@dataclass(frozen=True)
class SignatureMismatchFact:
    mismatch: bool | None
    source: str
    blocker: str | None


@dataclass(frozen=True)
class BlankChequeBankFact:
    valid: bool
    blocker: str | None
    member_id: object | None = None
    bank_account_id: object | None = None
    cancelled_cheque_id: object | None = None
    cancelled_cheque_document_id: object | None = None
    bank_account_masked: str | None = None
    ifsc: str | None = None
    branch_name: str | None = None
    bank_verification_decision_id: object | None = None
    verifier_user_id: object | None = None
    request_id: str | None = None
    workflow_event_id: object | None = None
    audit_log_id: object | None = None
    version_history_id: object | None = None
    cancelled_cheque_checksum_sha256: str | None = None


def resolve_blank_cheque_bank_fact(*, application_id):
    """Lock and resolve the exact application-retained bank/cancelled-cheque decision."""
    application = (
        LoanApplication.objects.select_for_update(of=("self",))
        .filter(pk=application_id)
        .first()
    )
    if application is None or not application.bank_account_id or not application.cancelled_cheque_id:
        return BlankChequeBankFact(False, "bank_cancelled_cheque_source_missing")
    bank = BankAccount.objects.select_for_update().filter(pk=application.bank_account_id).first()
    cheque = (
        CancelledCheque.objects.select_for_update()
        .filter(pk=application.cancelled_cheque_id)
        .first()
    )
    if bank is None or cheque is None:
        return BlankChequeBankFact(False, "bank_cancelled_cheque_source_missing")
    decision = (
        BankVerificationDecision.objects.select_for_update()
        .select_related(
            "cancelled_cheque_document", "workflow_event", "audit_log", "version_history"
        )
        .filter(loan_application=application)
        .order_by("-decision_version", "-bank_verification_decision_id")
        .first()
    )
    if decision is None:
        return BlankChequeBankFact(False, "bank_verification_decision_missing")
    terminal_facts = approval_facts.resolve_approved_facts(application_id=application.pk)
    if (
        terminal_facts is None
        or decision.approval_case_id_snapshot != terminal_facts.approval_case_id
        or decision.sanction_decision_id_snapshot != terminal_facts.sanction_decision_id
    ):
        return BlankChequeBankFact(
            False, "bank_verification_terminal_sanction_invalid"
        )
    related_cheques = list(
        CancelledCheque.objects.select_for_update()
        .filter(loan_application_id=application.pk, member_id=application.member_id)
        .values_list("cancelled_cheque_id", flat=True)
    )
    if related_cheques != [cheque.pk]:
        return BlankChequeBankFact(False, "bank_cancelled_cheque_source_conflicting")
    same_member = (
        bank.owner_party_type == "member"
        and bank.owner_party_id == application.member_id
        and cheque.member_id == application.member_id
    )
    exact_link = bank.cancelled_cheque_id == cheque.pk
    account_matches = (
        bool(bank.account_number_hash)
        and bank.account_number_hash == cheque.account_number_hash
        and bank.ifsc == cheque.ifsc
        and bank.account_number_last4 == cheque.account_number_last4
    )
    retained = decision_evidence(decision)
    ledger = decision.audit_log.new_value_json or {}
    history = decision.version_history.new_value_json or {}
    workflow = decision.workflow_event
    decision_current = (
        decision.member_id == application.member_id
        and decision.bank_account_id == bank.pk
        and decision.cancelled_cheque_id == cheque.pk
        and decision.cancelled_cheque_document_id == cheque.document_id
        and decision.cancelled_cheque_checksum_sha256
        == decision.cancelled_cheque_document.checksum_sha256
        and decision.bank_account_hash_snapshot == bank.account_number_hash
        and decision.ifsc_snapshot == bank.ifsc
        and decision.branch_name_snapshot == (bank.branch_name or cheque.branch_name or "")
        and decision.decision_status == BankVerificationDecision.STATUS_VERIFIED
        and decision.evidence_digest == evidence_digest(retained)
        and ledger == {**retained, "evidence_digest": decision.evidence_digest}
        and history == ledger
        and decision.audit_log.actor_user_id == decision.verifier_user_id
        and decision.audit_log.action == "bank_verification.decision_recorded"
        and decision.audit_log.entity_type == "bank_verification_decision"
        and decision.audit_log.entity_id == decision.pk
        and decision.version_history.versioned_entity_type
        == "bank_verification_decision"
        and decision.version_history.versioned_entity_id == decision.pk
        and decision.version_history.version_number == str(decision.decision_version)
        and decision.version_history.author_user_id == decision.verifier_user_id
        and workflow.workflow_name == "bank_verification"
        and workflow.entity_type == "bank_verification_decision"
        and workflow.entity_id == decision.pk
        and workflow.to_state == decision.decision_status
        and workflow.triggered_by_user_id == decision.verifier_user_id
        and workflow.trigger_reason == "bank_verification.decision_recorded"
    )
    verified = bank.status == "active" and cheque.loan_application_id == application.pk
    if not same_member or not exact_link or not account_matches:
        return BlankChequeBankFact(False, "bank_cancelled_cheque_source_conflicting")
    if not verified or not decision_current:
        return BlankChequeBankFact(False, "bank_cancelled_cheque_source_unverified")
    return BlankChequeBankFact(
        True,
        None,
        member_id=application.member_id,
        bank_account_id=bank.pk,
        cancelled_cheque_id=cheque.pk,
        cancelled_cheque_document_id=cheque.document_id,
        bank_account_masked=(
            f"{'*' * 8}{bank.account_number_last4}" if bank.account_number_last4 else None
        ),
        ifsc=bank.ifsc,
        branch_name=bank.branch_name or cheque.branch_name or None,
        bank_verification_decision_id=decision.pk,
        verifier_user_id=decision.verifier_user_id,
        request_id=decision.request_id,
        workflow_event_id=decision.workflow_event_id,
        audit_log_id=decision.audit_log_id,
        version_history_id=decision.version_history_id,
        cancelled_cheque_checksum_sha256=decision.cancelled_cheque_checksum_sha256,
    )


def reconcile_authorisation_bank_fact(*, application_id, frozen_evidence):
    """Resolve only the exact application-owned bank decision frozen at initiation."""
    fact = resolve_blank_cheque_bank_fact(application_id=application_id)
    expected = {
        "borrower_bank_account_id": fact.bank_account_id,
        "bank_verification_decision_id": fact.bank_verification_decision_id,
        "bank_cancelled_cheque_id": fact.cancelled_cheque_id,
        "bank_cancelled_cheque_document_id": fact.cancelled_cheque_document_id,
        "bank_cancelled_cheque_checksum_sha256": fact.cancelled_cheque_checksum_sha256,
        "bank_verifier_user_id": fact.verifier_user_id,
        "bank_request_id": fact.request_id,
        "bank_workflow_event_id": fact.workflow_event_id,
        "bank_audit_log_id": fact.audit_log_id,
        "bank_version_history_id": fact.version_history_id,
    }
    if not fact.valid or any(
        frozen_evidence.get(key) != (str(value) if value is not None else None)
        for key, value in expected.items()
    ):
        return BlankChequeBankFact(False, "bank_verification_decision_changed")
    return fact


def resolve_cancelled_cheque_signature_fact(*, application_id, member_id):
    """Return a decision only when every related cheque row is valid and verified."""
    rows = list(
        CancelledCheque.objects.filter(
            loan_application_id=application_id,
            member_id=member_id,
        ).values("verification_status", "signature_mismatch_flag")
    )
    if not rows:
        return SignatureMismatchFact(
            None,
            "signature_mismatch_source_missing",
            "signature_mismatch_source_missing",
        )
    valid_statuses = CancelledCheque.VERIFICATION_STATUSES
    if any(row["verification_status"] not in valid_statuses for row in rows):
        return SignatureMismatchFact(
            None,
            "signature_mismatch_source_malformed",
            "signature_mismatch_source_malformed",
        )
    if any(row["verification_status"] != "verified" for row in rows):
        return SignatureMismatchFact(
            None,
            "signature_mismatch_source_unverified",
            "signature_mismatch_source_unverified",
        )
    decisions = {row["signature_mismatch_flag"] for row in rows}
    if decisions == {True}:
        return SignatureMismatchFact(True, "persisted_signature_mismatch", None)
    if decisions == {False}:
        return SignatureMismatchFact(False, "persisted_signature_match", None)
    return SignatureMismatchFact(
        None,
        "persisted_signature_mismatch_conflict",
        "signature_mismatch_conflicting",
    )


def resolve_signature_mismatch_fact(*, legal_signature_rows, application_id, member_id):
    """Prefer unanimous verified legal-owner decisions over intake cheque facts.

    The caller owns retrieval of legal rows; this application-owned seam owns the meaning of
    downstream mismatch truth and therefore avoids an applications-to-legal ORM dependency.
    """
    unresolved_mismatch = False
    resolved_mismatch = False
    for row in legal_signature_rows:
        if not row.get("verified_by_user_id") or not row.get("verified_at"):
            continue
        if row.get("signature_status") != "mismatch":
            continue
        if row.get("mismatch_resolution_type"):
            resolved_mismatch = True
        else:
            unresolved_mismatch = True
    if unresolved_mismatch:
        return SignatureMismatchFact(True, "verified_signature_mismatch", None)
    if resolved_mismatch:
        return SignatureMismatchFact(False, "verified_signature_match_or_resolution", None)
    return resolve_cancelled_cheque_signature_fact(
        application_id=application_id,
        member_id=member_id,
    )
