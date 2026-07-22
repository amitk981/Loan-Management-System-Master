"""Canonical loan-balance owner for verified recovery proceeds."""

import hashlib
from dataclasses import asdict, dataclass
from decimal import Decimal

from django.db import transaction

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount


class RecoveryProceedsNotFound(Exception):
    pass


class RecoveryProceedsConflict(Exception):
    pass


@dataclass(frozen=True)
class RecoveryProceedsPosting:
    movement_reference: str
    source_type: str
    source_recovery_action_id: str
    loan_account_id: str
    credit_amount: str
    allocated_to_principal: str
    allocated_to_interest: str
    allocated_to_charges: str
    principal_before: str
    principal_after: str
    interest_before: str
    interest_after: str
    charges_before: str
    charges_after: str
    total_before: str
    total_after: str
    loan_status_before: str
    loan_status_after: str
    posting_audit_id: str
    posted_at: str
    external_sap_status: str

    def projection(self):
        return asdict(self)


@transaction.atomic
def post_verified_recovery_proceeds(
    *,
    actor,
    loan_account_id,
    recovery_action_id,
    amount,
    completed_at,
    remarks,
    request=None,
):
    """Apply one verified amount principal-first and return immutable posting evidence."""
    account = LoanAccount.objects.select_for_update().filter(pk=loan_account_id).first()
    if account is None:
        raise RecoveryProceedsNotFound
    if account.closed_at is not None:
        raise RecoveryProceedsConflict("The loan account is already closed.")
    if account.total_outstanding != (
        account.principal_outstanding
        + account.interest_outstanding
        + account.charges_outstanding
    ):
        raise RecoveryProceedsConflict(
            "The canonical loan balance is internally inconsistent."
        )
    allocatable = account.principal_outstanding + account.interest_outstanding
    if amount < Decimal("0.00") or amount > allocatable:
        raise RecoveryProceedsConflict(
            "The verified recovery amount cannot be negative or exceed the allocatable balance."
        )
    principal = min(amount, account.principal_outstanding)
    interest = min(amount - principal, account.interest_outstanding)
    principal_after = account.principal_outstanding - principal
    interest_after = account.interest_outstanding - interest
    total_after = principal_after + interest_after + account.charges_outstanding
    status_before = account.loan_account_status
    status_after = "repaid" if total_after == 0 else "partially_repaid"
    movement_reference = f"RECOVERY-{recovery_action_id}"
    evidence = {
        "movement_reference": movement_reference,
        "source_type": "verified_recovery_proceeds",
        "source_recovery_action_id": str(recovery_action_id),
        "loan_account_id": str(account.pk),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "credit_amount": f"{amount:.2f}",
        "allocated_to_principal": f"{principal:.2f}",
        "allocated_to_interest": f"{interest:.2f}",
        "allocated_to_charges": "0.00",
        "principal_before": f"{account.principal_outstanding:.2f}",
        "principal_after": f"{principal_after:.2f}",
        "interest_before": f"{account.interest_outstanding:.2f}",
        "interest_after": f"{interest_after:.2f}",
        "charges_before": f"{account.charges_outstanding:.2f}",
        "charges_after": f"{account.charges_outstanding:.2f}",
        "total_before": f"{account.total_outstanding:.2f}",
        "total_after": f"{total_after:.2f}",
        "loan_status_before": status_before,
        "loan_status_after": status_after,
        "posted_at": completed_at.isoformat().replace("+00:00", "Z"),
        "external_sap_status": "pending",
        "remarks_sha256": hashlib.sha256(remarks.encode()).hexdigest(),
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    audit = AuditLog.objects.create(
        actor_user=actor,
        action="recovery.proceeds_posted",
        entity_type="loan_account",
        entity_id=account.pk,
        old_value_json={
            "principal_outstanding": evidence["principal_before"],
            "interest_outstanding": evidence["interest_before"],
            "charges_outstanding": evidence["charges_before"],
            "total_outstanding": evidence["total_before"],
            "loan_account_status": status_before,
        },
        new_value_json=evidence,
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    account.principal_outstanding = principal_after
    account.interest_outstanding = interest_after
    account.total_outstanding = total_after
    account.loan_account_status = status_after
    account.save(
        update_fields=[
            "principal_outstanding",
            "interest_outstanding",
            "total_outstanding",
            "loan_account_status",
        ]
    )
    evidence["posting_audit_id"] = str(audit.pk)
    evidence.pop("actor_user_id")
    evidence.pop("actor_role_codes")
    evidence.pop("remarks_sha256")
    evidence.pop("request_id")
    return RecoveryProceedsPosting(**evidence)
