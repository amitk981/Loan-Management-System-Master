from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.disbursements.modules.disbursement_transfer_success import (
    completed_success_is_coherent,
)


@dataclass(frozen=True)
class PostTransferEvidence:
    disbursement_id: UUID
    loan_account_id: UUID
    loan_application_id: UUID
    member_id: UUID
    amount: Decimal
    initiated_by_user_id: UUID
    transfer_action_id: UUID
    transfer_evidence_digest: str
    bank_transfer_id: UUID
    loan_register_update_id: UUID
    advice_intent_id: UUID
    transfer_audit_id: UUID
    transfer_workflow_event_id: UUID
    initiated_at: object
    authorised_at: object
    disbursed_at: object

    def checklist_evidence(self):
        return {
            "disbursement_id": str(self.disbursement_id),
            "loan_account_id": str(self.loan_account_id),
            "loan_application_id": str(self.loan_application_id),
            "member_id": str(self.member_id),
            "disbursement_amount": f"{self.amount:.2f}",
            "transfer_success_action_id": str(self.transfer_action_id),
            "transfer_success_evidence_digest": self.transfer_evidence_digest,
            "bank_transfer_id": str(self.bank_transfer_id),
            "loan_register_update_id": str(self.loan_register_update_id),
            "disbursement_advice_communication_id": str(self.advice_intent_id),
            "transfer_success_audit_id": str(self.transfer_audit_id),
            "transfer_success_workflow_event_id": str(
                self.transfer_workflow_event_id
            ),
        }


def resolve_post_transfer_evidence(*, application_id, for_update=False):
    query = Disbursement.objects
    if for_update:
        query = query.select_for_update(of=("self",))
    rows = list(
        query.select_related(
            "loan_account",
            "loan_account__terms",
            "bank_transfer",
            "bank_transfer_evidence_document",
            "authorisation_audit",
            "authorisation_workflow_event",
            "transfer_success_actor_user",
            "transfer_success_audit",
            "transfer_success_workflow_event",
            "transfer_success_loan_status_history",
            "register_update",
            "loan_register_update",
            "advice_intent",
        )
        .filter(
            loan_application_id=application_id,
            bank_transfer_status="successful",
        )
        .order_by("disbursement_id")[:2]
    )
    if len(rows) != 1 or not completed_success_is_coherent(rows[0]):
        return None
    row = rows[0]
    return PostTransferEvidence(
        disbursement_id=row.pk,
        loan_account_id=row.loan_account_id,
        loan_application_id=row.loan_application_id,
        member_id=row.member_id,
        amount=row.disbursement_amount,
        initiated_by_user_id=row.initiated_by_user_id,
        transfer_action_id=row.transfer_success_action_id,
        transfer_evidence_digest=row.transfer_success_evidence_digest,
        bank_transfer_id=row.bank_transfer.pk,
        loan_register_update_id=row.loan_register_update.pk,
        advice_intent_id=row.advice_intent.pk,
        transfer_audit_id=row.transfer_success_audit_id,
        transfer_workflow_event_id=row.transfer_success_workflow_event_id,
        initiated_at=row.initiated_at,
        authorised_at=row.authorised_at,
        disbursed_at=row.disbursed_at,
    )
