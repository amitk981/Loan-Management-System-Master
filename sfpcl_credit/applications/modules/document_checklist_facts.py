"""Application-owned cancelled-cheque facts exposed to downstream checklists."""

from dataclasses import dataclass

from sfpcl_credit.members.models import CancelledCheque


@dataclass(frozen=True)
class SignatureMismatchFact:
    mismatch: bool | None
    source: str
    blocker: str | None


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
