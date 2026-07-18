from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import uuid


@dataclass(frozen=True)
class DisbursementAdviceContext:
    """Primitive advice intent supplied to communications after financial locking."""

    actor_id: uuid.UUID
    actor_role_code: str
    actor_team_codes: tuple[str, ...]
    advice_intent_id: uuid.UUID
    intent_created_at: datetime
    communication_id: uuid.UUID
    recipient_address: str
    recipient_party_id: uuid.UUID
    related_entity_type: str
    related_entity_id: uuid.UUID
    template_code_prefix: str
    template_type: str
    template_audience: str
    required_variables: tuple[str, ...]
    merge_values: tuple[tuple[str, str], ...]
    sensitive_values: tuple[str, ...]
    loan_account_id: uuid.UUID
    loan_application_id: uuid.UUID
    member_id: uuid.UUID
    disbursement_amount: Decimal
    disbursed_at: date
    masked_bank_reference: str
    transfer_success_action_id: uuid.UUID
    transfer_success_evidence_digest: str


__all__ = ["DisbursementAdviceContext"]
