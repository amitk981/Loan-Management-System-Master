import importlib
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.apps import apps
from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.applications.modules import bank_verification
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission
from sfpcl_credit.members.models import BankAccount, CancelledCheque
from sfpcl_credit.processes import security_instrument_evidence
from sfpcl_credit.security_instruments.models import BlankDatedCheque, SecurityPackage
from sfpcl_credit.security_instruments.modules import blank_dated_cheque
from sfpcl_credit.security_instruments.request_contracts import BlankDatedChequeRequest
from sfpcl_credit.shared.encryption import FieldEncryption
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.tests import test_power_of_attorney_api
from sfpcl_credit.workflows.models import WorkflowEvent


class BlankDatedChequeApiTests(TestCase):
    def setUp(self):
        fixture = test_power_of_attorney_api.PowerOfAttorneyApiTests(
            methodName="test_package_refresh_is_replay_safe_and_preserves_checklist_truth"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.client = fixture.client
        self.application = fixture.application
        self.member = fixture.member
        self.compliance = fixture.compliance
        permission, _ = Permission.objects.get_or_create(
            permission_code="security.blank_cheque.manage",
            defaults={
                "permission_name": "Manage blank-dated cheque",
                "module_name": "security",
                "risk_level": "critical",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.compliance.primary_role, permission=permission
        )
        checklist_permission, _ = Permission.objects.get_or_create(
            permission_code="documents.checklist.update",
            defaults={"permission_name": "Update checklist", "risk_level": "critical"},
        )
        RolePermission.objects.get_or_create(
            role=self.compliance.primary_role, permission=checklist_permission
        )
        cancelled_cheque_file = DocumentFile.objects.create(
            file_name="cancelled-cheque.pdf",
            storage_provider="local",
            storage_key="tests/cancelled-cheque.pdf",
            checksum_sha256="c" * 64,
            sensitivity_level="restricted",
        )
        self.cancelled_cheque = CancelledCheque.objects.create(
            loan_application_id=self.application.pk,
            member=self.member,
            document_id=cancelled_cheque_file.pk,
            account_number_encrypted="protected-cancelled-account",
            account_number_hash="retained-bank-hash",
            account_number_last4="4321",
            ifsc="HDFC0001234",
            branch_name="Nashik",
            verification_status="verified",
            signature_mismatch_flag=False,
        )
        self.bank_account = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.member.pk,
            account_holder_name=self.member.legal_name,
            account_number_encrypted="protected-bank-account",
            account_number_hash="retained-bank-hash",
            account_number_last4="4321",
            ifsc="HDFC0001234",
            bank_name="HDFC Bank",
            branch_name="Nashik",
            verification_status="verified",
            cancelled_cheque=self.cancelled_cheque,
            signature_verified_flag=True,
            status="active",
        )
        self.application.bank_account = self.bank_account
        self.application.cancelled_cheque = self.cancelled_cheque
        self.application.save(update_fields=["bank_account", "cancelled_cheque"])
        bank_verification.record_decision(
            actor=self.compliance,
            application_id=self.application.pk,
            payload={
                "bank_account_id": str(self.bank_account.pk),
                "cancelled_cheque_id": str(self.cancelled_cheque.pk),
                "decision_status": "verified",
            },
            metadata=bank_verification.RequestMetadata("blank-cheque-bank-decision"),
        )

    def test_compliance_collects_one_encrypted_masked_cheque_from_canonical_bank_facts(self):
        package = self.fixture._refresh_package()
        self.assertTrue(package["blank_cheque_required_flag"])
        self.assertTrue(package["cancelled_cheque_required_flag"])
        payload = {
            "member_id": str(self.member.pk),
            "bank_account_id": str(self.bank_account.pk),
            "cheque_number": "123456",
            "document_id": None,
            "cheque_status": "collected",
            "custody_location": None,
            "collected_at": timezone.localdate().isoformat(),
        }
        url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/blank-dated-cheque/"
        )

        response = self.client.post(
            url,
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-blank-cheque-create",
            HTTP_USER_AGENT="Blank Cheque Test Agent",
            REMOTE_ADDR="203.0.113.47",
            **self.fixture._auth(self.compliance),
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(data["cheque_number"], "******")
        self.assertEqual(data["cheque_status"], "collected")
        self.assertEqual(data["member_id"], str(self.member.pk))
        self.assertEqual(data["bank_account_id"], str(self.bank_account.pk))
        self.assertEqual(
            data["cancelled_cheque_id"], str(self.cancelled_cheque.pk)
        )
        self.assertIsNone(data["custodian_user_id"])
        self.assertNotIn("123456", str(data))

        retained = SecurityPackage.objects.get(pk=package["security_package_id"]).blank_dated_cheque
        self.assertNotIn("123456", retained.cheque_number_encrypted)
        self.assertEqual(
            FieldEncryption.decrypt(
                "blank_cheque.cheque_number", retained.cheque_number_encrypted
            ),
            "123456",
        )
        migration = importlib.import_module(
            "sfpcl_credit.security_instruments.migrations.0006_migrate_opaque_field_tokens"
        )
        retained.cheque_number_encrypted = migration._encrypt_v1(
            "blank_cheque.cheque_number", "123456"
        )
        retained.save(update_fields=["cheque_number_encrypted"])
        migration.migrate_forward(apps, None)
        migration.migrate_forward(apps, None)
        retained.refresh_from_db()
        self.assertTrue(retained.cheque_number_encrypted.startswith("field:v2:"))
        self.assertNotIn("3456", retained.cheque_number_encrypted.split(":")[:3])
        self.assertEqual(
            AuditLog.objects.filter(action="security.blank_cheque.collected").count(),
            1,
        )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="blank_dated_cheque"
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="blank_dated_cheque").count(),
            1,
        )
        evidence = AuditLog.objects.get(
            action="security.blank_cheque.collected"
        ).new_value_json
        self.assertEqual(evidence["cheque_number"], "******")
        self.assertEqual(evidence["request_id"], "req-blank-cheque-create")
        self.assertNotIn("123456", str(evidence))

    def test_patch_merges_one_mutable_field_and_preserves_omitted_values(self):
        package = self.fixture._refresh_package()
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/blank-dated-cheque/",
            self._payload(),
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        cheque_id = created.json()["data"]["blank_dated_cheque_id"]

        response = self.client.patch(
            f"/api/v1/blank-dated-cheques/{cheque_id}/",
            {"cheque_number": "654321"},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-partial-cheque-number",
            **self.fixture._auth(self.compliance),
        )

        self.assertEqual(response.status_code, 200, response.content)
        retained = BlankDatedCheque.objects.get(pk=cheque_id)
        self.assertEqual(
            FieldEncryption.decrypt(
                "blank_cheque.cheque_number", retained.cheque_number_encrypted
            ),
            "654321",
        )
        self.assertEqual(retained.member_id, self.member.pk)
        self.assertEqual(retained.bank_account_id, self.bank_account.pk)
        self.assertEqual(retained.cheque_status, "collected")
        self.assertIsNone(retained.document_id)
        self.assertIsNone(retained.custody_location)

        several = self.client.patch(
            f"/api/v1/blank-dated-cheques/{cheque_id}/",
            {"cheque_number": "777777", "document_id": None},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-partial-several-fields",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(several.status_code, 200, several.content)
        retained.refresh_from_db()
        self.assertEqual(
            FieldEncryption.decrypt(
                "blank_cheque.cheque_number", retained.cheque_number_encrypted
            ),
            "777777",
        )
        self.assertEqual(retained.member_id, self.member.pk)
        self.assertEqual(retained.bank_account_id, self.bank_account.pk)

    def test_patch_rejects_empty_unknown_immutable_null_and_incomplete_terminal_shapes(self):
        package = self.fixture._refresh_package()
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/blank-dated-cheque/",
            self._payload(), content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        cheque_id = created.json()["data"]["blank_dated_cheque_id"]
        url = f"/api/v1/blank-dated-cheques/{cheque_id}/"
        for payload, field in (
            ({}, "non_field_errors"),
            ({"unexpected": "value"}, "unexpected"),
            ({"presented_date": timezone.localdate().isoformat()}, "presented_date"),
            ({"member_id": str(uuid.uuid4())}, "member_id"),
            ({"cheque_number": None}, "cheque_number"),
            ({"cheque_status": "held"}, "custody_location"),
        ):
            with self.subTest(payload=payload):
                response = self.client.patch(
                    url, payload, content_type="application/json",
                    **self.fixture._auth(self.compliance),
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(field, response.json()["error"]["field_errors"])
        retained = BlankDatedCheque.objects.get(pk=cheque_id)
        self.assertEqual(retained.cheque_status, "collected")
        self.assertIsNone(retained.document_id)

        replay = self.client.patch(
            url, {"document_id": None}, content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(
            AuditLog.objects.filter(action="security.blank_cheque.changed").count(), 0
        )

    def test_patch_rejects_existing_member_and_bank_from_another_application(self):
        package = self.fixture._refresh_package()
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/blank-dated-cheque/",
            self._payload(), content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        cheque_id = created.json()["data"]["blank_dated_cheque_id"]
        other_member = type(self.member).objects.create(
            member_number="MEM-BLANK-CROSS",
            member_type="individual_farmer",
            legal_name="Other Blank Cheque Borrower",
            display_name="Other Blank Cheque Borrower",
            folio_number="FOL-BLANK-CROSS",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        other_application = type(self.application).objects.create(
            application_reference_number="LO-BLANK-CROSS",
            member=other_member,
            borrower_type="individual_farmer",
            received_by_user=self.compliance,
            created_by_user=self.compliance,
        )
        other_cancelled = CancelledCheque.objects.create(
            loan_application_id=other_application.pk,
            member=other_member,
            document_id=uuid.uuid4(),
            account_number_encrypted="protected-other-cancelled-account",
            account_number_hash="other-retained-bank-hash",
            account_number_last4="9876",
            ifsc="HDFC0009876",
            verification_status="verified",
        )
        other_bank = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=other_member.pk,
            account_holder_name=other_member.legal_name,
            account_number_encrypted="protected-other-bank-account",
            account_number_hash="other-retained-bank-hash",
            account_number_last4="9876",
            ifsc="HDFC0009876",
            bank_name="HDFC Bank",
            verification_status="verified",
            cancelled_cheque=other_cancelled,
            signature_verified_flag=True,
            status="active",
        )

        response = self.client.patch(
            f"/api/v1/blank-dated-cheques/{cheque_id}/",
            {
                "member_id": str(other_member.pk),
                "bank_account_id": str(other_bank.pk),
            },
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("member_id", response.json()["error"]["field_errors"])
        retained = BlankDatedCheque.objects.get(pk=cheque_id)
        self.assertEqual(retained.member_id, self.member.pk)
        self.assertEqual(retained.bank_account_id, self.bank_account.pk)

    def test_distinct_company_secretary_holds_then_reveals_with_central_audit(self):
        package = self.fixture._refresh_package()
        payload = self._payload()
        collection_url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/blank-dated-cheque/"
        )
        created = self.client.post(
            collection_url,
            payload,
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        cheque_id = created.json()["data"]["blank_dated_cheque_id"]
        secretary = self.fixture.fixture._user(
            "company_secretary",
            "Blank Cheque Custodian",
            "security.package.read",
            "security.blank_cheque.manage",
            "security.blank_cheque.reveal",
        )
        held = self.client.patch(
            f"/api/v1/blank-dated-cheques/{cheque_id}/",
            {**payload, "cheque_status": "held", "custody_location": "CS secure cabinet"},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-blank-cheque-held",
            **self.fixture._auth(secretary),
        )
        self.assertEqual(held.status_code, 200, held.content)
        held_action = held.json()["data"]
        self.assertEqual(held_action["new_status"], "held")
        self.assertEqual(held_action["available_actions"], [])
        held_read = self.client.get(collection_url, **self.fixture._auth(secretary))
        self.assertNotIn("custodian_user_id", held_read.json()["data"])
        self.assertNotIn("custody_evidence", held_read.json()["data"])
        self.assertEqual(held_read.json()["data"]["cheque_number"], "******")

        stale_change = self.client.patch(
            f"/api/v1/blank-dated-cheques/{cheque_id}/",
            {"cheque_number": "654321"},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(stale_change.status_code, 409, stale_change.content)
        retained = BlankDatedCheque.objects.get(pk=cheque_id)
        self.assertEqual(
            FieldEncryption.decrypt(
                "blank_cheque.cheque_number", retained.cheque_number_encrypted
            ),
            "123456",
        )

        revealed = self.client.post(
            f"/api/v1/blank-dated-cheques/{cheque_id}/reveal-cheque-number/",
            {"reason": "Physical custody reconciliation"},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-blank-cheque-reveal",
            **self.fixture._auth(secretary),
        )

        self.assertEqual(revealed.status_code, 200, revealed.content)
        self.assertEqual(revealed.json()["data"]["cheque_number"], "123456")
        self.assertEqual(revealed["Cache-Control"], "no-store")
        audit = AuditLog.objects.get(action="security.blank_cheque.number_revealed")
        self.assertEqual(audit.actor_user_id, secretary.pk)
        self.assertEqual(audit.new_value_json["reason"], "Physical custody reconciliation")
        self.assertNotIn("123456", str(audit.new_value_json))

    def _payload(self):
        return {
            "member_id": str(self.member.pk),
            "bank_account_id": str(self.bank_account.pk),
            "cheque_number": "123456",
            "document_id": None,
            "cheque_status": "collected",
            "custody_location": None,
            "collected_at": timezone.localdate().isoformat(),
        }

    def test_reveal_fails_closed_and_audits_when_field_key_is_unavailable(self):
        package = self.fixture._refresh_package()
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/blank-dated-cheque/",
            self._payload(),
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        cheque_id = created.json()["data"]["blank_dated_cheque_id"]
        secretary = self.fixture.fixture._user(
            "company_secretary",
            "Blank Cheque Key Failure Reader",
            "security.package.read",
            "security.blank_cheque.reveal",
        )

        with override_settings(FIELD_ENCRYPTION_KEYS={}):
            response = self.client.post(
                f"/api/v1/blank-dated-cheques/{cheque_id}/reveal-cheque-number/",
                {"reason": "Key availability regression"},
                content_type="application/json",
                **self.fixture._auth(secretary),
            )

        self.assertEqual(response.status_code, 409, response.content)
        denial = AuditLog.objects.get(
            action="security.blank_cheque.number_reveal_denied"
        )
        self.assertEqual(denial.new_value_json["denial_reason"], "ciphertext_unavailable")
        self.assertFalse(
            AuditLog.objects.filter(
                action="security.blank_cheque.number_revealed"
            ).exists()
        )

    def test_replay_reads_and_projection_preserve_checklist_and_package_truth(self):
        item = self.application.legal_document_checklist.items.get(
            item_code="blank_dated_cheque"
        )
        item.remarks = "Checklist-owned remarks stay unchanged."
        item.save(update_fields=["remarks"])
        package = self.fixture._refresh_package()
        collection_url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/blank-dated-cheque/"
        )
        payload = self._payload()
        created = self.client.post(
            collection_url, payload, content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        data = created.json()["data"]
        replay = self.client.post(
            collection_url, payload, content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        read = self.client.get(collection_url, **self.fixture._auth(self.compliance))
        detail_replay = self.client.patch(
            f"/api/v1/blank-dated-cheques/{data['blank_dated_cheque_id']}/",
            payload,
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        for response in (replay, detail_replay):
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(response.json()["data"], data)
        self.assertEqual(read.status_code, 200, read.content)
        public = read.json()["data"]
        for key in ("blank_dated_cheque_id", "cheque_number", "cheque_status"):
            self.assertEqual(public[key], data[key])
        self.assertFalse(
            {"prepared_by_user_id", "custodian_user_id", "custody_evidence"}
            .intersection(public)
        )
        self.assertEqual(
            AuditLog.objects.filter(entity_type="blank_dated_cheque").count(), 1
        )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="blank_dated_cheque"
            ).count(), 1
        )

        checklist_response = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(checklist_response.status_code, 200, checklist_response.content)
        projected = next(
            row for row in checklist_response.json()["data"]["items"]
            if row["item_code"] == "blank_dated_cheque"
        )
        self.assertEqual(projected["completion_status"], "pending")
        self.assertEqual(projected["blank_cheque_number"], "******")
        self.assertEqual(projected["blank_cheque_status"], "collected")
        self.assertEqual(
            projected["cancelled_cheque_id"], str(self.cancelled_cheque.pk)
        )
        item.refresh_from_db()
        self.assertEqual(item.remarks, "Checklist-owned remarks stay unchanged.")
        self.assertIsNone(item.loan_document_id)
        package_read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/",
            **self.fixture._auth(self.compliance),
        ).json()["data"]
        self.assertEqual(package_read["blank_dated_cheque"], public)
        self.assertEqual(package_read["security_status"], "pending")
        self.assertFalse(package_read["security_ready_flag"])
        self.assertIsNone(package_read["loan_account_id"])

        for invalid in (
            {**payload, "cheque_status": "invoked"},
            {**payload, "returned_at": timezone.localdate().isoformat()},
            {**payload, "presented_date": timezone.localdate().isoformat()},
        ):
            denied = self.client.patch(
                f"/api/v1/blank-dated-cheques/{data['blank_dated_cheque_id']}/",
                invalid,
                content_type="application/json",
                **self.fixture._auth(self.compliance),
            )
            self.assertEqual(denied.status_code, 400, denied.content)
        self.assertEqual(
            AuditLog.objects.filter(entity_type="blank_dated_cheque").count(), 1
        )

    def test_stale_cross_member_and_conflicting_bank_facts_block_atomically(self):
        package = self.fixture._refresh_package()
        url = f"/api/v1/security-packages/{package['security_package_id']}/blank-dated-cheque/"
        original_hash = self.bank_account.account_number_hash
        self.bank_account.account_number_hash = "changed-after-bank-decision"
        self.bank_account.save(update_fields=["account_number_hash"])
        pending = self.client.post(
            url, self._payload(), content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(pending.status_code, 400, pending.content)
        self.bank_account.account_number_hash = original_hash
        self.bank_account.save(update_fields=["account_number_hash"])
        conflicting = CancelledCheque.objects.create(
            loan_application_id=self.application.pk,
            member=self.member,
            document_id=uuid.uuid4(),
            account_number_encrypted="conflicting",
            account_number_hash="different-hash",
            account_number_last4="9999",
            ifsc="HDFC0009999",
            verification_status="verified",
        )
        conflict = self.client.post(
            url, self._payload(), content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(conflict.status_code, 400, conflict.content)
        conflicting.delete()
        wrong_bank = self.client.post(
            url,
            {**self._payload(), "bank_account_id": str(uuid.uuid4())},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(wrong_bank.status_code, 400, wrong_bank.content)
        self.assertEqual(BlankDatedCheque.objects.count(), 0)
        self.assertFalse(
            AuditLog.objects.filter(entity_type="blank_dated_cheque").exists()
        )

    def test_scan_requires_exact_upload_provenance_and_read_does_not_grant_mutation(self):
        package = self.fixture._refresh_package()
        url = f"/api/v1/security-packages/{package['security_package_id']}/blank-dated-cheque/"
        scan = DocumentFile.objects.create(
            file_name="blank-cheque-scan.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=12,
            storage_provider="local",
            storage_key="tests/blank-cheque-scan.pdf",
            checksum_sha256="8" * 64,
            uploaded_by_user=self.compliance,
            sensitivity_level="restricted",
        )
        missing_provenance = self.client.post(
            url,
            {**self._payload(), "document_id": str(scan.pk)},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(missing_provenance.status_code, 400, missing_provenance.content)
        AuditLog.objects.create(
            actor_user=self.compliance,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=scan.pk,
            new_value_json={
                "document_id": str(scan.pk),
                "file_name": scan.file_name,
                "file_extension": scan.file_extension,
                "mime_type": scan.mime_type,
                "file_size_bytes": scan.file_size_bytes,
                "storage_provider": scan.storage_provider,
                "storage_key": scan.storage_key,
                "checksum_sha256": scan.checksum_sha256,
                "sensitivity_level": scan.sensitivity_level,
                "document_category": "security",
                "related_entity_type": "application",
                "related_entity_id": str(self.application.pk),
            },
        )
        created = self.client.post(
            url,
            {**self._payload(), "document_id": str(scan.pk)},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        self.assertEqual(created.json()["data"]["document_id"], str(scan.pk))
        reader = self.fixture.fixture._user(
            "credit_manager", "Blank Cheque Read Only", "security.package.read"
        )
        read = self.client.get(url, **self.fixture._auth(reader))
        self.assertEqual(read.status_code, 200, read.content)
        denied = self.client.post(
            url,
            {"unexpected": "authority must fail before parsing"},
            content_type="application/json",
            **self.fixture._auth(reader),
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        reveal_denied = self.client.post(
            f"/api/v1/blank-dated-cheques/{created.json()['data']['blank_dated_cheque_id']}/reveal-cheque-number/",
            {"reason": "Read permission is insufficient"},
            content_type="application/json",
            **self.fixture._auth(reader),
        )
        self.assertEqual(reveal_denied.status_code, 403, reveal_denied.content)
        self.assertTrue(
            AuditLog.objects.filter(
                action="security.blank_cheque.number_reveal_denied"
            ).exists()
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL row-lock acceptance only")
class BlankDatedChequeConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = BlankDatedChequeApiTests(
            methodName="test_compliance_collects_one_encrypted_masked_cheque_from_canonical_bank_facts"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.actor = fixture.compliance
        package = fixture.fixture._refresh_package()
        self.package = SecurityPackage.objects.get(pk=package["security_package_id"])

    def test_five_changed_creates_retain_one_winner_and_zero_loser_success_evidence(self):
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = type(self.actor).objects.get(pk=self.actor.pk)
            payload = {**self.fixture._payload(), "cheque_number": f"12345{index}"}
            barrier.wait()
            try:
                security_instrument_evidence.create_blank_cheque(
                    actor=actor,
                    security_package_id=self.package.pk,
                    values=BlankDatedChequeRequest.parse(payload).as_values(),
                    metadata=blank_dated_cheque.RequestMetadata(
                        f"race-blank-create-{index}", "", ""
                    ),
                )
                return "created", index
            except blank_dated_cheque.Conflict:
                return "conflict", index
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        self.assertEqual([status for status, _ in results].count("created"), 1)
        self.assertEqual([status for status, _ in results].count("conflict"), 4)
        self.assertEqual(BlankDatedCheque.objects.count(), 1)
        retained = BlankDatedCheque.objects.get()
        winning_index = next(index for status, index in results if status == "created")
        winning_request = f"race-blank-create-{winning_index}"
        self.assertEqual(
            FieldEncryption.decrypt(
                "blank_cheque.cheque_number", retained.cheque_number_encrypted
            ),
            f"12345{winning_index}",
        )
        audit = AuditLog.objects.get(action="security.blank_cheque.collected")
        version = VersionHistory.objects.get(
            versioned_entity_type="blank_dated_cheque"
        )
        workflow = WorkflowEvent.objects.get(workflow_name="blank_dated_cheque")
        self.assertEqual(audit.new_value_json["request_id"], winning_request)
        self.assertEqual(version.new_value_json["request_id"], winning_request)
        self.assertEqual(audit.actor_user_id, self.actor.pk)
        self.assertEqual(version.author_user_id, self.actor.pk)
        self.assertEqual(workflow.triggered_by_user_id, self.actor.pk)
        success_evidence = str(audit.new_value_json) + str(version.new_value_json)
        for status, index in results:
            self.assertEqual(f"race-blank-create-{index}" in success_evidence, status == "created")

    def test_five_changed_custody_attempts_retain_one_terminal_custodian(self):
        seed = security_instrument_evidence.create_blank_cheque(
            actor=self.actor,
            security_package_id=self.package.pk,
            values=BlankDatedChequeRequest.parse(self.fixture._payload()).as_values(),
            metadata=blank_dated_cheque.RequestMetadata("race-blank-seed", "", ""),
        )
        checker = self.fixture.fixture.fixture._user(
            "company_secretary",
            "Blank Cheque Race Custodian",
            "security.blank_cheque.manage",
            "security.package.read",
        )
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = type(checker).objects.get(pk=checker.pk)
            payload = {
                "cheque_status": "held",
                "custody_location": f"CS secure cabinet {index}",
            }
            barrier.wait()
            try:
                security_instrument_evidence.update_blank_cheque(
                    actor=actor,
                    blank_dated_cheque_id=seed["blank_dated_cheque_id"],
                    values=payload,
                    metadata=blank_dated_cheque.RequestMetadata(
                        f"race-blank-custody-{index}", "", ""
                    ),
                )
                return "held", index
            except blank_dated_cheque.Conflict:
                return "conflict", index
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        self.assertEqual([status for status, _ in results].count("held"), 1)
        self.assertEqual([status for status, _ in results].count("conflict"), 4)
        retained = BlankDatedCheque.objects.get()
        terminal_audit = AuditLog.objects.get(action="security.blank_cheque.held")
        terminal_version = VersionHistory.objects.get(
            versioned_entity_type="blank_dated_cheque",
            change_summary="security.blank_cheque.held",
        )
        terminal_workflow = WorkflowEvent.objects.get(pk=retained.custody_workflow_event_id)
        winning_request = terminal_audit.new_value_json["request_id"]
        winning_index = int(winning_request.rsplit("-", 1)[1])
        self.assertEqual(retained.cheque_status, "held")
        self.assertEqual(retained.custodian_user_id, checker.pk)
        self.assertEqual(retained.custody_location, f"CS secure cabinet {winning_index}")
        self.assertEqual(terminal_version.new_value_json["request_id"], winning_request)
        self.assertEqual(terminal_audit.actor_user_id, checker.pk)
        self.assertEqual(terminal_version.author_user_id, checker.pk)
        self.assertEqual(terminal_workflow.triggered_by_user_id, checker.pk)
        retained_requests = set(
            AuditLog.objects.filter(entity_type="blank_dated_cheque")
            .values_list("new_value_json__request_id", flat=True)
        ) | set(
            VersionHistory.objects.filter(versioned_entity_type="blank_dated_cheque")
            .values_list("new_value_json__request_id", flat=True)
        )
        losers = {
            f"race-blank-custody-{index}"
            for status, index in results if status == "conflict"
        }
        self.assertTrue(losers.isdisjoint(retained_requests))
