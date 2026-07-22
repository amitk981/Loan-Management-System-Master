import json
from datetime import datetime, timezone
from uuid import uuid4

from django.db import IntegrityError, transaction
from django.test import Client, TestCase


class DirectRepaymentPostingApiTests(TestCase):
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
            "finance.repayment.create",
            "finance.repayment.mark_sap_posted",
        )
        self.client = Client()
        self.auth = fixture.fixture.owner.fixture._auth(self.actor)

    def test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount, Repayment, RepaymentSapPostingObligation

        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        payload = {
            "repayment_source": "direct_farmer",
            "amount_received": "100000.00",
            "received_date": "2026-12-01",
            "payment_method": "neft",
            "bank_reference_number": " UTR-Direct-001 ",
            "remarks": "Confirmed against the bank statement.",
        }

        first = self._capture(payload, "repayment-key-001")
        replay = self._capture(payload, "repayment-key-001")

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        repayment = Repayment.objects.get()
        obligation = RepaymentSapPostingObligation.objects.get()
        self.assertEqual(repayment.loan_account_id, self.account.pk)
        self.assertEqual(repayment.member_id, self.account.member_id)
        self.assertEqual(str(repayment.amount_received), "100000.00")
        self.assertEqual(repayment.repayment_source, "direct_farmer")
        self.assertEqual(repayment.payment_method, "neft")
        self.assertEqual(repayment.bank_reference_number, "UTR-Direct-001")
        self.assertEqual(repayment.bank_reference_number_normalized, "UTR-DIRECT-001")
        self.assertEqual(repayment.allocation_status, "pending")
        self.assertEqual(repayment.sap_posting_status, "pending")
        self.assertEqual(obligation.repayment_id, repayment.pk)
        self.assertEqual(obligation.status, "pending")
        self.assertEqual(obligation.due_date.isoformat(), "2026-12-02")
        self.assertEqual(AuditLog.objects.filter(action="repayment.receipt_created").count(), 1)
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(
            replay.json()["data"],
            {
                "idempotency_replayed": True,
                "original_response": first.json()["data"],
            },
        )

    def test_invalid_duplicate_and_changed_requests_are_zero_write(self):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import Repayment, RepaymentSapPostingObligation

        valid = self._payload()
        invalid_cases = (
            ({**valid, "amount_received": "0"}, "zero-amount"),
            ({**valid, "amount_received": "-1.00"}, "negative-amount"),
            ({**valid, "amount_received": "1.001"}, "fractional-cent"),
            ({**valid, "payment_method": "cash"}, "cash-method"),
            ({**valid, "repayment_source": "subsidiary_deduction"}, "wrong-source"),
            ({**valid, "bank_reference_number": " "}, "blank-reference"),
            ({**valid, "remarks": " "}, "blank-remarks"),
            ({**valid, "unexpected": "value"}, "unknown-field"),
        )
        for payload, key in invalid_cases:
            with self.subTest(key=key):
                response = self._capture(payload, key)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(self._write_counts(), (0, 0, 0, 0))

        missing_key = self._capture(valid, "")
        self.assertEqual(missing_key.status_code, 400, missing_key.content)
        self.assertEqual(self._write_counts(), (0, 0, 0, 0))

        first = self._capture(valid, "stable-key")
        self.assertEqual(first.status_code, 200, first.content)
        retained_counts = self._write_counts()
        changed = self._capture({**valid, "amount_received": "90000.00"}, "stable-key")
        cross_loan = self._capture(valid, "stable-key", account=type("Account", (), {"pk": uuid4()})())
        duplicate_reference = self._capture(valid, "different-key")
        duplicate_case = self._capture(
            {**valid, "bank_reference_number": valid["bank_reference_number"].lower()},
            "different-case-key",
        )
        for response in (changed, cross_loan, duplicate_reference, duplicate_case):
            self.assertEqual(response.status_code, 409, response.content)
            self.assertEqual(self._write_counts(), retained_counts)

        self.assertEqual(Repayment.objects.count(), 1)
        self.assertEqual(RepaymentSapPostingObligation.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(notification_type="repayment_sap_posting_due").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="repayment.receipt_created").count(), 1)

    def test_capture_requires_effective_authority_and_serviceable_loan(self):
        payload = self._payload()
        user_fixture = self.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.owner.fixture
        role_only = user_fixture._user("credit_manager", "Credit Role Only")
        permission_only = user_fixture._user("field_officer", "Field With Finance Grant")
        user_fixture._grant(permission_only, "finance.repayment.create")

        for auth, expected in (
            ({}, 401),
            (auth_fixture._auth(role_only), 403),
            (auth_fixture._auth(permission_only), 403),
        ):
            response = self._capture(payload, str(uuid4()), actor_auth=auth)
            self.assertEqual(response.status_code, expected, response.content)
            self.assertEqual(self._write_counts(), (0, 0, 0, 0))

        for status in ("sanctioned", "closed"):
            type(self.account).objects.filter(pk=self.account.pk).update(loan_account_status=status)
            response = self._capture(payload, str(uuid4()))
            self.assertEqual(response.status_code, 409, response.content)
            self.assertEqual(self._write_counts(), (0, 0, 0, 0))

    def test_sap_posting_requires_permission_reference_and_records_safe_audit_truth(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount, Repayment

        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        created = self._capture(self._payload(), "posting-key")
        repayment_id = created.json()["data"]["repayment_id"]
        payload = {
            "sap_entry_reference": " SAP-RCPT-123 ",
            "sap_posted_at": "2026-12-02T10:00:00Z",
            "remarks": "Sensitive operator remark must not enter audit.",
        }

        role_only = self.fixture.fixture.owner.fixture.fixture._user(
            "credit_manager", "Posting Role Only"
        )
        denied = self._mark(repayment_id, payload, self.fixture.fixture.owner.fixture._auth(role_only))
        blank = self._mark(repayment_id, {**payload, "sap_entry_reference": " "})
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(blank.status_code, 400, blank.content)

        posted = self._mark(repayment_id, payload)
        repeated = self._mark(repayment_id, payload)
        self.assertEqual(posted.status_code, 200, posted.content)
        self.assertEqual(repeated.status_code, 409, repeated.content)
        repayment = Repayment.objects.select_related("sap_posting_obligation").get()
        obligation = repayment.sap_posting_obligation
        self.assertEqual(repayment.sap_posting_status, "posted")
        self.assertEqual(obligation.status, "posted")
        self.assertEqual(obligation.sap_entry_reference, "SAP-RCPT-123")
        self.assertEqual(obligation.posted_by_user_id, self.actor.pk)
        self.assertEqual(obligation.posted_at, datetime(2026, 12, 2, 10, tzinfo=timezone.utc))
        audit = AuditLog.objects.get(action="repayment.sap_posted")
        self.assertEqual(audit.actor_user_id, self.actor.pk)
        self.assertNotIn("SAP-RCPT-123", str(audit.new_value_json))
        self.assertNotIn("Sensitive operator remark", str(audit.new_value_json))
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)

    def test_database_rejects_nonpositive_receipts_and_duplicate_canonical_references(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import Repayment

        created = self._capture(self._payload(), "database-proof-key")
        self.assertEqual(created.status_code, 200, created.content)
        row = Repayment.objects.get()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Repayment.objects.filter(pk=row.pk).update(amount_received="0.00")

        second_audit = AuditLog.objects.create(
            actor_user=self.actor,
            action="repayment.receipt_created",
            entity_type="repayment",
            entity_id=uuid4(),
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Repayment.objects.create(
                loan_account=row.loan_account,
                member=row.member,
                amount_received="1.00",
                received_date=row.received_date,
                payment_method="neft",
                bank_reference_number=row.bank_reference_number.lower(),
                bank_reference_number_normalized=row.bank_reference_number_normalized,
                remarks="Second receipt.",
                captured_by_user=self.actor,
                idempotency_key_digest="1" * 64,
                payload_digest="2" * 64,
                capture_audit=second_audit,
            )

    @staticmethod
    def _payload():
        return {
            "repayment_source": "direct_farmer",
            "amount_received": "100000.00",
            "received_date": "2026-12-04",
            "payment_method": "rtgs",
            "bank_reference_number": "UTR-DIRECT-VALIDATION-001",
            "remarks": "Confirmed receipt.",
        }

    @staticmethod
    def _write_counts():
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import Repayment, RepaymentSapPostingObligation

        return (
            Repayment.objects.count(),
            RepaymentSapPostingObligation.objects.count(),
            Notification.objects.filter(notification_type="repayment_sap_posting_due").count(),
            AuditLog.objects.filter(action__startswith="repayment.").count(),
        )

    def _mark(self, repayment_id, payload, auth=None):
        return self.client.post(
            f"/api/v1/repayments/{repayment_id}/mark-sap-posted/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-repayment-posting-001",
            **(auth or self.auth),
        )

    def _capture(self, payload, key, account=None, actor_auth=None):
        account = account or self.account
        return self.client.post(
            f"/api/v1/loan-accounts/{account.pk}/repayments/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-repayment-001",
            HTTP_USER_AGENT="repayment contract test",
            REMOTE_ADDR="203.0.113.50",
            **(self.auth if actor_auth is None else actor_auth),
        )
