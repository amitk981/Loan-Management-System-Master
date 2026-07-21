"""Public synthetic builders for servicing owner and PostgreSQL acceptance tests."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, timedelta
import json
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

from django.db import close_old_connections, connection, connections
from django.test import Client
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


@dataclass(frozen=True)
class InterestCapitalisationFixture:
    account: object
    actor: User
    auth: dict

    def submit(self, *, idempotency_key):
        return Client().post(
            f"/api/v1/loan-accounts/{self.account.pk}/interest-capitalisations/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "capitalisation_date": "2027-05-01",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=idempotency_key,
            HTTP_X_REQUEST_ID="req-interest-policy-integrity",
            **self.auth,
        )


@dataclass(frozen=True)
class TerminalReminderFixture:
    account: object
    actor: User
    template: object
    request: object

    def queue(self, *, idempotency_key):
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.monitoring.models import Reminder
        from sfpcl_credit.monitoring.modules.reminder_engine import ReminderEngine

        created = ReminderEngine.create_reminder(
            actor=self.actor,
            loan_account_id=self.account.pk,
            payload={
                "quarter_end_date": "2026-06-30",
                "reminder_type": "outstanding_beyond_one_year",
                "channel": "sms",
                "content_template_id": str(self.template.pk),
                "message_body": "Loan remains outstanding at quarter end.",
                "send_now": False,
            },
            request=self.request,
        )
        ReminderEngine.send_reminder(
            actor=self.actor,
            reminder_id=created["reminder_id"],
            idempotency_key=idempotency_key,
            request=self.request,
        )
        reminder = Reminder.objects.get(pk=created["reminder_id"])
        return CommunicationDeliveryJob.objects.get(
            communication_id=reminder.communication_id
        )


@dataclass(frozen=True)
class TerminalDirectRepaymentFixture:
    """Public API fixture for the terminal composite repayment command."""

    account: object
    actor: User
    client: Client
    auth: dict

    @staticmethod
    def payload():
        return {
            "repayment_source": "direct_farmer",
            "amount_received": "100000.00",
            "received_date": "2026-12-04",
            "payment_method": "rtgs",
            "bank_reference_number": "UTR-DIRECT-VALIDATION-001",
            "remarks": "Confirmed receipt.",
        }

    def schedule(self, principal):
        from sfpcl_credit.loans.models import RepaymentSchedule

        return RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=self.account.repayment_date,
            principal_due=principal,
            interest_due="0.00",
            charges_due="0.00",
            total_due=principal,
            schedule_status="pending",
        )


def build_terminal_reminder_fixture(*, suffix):
    """Build reminder-owner truth without borrowing another TestCase setup."""
    from sfpcl_credit.communications.models import ContentTemplate
    from sfpcl_credit.loans.models import RepaymentSchedule
    from sfpcl_credit.monitoring.models import DpdStatus

    facts = build_ready_epic009_fixture(
        password="SyntheticReminder123!",
        finance_email=f"terminal.finance.{suffix}@sfpcl.example",
        credit_email=f"terminal.credit.{suffix}@sfpcl.example",
        cfc_email=f"terminal.cfc.{suffix}@sfpcl.example",
        borrower_email=f"terminal.borrower.{suffix}@sfpcl.example",
    )
    account = facts["ready"]["account"]
    type(account).objects.filter(pk=account.pk).update(
        loan_account_status="active",
        disbursed_amount=account.sanctioned_amount,
        principal_outstanding=account.sanctioned_amount,
        interest_outstanding="0.00",
        charges_outstanding="0.00",
        total_outstanding=account.sanctioned_amount,
    )
    account.refresh_from_db()
    actor = facts["credit"]
    for code in (
        "finance.loan_account.read",
        "monitoring.dpd.read",
        "monitoring.dpd.calculate",
        "monitoring.reminder.create",
        "communications.communication.send",
    ):
        permission, _ = Permission.objects.get_or_create(
            permission_code=code,
            defaults={
                "permission_name": code,
                "module_name": "monitoring",
                "risk_level": "high",
            },
        )
        RolePermission.objects.get_or_create(role=actor.primary_role, permission=permission)
    account.member.mobile_number = "+919876543210"
    account.member.email = f"terminal.member.{suffix}@example.test"
    account.member.save(update_fields=["mobile_number", "email"])
    RepaymentSchedule.objects.create(
        loan_account=account,
        installment_number=1,
        due_date=date(2025, 6, 29),
        principal_due="1000.00",
        interest_due="100.00",
        charges_due="0.00",
        total_due="1100.00",
        schedule_status="pending",
    )
    request = SimpleNamespace(
        META={"REMOTE_ADDR": "127.0.0.1"},
        headers={"User-Agent": "terminal-reminder-owner", "X-Request-ID": suffix},
    )
    dpd_id = uuid4()
    audit = AuditLog.objects.create(
        actor_user=actor,
        action="monitoring.dpd.calculated",
        entity_type="dpd_status",
        entity_id=dpd_id,
        new_value_json={"loan_account_id": str(account.pk), "as_of_date": "2026-06-30"},
    )
    dpd = DpdStatus.objects.create(
        dpd_status_id=dpd_id,
        loan_account=account,
        as_of_date=date(2026, 6, 30),
        days_past_due=367,
        sop_bucket="one_to_two_years",
        principal_overdue_amount="1000.00",
        interest_overdue_amount="100.00",
        total_overdue_amount="1100.00",
        earliest_unpaid_due_date=date(2025, 6, 29),
        calculation_inputs_json={
            "policy_decision": {
                "sop_policy_version": "SFPCL-SOP-DPD-1",
                "sop_boundary_convention": "calendar_anniversary",
            }
        },
        calculated_by_user=actor,
        calculation_audit=audit,
    )
    type(account).objects.filter(pk=account.pk).update(current_dpd_status=dpd)
    account.current_dpd_status_id = dpd.pk
    template = ContentTemplate.objects.create(
        template_code=f"terminal_reminder_{suffix}",
        template_name="Terminal reminder",
        template_type="sms",
        audience="borrower",
        body_template="Loan {{loan_account_number}} remains outstanding.",
        variables_json=["loan_account_number", "quarter_end_date"],
        approval_status="approved",
        template_version="1",
        effective_from=date(2020, 1, 1),
    )
    return TerminalReminderFixture(
        account=account, actor=actor, template=template, request=request
    )


def build_terminal_direct_repayment_fixture(*, suffix):
    """Build the composite repayment API seam without another test case."""
    password = "SyntheticRepayment123!"
    facts = build_ready_epic009_fixture(
        password=password,
        finance_email=f"terminal.repayment.{suffix}@sfpcl.example",
        credit_email=f"terminal.repayment.credit.{suffix}@sfpcl.example",
        cfc_email=f"terminal.repayment.cfc.{suffix}@sfpcl.example",
        borrower_email=f"terminal.repayment.borrower.{suffix}@sfpcl.example",
    )
    account = facts["ready"]["account"]
    type(account).objects.filter(pk=account.pk).update(
        loan_account_status="active",
        disbursed_amount=account.sanctioned_amount,
        principal_outstanding=account.sanctioned_amount,
        interest_outstanding="0.00",
        charges_outstanding="0.00",
        total_outstanding=account.sanctioned_amount,
    )
    account.refresh_from_db()
    actor = facts["credit"]
    for code in (
        "finance.loan_account.read",
        "finance.repayment.create",
        "finance.repayment.mark_sap_posted",
        "finance.repayment.allocate",
    ):
        permission, _ = Permission.objects.get_or_create(
            permission_code=code,
            defaults={
                "permission_name": code,
                "module_name": "finance",
                "risk_level": "critical",
            },
        )
        RolePermission.objects.get_or_create(role=actor.primary_role, permission=permission)
    client = Client()
    login = client.post(
        "/api/v1/auth/login/",
        {"email": actor.email, "password": password},
        content_type="application/json",
    )
    if login.status_code != 200:
        raise AssertionError(login.content)
    return TerminalDirectRepaymentFixture(
        account=account,
        actor=actor,
        client=client,
        auth={
            "HTTP_AUTHORIZATION": f"Bearer {login.json()['data']['access_token']}"
        },
    )


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


def build_approved_interest_calculation_policy(
    *, fixture, version, effective_from=date(2026, 4, 1), effective_to=date(2027, 3, 31)
):
    """Create one fully specified approved policy for public owner tests."""
    from sfpcl_credit.interest.models import InterestInvoiceConfiguration

    return InterestInvoiceConfiguration.objects.create(
        version_number=version,
        effective_from=effective_from,
        effective_to=effective_to,
        calculation_method="simple_daily",
        day_count_basis=365,
        monetary_rounding_mode="half_up",
        monetary_precision="0.01",
        rounding_application_boundary="whole_decision",
        tax_rate="0.0000",
        fixed_fee_amount="0.00",
        owner_role_codes=["accounts_head"],
        status="active",
        approved_by_user=fixture.maker,
    )


def build_interest_capitalisation_fixture():
    """Build the complete public API fixture through the retained owner setup."""
    from sfpcl_credit.tests.test_interest_capitalisation_api import (
        InterestCapitalisationApiTests,
    )

    retained = InterestCapitalisationApiTests(
        "test_may_first_finalisation_moves_principal_once_and_retains_intimation_chain"
    )
    retained.setUp()
    return InterestCapitalisationFixture(
        account=retained.account,
        actor=retained.actor,
        auth=retained.auth,
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
