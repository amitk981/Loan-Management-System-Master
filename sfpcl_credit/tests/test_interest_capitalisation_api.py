import json
from datetime import date
from decimal import Decimal
from uuid import uuid4

from django.test import Client, TestCase


class InterestCapitalisationApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.communications.models import ContentTemplate
        from sfpcl_credit.tests.test_interest_invoice_api import InterestInvoiceApiTests

        fixture = InterestInvoiceApiTests(
            "test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.actor,
            "finance.interest_capitalise",
        )
        self.client = Client()
        self.auth = fixture.auth
        generated = fixture._generate("capitalisation-source-invoice")
        self.assertEqual(generated.status_code, 200, generated.content)
        issued = fixture._issue(
            generated.json()["data"]["interest_invoice_id"],
            "capitalisation-source-invoice-issue",
        )
        self.assertEqual(issued.status_code, 200, issued.content)
        from sfpcl_credit.loans.models import RepaymentSchedule

        self.account.interest_outstanding = "37000.00"
        self.account.total_outstanding = "437000.00"
        self.account.save(update_fields=["interest_outstanding", "total_outstanding"])
        self.account.refresh_from_db()
        self.interest_schedule = RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=999,
            due_date=date(2027, 3, 31),
            principal_due="0.00",
            interest_due="37000.00",
            charges_due="0.00",
            total_due="37000.00",
            schedule_status="pending",
        )
        ContentTemplate.objects.create(
            template_code="interest_capitalisation_notice",
            template_name="Interest capitalisation notice",
            template_type="email",
            audience="borrower",
            subject_template="Interest capitalised for {{financial_year}}",
            body_template=(
                "Unpaid interest {{unpaid_interest_amount}} was added to principal. "
                "Your revised principal is {{new_principal_amount}}."
            ),
            variables_json=[
                "financial_year",
                "unpaid_interest_amount",
                "new_principal_amount",
            ],
            approval_status="approved",
            template_version="1",
            effective_from=date(2026, 1, 1),
        )

    def test_mismatched_account_interest_rejects_every_capitalisation_side_effect(self):
        from sfpcl_credit.communications.models import (
            Communication,
            CommunicationDeliveryJob,
        )
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationHardCopyTask,
            InterestCapitalisationInvoiceEvidence,
            InterestCapitalisationLedgerEntry,
            InterestCapitalisationScheduleEvidence,
        )
        from sfpcl_credit.loans.models import LoanAccount, RepaymentSchedule

        self.account.interest_outstanding = "36999.99"
        self.account.total_outstanding = "436999.99"
        self.account.save(update_fields=["interest_outstanding", "total_outstanding"])
        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        schedule_before = list(
            RepaymentSchedule.objects.filter(loan_account=self.account).values()
        )
        counts_before = {
            "capitalisation": InterestCapitalisation.objects.count(),
            "invoice_evidence": InterestCapitalisationInvoiceEvidence.objects.count(),
            "schedule_evidence": InterestCapitalisationScheduleEvidence.objects.count(),
            "ledger": InterestCapitalisationLedgerEntry.objects.count(),
            "task": InterestCapitalisationHardCopyTask.objects.count(),
            "communication": Communication.objects.count(),
            "delivery_job": CommunicationDeliveryJob.objects.count(),
            "document": DocumentFile.objects.count(),
            "audit": AuditLog.objects.count(),
        }

        response = self._capitalise("capitalisation-account-mismatch")

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(
            list(RepaymentSchedule.objects.filter(loan_account=self.account).values()),
            schedule_before,
        )
        self.assertEqual(
            {
                "capitalisation": InterestCapitalisation.objects.count(),
                "invoice_evidence": InterestCapitalisationInvoiceEvidence.objects.count(),
                "schedule_evidence": InterestCapitalisationScheduleEvidence.objects.count(),
                "ledger": InterestCapitalisationLedgerEntry.objects.count(),
                "task": InterestCapitalisationHardCopyTask.objects.count(),
                "communication": Communication.objects.count(),
                "delivery_job": CommunicationDeliveryJob.objects.count(),
                "document": DocumentFile.objects.count(),
                "audit": AuditLog.objects.count(),
            },
            counts_before,
        )

    def test_mismatched_schedule_interest_rejects_every_capitalisation_side_effect(self):
        self.interest_schedule.interest_due = "36999.99"
        self.interest_schedule.total_due = "36999.99"
        self.interest_schedule.save(update_fields=["interest_due", "total_due"])
        before = self._financial_owner_snapshot()

        response = self._capitalise("capitalisation-schedule-mismatch")

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(self._financial_owner_snapshot(), before)

    def test_mismatched_interest_ledger_rejects_every_capitalisation_side_effect(self):
        from sfpcl_credit.loans.models import RepaymentLedgerEntry

        allocation = self._interest_allocation(
            received_date=date(2027, 4, 30),
            reference="LEDGER-MISMATCH",
            amount="1.00",
            apply_to_schedule=False,
        )
        RepaymentLedgerEntry.objects.create(
            allocation=allocation,
            loan_account=self.account,
            transaction_date=date(2027, 4, 30),
            credit_amount="1.00",
            principal_balance="400000.00",
            interest_balance="36999.99",
            charges_balance="0.00",
            total_outstanding="436999.99",
            actor_user=self.actor,
            actor_display_name=self.actor.full_name,
        )
        before = self._financial_owner_snapshot()

        response = self._capitalise("capitalisation-ledger-mismatch")

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(self._financial_owner_snapshot(), before)

    def test_mismatched_payment_owner_rejects_every_capitalisation_side_effect(self):
        self._interest_allocation(
            received_date=date(2027, 4, 30),
            reference="PAYMENT-OWNER-MISMATCH",
            amount="25.00",
        )
        before = self._financial_owner_snapshot()

        response = self._capitalise("capitalisation-payment-owner-mismatch")

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(self._financial_owner_snapshot(), before)

    def test_preview_derives_eligible_unpaid_interest_and_is_zero_write(self):
        from sfpcl_credit.communications.models import Communication, CommunicationDeliveryJob
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount

        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        counts_before = {
            "audit": AuditLog.objects.count(),
            "communication": Communication.objects.count(),
            "job": CommunicationDeliveryJob.objects.count(),
            "document": DocumentFile.objects.count(),
        }

        response = self.client.post(
            "/api/v1/interest-capitalisations/check/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "as_of_date": "2027-04-30",
                    "dry_run": True,
                }
            ),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"],
            {
                "financial_year": "FY2026-27",
                "as_of_date": "2027-04-30",
                "dry_run": True,
                "results": [
                    {
                        "loan_account_id": str(self.account.pk),
                        "eligible": True,
                        "reason_code": "eligible_unpaid_interest",
                        "old_principal_amount": "400000.00",
                        "unpaid_interest_amount": "37000.00",
                        "new_principal_amount": "437000.00",
                    }
                ],
            },
        )
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(
            {
                "audit": AuditLog.objects.count(),
                "communication": Communication.objects.count(),
                "job": CommunicationDeliveryJob.objects.count(),
                "document": DocumentFile.objects.count(),
            },
            counts_before,
        )

    def test_capitalisation_uses_gross_less_interest_paid_once_and_excludes_tax_and_fee(self):
        from django.db import connection

        from sfpcl_credit.interest.models import InterestCapitalisation, InterestInvoice

        invoice = InterestInvoice.objects.get(financial_year="FY2026-27")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE interest_invoices
                SET gross_interest_amount = %s,
                    interest_paid_amount = %s,
                    tax_rate = %s,
                    tax_amount = %s,
                    fixed_fee_amount = %s,
                    interest_amount = %s
                WHERE interest_invoice_id = %s
                """,
                [
                    "100.00", "25.00", "10.0000", "10.00", "5.00", "90.00",
                    invoice._meta.pk.get_db_prep_value(invoice.pk, connection, prepared=False),
                ],
            )
        self.account.interest_outstanding = "75.00"
        self.account.total_outstanding = "400075.00"
        self.account.save(update_fields=["interest_outstanding", "total_outstanding"])
        self.interest_schedule.interest_due = "75.00"
        self.interest_schedule.total_due = "75.00"
        self.interest_schedule.save(update_fields=["interest_due", "total_due"])

        response = self._capitalise("capitalisation-interest-only")

        self.assertEqual(response.status_code, 200, response.content)
        capitalisation = InterestCapitalisation.objects.get()
        self.assertEqual(str(capitalisation.unpaid_interest_amount), "75.00")
        self.assertEqual(str(capitalisation.new_principal_amount), "400075.00")

    def test_interest_allocation_after_invoice_through_cutoff_reduces_capitalisation_once(self):
        from sfpcl_credit.interest.models import InterestCapitalisation

        schedule = self.interest_schedule
        eligible = self._interest_allocation(
            received_date=date(2027, 4, 30),
            reference="CUT-OFF-PAYMENT",
            amount="25.00",
        )
        schedule.paid_interest = "25.00"
        schedule.save(update_fields=["paid_interest"])
        self.account.interest_outstanding = "36975.00"
        self.account.total_outstanding = "436975.00"
        self.account.save(update_fields=["interest_outstanding", "total_outstanding"])

        preview = self.client.post(
            "/api/v1/interest-capitalisations/check/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "as_of_date": "2027-04-30",
                    "dry_run": True,
                }
            ),
            content_type="application/json",
            **self.auth,
        )

        response = self._capitalise("capitalisation-cutoff-payment")

        self.assertEqual(preview.status_code, 200, preview.content)
        self.assertEqual(
            preview.json()["data"]["results"][0]["unpaid_interest_amount"],
            "36975.00",
        )
        self.assertEqual(response.status_code, 200, response.content)
        capitalisation = InterestCapitalisation.objects.get()
        self.assertEqual(str(capitalisation.unpaid_interest_amount), "36975.00")
        self.assertEqual(
            list(capitalisation.payment_evidence.values_list("repayment_allocation_id", flat=True)),
            [eligible.pk],
        )

    def _interest_allocation(
        self, *, received_date, reference, amount, apply_to_schedule=True
    ):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            Repayment,
            RepaymentAllocation,
            RepaymentScheduleAllocation,
        )

        repayment_id = uuid4()
        capture_audit = AuditLog.objects.create(
            actor_user=self.actor,
            action="repayment.receipt_created",
            entity_type="repayment",
            entity_id=repayment_id,
        )
        repayment = Repayment.objects.create(
            repayment_id=repayment_id,
            loan_account=self.account,
            member=self.account.member,
            amount_received=amount,
            received_date=received_date,
            payment_method="neft",
            bank_reference_number=reference,
            bank_reference_number_normalized=reference,
            remarks="Retained interest payment evidence.",
            allocation_status="allocated",
            sap_posting_status="posted",
            captured_by_user=self.actor,
            idempotency_key_digest=f"capture-{reference}",
            payload_digest=f"payload-{reference}",
            capture_audit=capture_audit,
        )
        allocation_id = uuid4()
        allocation_audit = AuditLog.objects.create(
            actor_user=self.actor,
            action="repayment.allocation.completed",
            entity_type="repayment_allocation",
            entity_id=allocation_id,
        )
        allocation = RepaymentAllocation.objects.create(
            repayment_allocation_id=allocation_id,
            repayment=repayment,
            loan_account=self.account,
            allocated_to_principal="0.00",
            allocated_to_interest=amount,
            allocated_to_charges="0.00",
            unallocated_amount="0.00",
            principal_before="400000.00",
            principal_after="400000.00",
            interest_before=amount,
            interest_after="0.00",
            charges_before="0.00",
            charges_after="0.00",
            total_before=Decimal("400000.00") + Decimal(amount),
            total_after="400000.00",
            allocated_by_user=self.actor,
            allocation_audit=allocation_audit,
        )
        if apply_to_schedule:
            RepaymentScheduleAllocation.objects.create(
                allocation=allocation,
                repayment_schedule=self.interest_schedule,
                principal_applied="0.00",
                interest_applied=amount,
                schedule_status_before="pending",
                schedule_status_after="pending",
            )
        return allocation

    def _financial_owner_snapshot(self):
        from sfpcl_credit.communications.models import Communication
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationHardCopyTask,
            InterestCapitalisationInvoiceEvidence,
            InterestCapitalisationLedgerEntry,
            InterestCapitalisationScheduleEvidence,
        )
        from sfpcl_credit.loans.models import LoanAccount, RepaymentSchedule

        return {
            "account": LoanAccount.objects.values().get(pk=self.account.pk),
            "schedules": list(
                RepaymentSchedule.objects.filter(loan_account=self.account).values()
            ),
            "capitalisations": InterestCapitalisation.objects.count(),
            "invoice_evidence": InterestCapitalisationInvoiceEvidence.objects.count(),
            "schedule_evidence": InterestCapitalisationScheduleEvidence.objects.count(),
            "capitalisation_ledger": InterestCapitalisationLedgerEntry.objects.count(),
            "tasks": InterestCapitalisationHardCopyTask.objects.count(),
            "communications": Communication.objects.count(),
            "documents": DocumentFile.objects.count(),
            "audits": AuditLog.objects.count(),
        }

    def test_may_first_finalisation_moves_principal_once_and_retains_intimation_chain(self):
        response = self._capitalise("capitalisation-final-001")
        replay = self._capitalise("capitalisation-final-001")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(replay.status_code, 200, replay.content)

        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationInvoiceEvidence,
            InterestCapitalisationLedgerEntry,
            InterestInvoice,
        )

        capitalisation = InterestCapitalisation.objects.get()
        self.account.refresh_from_db()
        source_invoice = InterestInvoice.objects.get(financial_year="FY2026-27")
        self.assertEqual(str(capitalisation.old_principal_amount), "400000.00")
        self.assertEqual(str(capitalisation.unpaid_interest_amount), "37000.00")
        self.assertEqual(str(capitalisation.new_principal_amount), "437000.00")
        self.assertEqual(str(self.account.principal_outstanding), "437000.00")
        self.assertEqual(str(self.account.total_outstanding), "437000.00")
        self.assertEqual(capitalisation.rate_versions_json, ["RATE-INVOICE-1"])
        self.assertEqual(capitalisation.calculation_versions_json, ["INV-CALC-1"])
        self.assertEqual(capitalisation.capitalised_by_user_id, self.actor.pk)
        self.assertIsNotNone(capitalisation.capitalisation_audit_id)
        self.assertIsNotNone(capitalisation.borrower_intimation_email_id)
        self.assertIsNotNone(capitalisation.borrower_intimation_letter_document_id)
        evidence = InterestCapitalisationInvoiceEvidence.objects.get()
        self.assertEqual(evidence.interest_invoice_id, source_invoice.pk)
        self.assertEqual(str(evidence.unpaid_interest_amount), "37000.00")
        ledger = InterestCapitalisationLedgerEntry.objects.get()
        self.assertEqual(str(ledger.debit_amount), "37000.00")
        self.assertEqual(str(ledger.principal_balance), "437000.00")
        self.assertEqual(str(ledger.total_outstanding), "437000.00")
        job = CommunicationDeliveryJob.objects.get(
            communication_id=capitalisation.borrower_intimation_email_id
        )
        self.assertEqual(job.status, "queued")
        self.assertEqual(
            AuditLog.objects.filter(action="interest.capitalisation.completed").count(),
            1,
        )
        self.assertEqual(source_invoice.invoice_status, "issued")
        self.assertEqual(str(source_invoice.interest_amount), "37000.00")
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(
            replay.json()["data"]["original_response"],
            response.json()["data"],
        )
        self.assertEqual(InterestCapitalisation.objects.count(), 1)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)
        from sfpcl_credit.loans.modules.loan_account_read import principal_balance_as_of

        self.assertEqual(
            str(
                principal_balance_as_of(
                    account=self.account,
                    as_of_date=date(2027, 4, 30),
                )
            ),
            "400000.00",
        )
        self.assertEqual(
            str(
                principal_balance_as_of(
                    account=self.account,
                    as_of_date=date(2027, 5, 31),
                )
            ),
            "437000.00",
        )
        account_response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/",
            **self.auth,
        )
        self.assertEqual(account_response.status_code, 200, account_response.content)
        self.assertEqual(
            account_response.json()["data"]["principal_outstanding"],
            "437000.00",
        )
        ledger_response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger/",
            **self.auth,
        )
        self.assertEqual(ledger_response.status_code, 200, ledger_response.content)
        self.assertEqual(
            ledger_response.json()["data"][-1]["transaction_type"],
            "interest_capitalisation",
        )
        self.assertEqual(
            ledger_response.json()["data"][-1]["principal_balance"],
            "437000.00",
        )

    def test_capitalisation_reclassifies_existing_interest_and_schedule_without_total_inflation(self):
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationHardCopyTask,
            InterestCapitalisationScheduleEvidence,
        )
        from sfpcl_credit.loans.models import RepaymentSchedule

        schedule = self.interest_schedule

        response = self._capitalise("capitalisation-reclassification")

        self.assertEqual(response.status_code, 200, response.content)
        self.account.refresh_from_db()
        schedule.refresh_from_db()
        capitalisation = InterestCapitalisation.objects.get()
        self.assertEqual(str(self.account.principal_outstanding), "437000.00")
        self.assertEqual(str(self.account.interest_outstanding), "0.00")
        self.assertEqual(str(self.account.total_outstanding), "437000.00")
        self.assertEqual(str(schedule.paid_interest), "37000.00")
        self.assertEqual(schedule.schedule_status, "paid")
        self.assertEqual(
            InterestCapitalisationScheduleEvidence.objects.get().repayment_schedule_id,
            schedule.pk,
        )
        task = InterestCapitalisationHardCopyTask.objects.get()
        self.assertEqual(task.capitalisation_id, capitalisation.pk)
        self.assertEqual(task.letter_document_id, capitalisation.borrower_intimation_letter_document_id)
        self.assertEqual(task.status, "pending")

    def test_cutoff_client_money_and_duplicate_or_changed_replay_fail_closed(self):
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationLedgerEntry,
        )

        before_cutoff = self.client.post(
            "/api/v1/interest-capitalisations/check/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "as_of_date": "2027-04-29",
                    "dry_run": True,
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        on_cutoff = self._capitalise(
            "capitalisation-cutoff",
            {
                "financial_year": "FY2026-27",
                "capitalisation_date": "2027-04-30",
            },
        )
        client_money = self._capitalise(
            "capitalisation-client-money",
            {
                "financial_year": "FY2026-27",
                "capitalisation_date": "2027-05-01",
                "unpaid_interest_amount": "1.00",
                "new_principal_amount": "400001.00",
            },
        )

        self.assertEqual(before_cutoff.status_code, 200, before_cutoff.content)
        self.assertFalse(before_cutoff.json()["data"]["results"][0]["eligible"])
        self.assertEqual(
            before_cutoff.json()["data"]["results"][0]["reason_code"],
            "cutoff_not_reached",
        )
        self.assertEqual(on_cutoff.status_code, 400, on_cutoff.content)
        self.assertEqual(client_money.status_code, 400, client_money.content)
        self.assertIn(
            "unpaid_interest_amount", client_money.json()["error"]["field_errors"]
        )
        self.assertEqual(InterestCapitalisation.objects.count(), 0)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 0)

        first = self._capitalise("capitalisation-duplicate-first")
        changed_replay = self._capitalise(
            "capitalisation-duplicate-first",
            {
                "financial_year": "FY2026-27",
                "capitalisation_date": "2027-05-02",
            },
        )
        duplicate_fy = self._capitalise("capitalisation-duplicate-second")

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(changed_replay.status_code, 409, changed_replay.content)
        self.assertEqual(duplicate_fy.status_code, 409, duplicate_fy.content)
        self.assertEqual(InterestCapitalisation.objects.count(), 1)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)

    def test_missing_intimation_configuration_rolls_back_every_financial_write(self):
        from sfpcl_credit.communications.models import ContentTemplate
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationInvoiceEvidence,
            InterestCapitalisationLedgerEntry,
        )

        ContentTemplate.objects.filter(
            template_code="interest_capitalisation_notice"
        ).delete()
        principal_before = self.account.principal_outstanding
        total_before = self.account.total_outstanding

        response = self._capitalise("capitalisation-missing-intimation")

        self.assertEqual(response.status_code, 409, response.content)
        self.account.refresh_from_db()
        self.assertEqual(self.account.principal_outstanding, principal_before)
        self.assertEqual(self.account.total_outstanding, total_before)
        self.assertEqual(InterestCapitalisation.objects.count(), 0)
        self.assertEqual(InterestCapitalisationInvoiceEvidence.objects.count(), 0)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 0)

    def test_permission_and_cross_scope_denials_are_zero_write(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.interest.models import InterestCapitalisation

        permission = Permission.objects.get(
            permission_code="finance.interest_capitalise"
        )
        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission=permission,
        ).delete()
        denied = self._capitalise("capitalisation-permission-denied")
        self.assertEqual(denied.status_code, 403, denied.content)

        root_fixture = self.fixture.fixture.fixture.owner.fixture.fixture
        outsider = root_fixture._user("sales", "Capitalisation scope outsider")
        root_fixture._grant(
            outsider,
            "finance.interest_capitalise",
            "finance.loan_account.read",
        )
        cross_scope = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/interest-capitalisations/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "capitalisation_date": "2027-05-01",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="capitalisation-cross-scope",
            **self.fixture.fixture.fixture.owner.fixture._auth(outsider),
        )
        self.assertEqual(cross_scope.status_code, 403, cross_scope.content)
        self.assertEqual(InterestCapitalisation.objects.count(), 0)

    def test_fully_paid_and_missing_invoice_truth_cannot_move_principal(self):
        from uuid import uuid4

        from django.utils import timezone

        from sfpcl_credit.communications.models import Communication
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import InterestCapitalisation, InterestInvoice

        source = InterestInvoice.objects.get(financial_year="FY2026-27")
        paid_invoice_id = uuid4()
        generation_audit = AuditLog.objects.create(
            actor_user=self.actor,
            action="interest.invoice.generated",
            entity_type="interest_invoice",
            entity_id=paid_invoice_id,
        )
        issuance_audit = AuditLog.objects.create(
            actor_user=self.actor,
            action="interest.invoice.issued",
            entity_type="interest_invoice",
            entity_id=paid_invoice_id,
        )
        document = DocumentFile.objects.create(
            file_name="paid-interest-invoice.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=1,
            storage_provider="test",
            storage_key="paid-interest-invoice.pdf",
            checksum_sha256="0" * 64,
            uploaded_by_user=self.actor,
            sensitivity_level="confidential",
        )
        communication = Communication.objects.create(
            related_entity_type="interest_invoice",
            related_entity_id=paid_invoice_id,
            recipient_party_type="borrower",
            recipient_party_id=self.account.member_id,
            recipient_address=self.account.member.email,
            channel="email",
            subject_snapshot="Paid interest invoice",
            body_snapshot="Paid in full.",
            sent_by_user=self.actor,
            delivery_status="pending",
        )
        InterestInvoice.objects.create(
            interest_invoice_id=paid_invoice_id,
            loan_account=self.account,
            member=self.account.member,
            loan_account_number=self.account.loan_account_number,
            member_number=self.account.member.member_number or "",
            member_display_name=self.account.member.display_name,
            financial_year="FY2025-26",
            invoice_number="INT-PAID-FY2025-26",
            invoice_date=date(2026, 3, 31),
            interest_period_start=date(2025, 4, 1),
            interest_period_end=date(2026, 3, 31),
            principal_base_amount=source.principal_base_amount,
            interest_rate=source.interest_rate,
            rate_config=source.rate_config,
            rate_version_number=source.rate_version_number,
            calculation_configuration=source.calculation_configuration,
            calculation_version=source.calculation_version,
            calculation_method=source.calculation_method,
            day_count_basis=source.day_count_basis,
            calculation_days=365,
            gross_interest_amount="100.00",
            interest_paid_amount="100.00",
            tax_rate="0.0000",
            tax_amount="0.00",
            fixed_fee_amount="0.00",
            interest_amount="100.00",
            invoice_status="issued",
            generated_by_user=self.actor,
            generated_at=timezone.now(),
            generation_idempotency_key_digest="paid-generation-key",
            generation_payload_digest="paid-generation-payload",
            generation_audit=generation_audit,
            document=document,
            communication=communication,
            issued_by_user=self.actor,
            issued_at=timezone.now(),
            issuance_idempotency_key_digest="paid-issuance-key",
            issuance_payload_digest="paid-issuance-payload",
            issuance_audit=issuance_audit,
        )
        principal_before = self.account.principal_outstanding

        paid = self._capitalise(
            "capitalisation-paid-invoice",
            {
                "financial_year": "FY2025-26",
                "capitalisation_date": "2026-05-01",
            },
        )
        missing = self._capitalise(
            "capitalisation-missing-invoice",
            {
                "financial_year": "FY2024-25",
                "capitalisation_date": "2025-05-01",
            },
        )

        self.assertEqual(paid.status_code, 409, paid.content)
        self.assertEqual(missing.status_code, 409, missing.content)
        self.account.refresh_from_db()
        self.assertEqual(self.account.principal_outstanding, principal_before)
        self.assertEqual(InterestCapitalisation.objects.count(), 0)

    def test_failed_email_delivery_and_retry_replay_never_recapitalise(self):
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationLedgerEntry,
        )

        first = self._capitalise("capitalisation-delivery-failure")
        self.assertEqual(first.status_code, 200, first.content)
        capitalisation = InterestCapitalisation.objects.get()
        job = CommunicationDeliveryJob.objects.get(
            communication_id=capitalisation.borrower_intimation_email_id
        )
        job.status = CommunicationDeliveryJob.STATUS_FAILED
        job.attempts = job.max_attempts
        job.last_failure_code = "provider_rejected"
        job.save(update_fields=["status", "attempts", "last_failure_code"])

        replay = self._capitalise("capitalisation-delivery-failure")

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(
            replay.json()["data"]["original_response"],
            first.json()["data"],
        )
        self.assertEqual(InterestCapitalisation.objects.count(), 1)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)
        self.account.refresh_from_db()
        self.assertEqual(str(self.account.principal_outstanding), "437000.00")

    def _capitalise(self, key, payload=None):
        return self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/interest-capitalisations/",
            data=json.dumps(
                payload
                or {
                    "financial_year": "FY2026-27",
                    "capitalisation_date": "2027-05-01",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-interest-capitalisation",
            HTTP_USER_AGENT="interest-capitalisation-contract-test",
            REMOTE_ADDR="203.0.113.81",
            **self.auth,
        )
