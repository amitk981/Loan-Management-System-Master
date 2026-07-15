import json
import importlib
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless
from django.core.exceptions import ValidationError
from django.apps import apps
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission
from sfpcl_credit.legal_documents.models import ChecklistItem
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.members.models import Member, Shareholding
from sfpcl_credit.security_instruments.models import CDSLSharePledge, SecurityPackage
from sfpcl_credit.security_instruments.modules import cdsl_share_pledge
from sfpcl_credit.processes import security_instrument_evidence
from sfpcl_credit.security_instruments.request_contracts import CDSLSharePledgeRequest
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.tests.test_power_of_attorney_api import PowerOfAttorneyApiTests
from sfpcl_credit.workflows.models import WorkflowEvent
class CDSLSharePledgeApiTests(TestCase):
    def setUp(self):
        fixture = PowerOfAttorneyApiTests(
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
            permission_code="security.cdsl_pledge.manage",
            defaults={
                "permission_name": "Manage CDSL pledge",
                "module_name": "security",
                "risk_level": "critical",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.compliance.primary_role, permission=permission
        )
        case = fixture.fixture.case
        case.appraisal_facts_json["shareholding"]["holding_mode"] = "demat"
        case.save(update_fields=["appraisal_facts_json"])
        document_checklist.refresh_for_approved_sanction(
            actor=fixture.fixture.actor,
            application_id=self.application.pk,
            source_reason="cdsl_test_demat_mode",
        )
        self.shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number="CDSL-BORROWER-FOLIO",
            number_of_shares=150,
            holding_mode="demat",
            demat_account_id="11111111-1111-1111-1111-111111111111",
            pledged_share_count=10,
            available_share_count=140,
            future_shares_pledge_flag=True,
            status="active",
        )

    def test_demat_package_supports_one_masked_replay_safe_prepared_pledge(self):
        package = self._refresh_package()
        self.assertFalse(package["physical_share_security_required_flag"])
        self.assertTrue(package["demat_pledge_required_flag"])
        self.assertIsNone(package["cdsl_share_pledge"])
        evidence, _, _ = self.fixture._poa_evidence("cdsl_pledge_evidence")
        payload = self._payload(evidence.document_id)
        url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/cdsl-share-pledge/"
        )
        first = self.client.post(
            url,
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-cdsl-create",
            HTTP_USER_AGENT="CDSL Test Agent",
            REMOTE_ADDR="203.0.113.46",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(first.status_code, 200, first.content)
        assert_success_envelope(self, first.json())
        data = first.json()["data"]
        self.assertEqual(data["pledgor_bo_account"], "************3456")
        self.assertEqual(data["pledgee_bo_account"], "************7654")
        self.assertEqual(data["prf_status"], "prepared")
        self.assertEqual(data["pledge_acceptance_status"], "pending")
        self.assertEqual(data["pledge_status"], "pending")
        self.assertTrue(data["future_shares_pledged_flag"])
        self.assertEqual(data["prepared_by_user_id"], str(self.compliance.pk))
        self.assertIsNone(data["verified_by_user_id"])
        self.assertNotIn("document_download_url", data)

        replay = self.client.post(
            url,
            payload,
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], data)
        read = self.client.get(url, **self.fixture._auth(self.compliance))
        self.assertEqual(read.status_code, 200, read.content)
        public = read.json()["data"]
        for key in ("cdsl_share_pledge_id", "pledgor_bo_account", "prf_status", "pledge_status"):
            self.assertEqual(public[key], data[key])
        self.assertFalse(
            {"prepared_by_user_id", "verified_by_user_id", "acceptance_evidence"}
            .intersection(public)
        )
        package_read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/",
            **self.fixture._auth(self.compliance),
        ).json()["data"]
        self.assertEqual(package_read["cdsl_share_pledge"], public)
        self.assertEqual(package_read["security_status"], "pending")
        self.assertFalse(package_read["security_ready_flag"])
        self.assertEqual(AuditLog.objects.filter(action="security.cdsl_pledge.created").count(), 1)
        self.assertEqual(VersionHistory.objects.filter(
            versioned_entity_type="cdsl_share_pledge").count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="cdsl_share_pledge").count(), 1)

    def test_pending_pledge_accepts_null_evidence_and_projects_null_metadata(self):
        package = self._refresh_package()
        payload = {**self._payload(uuid.uuid4()), "evidence_document_id": None}
        url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/cdsl-share-pledge/"
        )

        response = self.client.post(
            url,
            payload,
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertIsNone(data["evidence_document_id"])
        self.assertIsNone(
            ChecklistItem.objects.get(
                document_checklist__loan_application=self.application,
                item_code="cdsl_pledge",
            ).loan_document_id
        )
        retained = CDSLSharePledge.objects.get(pk=data["cdsl_share_pledge_id"])
        self.assertIsNone(retained.evidence_document_id)

        submitted = {
            **payload,
            "pledgor_dp_name": "Corrected Pledgor DP",
            "pledgee_dp_name": "Pledgee DP",
            "prf_status": "submitted",
            "pledge_sequence_number": "PSN-NULL-EVIDENCE",
            "pledged_share_count": 100,
            "agreement_number": "LA-NULL-EVIDENCE",
        }
        changed = self.client.patch(
            f"/api/v1/cdsl-share-pledges/{retained.pk}/",
            submitted,
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(changed.status_code, 200, changed.content)
        self.assertIsNone(changed.json()["data"]["evidence_document_id"])

        checker = self.fixture.fixture._user(
            "company_secretary",
            "CDSL Null Evidence Checker",
            "security.cdsl_pledge.manage",
            "security.package.read",
        )
        accepted = {
            **submitted,
            "pledge_acceptance_status": "accepted",
            "pledge_status": "created",
        }
        terminal = self.client.patch(
            f"/api/v1/cdsl-share-pledges/{retained.pk}/",
            accepted,
            content_type="application/json",
            **self.fixture._auth(checker),
        )
        self.assertEqual(terminal.status_code, 400, terminal.content)
        retained.refresh_from_db()
        self.assertEqual(retained.pledge_acceptance_status, "pending")
        self.assertIsNone(retained.acceptance_workflow_event_id)
        self.assertFalse(
            AuditLog.objects.filter(
                action="security.cdsl_pledge.accepted", entity_id=retained.pk
            ).exists()
        )

    def test_distinct_company_secretary_accepts_submitted_prf_and_freezes_evidence(self):
        package = self._refresh_package()
        evidence, _, _ = self.fixture._poa_evidence("cdsl_pledge_evidence")
        collection_url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/cdsl-share-pledge/"
        )
        created = self.client.post(
            collection_url,
            self._payload(evidence.document_id),
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        pledge_id = created.json()["data"]["cdsl_share_pledge_id"]
        detail_url = f"/api/v1/cdsl-share-pledges/{pledge_id}/"
        second_compliance = self.fixture.fixture._user(
            "compliance_team_member",
            "Second CDSL Compliance",
            "security.cdsl_pledge.manage",
            "security.package.read",
        )
        submitted = {
            **self._payload(evidence.document_id),
            "prf_status": "submitted",
            "pledge_sequence_number": "PSN-CDSL-0001",
            "pledged_share_count": 100,
            "agreement_number": "LA-CDSL-0001",
        }
        submission = self.client.patch(
            detail_url,
            submitted,
            content_type="application/json",
            **self.fixture._auth(second_compliance),
        )
        self.assertEqual(submission.status_code, 200, submission.content)
        self.assertEqual(submission.json()["data"]["prepared_by_user_id"],
            str(second_compliance.pk))
        checker = self.fixture.fixture._user(
            "company_secretary",
            "CDSL Company Secretary",
            "security.cdsl_pledge.manage",
            "security.package.read",
            "documents.checklist.read",
        )
        accepted = {
            **submitted,
            "pledge_acceptance_status": "accepted",
            "pledged_share_count": 100,
            "agreement_number": "LA-CDSL-0001",
            "pledge_status": "created",
        }
        response = self.client.patch(
            detail_url,
            accepted,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-cdsl-accepted",
            HTTP_USER_AGENT="CDSL Acceptance Agent",
            REMOTE_ADDR="203.0.113.47",
            **self.fixture._auth(checker),
        )
        self.assertEqual(response.status_code, 200, response.content)
        action = response.json()["data"]
        self.assertEqual(action["entity_type"], "cdsl_share_pledge")
        self.assertEqual(action["entity_id"], pledge_id)
        self.assertEqual(action["previous_status"], "pending")
        self.assertEqual(action["new_status"], "created")
        self.assertIsNotNone(action["workflow_event_id"])
        self.assertEqual(action["available_actions"], [])
        replay = self.client.patch(
            detail_url,
            accepted,
            content_type="application/json",
            **self.fixture._auth(checker),
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], action)

        read = self.client.get(collection_url, **self.fixture._auth(checker))
        retained = read.json()["data"]
        self.assertEqual(retained["pledge_status"], "created")
        self.assertEqual(retained["pledge_acceptance_status"], "accepted")
        self.assertFalse(
            {"verified_by_user_id", "prepared_by_user_id", "acceptance_evidence"}
            .intersection(retained)
        )
        frozen = CDSLSharePledge.objects.get(pk=pledge_id).acceptance_evidence_json
        self.assertNotIn("pledgor_bo_account_hash", frozen)
        self.assertNotIn("pledgor_bo_account_encrypted", frozen)
        self.shareholding.refresh_from_db()
        self.assertEqual(self.shareholding.available_share_count, 140)
        self.assertEqual(self.shareholding.pledged_share_count, 10)
        self.assertEqual(VersionHistory.objects.filter(
            versioned_entity_type="cdsl_share_pledge").count(), 3)
        self.assertEqual(AuditLog.objects.filter(
            action="security.cdsl_pledge.accepted").count(), 1)
        checklist = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
            **self.fixture._auth(checker),
        )
        self.assertEqual(checklist.status_code, 200, checklist.content)
        item = next(
            row for row in checklist.json()["data"]["items"]
            if row["item_code"] == "cdsl_pledge"
        )
        expected = {
            "completion_status": "pending", "cdsl_prf_status": "submitted",
            "cdsl_pledge_sequence_number": "PSN-CDSL-0001",
            "cdsl_acceptance_status": "accepted", "cdsl_pledge_status": "created",
            "cdsl_pledged_share_count": 100,
        }
        self.assertEqual({key: item[key] for key in expected}, expected)
        self.assertNotIn("cdsl_prepared_by_user_id", item)
        self.assertNotIn("cdsl_verified_by_user_id", item)

    def test_invalid_scope_shape_state_and_projection_conflict_write_no_pledge(self):
        package = self._refresh_package()
        evidence, _, _ = self.fixture._poa_evidence("cdsl_pledge_evidence")
        payload = self._payload(evidence.document_id)
        url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/cdsl-share-pledge/"
        )
        read_only = self.fixture.fixture._user(
            "compliance_read_only",
            "CDSL Read Only",
            "security.package.read",
        )
        checker = self.fixture.fixture._user(
            "company_secretary",
            "CDSL Create Checker",
            "security.cdsl_pledge.manage",
            "security.package.read",
        )
        cases = [
            ({"pledge_status": "invoked"}, read_only, 403),
            (payload, checker, 403),
            ({**payload, "invoked_at": "2026-07-14T10:00:00Z"}, self.compliance, 400),
            ({**payload, "pledge_status": "invoked"}, self.compliance, 400),
            ({**payload, "pledge_status": "unpledged"}, self.compliance, 400),
            ({**payload, "pledgee_bo_account": payload["pledgor_bo_account"]}, self.compliance, 400),
            ({**payload, "pledgor_bo_account": "not-a-bo-account"}, self.compliance, 400),
            ({**payload, "prf_status": "submitted"}, self.compliance, 400),
            ({**payload, "pledged_share_count": 141}, self.compliance, 400),
        ]
        for invalid_payload, actor, status in cases:
            response = self.client.post(
                url, invalid_payload, content_type="application/json",
                **self.fixture._auth(actor),
            )
            self.assertEqual(response.status_code, status, response.content)
        wrong_member = Member.objects.create(
            member_number="CDSL-WRONG-001",
            member_type="individual_farmer",
            legal_name="Wrong CDSL Member",
            display_name="Wrong CDSL Member",
            folio_number="CDSL-WRONG-FOLIO",
            membership_status="active",
            pan_encrypted="wrong-pan",
            pan_hash="wrong-cdsl-pan-hash",
            aadhaar_encrypted="wrong-aadhaar",
            aadhaar_hash="wrong-cdsl-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        wrong_borrower = self.client.post(
            url,
            {**payload, "pledgor_member_id": str(wrong_member.pk)},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(wrong_borrower.status_code, 400, wrong_borrower.content)
        case = self.fixture.fixture.case
        for inapplicable_mode in ("physical", "mixed", None):
            case.appraisal_facts_json["shareholding"]["holding_mode"] = inapplicable_mode
            case.save(update_fields=["appraisal_facts_json"])
            inapplicable = self.client.post(
                url, payload, content_type="application/json",
                **self.fixture._auth(self.compliance),
            )
            self.assertEqual(inapplicable.status_code, 400, inapplicable.content)
        case.appraisal_facts_json["shareholding"]["holding_mode"] = "demat"
        case.save(update_fields=["appraisal_facts_json"])
        ChecklistItem.objects.get(
            document_checklist__loan_application=self.application,
            item_code="cdsl_pledge",
        ).delete()
        rollback = self.client.post(
            url, payload, content_type="application/json", **self.fixture._auth(self.compliance)
        )
        self.assertEqual(rollback.status_code, 409, rollback.content)
        self.assertEqual(CDSLSharePledge.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(
            action__startswith="security.cdsl_pledge.").count(), 0)
        self.assertEqual(VersionHistory.objects.filter(
            versioned_entity_type="cdsl_share_pledge").count(), 0)

    def test_explicit_company_secretary_reveal_is_one_time_and_separately_audited(self):
        package = self._refresh_package()
        evidence, _, _ = self.fixture._poa_evidence("cdsl_pledge_evidence")
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/cdsl-share-pledge/",
            self._payload(evidence.document_id),
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        pledge_id = created.json()["data"]["cdsl_share_pledge_id"]
        reveal_url = f"/api/v1/cdsl-share-pledges/{pledge_id}/reveal-bo-accounts/"
        denied = self.fixture.fixture._user(
            "company_secretary",
            "CDSL Reveal Denied",
            "security.package.read",
            "security.cdsl_pledge.manage",
        )
        denied_response = self.client.post(
            reveal_url,
            {"reason": "Verify retained DP instructions."},
            content_type="application/json",
            **self.fixture._auth(denied),
        )
        self.assertEqual(denied_response.status_code, 403, denied_response.content)
        revealer = self.fixture.fixture._user(
            "company_secretary",
            "CDSL Reveal Secretary",
            "security.package.read",
            "security.cdsl_pledge.reveal",
        )
        response = self.client.post(
            reveal_url,
            {"reason": "Verify retained DP instructions."},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-cdsl-reveal",
            HTTP_USER_AGENT="CDSL Reveal Agent",
            REMOTE_ADDR="203.0.113.48",
            **self.fixture._auth(revealer),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(response["Pragma"], "no-cache")
        data = response.json()["data"]
        self.assertEqual(data["cdsl_share_pledge_id"], pledge_id)
        self.assertEqual(data["pledgor_bo_account"], "1234567890123456")
        self.assertEqual(data["pledgee_bo_account"], "9876543210987654")
        self.assertIsNotNone(data["expires_at"])
        success = AuditLog.objects.get(action="security.cdsl_pledge.bo_accounts_revealed")
        self.assertEqual(success.new_value_json["reason"], "Verify retained DP instructions.")
        self.assertEqual(success.new_value_json["request_id"], "req-cdsl-reveal")
        self.assertFalse(success.new_value_json["reauthentication_required"])
        self.assertTrue(success.new_value_json["reauthentication_satisfied"])
        self.assertEqual(success.new_value_json["rate_limit_count"], 1)
        self.assertEqual(success.new_value_json["rate_limit_window_seconds"], 300)
        self.assertNotIn("1234567890123456", json.dumps(success.new_value_json))
        denial = AuditLog.objects.get(action="security.cdsl_pledge.bo_accounts_reveal_denied")
        self.assertEqual(denial.new_value_json["outcome"], "denied")
        ordinary = AuditLog.objects.filter(
            action__startswith="security.cdsl_pledge."
        ).exclude(action="security.cdsl_pledge.bo_accounts_revealed")
        self.assertNotIn(
            "1234567890123456",
            json.dumps(list(ordinary.values_list("new_value_json", flat=True))),
        )
        repeated = self.client.post(
            reveal_url,
            {"reason": "Repeat the same DP instruction check."},
            content_type="application/json",
            **self.fixture._auth(revealer),
        )
        self.assertEqual(repeated.status_code, 429, repeated.content)
        self.assertEqual(repeated.json()["error"]["code"], "RATE_LIMITED")
        rate_denial = AuditLog.objects.filter(
            action="security.cdsl_pledge.bo_accounts_reveal_denied",
            new_value_json__denial_reason="rate_limited",
        )
        self.assertEqual(rate_denial.count(), 1)

    def test_central_reveal_validates_reason_and_denies_lost_object_scope(self):
        package = self._refresh_package()
        evidence, _, _ = self.fixture._poa_evidence("cdsl_pledge_evidence")
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/cdsl-share-pledge/",
            self._payload(evidence.document_id),
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        pledge_id = created.json()["data"]["cdsl_share_pledge_id"]
        revealer = self.fixture.fixture._user(
            "company_secretary",
            "CDSL Scoped Revealer",
            "security.package.read",
            "security.cdsl_pledge.reveal",
        )
        reveal_url = f"/api/v1/cdsl-share-pledges/{pledge_id}/reveal-bo-accounts/"

        missing_reason = self.client.post(
            reveal_url,
            {},
            content_type="application/json",
            **self.fixture._auth(revealer),
        )
        self.assertEqual(missing_reason.status_code, 400, missing_reason.content)
        self.assertEqual(
            AuditLog.objects.filter(
                action="security.cdsl_pledge.bo_accounts_reveal_denied",
                entity_id=pledge_id,
                new_value_json__denial_reason="validation_failed",
            ).count(),
            1,
        )

        AuditLog.objects.filter(
            action="document_checklist.created",
            entity_type="document_checklist",
        ).delete()
        denied = self.client.post(
            reveal_url,
            {"reason": "Verify retained DP instructions."},
            content_type="application/json",
            **self.fixture._auth(revealer),
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(
            AuditLog.objects.filter(
                action="security.cdsl_pledge.bo_accounts_reveal_denied",
                entity_id=pledge_id,
                new_value_json__denial_reason="object_access_denied",
            ).count(),
            1,
        )

    def test_role_change_cannot_collapse_maker_checker_or_bypass_database_guard(self):
        package = self._refresh_package()
        evidence, _, _ = self.fixture._poa_evidence("cdsl_pledge_evidence")
        submitted = {
            **self._payload(evidence.document_id),
            "prf_status": "submitted",
            "pledge_sequence_number": "PSN-CDSL-SELF-CHECK",
            "pledged_share_count": 100,
            "agreement_number": "LA-CDSL-SELF-CHECK",
        }
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/cdsl-share-pledge/",
            submitted,
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        pledge_id = created.json()["data"]["cdsl_share_pledge_id"]
        secretary = self.fixture.fixture._user(
            "company_secretary",
            "CDSL Role Change Secretary",
            "security.cdsl_pledge.manage",
            "security.package.read",
        )
        self.compliance.primary_role = secretary.primary_role
        self.compliance.save(update_fields=["primary_role"])
        accepted = {
            **submitted,
            "pledge_acceptance_status": "accepted",
            "pledge_status": "created",
        }
        response = self.client.patch(
            f"/api/v1/cdsl-share-pledges/{pledge_id}/",
            accepted,
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(VersionHistory.objects.filter(
            versioned_entity_type="cdsl_share_pledge").count(), 1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            CDSLSharePledge.objects.filter(pk=pledge_id).update(
                pledge_acceptance_status="accepted",
                pledge_status="created",
                verified_by_user=self.compliance,
                acceptance_workflow_event_id=uuid.uuid4(),
                created_at_cdsl=timezone.now(),
            )

    def test_corrupt_ciphertext_fails_reveal_without_plaintext_or_success_audit(self):
        package = self._refresh_package()
        evidence, _, _ = self.fixture._poa_evidence("cdsl_pledge_evidence")
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/cdsl-share-pledge/",
            self._payload(evidence.document_id),
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        pledge_id = created.json()["data"]["cdsl_share_pledge_id"]
        retained = CDSLSharePledge.objects.get(pk=pledge_id)
        replacement = (
            "A" if retained.pledgor_bo_account_encrypted[-1] != "A" else "B"
        )
        retained.pledgor_bo_account_encrypted = (
            retained.pledgor_bo_account_encrypted[:-1] + replacement
        )
        retained.save(update_fields=["pledgor_bo_account_encrypted"])
        revealer = self.fixture.fixture._user(
            "company_secretary",
            "CDSL Corruption Revealer",
            "security.package.read",
            "security.cdsl_pledge.reveal",
        )

        response = self.client.post(
            f"/api/v1/cdsl-share-pledges/{pledge_id}/reveal-bo-accounts/",
            {"reason": "Verify retained DP instructions."},
            content_type="application/json",
            **self.fixture._auth(revealer),
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertFalse(
            AuditLog.objects.filter(
                action="security.cdsl_pledge.bo_accounts_revealed",
                entity_id=pledge_id,
            ).exists()
        )
        evidence_json = json.dumps(
            list(AuditLog.objects.values_list("new_value_json", flat=True))
        )
        self.assertNotIn("1234567890123456", evidence_json)

    def test_legacy_ciphertext_migration_reconciles_hash_last4_and_row_count(self):
        package = self._refresh_package()
        evidence, _, _ = self.fixture._poa_evidence("cdsl_pledge_evidence")
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/cdsl-share-pledge/",
            self._payload(evidence.document_id),
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        retained = CDSLSharePledge.objects.get(
            pk=created.json()["data"]["cdsl_share_pledge_id"]
        )
        migration = importlib.import_module(
            "sfpcl_credit.security_instruments.migrations.0004_migrate_cdsl_field_encryption"
        )
        retained.pledgor_bo_account_encrypted = migration._legacy_encrypt(
            "1234567890123456"
        )
        retained.pledgor_bo_account_hash = migration._legacy_hash(
            "1234567890123456"
        )
        retained.pledgee_bo_account_encrypted = migration._legacy_encrypt(
            "9876543210987654"
        )
        retained.pledgee_bo_account_hash = migration._legacy_hash(
            "9876543210987654"
        )
        retained.save(
            update_fields=[
                "pledgor_bo_account_encrypted",
                "pledgor_bo_account_hash",
                "pledgee_bo_account_encrypted",
                "pledgee_bo_account_hash",
            ]
        )

        migration.migrate_forward(apps, None)
        migration.migrate_forward(apps, None)

        retained.refresh_from_db()
        opaque_migration = importlib.import_module(
            "sfpcl_credit.security_instruments.migrations.0006_migrate_opaque_field_tokens"
        )
        retained.pledgor_bo_account_encrypted = opaque_migration._encrypt_v1(
            "cdsl.pledgor_bo_account", "1234567890123456"
        )
        retained.pledgee_bo_account_encrypted = opaque_migration._encrypt_v1(
            "cdsl.pledgee_bo_account", "9876543210987654"
        )
        retained.pledgor_bo_account_last4 = "0000"
        retained.pledgee_bo_account_last4 = "1111"
        retained.save(update_fields=[
            "pledgor_bo_account_encrypted", "pledgee_bo_account_encrypted",
            "pledgor_bo_account_last4", "pledgee_bo_account_last4",
        ])
        opaque_migration.migrate_forward(apps, None)
        opaque_migration.migrate_forward(apps, None)
        retained.refresh_from_db()
        self.assertTrue(retained.pledgor_bo_account_encrypted.startswith("field:v2:"))
        self.assertTrue(retained.pledgee_bo_account_encrypted.startswith("field:v2:"))
        self.assertNotIn("3456", retained.pledgor_bo_account_encrypted.split(":")[:3])
        self.assertNotIn("7654", retained.pledgee_bo_account_encrypted.split(":")[:3])
        self.assertEqual(retained.pledgor_bo_account_last4, "3456")
        self.assertEqual(retained.pledgee_bo_account_last4, "7654")
        self.assertEqual(
            security_instrument_evidence.read_pledge(
                actor=self.compliance, security_package_id=package["security_package_id"]
            )["pledgor_bo_account"],
            "************3456",
        )
        database_values = json.dumps(
            list(
                CDSLSharePledge.objects.values(
                    "pledgor_bo_account_encrypted",
                    "pledgor_bo_account_hash",
                    "pledgee_bo_account_encrypted",
                    "pledgee_bo_account_hash",
                )
            )
        )
        self.assertNotIn("1234567890123456", database_values)
        self.assertNotIn("9876543210987654", database_values)

    def _payload(self, evidence_document_id):
        return {
            "pledgor_member_id": str(self.member.pk),
            "pledgee_entity_name": "Sahyadri Farmers Producer Company Limited",
            "pledgor_bo_account": "1234567890123456",
            "pledgee_bo_account": "9876543210987654",
            "pledgor_dp_name": "Pledgor DP",
            "pledgee_dp_name": "Pledgee DP",
            "prf_status": "prepared",
            "pledge_sequence_number": None,
            "pledge_acceptance_status": "pending",
            "pledged_share_count": None,
            "agreement_number": None,
            "pledge_status": "pending",
            "evidence_document_id": str(evidence_document_id),
        }

    def _refresh_package(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/refresh/",
            {},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]


@skipUnless(connection.vendor == "postgresql", "PostgreSQL row-lock acceptance only")
class CDSLSharePledgeConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = CDSLSharePledgeApiTests(
            methodName="test_demat_package_supports_one_masked_replay_safe_prepared_pledge"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.actor = fixture.compliance
        package = fixture._refresh_package()
        self.package = SecurityPackage.objects.get(pk=package["security_package_id"])
        self.evidence, _, _ = fixture.fixture._poa_evidence("cdsl_pledge_evidence")

    def test_five_different_psn_creates_retain_one_masked_current_pledge(self):
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = type(self.actor).objects.get(pk=self.actor.pk)
            payload = {
                **self.fixture._payload(self.evidence.document_id),
                "prf_status": "submitted",
                "pledge_sequence_number": f"PSN-CDSL-RACE-{index}",
                "pledged_share_count": 90 + index,
                "agreement_number": f"LA-CDSL-RACE-{index}",
            }
            values = CDSLSharePledgeRequest.parse(payload).as_values()
            barrier.wait()
            try:
                security_instrument_evidence.create_pledge(
                    actor=actor,
                    security_package_id=self.package.pk,
                    values=values,
                    metadata=cdsl_share_pledge.RequestMetadata(
                        f"race-cdsl-create-{index}", "", ""
                    ),
                )
                return "created", index
            except cdsl_share_pledge.Conflict:
                return "conflict", index
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        self.assertEqual([result for result, _ in results].count("created"), 1)
        self.assertEqual([result for result, _ in results].count("conflict"), 4)
        self.assertEqual(CDSLSharePledge.objects.count(), 1)
        retained = CDSLSharePledge.objects.get()
        data = security_instrument_evidence.read_pledge(
            actor=self.actor, security_package_id=self.package.pk
        )
        self.assertEqual(data["pledgor_bo_account"], "************3456")
        self.assertEqual(data["pledgee_bo_account"], "************7654")
        self.assertNotIn("1234567890123456", retained.pledgor_bo_account_encrypted)
        winning_index = next(index for result, index in results if result == "created")
        winning_request = f"race-cdsl-create-{winning_index}"
        self.assertEqual(retained.pledge_sequence_number, f"PSN-CDSL-RACE-{winning_index}")
        self.assertEqual(
            AuditLog.objects.get(action="security.cdsl_pledge.created")
            .new_value_json["request_id"],
            winning_request,
        )
        version = VersionHistory.objects.get(
            versioned_entity_type="cdsl_share_pledge"
        )
        workflow = WorkflowEvent.objects.get(workflow_name="cdsl_share_pledge")
        self.assertEqual(version.new_value_json["request_id"], winning_request)
        self.assertEqual(version.author_user_id, self.actor.pk)
        self.assertEqual(workflow.triggered_by_user_id, self.actor.pk)
        evidence = str(
            list(AuditLog.objects.values_list("new_value_json", flat=True))
            + list(VersionHistory.objects.values_list("new_value_json", flat=True))
        )
        for result, index in results:
            self.assertEqual(
                f"race-cdsl-create-{index}" in evidence, result == "created"
            )

    def test_five_changed_acceptance_attempts_retain_one_terminal_winner(self):
        submitted = {
            **self.fixture._payload(self.evidence.document_id),
            "prf_status": "submitted",
            "pledge_sequence_number": "PSN-CDSL-ACCEPT-RACE",
            "pledged_share_count": 100,
            "agreement_number": "LA-CDSL-ACCEPT-RACE",
        }
        seed = security_instrument_evidence.create_pledge(
            actor=self.actor,
            security_package_id=self.package.pk,
            values=CDSLSharePledgeRequest.parse(submitted).as_values(),
            metadata=cdsl_share_pledge.RequestMetadata("race-cdsl-seed", "", ""),
        )
        checker = self.fixture.fixture.fixture._user(
            "company_secretary",
            "CDSL Race Secretary",
            "security.cdsl_pledge.manage",
            "security.package.read",
        )
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = type(checker).objects.get(pk=checker.pk)
            acceptance = "accepted" if index % 2 == 0 else "rejected"
            payload = {
                **submitted,
                "pledge_acceptance_status": acceptance,
                "pledge_status": "created" if acceptance == "accepted" else "pending",
            }
            values = CDSLSharePledgeRequest.parse(payload).as_values()
            barrier.wait()
            try:
                security_instrument_evidence.update_pledge(
                    actor=actor,
                    cdsl_share_pledge_id=seed["cdsl_share_pledge_id"],
                    values=values,
                    metadata=cdsl_share_pledge.RequestMetadata(
                        f"race-cdsl-acceptance-{index}", "", ""
                    ),
                )
                return "returned", index, str(
                    CDSLSharePledge.objects.get(pk=seed["cdsl_share_pledge_id"])
                    .acceptance_workflow_event_id
                )
            except cdsl_share_pledge.Conflict:
                return "conflict", index, None
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        self.assertEqual(len(results), 5)
        self.assertTrue(
            all(result in {"returned", "conflict"} for result, _, _ in results)
        )
        retained = CDSLSharePledge.objects.get()
        self.assertEqual(retained.verified_by_user_id, checker.pk)
        self.assertIsNotNone(retained.acceptance_workflow_event_id)
        terminal_audits = AuditLog.objects.filter(
            action__in=[
                "security.cdsl_pledge.accepted",
                "security.cdsl_pledge.rejected",
            ]
        )
        self.assertEqual(terminal_audits.count(), 1)
        terminal_audit = terminal_audits.get()
        winning_request = terminal_audit.new_value_json["request_id"]
        winning_index = int(winning_request.rsplit("-", 1)[1])
        expected_acceptance = "accepted" if winning_index % 2 == 0 else "rejected"
        self.assertEqual(retained.pledge_acceptance_status, expected_acceptance)
        self.assertEqual(winning_request, f"race-cdsl-acceptance-{winning_index}")
        loser_requests = {
            f"race-cdsl-acceptance-{index}"
            for _result, index, _event_id in results if index != winning_index
        }
        retained_requests = set(
            AuditLog.objects.filter(entity_type="cdsl_share_pledge")
            .values_list("new_value_json__request_id", flat=True)
        ) | set(
            VersionHistory.objects.filter(
                versioned_entity_type="cdsl_share_pledge"
            ).values_list("new_value_json__request_id", flat=True)
        )
        self.assertTrue(loser_requests.isdisjoint(retained_requests))
        self.assertEqual(VersionHistory.objects.filter(
            versioned_entity_type="cdsl_share_pledge").count(), 2)
        terminal_version = VersionHistory.objects.get(
            versioned_entity_type="cdsl_share_pledge",
            change_summary__in=[
                "security.cdsl_pledge.accepted",
                "security.cdsl_pledge.rejected",
            ],
        )
        workflow = WorkflowEvent.objects.get(pk=retained.acceptance_workflow_event_id)
        self.assertEqual(terminal_audit.actor_user_id, checker.pk)
        self.assertEqual(terminal_version.author_user_id, checker.pk)
        self.assertEqual(terminal_version.new_value_json["request_id"], winning_request)
        self.assertEqual(workflow.triggered_by_user_id, checker.pk)
        self.assertEqual(
            {event_id for status, _, event_id in results if status == "returned"},
            {str(workflow.pk)},
        )
