from datetime import timedelta

from django.db import connection
from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.communications.models import CommunicationDeliveryOutbox
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.disbursements.models import (
    BankTransfer,
    Disbursement,
    DisbursementAdviceIntent,
)
from sfpcl_credit.identity.models import AuditLog, PortalAccount, Role, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import assert_success_envelope


class PortalDisbursementStatusApiTests(TestCase):
    password = "PortalDisbursement123!"

    def setUp(self):
        from sfpcl_credit.tests.test_disbursement_advice_api import (
            DisbursementAdviceApiTests,
        )

        owner = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        owner.setUp()
        sent = owner._post()
        self.assertEqual(sent.status_code, 200, sent.content)
        self.owner = owner
        self.row = owner.row
        self.row.refresh_from_db()
        portal_role, _ = Role.objects.get_or_create(
            role_code="borrower_portal_user",
            defaults={
                "role_name": "Borrower Portal User",
                "is_system_role": True,
                "status": "active",
            },
        )
        self.portal_user = User.objects.create(
            full_name=self.row.member.display_name,
            email="portal.disbursement@sfpcl.example",
            status="active",
            primary_role=portal_role,
        )
        self.portal_user.set_password(self.password)
        self.portal_user.save()
        self.portal_account = PortalAccount.objects.create(
            member=self.row.member,
            user=self.portal_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        self.client = Client()

    def test_own_completed_disbursement_returns_only_borrower_safe_current_truth(self):
        auth = self._portal_auth()
        audit_count = AuditLog.objects.count()

        response = self.client.get(self._status_url(), headers=auth)

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(
            set(data),
            {
                "loan_application_id",
                "loan_account_id",
                "status_code",
                "status_label",
                "sanctioned_amount",
                "disbursement_amount",
                "destination_account_last4",
                "disbursed_at",
                "bank_reference_last4",
                "advice_available",
                "timeline",
            },
        )
        self.assertEqual(data["loan_application_id"], str(self.row.loan_application_id))
        self.assertEqual(data["loan_account_id"], str(self.row.loan_account_id))
        self.assertEqual(data["status_code"], "disbursed")
        self.assertEqual(data["status_label"], "Loan amount transferred.")
        self.assertEqual(data["sanctioned_amount"], f"{self.row.loan_account.sanctioned_amount:.2f}")
        self.assertEqual(data["disbursement_amount"], f"{self.row.disbursement_amount:.2f}")
        self.assertEqual(data["destination_account_last4"], "4321")
        self.assertTrue(data["disbursed_at"].endswith("Z"))
        self.assertEqual(data["bank_reference_last4"], "9876")
        self.assertTrue(data["advice_available"])
        self.assertEqual(
            [item["code"] for item in data["timeline"]],
            [
                "documentation_complete",
                "sap_setup",
                "payment_initiated",
                "cfc_authorisation",
                "transfer_completed",
                "advice_issued",
            ],
        )
        self.assertTrue(all(set(item) == {"code", "label", "status", "completed_at"} for item in data["timeline"]))
        self.assertEqual(AuditLog.objects.count(), audit_count)
        serialized = str(response.json()).lower()
        for forbidden in (
            "rbl-advice-9876",
            "borrower.advice@example.com",
            "sap_customer_code",
            "ifsc",
            "actor",
            "evidence",
            "checksum",
            "communication_id",
            "outbox",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_stale_success_evidence_falls_back_to_safe_blocked_status(self):
        BankTransfer.objects.filter(disbursement=self.row).update(
            amount=self.row.disbursement_amount + 1
        )

        response = self.client.get(self._status_url(), headers=self._portal_auth())

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status_code"], "disbursement_blocked")
        self.assertEqual(data["status_label"], "Action required / SFPCL review needed.")
        self.assertEqual(data["loan_account_id"], str(self.row.loan_account_id))
        self.assertIsNone(data["disbursement_amount"])
        self.assertIsNone(data["destination_account_last4"])
        self.assertIsNone(data["disbursed_at"])
        self.assertIsNone(data["bank_reference_last4"])
        self.assertFalse(data["advice_available"])
        self.assertTrue(all(item["status"] != "complete" for item in data["timeline"]))

    def test_advice_capability_replaces_then_consumes_once_with_safe_audits(self):
        auth = self._portal_auth()
        first = self.client.post(
            self._capability_url(), data={}, content_type="application/json", headers=auth
        )
        second = self.client.post(
            self._capability_url(), data={}, content_type="application/json", headers=auth
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(set(second.json()["data"]), {"download_url", "expires_at"})
        self.assertNotEqual(
            first.json()["data"]["download_url"], second.json()["data"]["download_url"]
        )

        replaced = self.client.get(first.json()["data"]["download_url"], headers=auth)
        downloaded = self.client.get(second.json()["data"]["download_url"], headers=auth)
        replay = self.client.get(second.json()["data"]["download_url"], headers=auth)

        self.assertEqual(replaced.status_code, 404, replaced.content)
        self.assertEqual(downloaded.status_code, 200, downloaded.content)
        communication = self.row.disbursement_advice_communication
        self.assertEqual(
            downloaded.content,
            f"{communication.subject_snapshot}\n\n{communication.body_snapshot}\n".encode(),
        )
        self.assertEqual(downloaded["X-Content-Type-Options"], "nosniff")
        self.assertEqual(downloaded["Cache-Control"], "no-store")
        self.assertIn("attachment;", downloaded["Content-Disposition"])
        self.assertEqual(replay.status_code, 404, replay.content)
        audits = list(
            AuditLog.objects.filter(action="portal.document.downloaded").order_by(
                "created_at", "audit_log_id"
            )
        )
        self.assertEqual(
            [row.new_value_json["outcome"] for row in audits],
            ["issued", "issued", "denied", "accepted", "denied"],
        )
        serialized = str([row.new_value_json for row in audits]).lower()
        for forbidden in (
            "borrower.advice@example.com",
            "rbl-advice-9876",
            communication.subject_snapshot.lower(),
            communication.body_snapshot.lower(),
            "token",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_legacy_partial_advice_is_not_current_or_downloadable(self):
        auth = self._portal_auth()
        issued = self.client.post(
            self._capability_url(), data={}, content_type="application/json", headers=auth
        )
        self.assertEqual(issued.status_code, 200, issued.content)
        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        attempt = outbox.accepted_provider_attempt
        attempt.adapter_kind = "legacy:pre-outbox"
        attempt.evidence_digest = CommunicationDispatcher._attempt_digest(
            {
                "outbox": outbox,
                "advice_intent_id": attempt.advice_intent_id,
                "communication_id": attempt.communication_id,
                "idempotency_key": attempt.idempotency_key,
                "payload_digest": attempt.payload_digest,
                "adapter_kind": attempt.adapter_kind,
                "outcome": attempt.outcome,
                "provider_external_message_id": attempt.provider_external_message_id,
                "provider_delivery_status": attempt.provider_delivery_status,
                "provider_accepted_at": attempt.provider_accepted_at,
                "attempted_at": attempt.attempted_at,
            }
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE communication_provider_attempts "
                "SET adapter_kind = %s, evidence_digest = %s "
                "WHERE provider_attempt_id = %s",
                [attempt.adapter_kind, attempt.evidence_digest, attempt.pk.hex],
            )
            self.assertEqual(cursor.rowcount, 1)
        CommunicationDeliveryOutbox.objects.filter(pk=outbox.pk).update(
            template_provenance_status="legacy_partial",
            template_provenance_origin="legacy_0005",
            content_template_id=None,
            template_code_snapshot=None,
            template_name_snapshot=None,
            template_type_snapshot=None,
            template_language_code_snapshot=None,
            template_audience_snapshot=None,
            template_version_snapshot=None,
            template_approval_status_snapshot=None,
            template_effective_from_snapshot=None,
            template_effective_to_snapshot=None,
            template_variables_snapshot=None,
            subject_template_snapshot=None,
            body_template_snapshot=None,
            template_checksum_sha256=None,
        )

        status = self.client.get(self._status_url(), headers=auth)
        download = self.client.get(issued.json()["data"]["download_url"], headers=auth)

        self.assertEqual(status.status_code, 200, status.content)
        self.assertFalse(status.json()["data"]["advice_available"])
        advice_stage = next(
            row
            for row in status.json()["data"]["timeline"]
            if row["code"] == "advice_issued"
        )
        self.assertNotEqual(advice_stage["status"], "complete")
        self.assertEqual(download.status_code, 404, download.content)

    def test_status_permission_query_and_nondisclosure_matrix(self):
        auth = self._portal_auth()
        missing_url = (
            "/api/v1/portal/applications/10000000-0000-0000-0000-000000000099/"
            "disbursement-status/"
        )
        missing = self.client.get(missing_url, headers=auth)
        unknown_query = self.client.get(f"{self._status_url()}?include=evidence", headers=auth)
        staff = self.client.get(
            self._status_url(),
            **self.owner.owner.owner.fixture._auth(self.owner.actor),
        )

        other_member = Member.objects.create(
            member_number="M-PORTAL-OTHER",
            member_type="individual_farmer",
            legal_name="Other Portal Member",
            display_name="Other Portal Member",
            folio_number="FOL-PORTAL-OTHER",
            membership_status="active",
            pan_encrypted="other-pan-token",
            pan_hash="other-portal-pan-hash",
            aadhaar_encrypted="other-aadhaar-token",
            aadhaar_hash="other-portal-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        other_user = User.objects.create(
            full_name=other_member.display_name,
            email="other.portal.disbursement@sfpcl.example",
            status="active",
            primary_role=self.portal_user.primary_role,
        )
        other_user.set_password(self.password)
        other_user.save()
        PortalAccount.objects.create(
            member=other_member,
            user=other_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        cross = self.client.get(self._status_url(), headers=self._auth_for(other_user))

        self.portal_account.status = PortalAccount.STATUS_SUSPENDED
        self.portal_account.save(update_fields=["status"])
        inactive = self.client.get(self._status_url(), headers=auth)

        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json()["error"]["code"], "NOT_FOUND")
        self.assertEqual(cross.status_code, 404)
        self.assertEqual(cross.json()["error"], missing.json()["error"])
        self.assertEqual(staff.status_code, 403)
        self.assertEqual(staff.json()["error"]["code"], "FORBIDDEN")
        self.assertEqual(unknown_query.status_code, 400)
        self.assertEqual(unknown_query.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(inactive.status_code, 401)

    def test_changed_advice_finalization_ledger_removes_availability_and_capability(self):
        DisbursementAdviceIntent.objects.filter(disbursement=self.row).update(
            delivery_evidence_digest="0" * 64
        )

        status = self.client.get(self._status_url(), headers=self._portal_auth())
        capability = self.client.post(
            self._capability_url(),
            data={},
            content_type="application/json",
            headers=self._portal_auth(),
        )

        self.assertEqual(status.status_code, 200, status.content)
        self.assertEqual(status.json()["data"]["status_code"], "disbursed")
        self.assertFalse(status.json()["data"]["advice_available"])
        self.assertEqual(status.json()["data"]["timeline"][-1]["status"], "pending")
        self.assertEqual(capability.status_code, 404, capability.content)

    def test_capability_rejects_nonempty_body_tamper_and_persisted_expiry(self):
        auth = self._portal_auth()
        invalid_body = self.client.post(
            self._capability_url(),
            data={"communication_id": str(self.row.disbursement_advice_communication_id)},
            content_type="application/json",
            headers=auth,
        )
        issued = self.client.post(
            self._capability_url(), data={}, content_type="application/json", headers=auth
        )
        download_url = issued.json()["data"]["download_url"]
        tampered = self.client.get(
            f"{download_url[:-1]}{'a' if download_url[-1] != 'a' else 'b'}", headers=auth
        )
        CommunicationDeliveryOutbox.objects.filter(
            communication_id=self.row.disbursement_advice_communication_id
        ).update(portal_capability_expires_at=timezone.now() - timedelta(seconds=1))
        expired = self.client.get(download_url, headers=auth)

        self.assertEqual(invalid_body.status_code, 400, invalid_body.content)
        self.assertEqual(invalid_body.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(tampered.status_code, 404, tampered.content)
        self.assertEqual(expired.status_code, 404, expired.content)
        self.assertEqual(tampered.json()["error"], expired.json()["error"])

    def _status_url(self):
        return (
            f"/api/v1/portal/applications/{self.row.loan_application_id}/"
            "disbursement-status/"
        )

    def _capability_url(self):
        return (
            f"/api/v1/portal/applications/{self.row.loan_application_id}/"
            "disbursement-advice/download-capability/"
        )

    def _portal_auth(self):
        return self._auth_for(self.portal_user)

    def _auth_for(self, user):
        response = self.client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


class PortalDisbursementStageApiTests(TestCase):
    password = "PortalDisbursement123!"

    def test_sanctioned_application_before_loan_account_stays_at_finance_setup(self):
        from sfpcl_credit.tests.test_portal_documentation_actions_api import (
            PortalDocumentationActionsApiTests,
        )

        owner = PortalDocumentationActionsApiTests(
            "test_own_sanctioned_application_returns_ordered_borrower_safe_actions"
        )
        owner.setUp()
        response = owner.client.get(
            f"/api/v1/portal/applications/{owner.application.pk}/disbursement-status/",
            headers=owner._portal_auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status_code"], "finance_setup_pending")
        self.assertIsNone(data["loan_account_id"])
        self.assertTrue(data["sanctioned_amount"])
        self.assertTrue(all(item["status"] == "pending" for item in data["timeline"]))

    def test_successful_transfer_without_sent_advice_is_disbursed_but_unavailable(self):
        from sfpcl_credit.tests.test_disbursement_transfer_success_api import (
            DisbursementTransferSuccessApiTests,
        )

        owner = DisbursementTransferSuccessApiTests(
            "test_public_success_records_transfer_and_activates_exact_loan_atomically"
        )
        owner.setUp()
        transferred = owner._post(
            bank_reference_number="RBL-PORTAL-2468", disbursed_at=timezone.now()
        )
        self.assertEqual(transferred.status_code, 200, transferred.content)
        row = Disbursement.objects.select_related("member").get(pk=owner.owner.disbursement_id)
        portal_user = self._portal_user(row.member)

        response = Client().get(
            self._status_url(row), headers=self._portal_auth(portal_user)
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status_code"], "disbursed")
        self.assertEqual(data["bank_reference_last4"], "2468")
        self.assertFalse(data["advice_available"])
        self.assertEqual(data["timeline"][-1]["status"], "pending")

    def test_initiated_payment_waiting_for_cfc_cannot_skip_forward(self):
        from sfpcl_credit.tests.test_disbursement_authorisation_api import (
            DisbursementAuthorisationApiTests,
        )

        owner = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        owner.setUp()
        row = Disbursement.objects.select_related("member", "loan_account").get(
            pk=owner.disbursement_id
        )
        portal_user = self._portal_user(row.member)

        response = Client().get(
            self._status_url(row), headers=self._portal_auth(portal_user)
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status_code"], "cfc_authorisation_pending")
        self.assertEqual(data["status_label"], "Payment approval in progress.")
        self.assertEqual(data["sanctioned_amount"], f"{row.loan_account.sanctioned_amount:.2f}")
        self.assertIsNone(data["disbursement_amount"])
        self.assertEqual(
            [item["status"] for item in data["timeline"]],
            ["complete", "complete", "complete", "pending", "pending", "pending"],
        )
        self.assertIsNone(data["disbursed_at"])
        self.assertIsNone(data["bank_reference_last4"])
        self.assertFalse(data["advice_available"])

    def test_current_cfc_rejection_exposes_only_safe_blocked_copy(self):
        from sfpcl_credit.tests.test_disbursement_authorisation_api import (
            DisbursementAuthorisationApiTests,
        )

        owner = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        owner.setUp()
        rejected = owner._post("rejected", "Beneficiary details require correction.")
        self.assertEqual(rejected.status_code, 200, rejected.content)
        row = Disbursement.objects.select_related("member", "loan_account").get(
            pk=owner.disbursement_id
        )
        portal_user = self._portal_user(row.member)

        response = Client().get(
            self._status_url(row), headers=self._portal_auth(portal_user)
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status_code"], "disbursement_blocked")
        self.assertEqual(data["status_label"], "Action required / SFPCL review needed.")
        self.assertEqual(
            [item["status"] for item in data["timeline"]],
            ["complete", "complete", "complete", "blocked", "pending", "pending"],
        )
        self.assertNotIn("beneficiary", str(response.json()).lower())
        self.assertNotIn("rejected", str(response.json()).lower())

    def _portal_user(self, member):
        role, _ = Role.objects.get_or_create(
            role_code="borrower_portal_user",
            defaults={"role_name": "Borrower Portal User", "is_system_role": True, "status": "active"},
        )
        user = User.objects.create(
            full_name=member.display_name,
            email="portal.stage@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save()
        PortalAccount.objects.create(
            member=member,
            user=user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        return user

    def _portal_auth(self, user):
        client = Client()
        response = client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

    @staticmethod
    def _status_url(row):
        return f"/api/v1/portal/applications/{row.loan_application_id}/disbursement-status/"
