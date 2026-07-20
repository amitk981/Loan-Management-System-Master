import json
from datetime import date

from django.test import Client, TestCase


class InterestInvoiceApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_reads_api import (
            ActiveLoanAccountReadApiTests,
        )

        fixture = ActiveLoanAccountReadApiTests(
            "test_exact_transfer_projects_active_funded_amounts_and_activation_time"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.reader
        fixture.fixture.owner.fixture.fixture._grant(
            self.actor,
            "finance.interest_invoice.create",
            "finance.interest_invoice.issue",
        )
        self.client = Client()
        self.auth = fixture.fixture.owner.fixture._auth(self.actor)
        self.account.member.email = "invoice.borrower@sfpcl.example"
        self.account.member.save(update_fields=["email"])
        self._configure_rate()

        from sfpcl_credit.interest.models import InterestInvoiceConfiguration

        self.configuration = InterestInvoiceConfiguration.objects.create(
            version_number="INV-CALC-1",
            effective_from=date(2026, 4, 1),
            effective_to=date(2027, 3, 31),
            calculation_method="simple_daily",
            day_count_basis=365,
            tax_rate="0.0000",
            fixed_fee_amount="0.00",
            owner_role_codes=["accounts_head"],
            status="active",
            approved_by_user=self.actor,
        )

    def test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged(self):
        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import InterestInvoice
        from sfpcl_credit.loans.models import LoanAccount, RepaymentLedgerEntry

        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        ledger_before = list(RepaymentLedgerEntry.objects.values())

        response = self._generate("invoice-generate-001")

        self.assertEqual(response.status_code, 200, response.content)
        invoice = InterestInvoice.objects.get()
        self.assertEqual(invoice.loan_account_id, self.account.pk)
        self.assertEqual(invoice.member_id, self.account.member_id)
        self.assertEqual(invoice.financial_year, "FY2026-27")
        self.assertEqual(invoice.interest_period_start, date(2026, 4, 1))
        self.assertEqual(invoice.interest_period_end, date(2027, 3, 31))
        self.assertEqual(str(invoice.principal_base_amount), "400000.00")
        self.assertEqual(str(invoice.interest_rate), "9.2500")
        self.assertEqual(str(invoice.gross_interest_amount), "37000.00")
        self.assertEqual(str(invoice.interest_paid_amount), "0.00")
        self.assertEqual(str(invoice.interest_amount), "37000.00")
        self.assertEqual(invoice.invoice_status, "draft")
        self.assertEqual(invoice.rate_version_number, "RATE-INVOICE-1")
        self.assertEqual(invoice.calculation_version, "INV-CALC-1")
        self.assertEqual(invoice.generated_by_user_id, self.actor.pk)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.invoice.generated").count(), 1
        )
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(list(RepaymentLedgerEntry.objects.values()), ledger_before)
        self.assertEqual(response.json()["data"]["interest_amount"], "37000.00")
        self.assertNotIn("invoice.borrower@sfpcl.example", str(response.json()))

    def test_exact_replay_and_scoped_list_return_one_retained_invoice(self):
        from sfpcl_credit.interest.models import InterestInvoice

        first = self._generate("invoice-replay-001")
        replay = self._generate("invoice-replay-001")
        duplicate = self._generate("invoice-replay-duplicate")
        listing = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/interest-invoices/",
            {"financial_year": "FY2026-27", "invoice_status": "draft"},
            **self.auth,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(
            replay.json()["data"]["original_response"], first.json()["data"]
        )
        self.assertEqual(duplicate.status_code, 409, duplicate.content)
        self.assertEqual(InterestInvoice.objects.count(), 1)
        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["pagination"]["total_count"], 1)
        self.assertEqual(listing.json()["data"], [first.json()["data"]])

    def test_issue_binds_one_document_communication_job_and_audit_chain(self):
        from sfpcl_credit.communications.models import (
            Communication,
            CommunicationDeliveryJob,
            ContentTemplate,
        )
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import InterestInvoice

        template = ContentTemplate.objects.create(
            template_code="annual_interest_invoice_email",
            template_name="Annual interest invoice",
            template_type="email",
            audience="borrower",
            subject_template="Interest invoice {{invoice_number}}",
            body_template=(
                "Your {{financial_year}} interest invoice {{invoice_number}} "
                "for {{interest_amount}} is attached."
            ),
            variables_json=["financial_year", "invoice_number", "interest_amount"],
            approval_status="approved",
            template_version="1",
            effective_from=date(2026, 1, 1),
        )
        self.configuration.communication_template = template
        self.configuration.save(update_fields=["communication_template"])
        generated = self._generate("invoice-issue-generate")
        invoice_id = generated.json()["data"]["interest_invoice_id"]
        document_count = DocumentFile.objects.count()
        communication_count = Communication.objects.count()
        job_count = CommunicationDeliveryJob.objects.count()

        issued = self._issue(invoice_id, "invoice-issue-001")
        replay = self._issue(invoice_id, "invoice-issue-001")

        self.assertEqual(issued.status_code, 200, issued.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        invoice = InterestInvoice.objects.get(pk=invoice_id)
        self.assertEqual(invoice.invoice_status, "issued")
        self.assertIsNotNone(invoice.document_id)
        self.assertIsNotNone(invoice.communication_id)
        self.assertIsNotNone(invoice.issuance_audit_id)
        self.assertEqual(DocumentFile.objects.count(), document_count + 1)
        self.assertEqual(Communication.objects.count(), communication_count + 1)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), job_count + 1)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.invoice.issued").count(), 1
        )
        self.assertEqual(issued.json()["data"]["delivery_status"], "queued")
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertNotEqual(issued.json()["data"]["invoice_status"], "paid")
        self.assertNotIn("paid_at", issued.json()["data"])

    def test_create_permission_without_loan_scope_is_safe_zero_write_denial(self):
        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import InterestInvoice

        root_fixture = self.fixture.fixture.owner.fixture.fixture
        outsider = root_fixture._user("sales", "Configured-code outsider")
        root_fixture._grant(outsider, "finance.interest_invoice.create")
        outsider_auth = self.fixture.fixture.owner.fixture._auth(outsider)

        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/interest-invoices/",
            data=json.dumps({"financial_year": "FY2026-27"}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="invoice-out-of-scope",
            **outsider_auth,
        )

        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(response.json()["error"]["code"], "FORBIDDEN")
        self.assertNotIn(self.account.member.email, str(response.json()))
        self.assertEqual(InterestInvoice.objects.count(), 0)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.invoice.generated").count(), 0
        )

    def test_retained_calculation_rejects_bulk_rewrite(self):
        from django.core.exceptions import ValidationError
        from sfpcl_credit.interest.models import InterestInvoice

        generated = self._generate("invoice-immutable-001")
        self.assertEqual(generated.status_code, 200, generated.content)
        retained = InterestInvoice.objects.get()
        before = generated.json()["data"]

        with self.assertRaises(ValidationError):
            InterestInvoice.objects.filter(pk=retained.pk).update(
                interest_amount="1.00"
            )

        retained.refresh_from_db()
        self.assertEqual(f"{retained.interest_amount:.2f}", before["interest_amount"])

    def test_client_money_and_missing_accounting_configuration_fail_closed(self):
        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import InterestInvoice, InterestInvoiceConfiguration

        client_money = self._generate(
            "invoice-client-money",
            {"financial_year": "FY2026-27", "interest_amount": "1.00"},
        )
        self.assertEqual(client_money.status_code, 400, client_money.content)
        self.assertIn("interest_amount", client_money.json()["error"]["field_errors"])

        InterestInvoiceConfiguration.objects.all().delete()
        missing_config = self._generate("invoice-missing-config")
        self.assertEqual(missing_config.status_code, 409, missing_config.content)
        self.assertEqual(InterestInvoice.objects.count(), 0)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.invoice.generated").count(), 0
        )

    def _issue(self, invoice_id, key, payload=None):
        return self.client.post(
            f"/api/v1/interest-invoices/{invoice_id}/issue/",
            data=json.dumps(
                payload
                or {
                    "channel": "email",
                    "recipient_email": "invoice.borrower@sfpcl.example",
                    "remarks": "Annual interest invoice issued.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-interest-invoice-issue",
            **self.auth,
        )

    def _generate(self, key, payload=None):
        return self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/interest-invoices/",
            data=json.dumps(payload or {"financial_year": "FY2026-27"}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-interest-invoice",
            HTTP_USER_AGENT="interest-invoice-contract-test",
            REMOTE_ADDR="203.0.113.80",
            **self.auth,
        )

    def _configure_rate(self):
        from types import SimpleNamespace

        from sfpcl_credit.configurations.models import InterestRateConfig
        from sfpcl_credit.configurations.modules.interest_rate_configuration import activate
        from sfpcl_credit.identity.models import User

        self.fixture.fixture.owner.fixture.fixture._grant(
            self.actor,
            "config.interest_rate.manage",
            "communications.communication.send",
        )
        checker = User.objects.create(
            full_name="Invoice Rate Checker",
            email="invoice.rate.checker@sfpcl.example",
            status="active",
            primary_role=self.actor.primary_role,
        )
        row = InterestRateConfig.objects.create(
            version_number="RATE-INVOICE-1",
            rate_type="floating",
            effective_rate="9.2500",
            effective_from=date(2026, 4, 1),
            effective_to=date(2027, 3, 31),
            benchmark_name="RBL_BASE",
            spread_rate="1.2500",
            reset_frequency="annual",
            communication_required=False,
            board_approval_reference="BOARD-RATE-INVOICE-1",
            created_by_user=self.actor,
        )
        activate(
            actor=checker,
            request=SimpleNamespace(META={}, headers={}),
            interest_rate_config_id=row.pk,
            idempotency_key="activate-rate-invoice-1",
        )
