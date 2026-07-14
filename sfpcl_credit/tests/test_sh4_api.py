from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.core.exceptions import ValidationError
from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.applications.models import Witness
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission
from sfpcl_credit.legal_documents.models import ChecklistItem, SignatureRecord, StampDutyRecord
from sfpcl_credit.legal_documents.modules import signatures, stamp_notary
from sfpcl_credit.members.models import Member, Shareholding
from sfpcl_credit.security_instruments.models import SecurityPackage
from sfpcl_credit.security_instruments.models import SH4ShareTransferForm
from sfpcl_credit.security_instruments.modules import sh4
from sfpcl_credit.processes import security_instrument_evidence
from sfpcl_credit.security_instruments.request_contracts import SH4ShareTransferFormRequest
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.tests.test_power_of_attorney_api import PowerOfAttorneyApiTests
from sfpcl_credit.workflows.models import WorkflowEvent


class SH4ApiTests(TestCase):
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
        sh4_permission, _ = Permission.objects.get_or_create(
            permission_code="security.sh4.manage",
            defaults={
                "permission_name": "Manage SH-4",
                "module_name": "security",
                "risk_level": "critical",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.compliance.primary_role, permission=sh4_permission
        )
        self.borrower_shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number="SH4-BORROWER-FOLIO",
            number_of_shares=100,
            holding_mode="physical",
            pledged_share_count=10,
            available_share_count=90,
            status="active",
        )
        witness_member = Member.objects.create(
            member_number="SH4-WITNESS-001",
            member_type="individual_farmer",
            legal_name="Verified Shareholder Witness",
            display_name="Verified Shareholder Witness",
            folio_number="SH4-WITNESS-FOLIO",
            membership_status="active",
            pan_encrypted="witness-pan",
            pan_hash="sh4-witness-pan-hash",
            aadhaar_encrypted="witness-aadhaar",
            aadhaar_hash="sh4-witness-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        witness_shareholding = Shareholding.objects.create(
            member=witness_member,
            folio_number="SH4-WITNESS-FOLIO",
            number_of_shares=5,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=5,
            status="active",
        )
        self.witness = Witness.objects.create(
            loan_application=self.application,
            member=witness_member,
            witness_name=witness_member.legal_name,
            pan_encrypted="witness-pan",
            pan_hash="sh4-witness-pan-hash",
            aadhaar_encrypted="witness-aadhaar",
            aadhaar_hash="sh4-witness-aadhaar-hash",
            verification_shareholding=witness_shareholding,
            verification_folio_number=witness_shareholding.folio_number,
            shareholder_verified_flag=True,
            verification_status="verified",
            verified_by_user=self.compliance,
            verified_at=timezone.now(),
        )

    def test_physical_package_supports_one_replay_safe_pending_sh4_through_public_api(self):
        package = self._refresh_package()
        self.assertTrue(package["physical_share_security_required_flag"])
        self.assertFalse(package["demat_pledge_required_flag"])
        self.assertIsNone(package["sh4_share_transfer_form"])

        document, _, _ = self.fixture._poa_evidence("sh4")
        payload = {
            "member_id": str(self.member.pk),
            "witness_id": str(self.witness.pk),
            "shareholding_id": str(self.borrower_shareholding.pk),
            "share_count": 75,
            "loan_document_id": str(document.pk),
            "form_status": "pending",
            "custody_location": None,
            "signed_at": None,
        }
        url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/sh4-share-transfer-form/"
        )
        first = self.client.post(
            url,
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-sh4-create",
            HTTP_USER_AGENT="SH4 Test Agent",
            REMOTE_ADDR="203.0.113.44",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(first.status_code, 200, first.content)
        assert_success_envelope(self, first.json())
        data = first.json()["data"]
        self.assertEqual(data["form_status"], "pending")
        self.assertEqual(data["prepared_by_user_id"], str(self.compliance.pk))
        self.assertIsNone(data["custodian_user_id"])
        self.assertNotIn("document_download_url", data)

        replay = self.client.post(
            url, payload, content_type="application/json", **self.fixture._auth(self.compliance)
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], data)
        self.assertEqual(AuditLog.objects.filter(action="security.sh4.created").count(), 1)
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="sh4_share_transfer_form"
            ).count(),
            1,
        )
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="sh4").count(), 1)

        read = self.client.get(url, **self.fixture._auth(self.compliance))
        self.assertEqual(read.status_code, 200, read.content)
        self.assertEqual(read.json()["data"], data)
        package_read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(package_read.json()["data"]["sh4_share_transfer_form"], data)
        self.assertEqual(package_read.json()["data"]["security_status"], "pending")
        self.assertFalse(package_read.json()["data"]["security_ready_flag"])
        self.assertEqual(SecurityPackage.objects.count(), 1)

    def test_distinct_company_secretary_records_terminal_custody_from_exact_legal_evidence(self):
        package = self._refresh_package()
        document, stamp, _ = self.fixture._poa_evidence("sh4")
        pending = self._payload(document, form_status="pending")
        collection_url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/sh4-share-transfer-form/"
        )
        created = self.client.post(
            collection_url, pending, content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        sh4_id = created.json()["data"]["sh4_share_transfer_form_id"]
        custodian = self.fixture._user(
            "company_secretary", "security.sh4.manage", "security.package.read",
            "documents.stamp.record", "documents.checklist.read",
        )
        stamp_notary.record_stamp(
            actor=custodian, loan_document_id=document.pk,
            payload={
                "stamp_paper_amount": "1.00", "stamp_type": "physical",
                "stamp_number": "SH4-NOMINAL-001", "stamp_purchase_date": "2026-07-13",
                "executed_date": "2026-07-14", "status": "adequate",
                "remarks": "Retained governed stamp evidence.",
            },
            metadata=stamp_notary.RequestMetadata("sh4-stamp-check", "", ""),
        )
        signed_time = timezone.now()
        for party_type, party_id, party_name in (
            ("borrower", self.member.pk, self.member.legal_name),
            ("witness", self.witness.pk, self.witness.witness_name),
        ):
            signatures.record(
                actor=self.compliance, loan_document_id=document.pk,
                payload={
                    "signer_party_type": party_type, "signer_party_id": party_id,
                    "signer_name_snapshot": party_name, "signature_method": "wet_ink",
                    "signature_status": "signed", "signed_at": signed_time.isoformat(),
                    "signature_mismatch_flag": False,
                },
                metadata=signatures.RequestMetadata(f"sh4-{party_type}-signature", "", ""),
            )
        signed = self._payload(
            document, form_status="signed", signed_at=timezone.localdate().isoformat()
        )
        detail_url = f"/api/v1/sh4-share-transfer-forms/{sh4_id}/"
        borrower_signature = SignatureRecord.objects.get(
            loan_document=document, signer_party_type="borrower"
        )
        borrower_signature.legacy_maker_attribution = True
        borrower_signature.save(update_fields=["legacy_maker_attribution"])
        legacy_signature = self.client.patch(
            detail_url, signed, content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(legacy_signature.status_code, 400, legacy_signature.content)
        borrower_signature.legacy_maker_attribution = False
        borrower_signature.save(update_fields=["legacy_maker_attribution"])
        StampDutyRecord.objects.filter(pk=stamp.pk).update(legacy_maker_attribution=True)
        legacy_stamp = self.client.patch(
            detail_url, signed, content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(legacy_stamp.status_code, 400, legacy_stamp.content)
        StampDutyRecord.objects.filter(pk=stamp.pk).update(legacy_maker_attribution=False)
        signed_response = self.client.patch(
            detail_url, signed, content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(signed_response.status_code, 200, signed_response.content)
        self.assertEqual(signed_response.json()["data"]["form_status"], "signed")
        signed_audit = AuditLog.objects.get(action="security.sh4.changed")
        self.assertEqual(signed_audit.new_value_json["stamp_duty_record_id"], str(stamp.pk))
        self.assertEqual(len(signed_audit.new_value_json["signature_record_ids"]), 2)
        self.assertEqual(
            set(signed_audit.new_value_json["signature_party_types"]),
            {"borrower", "witness"},
        )

        held = {
            **signed, "form_status": "held_in_custody",
            "custody_location": "CS physical custody cabinet A-14",
        }
        custody = self.client.patch(
            detail_url, held, content_type="application/json",
            HTTP_X_REQUEST_ID="req-sh4-custody", HTTP_USER_AGENT="SH4 Custody Agent",
            REMOTE_ADDR="203.0.113.45", **self.fixture._auth(custodian),
        )
        self.assertEqual(custody.status_code, 200, custody.content)
        action = custody.json()["data"]
        self.assertEqual(action["entity_type"], "sh4_share_transfer_form")
        self.assertEqual(action["entity_id"], sh4_id)
        self.assertEqual(action["previous_status"], "signed")
        self.assertEqual(action["new_status"], "held_in_custody")
        self.assertIsNotNone(action["workflow_event_id"])
        self.assertEqual(action["available_actions"], [])
        replay = self.client.patch(
            detail_url, held, content_type="application/json", **self.fixture._auth(custodian)
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], action)

        package_read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/",
            **self.fixture._auth(custodian),
        ).json()["data"]
        retained = package_read["sh4_share_transfer_form"]
        self.assertEqual(retained["form_status"], "held_in_custody")
        self.assertEqual(retained["custodian_user_id"], str(custodian.pk))
        self.assertEqual(retained["custody_evidence"]["stamp_duty_record_id"], str(stamp.pk))
        self.assertEqual(len(retained["custody_evidence"]["signatures"]), 2)
        self.assertEqual(package_read["security_status"], "pending")
        self.assertFalse(package_read["security_ready_flag"])

        checklist = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
            **self.fixture._auth(custodian),
        )
        self.assertEqual(checklist.status_code, 200, checklist.content)
        sh4_item = next(
            item for item in checklist.json()["data"]["items"] if item["item_code"] == "sh4"
        )
        self.assertEqual(sh4_item["completion_status"], "pending")
        self.assertEqual(sh4_item["sh4_form_status"], "held_in_custody")
        self.assertEqual(sh4_item["sh4_custodian_user_id"], str(custodian.pk))
        self.assertEqual(sh4_item["sh4_signature_status"], "signed")

        with self.assertRaises(signatures.InvalidState):
            signatures.record(
                actor=self.compliance, loan_document_id=document.pk,
                payload={
                    "signer_party_type": "witness", "signer_party_id": self.witness.pk,
                    "signer_name_snapshot": self.witness.witness_name,
                    "signature_method": "scanned", "signature_status": "signed",
                    "signed_at": signed_time.isoformat(), "signature_mismatch_flag": False,
                },
                metadata=signatures.RequestMetadata("blocked-sh4-signature", "", ""),
            )
        with self.assertRaises(ValidationError):
            stamp_notary.record_stamp(
                actor=self.compliance, loan_document_id=document.pk,
                payload={
                    "stamp_paper_amount": "2.00", "stamp_type": "physical",
                    "stamp_number": "SH4-NOMINAL-002", "stamp_purchase_date": "2026-07-13",
                    "executed_date": "2026-07-14", "status": "adequate",
                    "remarks": "Must remain blocked after custody.",
                },
                metadata=stamp_notary.RequestMetadata("blocked-sh4-stamp", "", ""),
            )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="sh4_share_transfer_form"
            ).count(), 3,
        )
        self.assertEqual(AuditLog.objects.filter(action="security.sh4.custodied").count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="sh4").count(), 3)

    def test_invalid_authority_shape_scope_and_projection_fail_with_zero_success_writes(self):
        package = self._refresh_package()
        document, _, _ = self.fixture._poa_evidence("sh4")
        payload = self._payload(document, form_status="pending")
        url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/sh4-share-transfer-form/"
        )
        custodian = self.fixture._user(
            "company_secretary", "security.sh4.manage", "security.package.read"
        )
        denied_role = self.client.post(
            url, payload, content_type="application/json", **self.fixture._auth(custodian)
        )
        self.assertEqual(denied_role.status_code, 403, denied_role.content)
        missing_permission = self.fixture._user(
            "compliance_read_only", "security.package.read"
        )
        authority_first = self.client.post(
            url, {"form_status": "invoked"}, content_type="application/json",
            **self.fixture._auth(missing_permission),
        )
        self.assertEqual(authority_first.status_code, 403, authority_first.content)
        unknown_field = self.client.post(
            url, {**payload, "returned_at": "2026-07-14"},
            content_type="application/json", **self.fixture._auth(self.compliance),
        )
        self.assertEqual(unknown_field.status_code, 400, unknown_field.content)
        for forbidden_status in ("invoked", "returned"):
            forbidden = self.client.post(
                url, {**payload, "form_status": forbidden_status},
                content_type="application/json", **self.fixture._auth(self.compliance),
            )
            self.assertEqual(forbidden.status_code, 400, forbidden.content)
        excessive = self.client.post(
            url, {**payload, "share_count": 91}, content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(excessive.status_code, 400, excessive.content)
        wrong_witness = self.client.post(
            url, {**payload, "witness_id": str(self.member.pk)},
            content_type="application/json", **self.fixture._auth(self.compliance),
        )
        self.assertEqual(wrong_witness.status_code, 400, wrong_witness.content)
        current_witness = Witness.objects.create(
            loan_application=self.application, member=self.witness.member,
            witness_name=self.witness.witness_name,
            pan_encrypted="current-witness-pan", pan_hash="current-sh4-witness-pan-hash",
            aadhaar_encrypted="current-witness-aadhaar",
            aadhaar_hash="current-sh4-witness-aadhaar-hash",
            verification_shareholding=self.witness.verification_shareholding,
            verification_folio_number=self.witness.verification_folio_number,
            shareholder_verified_flag=True, verification_status="verified",
            verified_by_user=self.compliance, verified_at=timezone.now(), version=2,
        )
        stale_witness = self.client.post(
            url, payload, content_type="application/json", **self.fixture._auth(self.compliance)
        )
        self.assertEqual(stale_witness.status_code, 400, stale_witness.content)
        payload = {**payload, "witness_id": str(current_witness.pk)}
        sh4_item = ChecklistItem.objects.get(
            document_checklist__loan_application=self.application, item_code="sh4"
        )
        sh4_item.delete()
        rollback = self.client.post(
            url, payload, content_type="application/json", **self.fixture._auth(self.compliance)
        )
        self.assertEqual(rollback.status_code, 409, rollback.content)
        self.assertEqual(SH4ShareTransferForm.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="security.sh4.").count(), 0)
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="sh4_share_transfer_form"
            ).count(), 0,
        )

    def _payload(self, document, *, form_status, signed_at=None, custody_location=None):
        return {
            "member_id": str(self.member.pk), "witness_id": str(self.witness.pk),
            "shareholding_id": str(self.borrower_shareholding.pk), "share_count": 75,
            "loan_document_id": str(document.pk), "form_status": form_status,
            "custody_location": custody_location, "signed_at": signed_at,
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
class SH4ConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = SH4ApiTests(
            methodName=(
                "test_physical_package_supports_one_replay_safe_pending_sh4_through_public_api"
            )
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.actor = fixture.compliance
        package = fixture._refresh_package()
        self.package = SecurityPackage.objects.get(pk=package["security_package_id"])
        self.document, self.stamp, _ = fixture.fixture._poa_evidence("sh4")
        self.base_payload = fixture._payload(self.document, form_status="pending")
        self.base_values = SH4ShareTransferFormRequest.parse(
            self.base_payload
        ).as_values()

    def test_five_changed_creates_retain_one_current_form_and_complete_winner_identity(self):
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = type(self.actor).objects.get(pk=self.actor.pk)
            values = {**self.base_values, "share_count": 70 + index}
            barrier.wait()
            try:
                security_instrument_evidence.create_sh4(
                    actor=actor, security_package_id=self.package.pk, values=values,
                    metadata=sh4.RequestMetadata(f"race-sh4-create-{index}", "", ""),
                )
                return "created", index
            except sh4.Conflict:
                return "conflict", index
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        self.assertEqual([result for result, _ in results].count("created"), 1)
        self.assertEqual([result for result, _ in results].count("conflict"), 4)
        self.assertEqual(SH4ShareTransferForm.objects.count(), 1)
        audit = AuditLog.objects.get(action="security.sh4.created")
        version = VersionHistory.objects.get(
            versioned_entity_type="sh4_share_transfer_form"
        )
        workflow = WorkflowEvent.objects.get(workflow_name="sh4")
        winning_index = next(index for result, index in results if result == "created")
        winning_request = f"race-sh4-create-{winning_index}"
        self.assertEqual(audit.new_value_json["request_id"], winning_request)
        self.assertEqual(version.new_value_json["request_id"], winning_request)
        self.assertEqual(version.author_user_id, self.actor.pk)
        self.assertEqual(workflow.triggered_by_user_id, self.actor.pk)

    def test_five_changed_custody_submissions_retain_one_terminal_winner(self):
        form = security_instrument_evidence.create_sh4(
            actor=self.actor, security_package_id=self.package.pk,
            values=self.base_values,
            metadata=sh4.RequestMetadata("race-sh4-seed", "", ""),
        )
        custodian = self.fixture.fixture._user(
            "company_secretary", "security.sh4.manage", "documents.stamp.record"
        )
        StampDutyRecord.objects.filter(pk=self.stamp.pk).update(
            status="adequate", stamp_paper_amount="1.00",
            stamp_purchase_date="2026-07-13", executed_date="2026-07-14",
            verified_by_user=custodian,
        )
        signed_at = timezone.now()
        for party_type, party_id, name in (
            ("borrower", self.fixture.member.pk, self.fixture.member.legal_name),
            ("witness", self.fixture.witness.pk, self.fixture.witness.witness_name),
        ):
            SignatureRecord.objects.create(
                loan_document=self.document, signer_party_type=party_type,
                signer_party_id=party_id, signer_name_snapshot=name,
                signature_method="wet_ink", signature_status="signed",
                signature_mismatch_flag=False, signed_at=signed_at,
                captured_by_user=self.actor, verified_by_user=self.actor,
                verified_at=signed_at,
            )
        signed_values = SH4ShareTransferFormRequest.parse(
            self.fixture._payload(
                self.document, form_status="signed",
                signed_at=timezone.localdate().isoformat(),
            )
        ).as_values()
        security_instrument_evidence.update_sh4(
            actor=self.actor,
            sh4_share_transfer_form_id=form["sh4_share_transfer_form_id"],
            values=signed_values,
            metadata=sh4.RequestMetadata("race-sh4-signed", "", ""),
        )
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = type(custodian).objects.get(pk=custodian.pk)
            values = {
                **signed_values, "form_status": "held_in_custody",
                "custody_location": f"Race custody cabinet {index}",
            }
            barrier.wait()
            try:
                security_instrument_evidence.update_sh4(
                    actor=actor,
                    sh4_share_transfer_form_id=form["sh4_share_transfer_form_id"],
                    values=values,
                    metadata=sh4.RequestMetadata(f"race-sh4-custody-{index}", "", ""),
                )
                return "custodied", index
            except sh4.Conflict:
                return "conflict", index
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        self.assertEqual([result for result, _ in results].count("custodied"), 1)
        self.assertEqual([result for result, _ in results].count("conflict"), 4)
        retained = SH4ShareTransferForm.objects.get()
        self.assertEqual(retained.form_status, "held_in_custody")
        self.assertEqual(retained.custodian_user_id, custodian.pk)
        winning_index = next(index for result, index in results if result == "custodied")
        winning_request = f"race-sh4-custody-{winning_index}"
        custody_audit = AuditLog.objects.get(action="security.sh4.custodied")
        self.assertEqual(custody_audit.new_value_json["request_id"], winning_request)
        self.assertEqual(custody_audit.actor_user_id, custodian.pk)
        custody_version = VersionHistory.objects.get(
            versioned_entity_type="sh4_share_transfer_form",
            change_summary="security.sh4.custodied",
        )
        self.assertEqual(custody_version.new_value_json["request_id"], winning_request)
        self.assertEqual(custody_version.author_user_id, custodian.pk)
        custody_workflow = WorkflowEvent.objects.get(
            pk=retained.custody_workflow_event_id
        )
        self.assertEqual(custody_workflow.triggered_by_user_id, custodian.pk)
        self.assertEqual(custody_workflow.from_state, "signed")
        self.assertEqual(custody_workflow.to_state, "held_in_custody")
        consumed = AuditLog.objects.get(
            action="documents.execution.consumed",
            new_value_json__consumer_entity_type="sh4_share_transfer_form",
        )
        self.assertEqual(consumed.new_value_json["request_id"], winning_request)
        self.assertEqual(
            consumed.new_value_json["workflow_event_id"], str(custody_workflow.pk)
        )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="sh4_share_transfer_form"
            ).count(), 3,
        )
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="sh4").count(), 3)
        loser_requests = {
            f"race-sh4-custody-{index}"
            for result, index in results if result == "conflict"
        }
        retained_requests = set(
            AuditLog.objects.filter(
                entity_type="sh4_share_transfer_form"
            ).values_list("new_value_json__request_id", flat=True)
        ) | set(
            VersionHistory.objects.filter(
                versioned_entity_type="sh4_share_transfer_form"
            ).values_list("new_value_json__request_id", flat=True)
        )
        self.assertTrue(loser_requests.isdisjoint(retained_requests))
        self.assertEqual(self.package.security_status, "pending")
