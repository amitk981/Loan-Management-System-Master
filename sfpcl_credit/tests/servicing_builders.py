"""Public synthetic builders for servicing owner and PostgreSQL acceptance tests."""

from dataclasses import dataclass
from datetime import date, timedelta
from types import SimpleNamespace
from uuid import uuid4

from django.utils import timezone

from sfpcl_credit.identity.epic009_e2e_fixture import build_ready_epic009_fixture
from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission, User
from sfpcl_credit.loans.models import (
    Repayment,
    RepaymentAllocation,
    RepaymentLedgerEntry,
    RepaymentReversal,
    RepaymentReversalLedgerEntry,
)


@dataclass(frozen=True)
class ServicingOwnerFixture:
    account: object
    maker: User
    checker: User
    request: object


def build_servicing_owner_fixture(*, suffix):
    """Return owner-backed loan and actors without importing another test case."""
    facts = build_ready_epic009_fixture(
        password="SyntheticServicing123!",
        finance_email=f"servicing.finance.{suffix}@sfpcl.example",
        credit_email=f"servicing.credit.{suffix}@sfpcl.example",
        cfc_email=f"servicing.cfc.{suffix}@sfpcl.example",
        borrower_email=f"servicing.borrower.{suffix}@sfpcl.example",
    )
    account = facts["ready"]["account"]
    account.loan_account_status = "active"
    account.disbursed_amount = account.sanctioned_amount
    account.principal_outstanding = account.sanctioned_amount
    account.total_outstanding = account.sanctioned_amount
    account.save(
        update_fields=[
            "loan_account_status",
            "disbursed_amount",
            "principal_outstanding",
            "total_outstanding",
        ]
    )
    maker = facts["finance"]
    checker = User.objects.create(
        full_name=f"Servicing Rate Checker {suffix}",
        email=f"servicing.checker.{suffix}@sfpcl.example",
        status="active",
        primary_role=maker.primary_role,
    )
    for code in (
        "config.interest_rate.manage",
        "communications.communication.send",
    ):
        permission, _ = Permission.objects.get_or_create(
            permission_code=code,
            defaults={
                "permission_name": code,
                "module_name": "config",
                "risk_level": "critical",
            },
        )
        RolePermission.objects.get_or_create(
            role=maker.primary_role,
            permission=permission,
        )
    return ServicingOwnerFixture(
        account=account,
        maker=maker,
        checker=checker,
        request=SimpleNamespace(
            META={"REMOTE_ADDR": "127.0.0.1"},
            headers={"User-Agent": "servicing-owner-postgresql-acceptance"},
        ),
    )


def append_servicing_ledger_movements(*, fixture, count, start_index=0):
    """Append deterministic synthetic owner chains for read-pagination acceptance."""
    for index in range(start_index, start_index + count):
        created_at = timezone.now() + timedelta(microseconds=index)
        repayment_id = uuid4()
        allocation_id = uuid4()
        capture_audit = AuditLog.objects.create(
            actor_user=fixture.maker,
            action="repayment.receipt_created",
            entity_type="repayment",
            entity_id=repayment_id,
        )
        repayment = Repayment.objects.create(
            repayment_id=repayment_id,
            loan_account=fixture.account,
            member=fixture.account.member,
            amount_received="1.00",
            received_date=date(2026, 8, 1),
            payment_method="neft",
            bank_reference_number=f"WINDOW-{index:03d}",
            bank_reference_number_normalized=f"WINDOW-{index:03d}",
            remarks="Synthetic ledger pagination evidence.",
            allocation_status="reversed" if index % 2 else "allocated",
            sap_posting_status="posted",
            captured_by_user=fixture.maker,
            idempotency_key_digest=f"capture-{index:03d}",
            payload_digest=f"capture-payload-{index:03d}",
            capture_audit=capture_audit,
            created_at=created_at,
        )
        allocation_audit = AuditLog.objects.create(
            actor_user=fixture.maker,
            action="repayment.allocated",
            entity_type="repayment_allocation",
            entity_id=allocation_id,
        )
        allocation = RepaymentAllocation.objects.create(
            repayment_allocation_id=allocation_id,
            repayment=repayment,
            loan_account=fixture.account,
            allocated_to_principal="1.00",
            allocated_to_interest="0.00",
            allocated_to_charges="0.00",
            unallocated_amount="0.00",
            principal_before="1.00",
            principal_after="0.00",
            interest_before="0.00",
            interest_after="0.00",
            charges_before="0.00",
            charges_after="0.00",
            total_before="1.00",
            total_after="0.00",
            decision_reason="Synthetic ledger pagination evidence.",
            idempotency_key_digest=f"allocation-{index:03d}",
            payload_digest=f"allocation-payload-{index:03d}",
            loan_status_before="active",
            loan_status_after="partially_repaid",
            allocated_by_user=fixture.maker,
            allocation_audit=allocation_audit,
            allocated_at=created_at,
        )
        if index % 2 == 0:
            RepaymentLedgerEntry.objects.create(
                allocation=allocation,
                loan_account=fixture.account,
                transaction_date=date(2026, 8, 1),
                credit_amount="1.00",
                principal_balance="0.00",
                interest_balance="0.00",
                charges_balance="0.00",
                total_outstanding="0.00",
                actor_user=fixture.maker,
                actor_display_name=fixture.maker.full_name,
                created_at=created_at,
            )
            continue
        reversal_id = uuid4()
        reversal_audit = AuditLog.objects.create(
            actor_user=fixture.maker,
            action="repayment.reversed",
            entity_type="repayment_reversal",
            entity_id=reversal_id,
        )
        reversal = RepaymentReversal.objects.create(
            repayment_reversal_id=reversal_id,
            allocation=allocation,
            repayment=repayment,
            loan_account=fixture.account,
            reversal_reason="Synthetic ledger pagination evidence.",
            principal_restored="1.00",
            interest_restored="0.00",
            charges_restored="0.00",
            total_before="0.00",
            total_after="1.00",
            reversed_by_user=fixture.maker,
            reversal_audit=reversal_audit,
            idempotency_key_digest=f"reversal-{index:03d}",
            payload_digest=f"reversal-payload-{index:03d}",
            reversed_at=created_at,
        )
        RepaymentReversalLedgerEntry.objects.create(
            reversal=reversal,
            loan_account=fixture.account,
            transaction_date=date(2026, 8, 1),
            debit_amount="1.00",
            principal_balance="1.00",
            interest_balance="0.00",
            charges_balance="0.00",
            total_outstanding="1.00",
            actor_user=fixture.maker,
            actor_display_name=fixture.maker.full_name,
            created_at=created_at,
        )
__all__ = [
    "ServicingOwnerFixture",
    "append_servicing_ledger_movements",
    "build_servicing_owner_fixture",
]
