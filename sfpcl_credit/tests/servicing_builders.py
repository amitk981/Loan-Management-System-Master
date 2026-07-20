"""Public synthetic builders for servicing owner and PostgreSQL acceptance tests."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, timedelta
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

from django.db import close_old_connections, connection, connections
from django.utils import timezone

from sfpcl_credit.configurations.models import InterestRateConfig
from sfpcl_credit.configurations.modules.interest_rate_configuration import (
    InterestRateConflict,
    activate,
)
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


def build_interest_rate_proposal(
    *, fixture, version, effective_from, rate="9.2500", effective_to=None
):
    """Create a proposed rate through the supported public test-fixture seam."""
    return InterestRateConfig.objects.create(
        version_number=version,
        rate_type="floating",
        effective_rate=rate,
        effective_from=effective_from,
        effective_to=effective_to,
        communication_required=False,
        board_approval_reference=f"BOARD-{version}",
        created_by_user=fixture.maker,
    )


def activate_interest_rate(*, fixture, proposal, idempotency_key):
    """Activate a public proposal without exposing test-case-private helper chains."""
    return activate(
        actor=fixture.checker,
        request=fixture.request,
        interest_rate_config_id=proposal.pk,
        idempotency_key=idempotency_key,
    )


def restore_servicing_account_to_created_read_state(*, fixture):
    """Restore the exact unfunded creation projection for public read-boundary tests."""
    type(fixture.account).objects.filter(pk=fixture.account.pk).update(
        loan_account_status="sanctioned",
        disbursed_amount="0.00",
        principal_outstanding="0.00",
        interest_outstanding="0.00",
        charges_outstanding="0.00",
        total_outstanding="0.00",
        tenure_start_date=None,
        tenure_end_date=None,
    )
    from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest

    sap_request = SapCustomerProfileRequest.objects.select_related(
        "assigned_to_user", "sent_communication"
    ).get(loan_application_id=fixture.account.loan_application_id)
    sap_request.assigned_to_user.email = (
        sap_request.sent_communication.recipient_address
    )
    sap_request.assigned_to_user.save(update_fields=["email"])
    fixture.account.refresh_from_db()
    return fixture.account


def clone_servicing_account(*, fixture, suffix):
    """Create a distinct owner-valid account for bounded portfolio acceptance."""
    from sfpcl_credit.identity.models import AuditLog
    from sfpcl_credit.workflows.models import WorkflowEvent

    def copy_for_insert(instance):
        values = {
            field.attname: deepcopy(getattr(instance, field.attname))
            for field in instance._meta.concrete_fields
            if not field.primary_key
        }
        return type(instance)(**values)

    original = fixture.account
    application = copy_for_insert(original.loan_application)
    application.pk = uuid4()
    application.application_reference_number = f"LO-RATE-{suffix}"
    application.save(force_insert=True)

    approval_case = copy_for_insert(original.sanction_decision.approval_case)
    approval_case.pk = uuid4()
    approval_case.loan_application = application
    approval_case.workflow_event = None
    approval_case.save(force_insert=True)

    sanction = copy_for_insert(original.sanction_decision)
    sanction.pk = uuid4()
    sanction.loan_application = application
    sanction.approval_case = approval_case
    sanction.save(force_insert=True)

    account = copy_for_insert(original)
    account.pk = uuid4()
    account.loan_application = application
    account.sanction_decision = sanction
    account.loan_account_number = f"LN-RATE-{suffix}"
    account.loan_account_number_normalized = account.loan_account_number.lower()
    account.created_at = original.created_at + timedelta(seconds=1)
    account.save(force_insert=True)

    terms = copy_for_insert(original.terms)
    terms.pk = uuid4()
    terms.loan_account = account
    terms.created_at = account.created_at
    terms.save(force_insert=True)

    original_history = original.status_history.get(outcome="created")
    history = copy_for_insert(original_history)
    history.pk = uuid4()
    history.loan_account = account
    history.loan_application_id_snapshot = application.pk
    history.sanction_decision_id_snapshot = sanction.pk
    history.loan_terms_id_snapshot = terms.pk
    history.changed_at = account.created_at
    history.save(force_insert=True)

    original_audit = AuditLog.objects.get(
        action="finance.loan_account.created", entity_id=original.pk
    )
    audit = copy_for_insert(original_audit)
    audit.pk = uuid4()
    audit.entity_id = account.pk
    audit.created_at = account.created_at
    audit.new_value_json = {
        **original_audit.new_value_json,
        "loan_account_id": str(account.pk),
        "loan_application_id": str(application.pk),
        "sanction_decision_id": str(sanction.pk),
        "loan_terms_id": str(terms.pk),
    }
    from sfpcl_credit.loans.modules.loan_account_lifecycle import (
        _canonical_manifest_json,
        _selector_manifest,
    )

    audit.old_value_json = _selector_manifest(audit.new_value_json)
    audit.selector_manifest_json = _canonical_manifest_json(audit.new_value_json)
    audit.selector_manifest_sha256 = audit.old_value_json["selector_manifest_sha256"]
    audit.save(force_insert=True)

    original_workflow = WorkflowEvent.objects.get(
        workflow_name="LoanAccountCreated", entity_id=original.pk
    )
    workflow = copy_for_insert(original_workflow)
    workflow.pk = uuid4()
    workflow.entity_id = account.pk
    workflow.created_at = account.created_at
    workflow.save(force_insert=True)
    return account


def race_interest_rate_activations(*, fixture, proposals, idempotency_keys):
    """Run the public activation facade concurrently for PostgreSQL acceptance."""
    items = list(zip(proposals, idempotency_keys, strict=True))
    if connection.vendor != "postgresql":
        outcomes = []
        for proposal, key in items:
            try:
                activate_interest_rate(
                    fixture=fixture,
                    proposal=proposal,
                    idempotency_key=key,
                )
                outcomes.append("success")
            except InterestRateConflict:
                outcomes.append("conflict")
        return outcomes
    barrier = Barrier(len(items))
    checker_id = fixture.checker.pk

    def contender(item):
        close_old_connections()
        try:
            checker = User.objects.get(pk=checker_id)
            barrier.wait(timeout=15)
            try:
                activate(
                    actor=checker,
                    request=fixture.request,
                    interest_rate_config_id=item[0].pk,
                    idempotency_key=item[1],
                )
                return "success"
            except InterestRateConflict:
                return "conflict"
        finally:
            connections["default"].close()

    with ThreadPoolExecutor(max_workers=len(items)) as pool:
        return list(pool.map(contender, items))


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
    "activate_interest_rate",
    "append_servicing_ledger_movements",
    "build_interest_rate_proposal",
    "build_servicing_owner_fixture",
    "race_interest_rate_activations",
]
