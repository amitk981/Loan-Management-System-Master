import json
from tempfile import TemporaryDirectory
from uuid import uuid4

from django.test import Client, TestCase, override_settings
from django.utils import timezone

from sfpcl_credit.identity.models import PortalAccount, Role, User
from sfpcl_credit.tests.api_contracts import assert_success_envelope


class PortalLoanAccountsApiTests(TestCase):
    password = "PortalServicing123!"

    def setUp(self):
        self.document_storage = TemporaryDirectory()
        self.storage_override = override_settings(
            DOCUMENT_STORAGE_ROOT=self.document_storage.name
        )
        self.storage_override.enable()
        self.addCleanup(self.storage_override.disable)
        self.addCleanup(self.document_storage.cleanup)

        from sfpcl_credit.tests.test_repayment_allocation_api import RepaymentAllocationApiTests

        owner = RepaymentAllocationApiTests(
            "test_partial_receipt_reduces_principal_and_appends_immutable_evidence"
        )
        owner.setUp()
        self.owner = owner
        self.account = owner.account
        self.client = Client()
        role, _ = Role.objects.get_or_create(
            role_code="borrower_portal_user",
            defaults={"role_name": "Borrower Portal User", "is_system_role": True, "status": "active"},
        )
        self.portal_user = User.objects.create(
            full_name=self.account.member.display_name,
            email="portal.servicing@sfpcl.example",
            status="active",
            primary_role=role,
        )
        self.portal_user.set_password(self.password)
        self.portal_user.save()
        self.portal_account = PortalAccount.objects.create(
            member=self.account.member,
            user=self.portal_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )

    def test_owner_list_detail_and_nested_reads_project_only_borrower_safe_truth(self):
        captured = self.owner.fixture._capture(self.owner.fixture._payload(), "portal-posted")
        repayment_id = captured.json()["data"]["repayment_id"]
        self.owner._schedule("400000.00")
        self.owner._ensure_posted(repayment_id)
        allocated = self.owner._allocate(repayment_id)
        self.assertEqual(allocated.status_code, 200, allocated.content)
        pending_payload = {
            **self.owner.fixture._payload(),
            "amount_received": "123.00",
            "bank_reference_number": "PENDING-PORTAL-HIDDEN",
        }
        pending = self.owner.fixture._capture(pending_payload, "pending-portal-hidden")
        self.assertEqual(pending.status_code, 200, pending.content)
        auth = self._portal_auth()

        listing = self.client.get("/api/v1/portal/loan-accounts/?page=1&page_size=20", headers=auth)
        detail = self.client.get(f"/api/v1/portal/loan-accounts/{self.account.pk}/", headers=auth)
        schedule = self.client.get(f"/api/v1/portal/loan-accounts/{self.account.pk}/schedule/?page=1&page_size=20", headers=auth)
        repayments = self.client.get(f"/api/v1/portal/loan-accounts/{self.account.pk}/repayments/?page=1&page_size=20", headers=auth)
        invoices = self.client.get(f"/api/v1/portal/loan-accounts/{self.account.pk}/invoices/?page=1&page_size=20", headers=auth)

        for response in (listing, detail, schedule, repayments, invoices):
            self.assertEqual(response.status_code, 200, response.content)
            assert_success_envelope(self, response.json())
        self.assertEqual(listing.json()["data"][0]["loan_account_id"], str(self.account.pk))
        self.assertEqual(detail.json()["data"]["principal_outstanding"], "300000.00")
        self.assertEqual(schedule.json()["data"][0]["paid_principal"], "100000.00")
        self.assertEqual(len(repayments.json()["data"]), 1)
        history = repayments.json()["data"][0]
        self.assertEqual(history["reference"], self.owner.fixture._payload()["bank_reference_number"])
        self.assertEqual(history["allocated_to_principal"], "100000.00")
        self.assertNotIn("PENDING-PORTAL-HIDDEN", json.dumps(repayments.json()))
        self.assertEqual(invoices.json()["data"], [])
        forbidden = ("actor", "captured_by", "remarks", "sap", "exception", "provider")
        serialized = json.dumps([response.json() for response in (listing, detail, schedule, repayments, invoices)]).lower()
        for field in forbidden:
            self.assertNotIn(field, serialized)

    def test_direct_instructions_are_masked_read_only_and_server_owned(self):
        from datetime import date, datetime, timezone as datetime_timezone
        from sfpcl_credit.configurations.models import RepaymentInstructionVersion

        RepaymentInstructionVersion.objects.create(
            version="PORTAL-REPAYMENT-2026-01",
            beneficiary_name="SFPCL Collections",
            bank_name="Approved Bank",
            account_number_last4="4321",
            ifsc="APPR0001234",
            effective_from=date(2026, 4, 1),
            approved_by_user=self.owner.actor,
            approved_at=datetime(2026, 4, 1, tzinfo=datetime_timezone.utc),
        )
        response = self.client.get(
            f"/api/v1/portal/loan-accounts/{self.account.pk}/direct-instructions/",
            headers=self._portal_auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"], {
            "available": True,
            "projection_version": "PORTAL-REPAYMENT-2026-01",
            "approved_at": "2026-04-01T00:00:00Z",
            "beneficiary_name": "SFPCL Collections",
            "bank_name": "Approved Bank",
            "account_number_masked": "********4321",
            "ifsc": "APPR0001234",
            "required_narration": self.account.loan_account_number,
            "amount_due": f"{self.account.total_outstanding:.2f}",
            "proof_submission_enabled": False,
            "available_actions": [],
            "disclaimer": "Repayment will be updated in the portal after SFPCL verifies the bank receipt and posts the repayment in its records.",
        })

    def test_foreign_guessed_staff_claimed_member_and_inactive_portal_are_nondisclosing(self):
        from sfpcl_credit.members.models import Member
        auth = self._portal_auth()
        guessed = uuid4()
        foreign_member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Foreign Portal Test Member",
            display_name="Foreign Portal Test Member",
            folio_number="FOLIO-FOREIGN-PORTAL",
            membership_status="active",
            pan_encrypted="encrypted-foreign-pan",
            pan_hash="foreign-portal-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        type(self.account).objects.filter(pk=self.account.pk).update(
            member=foreign_member
        )
        urls = tuple(
            endpoint.format(account_id=account_id)
            for account_id in (guessed, self.account.pk)
            for endpoint in (
                "/api/v1/portal/loan-accounts/{account_id}/",
                "/api/v1/portal/loan-accounts/{account_id}/schedule/",
                "/api/v1/portal/loan-accounts/{account_id}/repayments/",
                "/api/v1/portal/loan-accounts/{account_id}/invoices/",
                "/api/v1/portal/loan-accounts/{account_id}/direct-instructions/",
            )
        )
        for url in urls:
            response = self.client.get(url, headers=auth)
            self.assertEqual(response.status_code, 404, response.content)
            self.assertEqual(response.json()["error"]["code"], "NOT_FOUND")

        claimed = self.client.get(
            f"/api/v1/portal/loan-accounts/?member_id={uuid4()}", headers=auth
        )
        self.assertEqual(claimed.status_code, 403, claimed.content)

        staff = self.client.get("/api/v1/portal/loan-accounts/", **self.owner.auth)
        self.assertEqual(staff.status_code, 403, staff.content)
        self.portal_account.status = PortalAccount.STATUS_SUSPENDED
        self.portal_account.save(update_fields=["status"])
        locked = self.client.get("/api/v1/portal/loan-accounts/", headers=auth)
        self.assertIn(locked.status_code, (401, 403), locked.content)

    def _portal_auth(self):
        response = self.client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": self.portal_user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}
