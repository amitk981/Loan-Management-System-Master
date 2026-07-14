"""Application-owned cancelled-cheque facts exposed to downstream checklists."""

from dataclasses import dataclass

from sfpcl_credit.applications.models import LoanApplication
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
    verified = (
        bank.verification_status == "verified"
        and bank.status == "active"
        and cheque.verification_status == "verified"
        and cheque.loan_application_id == application.pk
    )
    if not same_member or not exact_link or not account_matches:
        return BlankChequeBankFact(False, "bank_cancelled_cheque_source_conflicting")
    if not verified:
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
    )


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
