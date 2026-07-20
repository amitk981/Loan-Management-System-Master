import json
from datetime import date
from uuid import uuid4

from django.test import Client, TestCase
from django.utils import timezone


class MonthlyInterestAccrualApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_interest_invoice_api import InterestInvoiceApiTests

        fixture = InterestInvoiceApiTests(
            "test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.account.tenure_start_date = date(2026, 7, 1)
        self.account.save(update_fields=["tenure_start_date"])
        self.actor = fixture.actor
        fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.actor,
            "finance.accrual.create",
            "finance.accrual.bulk_generate",
        )
        self.client = Client()
        self.auth = fixture.auth

    def test_single_month_uses_server_owned_snapshots_and_creates_pending_sap_obligation(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount, RepaymentLedgerEntry

        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        ledger_before = list(RepaymentLedgerEntry.objects.values())

        response = self._create("accrual-create-001")

        self.assertEqual(response.status_code, 200, response.content)

        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.interest.models import AccrualEntry, AccrualSapPostingObligation

        accrual = AccrualEntry.objects.get()
        self.assertEqual(accrual.loan_account_id, self.account.pk)
        self.assertEqual(accrual.accrual_month, "2026-07")
        self.assertEqual(accrual.interest_period_start.isoformat(), "2026-07-01")
        self.assertEqual(accrual.interest_period_end.isoformat(), "2026-07-31")
        self.assertEqual(str(accrual.principal_base_amount), "400000.00")
        self.assertEqual(str(accrual.interest_rate), "9.2500")
        self.assertEqual(accrual.calculation_days, 31)
        self.assertEqual(accrual.day_count_basis, 365)
        self.assertEqual(str(accrual.interest_accrued_amount), "3142.47")
        self.assertEqual(accrual.rate_version_number, "RATE-INVOICE-1")
        self.assertEqual(accrual.calculation_version, "INV-CALC-1")
        self.assertEqual(accrual.posted_status, "pending")
        self.assertEqual(AccrualSapPostingObligation.objects.count(), 1)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.accrual.generated").count(), 1
        )
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(list(RepaymentLedgerEntry.objects.values()), ledger_before)
        self.assertEqual(response.json()["data"]["interest_accrued_amount"], "3142.47")
        self.assertEqual(response.json()["data"]["sap_posting_status"], "pending")

    def test_single_month_segments_an_approved_mid_month_rate_change(self):
        from types import SimpleNamespace

        from sfpcl_credit.configurations.models import InterestRateConfig
        from sfpcl_credit.configurations.modules.interest_rate_configuration import activate
        from sfpcl_credit.identity.models import User
        from sfpcl_credit.interest.models import AccrualEntry

        first = InterestRateConfig.objects.get(version_number="RATE-INVOICE-1")
        InterestRateConfig.objects.filter(pk=first.pk)._canonical_update(effective_to=None)
        checker = User.objects.create(
            full_name="Accrual Successor Rate Checker",
            email="accrual.successor.checker@sfpcl.example",
            status="active",
            primary_role=self.actor.primary_role,
        )
        successor = InterestRateConfig.objects.create(
            version_number="RATE-ACCRUAL-2",
            rate_type="floating",
            effective_rate="10.2500",
            effective_from=date(2026, 7, 16),
            benchmark_name="RBL_BASE",
            spread_rate="2.2500",
            reset_frequency="annual",
            communication_required=False,
            board_approval_reference="BOARD-RATE-ACCRUAL-2",
            created_by_user=self.actor,
        )
        activate(
            actor=checker,
            request=SimpleNamespace(META={}, headers={}),
            interest_rate_config_id=successor.pk,
            idempotency_key="activate-rate-accrual-2",
        )

        response = self._create("accrual-rate-segments")

        self.assertEqual(response.status_code, 200, response.content)
        accrual = AccrualEntry.objects.get()
        self.assertEqual(str(accrual.interest_accrued_amount), "3317.81")
        self.assertEqual(
            [segment["rate_version_number"] for segment in accrual.calculation_segments_json],
            ["RATE-INVOICE-1", "RATE-ACCRUAL-2"],
        )
        self.assertEqual(
            [segment["gross_interest_amount"] for segment in accrual.calculation_segments_json],
            [
                "1520.547945205479452054794521",
                "1797.260273972602739726027397",
            ],
        )

    def test_bulk_dry_run_reports_calculated_outcome_without_any_write(self):
        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import AccrualEntry, AccrualSapPostingObligation

        response = self.client.post(
            "/api/v1/accrual-entries/bulk-generate/",
            data=json.dumps(
                {
                    "accrual_month": "2026-07",
                    "dry_run": True,
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="accrual-bulk-dry-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["dry_run"], True)
        self.assertEqual(
            response.json()["data"]["results"],
            [
                {
                    "loan_account_id": str(self.account.pk),
                    "outcome": "created",
                    "persisted": False,
                    "interest_accrued_amount": "3142.47",
                }
            ],
        )
        self.assertEqual(AccrualEntry.objects.count(), 0)
        self.assertEqual(AccrualSapPostingObligation.objects.count(), 0)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action__startswith="interest.accrual").count(), 0
        )

    def test_authorised_sap_reference_capture_is_audited_and_exactly_replayable(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import AccrualEntry

        created = self._create("accrual-sap-create-001")
        accrual_id = created.json()["data"]["accrual_entry_id"]
        payload = {
            "posted_status": "posted",
            "sap_entry_reference": "SAP-ACCRUAL-2026-07-001",
            "remarks": "Posting evidence captured from the monthly finance process.",
        }

        posted = self.client.post(
            f"/api/v1/accrual-entries/{accrual_id}/mark-sap-posted/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="accrual-sap-post-001",
            **self.auth,
        )
        replay = self.client.post(
            f"/api/v1/accrual-entries/{accrual_id}/mark-sap-posted/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="accrual-sap-post-001",
            **self.auth,
        )
        generation_replay = self._create("accrual-sap-create-001")

        self.assertEqual(posted.status_code, 200, posted.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        accrual = AccrualEntry.objects.select_related("sap_posting_obligation").get()
        self.assertEqual(accrual.posted_status, "posted")
        self.assertEqual(accrual.sap_entry_reference, "SAP-ACCRUAL-2026-07-001")
        self.assertEqual(accrual.posted_by_user_id, self.actor.pk)
        self.assertEqual(accrual.sap_posting_obligation.status, "posted")
        self.assertIsNotNone(accrual.sap_posting_obligation.resolved_at)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.accrual.sap_status_recorded").count(), 1
        )
        posting_audit = AuditLog.objects.get(action="interest.accrual.sap_status_recorded")
        self.assertNotIn("SAP-ACCRUAL-2026-07-001", str(posting_audit.new_value_json))
        self.assertNotIn("monthly finance process", str(posting_audit.new_value_json))
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(replay.json()["data"]["original_response"], posted.json()["data"])
        self.assertEqual(
            generation_replay.json()["data"]["original_response"],
            created.json()["data"],
        )

    def test_replay_duplicate_client_money_and_missing_configuration_fail_closed(self):
        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import (
            AccrualEntry,
            AccrualSapPostingObligation,
            InterestInvoiceConfiguration,
        )

        missing_config = self._create(
            "accrual-missing-config", {"accrual_month": "2027-04"}
        )
        first = self._create("accrual-replay-001")
        replay = self._create("accrual-replay-001")
        duplicate = self._create("accrual-replay-duplicate")
        client_money = self._create(
            "accrual-client-money",
            {"accrual_month": "2026-08", "interest_accrued_amount": "1.00"},
        )
        InterestInvoiceConfiguration.objects.create(
            version_number="INV-CALC-NO-RATE",
            effective_from=date(2028, 4, 1),
            effective_to=date(2029, 3, 31),
            calculation_method="simple_daily",
            day_count_basis=365,
            monetary_rounding_mode="half_up",
            monetary_precision="0.01",
            rounding_application_boundary="whole_decision",
            tax_rate="0.0000",
            fixed_fee_amount="0.00",
            owner_role_codes=["accounts_head"],
            status="active",
            approved_by_user=self.actor,
        )
        missing_rate = self._create(
            "accrual-missing-rate", {"accrual_month": "2028-04"}
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(duplicate.status_code, 409, duplicate.content)
        self.assertEqual(client_money.status_code, 400, client_money.content)
        self.assertIn(
            "interest_accrued_amount", client_money.json()["error"]["field_errors"]
        )
        self.assertEqual(missing_config.status_code, 409, missing_config.content)
        self.assertEqual(missing_rate.status_code, 409, missing_rate.content)
        self.assertEqual(AccrualEntry.objects.count(), 1)
        self.assertEqual(AccrualSapPostingObligation.objects.count(), 1)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.accrual.generated").count(), 1
        )

    def test_post_closure_and_permission_scope_denials_are_zero_write(self):
        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import AccrualEntry, AccrualSapPostingObligation

        self.account.closed_at = timezone.make_aware(
            timezone.datetime(2026, 7, 15, 12, 0, 0)
        )
        self.account.save(update_fields=["closed_at"])
        closed = self._create("accrual-closed-001")

        root_fixture = self.fixture.fixture.fixture.owner.fixture.fixture
        outsider = root_fixture._user("sales", "Accrual scope outsider")
        root_fixture._grant(outsider, "finance.accrual.create")
        outsider_auth = self.fixture.fixture.fixture.owner.fixture._auth(outsider)
        outside_scope = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/accrual-entries/",
            data=json.dumps({"accrual_month": "2026-08"}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="accrual-scope-denial",
            **outsider_auth,
        )

        self.assertEqual(closed.status_code, 409, closed.content)
        self.assertEqual(outside_scope.status_code, 403, outside_scope.content)
        self.assertEqual(AccrualEntry.objects.count(), 0)
        self.assertEqual(AccrualSapPostingObligation.objects.count(), 0)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action__startswith="interest.accrual").count(), 0
        )

    def test_bulk_keeps_per_loan_success_when_another_selected_loan_fails(self):
        from sfpcl_credit.interest.models import AccrualEntry, AccrualSapPostingObligation

        inaccessible_id = str(uuid4())
        response = self.client.post(
            "/api/v1/accrual-entries/bulk-generate/",
            data=json.dumps(
                {
                    "accrual_month": "2026-07",
                    "loan_account_ids": [str(self.account.pk), inaccessible_id],
                    "dry_run": False,
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="accrual-bulk-create-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"]["results"],
            [
                {
                    "loan_account_id": str(self.account.pk),
                    "outcome": "created",
                    "persisted": True,
                    "interest_accrued_amount": "3142.47",
                },
                {
                    "loan_account_id": inaccessible_id,
                    "outcome": "failed",
                    "persisted": False,
                    "reason": "inaccessible",
                },
            ],
        )
        self.assertEqual(AccrualEntry.objects.count(), 1)
        self.assertEqual(AccrualSapPostingObligation.objects.count(), 1)

    def test_financial_year_rate_change_and_leap_month_use_historical_versions(self):
        from types import SimpleNamespace

        from sfpcl_credit.configurations.models import InterestRateConfig
        from sfpcl_credit.configurations.modules.interest_rate_configuration import activate
        from sfpcl_credit.identity.models import User
        from sfpcl_credit.interest.models import AccrualEntry, InterestInvoiceConfiguration

        InterestInvoiceConfiguration.objects.create(
            version_number="INV-CALC-2",
            effective_from=date(2027, 4, 1),
            effective_to=date(2028, 3, 31),
            calculation_method="simple_daily",
            day_count_basis=365,
            monetary_rounding_mode="half_up",
            monetary_precision="0.01",
            rounding_application_boundary="whole_decision",
            tax_rate="0.0000",
            fixed_fee_amount="0.00",
            owner_role_codes=["accounts_head"],
            status="active",
            approved_by_user=self.actor,
        )
        checker = User.objects.create(
            full_name="Accrual Rate Checker",
            email="accrual.rate.checker@sfpcl.example",
            status="active",
            primary_role=self.actor.primary_role,
        )
        next_rate = InterestRateConfig.objects.create(
            version_number="RATE-ACCRUAL-2",
            rate_type="floating",
            effective_rate="10.0000",
            effective_from=date(2027, 4, 1),
            effective_to=date(2028, 3, 31),
            benchmark_name="RBL_BASE",
            spread_rate="2.0000",
            reset_frequency="annual",
            communication_required=False,
            board_approval_reference="BOARD-RATE-ACCRUAL-2",
            created_by_user=self.actor,
        )
        activate(
            actor=checker,
            request=SimpleNamespace(META={}, headers={}),
            interest_rate_config_id=next_rate.pk,
            idempotency_key="activate-rate-accrual-2",
        )

        march = self._create("accrual-rate-march", {"accrual_month": "2027-03"})
        april = self._create("accrual-rate-april", {"accrual_month": "2027-04"})
        leap_february = self._create(
            "accrual-rate-leap-february", {"accrual_month": "2028-02"}
        )

        self.assertEqual(march.status_code, 200, march.content)
        self.assertEqual(april.status_code, 200, april.content)
        self.assertEqual(leap_february.status_code, 200, leap_february.content)
        march_row = AccrualEntry.objects.get(accrual_month="2027-03")
        march_snapshot = (
            march_row.rate_version_number,
            march_row.interest_rate,
            march_row.interest_accrued_amount,
        )
        self.assertEqual(march_snapshot[0], "RATE-INVOICE-1")
        self.assertEqual(f"{march_snapshot[1]:.4f}", "9.2500")
        self.assertEqual(f"{march_snapshot[2]:.2f}", "3142.47")
        self.assertEqual(april.json()["data"]["rate_version_number"], "RATE-ACCRUAL-2")
        self.assertEqual(april.json()["data"]["interest_accrued_amount"], "3287.67")
        self.assertEqual(leap_february.json()["data"]["calculation_days"], 29)
        self.assertEqual(
            leap_february.json()["data"]["interest_accrued_amount"], "3178.08"
        )
        march_row.refresh_from_db()
        self.assertEqual(
            (
                march_row.rate_version_number,
                march_row.interest_rate,
                march_row.interest_accrued_amount,
            ),
            march_snapshot,
        )
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            AccrualEntry.objects.filter(pk=march_row.pk).update(
                interest_accrued_amount="1.00"
            )

    def test_principal_snapshot_is_resolved_as_of_month_end_not_from_later_repayment(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            Repayment,
            RepaymentAllocation,
            RepaymentLedgerEntry,
        )

        repayment_id = uuid4()
        allocation_id = uuid4()
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
            amount_received="100000.00",
            received_date=date(2026, 8, 15),
            payment_method="neft",
            bank_reference_number="ACCRUAL-LATER-REPAYMENT",
            bank_reference_number_normalized="ACCRUAL-LATER-REPAYMENT",
            remarks="Canonical later repayment fixture.",
            allocation_status="allocated",
            sap_posting_status="posted",
            captured_by_user=self.actor,
            idempotency_key_digest="accrual-later-repayment-capture",
            payload_digest="accrual-later-repayment-capture-payload",
            capture_audit=capture_audit,
        )
        allocation_audit = AuditLog.objects.create(
            actor_user=self.actor,
            action="repayment.allocated",
            entity_type="repayment_allocation",
            entity_id=allocation_id,
        )
        allocation = RepaymentAllocation.objects.create(
            repayment_allocation_id=allocation_id,
            repayment=repayment,
            loan_account=self.account,
            allocated_to_principal="100000.00",
            allocated_to_interest="0.00",
            allocated_to_charges="0.00",
            unallocated_amount="0.00",
            principal_before="400000.00",
            principal_after="300000.00",
            interest_before="0.00",
            interest_after="0.00",
            charges_before="0.00",
            charges_after="0.00",
            total_before="400000.00",
            total_after="300000.00",
            allocation_rule="principal_first",
            allocation_rule_version="v1",
            decision_reason="Canonical principal-first allocation fixture.",
            loan_status_before="active",
            loan_status_after="partially_repaid",
            allocated_by_user=self.actor,
            allocation_audit=allocation_audit,
        )
        RepaymentLedgerEntry.objects.create(
            allocation=allocation,
            loan_account=self.account,
            transaction_date=date(2026, 8, 15),
            credit_amount="100000.00",
            principal_balance="300000.00",
            interest_balance="0.00",
            charges_balance="0.00",
            total_outstanding="300000.00",
            actor_user=self.actor,
            actor_display_name=self.actor.full_name,
        )
        self.account.principal_outstanding = "300000.00"
        self.account.total_outstanding = "300000.00"
        self.account.loan_account_status = "partially_repaid"
        self.account.save(
            update_fields=[
                "principal_outstanding",
                "total_outstanding",
                "loan_account_status",
            ]
        )

        july = self._create("accrual-principal-july", {"accrual_month": "2026-07"})
        september = self._create(
            "accrual-principal-september", {"accrual_month": "2026-09"}
        )

        self.assertEqual(july.status_code, 200, july.content)
        self.assertEqual(september.status_code, 200, september.content)
        self.assertEqual(july.json()["data"]["principal_base_amount"], "400000.00")
        self.assertEqual(july.json()["data"]["interest_accrued_amount"], "3142.47")
        self.assertEqual(september.json()["data"]["principal_base_amount"], "300000.00")
        self.assertEqual(
            september.json()["data"]["interest_accrued_amount"], "2280.82"
        )

    def _create(self, key, payload=None):
        return self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/accrual-entries/",
            data=json.dumps(payload or {"accrual_month": "2026-07"}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-interest-accrual",
            HTTP_USER_AGENT="interest-accrual-contract-test",
            REMOTE_ADDR="203.0.113.81",
            **self.auth,
        )
