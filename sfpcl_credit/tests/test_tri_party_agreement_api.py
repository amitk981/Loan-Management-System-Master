from concurrent.futures import ThreadPoolExecutor
import tempfile
from threading import Barrier
from unittest import skipUnless

from django.core.files.base import ContentFile
from django.db import close_old_connections, connection, connections
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.legal_documents.models import (
    LoanDocument,
    SignatureRecord,
)
from sfpcl_credit.legal_documents.modules import document_checklist, document_generation, signatures
from sfpcl_credit.legal_documents.modules import loan_document_verification
from sfpcl_credit.members.models import Nominee
from sfpcl_credit.security_instruments.models import SecurityPackage
from sfpcl_credit.tests import test_document_checklist_api
from sfpcl_credit.tests import test_loan_document_generation_api as generation_tests
from sfpcl_credit.workflows.models import WorkflowEvent


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-tri-party-tests-"))
class TriPartyAgreementApiTests(TestCase):
    def setUp(self):
        fixture = test_document_checklist_api.DocumentChecklistApiTests(
            methodName="test_approved_sanction_creates_ordered_applicability_once_with_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = fixture.client
        self.password = fixture.password
        self.application = fixture.application
        self.compliance = fixture._user(
            "compliance_team_member",
            "Agreement Preparer",
            "documents.signature.record",
            "documents.loan_document.generate",
            "documents.loan_document.verify",
            "documents.loan_document.read",
            "documents.checklist.read",
            "documents.template.file_reference",
        )
        self.secretary = fixture._user(
            "company_secretary",
            "Agreement Secretary",
            "documents.loan_document.verify",
            "documents.loan_document.read",
            "documents.checklist.read",
        )
        self.application.created_by_user = self.compliance
        self.application.received_by_user = self.compliance
        self.application.save(update_fields=["created_by_user", "received_by_user"])
        self.nominee = Nominee.objects.create(
            member=self.application.member,
            nominee_name="Agreement Nominee",
            gender="female",
            pan_encrypted="encrypted-pan",
            pan_hash="agreement-pan-hash",
            aadhaar_encrypted="encrypted-aadhaar",
            aadhaar_hash="agreement-aadhaar-hash",
        )
        self.application.nominee = self.nominee
        self.application.save(update_fields=["nominee"])
        self.checklist = document_checklist.refresh_for_approved_sanction(
            actor=fixture.actor,
            application_id=self.application.pk,
            source_reason="tri_party_test_setup",
        )
        self.package = SecurityPackage.objects.create(loan_application=self.application)
        stored_template = LocalDocumentStorage().store(
            ContentFile(
                generation_tests.LoanDocumentGenerationApiTests._genuine_docx_fixture([]),
                name="tri-party-agreement.docx",
            )
        )
        template_source = DocumentFile.objects.create(
            file_name="tri-party-agreement.docx",
            file_extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=stored_template.file_size_bytes,
            storage_provider=stored_template.storage_provider,
            storage_key=stored_template.storage_key,
            checksum_sha256=stored_template.checksum_sha256,
            uploaded_by_user=self.compliance,
            sensitivity_level="internal",
        )
        AuditLog.objects.create(
            actor_user=self.compliance,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=template_source.pk,
            new_value_json={
                "document_id": str(template_source.pk),
                "file_name": template_source.file_name,
                "file_extension": template_source.file_extension,
                "mime_type": template_source.mime_type,
                "file_size_bytes": template_source.file_size_bytes,
                "storage_provider": template_source.storage_provider,
                "storage_key": template_source.storage_key,
                "checksum_sha256": template_source.checksum_sha256,
                "sensitivity_level": template_source.sensitivity_level,
                "document_category": "template_source",
                "related_entity_type": "global",
                "related_entity_id": None,
            },
        )
        template = DocumentTemplate.objects.create(
            template_code="tri-party-v1",
            template_name="Tri-party Agreement",
            document_type="tri_party_agreement",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=template_source,
            merge_fields_json=[],
            approval_status="approved",
            effective_from="2026-01-01",
        )
        generated = document_generation.generate(
            actor=self.compliance,
            application_id=self.application.pk,
            payload={
                "document_type": "tri_party_agreement",
                "template_id": str(template.pk),
                "output_format": "pdf",
            },
            metadata=document_generation.RequestMetadata(
                "tri-party-public-generation", "203.0.113.79", "Tri-party Test"
            ),
        )
        self.document = LoanDocument.objects.get(pk=generated["loan_document_id"])
        item = self.checklist.items.get(item_code="tri_party_agreement")
        item.loan_document = self.document
        item.remarks = "Preserve checklist completion remarks."
        item.save(update_fields=["loan_document", "remarks"])
        signed_at = timezone.now()
        for party_type, party_id, party_name in (
            ("borrower", self.application.member_id, self.application.member.legal_name),
            ("nominee", self.nominee.pk, self.nominee.nominee_name),
        ):
            signatures.record(
                actor=self.compliance,
                loan_document_id=self.document.pk,
                payload={
                    "signer_party_type": party_type,
                    "signer_party_id": party_id,
                    "signer_name_snapshot": party_name,
                    "signature_method": "wet_ink",
                    "signature_status": "signed",
                    "signed_at": signed_at.isoformat(),
                    "signature_mismatch_flag": False,
                },
                metadata=signatures.RequestMetadata(
                    f"tri-party-{party_type}-capture", "", ""
                ),
            )

    def test_company_secretary_verifies_applicable_current_signed_agreement(self):
        response = self.client.post(
            f"/api/v1/loan-documents/{self.document.pk}/verify/",
            {
                "verification_status": "verified",
                "remarks": "Borrower and nominee execution verified.",
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-tri-party-verify",
            HTTP_USER_AGENT="Tri-party Test Agent",
            REMOTE_ADDR="203.0.113.80",
            **self._auth(self.secretary),
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(
            set(data),
            {
                "entity_type",
                "entity_id",
                "previous_status",
                "new_status",
                "workflow_event_id",
                "available_actions",
            },
        )
        self.assertEqual(data["entity_type"], "loan_document")
        self.assertEqual(data["entity_id"], str(self.document.pk))
        self.assertEqual(data["previous_status"], "pending")
        self.assertEqual(data["new_status"], "verified")
        self.assertTrue(data["workflow_event_id"])
        self.assertEqual(data["available_actions"], [])

        self.document.refresh_from_db()
        self.assertEqual(self.document.verification_status, "verified")
        self.assertEqual(self.document.verified_by_user_id, self.secretary.pk)
        self.assertIsNotNone(self.document.verified_at)
        item = self.checklist.items.get(item_code="tri_party_agreement")
        self.assertEqual(item.completion_status, "pending")
        self.assertIsNone(item.verified_by_user_id)
        self.assertEqual(item.remarks, "Preserve checklist completion remarks.")

        audit = AuditLog.objects.get(action="loan_document.tri_party_verified")
        signature_ids = set(
            SignatureRecord.objects.filter(loan_document=self.document).values_list(
                "signature_record_id", flat=True
            )
        )
        self.assertEqual(
            set(map(str, audit.new_value_json["signature_record_ids"])),
            set(map(str, signature_ids)),
        )
        self.assertEqual(audit.new_value_json["request_id"], "req-tri-party-verify")
        self.assertEqual(audit.ip_address, "203.0.113.80")
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="loan_document_verification",
                versioned_entity_id=self.document.pk,
            ).count(),
            1,
        )
        workflow = WorkflowEvent.objects.get(
            workflow_name="loan_document_verification",
            entity_id=self.document.pk,
        )
        self.assertEqual(data["workflow_event_id"], str(workflow.pk))

    def test_exact_replay_change_history_and_read_projections_preserve_other_truth(self):
        first = self._verify("Initial execution check.")
        self.assertEqual(first.status_code, 200, first.content)
        self.document.refresh_from_db()
        retained_at = self.document.verified_at
        replay = self._verify("Initial execution check.")
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(
            AuditLog.objects.filter(action="loan_document.tri_party_verified").count(), 1
        )

        changed = self._verify("Corrected retained verification note.")
        self.assertEqual(changed.status_code, 200, changed.content)
        self.document.refresh_from_db()
        self.assertNotEqual(self.document.verified_at, retained_at)
        self.assertEqual(changed.json()["data"]["previous_status"], "verified")
        self.assertEqual(
            AuditLog.objects.filter(action="loan_document.tri_party_verified").count(), 2
        )
        versions = VersionHistory.objects.filter(
            versioned_entity_type="loan_document_verification",
            versioned_entity_id=self.document.pk,
        ).order_by("version_number")
        self.assertEqual([row.version_number for row in versions], ["1", "2"])
        self.assertEqual(
            versions[1].old_value_json["remarks"], "Initial execution check."
        )

        listed = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/",
            **self._auth(self.compliance),
        )
        self.assertEqual(listed.status_code, 200, listed.content)
        row = next(
            value
            for value in listed.json()["data"]
            if value["loan_document_id"] == str(self.document.pk)
        )
        self.assertEqual(row["verification_status"], "verified")
        self.assertEqual(row["verified_by_user_id"], str(self.secretary.pk))
        self.assertEqual(
            row["verification_remarks"], "Corrected retained verification note."
        )

        checklist = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
            **self._auth(self.secretary),
        )
        self.assertEqual(checklist.status_code, 200, checklist.content)
        item = next(
            value
            for value in checklist.json()["data"]["items"]
            if value["item_code"] == "tri_party_agreement"
        )
        self.assertEqual(item["completion_status"], "pending")
        self.assertEqual(item["loan_document_verification_status"], "verified")
        self.assertEqual(
            item["loan_document_verification_remarks"],
            "Corrected retained verification note.",
        )
        self.assertEqual(checklist.json()["data"]["checklist_status"], "in_progress")
        self.package.refresh_from_db()
        self.assertEqual(self.package.security_status, "pending")
        self.assertTrue(self.package.poa_required_flag)
        self.assertFalse(self.package.physical_share_security_required_flag)
        self.assertFalse(self.package.demat_pledge_required_flag)

    def test_strict_request_and_company_secretary_checker_authority_precede_lookup(self):
        url = f"/api/v1/loan-documents/{self.document.pk}/verify/"
        denied = self.client.post(
            url,
            {"unexpected": True},
            content_type="application/json",
            **self._auth(self.compliance),
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(LoanDocument.objects.get(pk=self.document.pk).verification_status, "pending")

        for payload in (
            {"verification_status": "verified"},
            {"verification_status": "pending", "remarks": None},
            {"verification_status": "verified", "remarks": None, "unexpected": True},
        ):
            response = self.client.post(
                url,
                payload,
                content_type="application/json",
                **self._auth(self.secretary),
            )
            self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            AuditLog.objects.filter(action="loan_document.tri_party_verified").count(), 0
        )

    def test_false_or_missing_frozen_applicability_blocks_without_success_evidence(self):
        facts = self.fixture.case.appraisal_facts_json
        active = facts["eligibility"]["active_member_snapshot"]
        active["supplied_to_subsidiary_flag"] = False
        active["supplied_to_stepdown_flag"] = False
        self.fixture.case.appraisal_facts_json = facts
        self.fixture.case.save(update_fields=["appraisal_facts_json"])
        from sfpcl_credit.approvals.modules.approval_case_projection import (
            refresh_approval_case_projection,
        )

        refresh_approval_case_projection(self.fixture.case)
        response = self._verify("Must remain blocked.")
        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(
            AuditLog.objects.filter(action="loan_document.tri_party_verified").count(), 0
        )
        self.document.refresh_from_db()
        self.assertEqual(self.document.verification_status, "pending")

    def test_invalid_signature_wrong_type_legacy_renderer_and_projection_conflict_block(self):
        signature = SignatureRecord.objects.get(
            loan_document=self.document, signer_party_type="nominee"
        )
        SignatureRecord.objects.filter(pk=signature.pk).update(
            signature_status="mismatch", signature_mismatch_flag=True
        )
        mismatch = self._verify("Mismatch cannot verify.")
        self.assertEqual(mismatch.status_code, 409, mismatch.content)

        SignatureRecord.objects.filter(pk=signature.pk).update(
            signature_status="signed", signature_mismatch_flag=False
        )
        self.document.document_type = "term_sheet"
        self.document.save(update_fields=["document_type"])
        wrong_type = self._verify("Wrong type.")
        self.assertEqual(wrong_type.status_code, 404, wrong_type.content)

        self.document.document_type = "tri_party_agreement"
        self.document.save(update_fields=["document_type"])
        LoanDocument.objects.filter(pk=self.document.pk).update(document_id=None)
        legacy = self._verify("Legacy renderer.")
        self.assertEqual(legacy.status_code, 409, legacy.content)

    def test_projection_conflict_rolls_back_document_and_all_success_ledgers(self):
        self.checklist.items.get(item_code="tri_party_agreement").delete()
        response = self._verify("No projection target.")
        self.assertEqual(response.status_code, 409, response.content)
        self.document.refresh_from_db()
        self.assertEqual(self.document.verification_status, "pending")
        self.assertIsNone(self.document.verified_by_user_id)
        self.assertEqual(
            AuditLog.objects.filter(action="loan_document.tri_party_verified").count(), 0
        )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="loan_document_verification"
            ).count(),
            0,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="loan_document_verification"
            ).count(),
            0,
        )

    def test_verified_tri_party_consumed_signatures_cannot_be_rewritten(self):
        verified = self._verify("Freeze exact execution evidence.")
        self.assertEqual(verified.status_code, 200, verified.content)
        borrower = SignatureRecord.objects.get(
            loan_document=self.document, signer_party_type="borrower"
        )
        counts = (
            AuditLog.objects.filter(
                action__in=["documents.signature.changed", "loan_document.tri_party_verified"]
            ).count(),
            VersionHistory.objects.filter(
                versioned_entity_type__in=[
                    "signature_record", "loan_document_verification"
                ]
            ).count(),
            WorkflowEvent.objects.filter(
                workflow_name__in=[
                    "loan_document_signature", "loan_document_verification"
                ]
            ).count(),
        )
        changed = self.client.post(
            f"/api/v1/loan-documents/{self.document.pk}/signatures/",
            {
                "signer_party_type": "borrower",
                "signer_party_id": str(self.application.member_id),
                "signer_name_snapshot": self.application.member.legal_name,
                "signature_method": "wet_ink",
                "signature_status": "pending",
                "signed_at": None,
                "signature_mismatch_flag": False,
            },
            content_type="application/json",
            **self._auth(self.compliance),
        )
        self.assertEqual(changed.status_code, 409, changed.content)
        borrower.refresh_from_db()
        self.document.refresh_from_db()
        self.assertEqual(borrower.signature_status, "signed")
        self.assertEqual(self.document.verification_status, "verified")
        self.assertEqual(
            (
                AuditLog.objects.filter(
                    action__in=[
                        "documents.signature.changed", "loan_document.tri_party_verified"
                    ]
                ).count(),
                VersionHistory.objects.filter(
                    versioned_entity_type__in=[
                        "signature_record", "loan_document_verification"
                    ]
                ).count(),
                WorkflowEvent.objects.filter(
                    workflow_name__in=[
                        "loan_document_signature", "loan_document_verification"
                    ]
                ).count(),
            ),
            counts,
        )
        verification = VersionHistory.objects.get(
            versioned_entity_type="loan_document_verification",
            versioned_entity_id=self.document.pk,
        )
        consumed = verification.new_value_json["consumed_signatures"]
        self.assertEqual(
            {row["signature_record_id"] for row in consumed},
            {
                str(row.pk)
                for row in SignatureRecord.objects.filter(loan_document=self.document)
            },
        )
        self.assertTrue(
            all(
                row["signer_name_snapshot"]
                and row["captured_by_user_id"]
                and row["signed_at"]
                for row in consumed
            )
        )

    def _verify(self, remarks):
        return self.client.post(
            f"/api/v1/loan-documents/{self.document.pk}/verify/",
            {"verification_status": "verified", "remarks": remarks},
            content_type="application/json",
            **self._auth(self.secretary),
        )

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"
        }


@skipUnless(connection.vendor == "postgresql", "PostgreSQL row-lock acceptance only")
class TriPartyAgreementConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def test_five_concurrent_exact_verifications_run_one(self):
        self._run_five(exact=True)

    def test_five_concurrent_exact_verifications_run_two(self):
        self._run_five(exact=True)

    def test_five_concurrent_changed_verifications_run_one(self):
        self._run_five(exact=False)

    def test_five_concurrent_changed_verifications_run_two(self):
        self._run_five(exact=False)

    def _run_five(self, *, exact):
        fixture = TriPartyAgreementApiTests(
            methodName="test_company_secretary_verifies_applicable_current_signed_agreement"
        )
        fixture.setUp()
        actor_id = fixture.secretary.pk
        document_id = fixture.document.pk
        if not exact:
            loan_document_verification.verify(
                actor=fixture.secretary,
                loan_document_id=document_id,
                payload={
                    "verification_status": "verified",
                    "remarks": "Changed-race seed.",
                },
                metadata=loan_document_verification.RequestMetadata(
                    "tri-party-race-seed", "203.0.113.100", "Race"
                ),
            )
        gate = Barrier(5)

        def worker(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=actor_id)
                gate.wait(timeout=10)
                try:
                    action = loan_document_verification.verify(
                        actor=actor,
                        loan_document_id=document_id,
                        payload={
                            "verification_status": "verified",
                            "remarks": (
                                "Concurrent exact execution verification."
                                if exact
                                else f"Concurrent changed execution verification {index}."
                            ),
                        },
                        metadata=loan_document_verification.RequestMetadata(
                            f"tri-party-race-{index}", f"203.0.113.{index + 1}", "Race"
                        ),
                    )
                    return "returned", index, action["workflow_event_id"]
                except loan_document_verification.Conflict:
                    return "conflict", index, None
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        returned = [row for row in results if row[0] == "returned"]
        conflicts = [row for row in results if row[0] == "conflict"]
        self.assertEqual(len(returned), 5 if exact else 1)
        self.assertEqual(len(conflicts), 0 if exact else 4)
        expected = 1 if exact else 2
        audits = AuditLog.objects.filter(action="loan_document.tri_party_verified")
        self.assertEqual(audits.count(), expected)
        self.assertEqual(
            len(
                {
                    row["request_id"]
                    for row in audits.values_list("new_value_json", flat=True)
                }
            ),
            expected,
        )
        workflows = WorkflowEvent.objects.filter(
            workflow_name="loan_document_verification", entity_id=document_id
        )
        self.assertEqual(workflows.count(), expected)
        if not exact:
            winner_index = returned[0][1]
            winner_request = f"tri-party-race-{winner_index}"
            winner = audits.order_by("created_at", "audit_log_id").last()
            self.assertEqual(winner.new_value_json["request_id"], winner_request)
            self.assertEqual(winner.actor_user_id, actor_id)
            winner_version = VersionHistory.objects.filter(
                versioned_entity_type="loan_document_verification",
                versioned_entity_id=document_id,
            ).order_by("created_at", "version_history_id").last()
            winner_workflow = workflows.order_by(
                "created_at", "workflow_event_id"
            ).last()
            self.assertEqual(winner_version.new_value_json["request_id"], winner_request)
            self.assertEqual(winner_version.author_user_id, actor_id)
            self.assertEqual(winner_workflow.triggered_by_user_id, actor_id)
            self.assertEqual(returned[0][2], str(winner_workflow.pk))
            retained = str(
                list(audits.values_list("new_value_json", flat=True))
                + list(
                    VersionHistory.objects.filter(
                        versioned_entity_type="loan_document_verification",
                        versioned_entity_id=document_id,
                    ).values_list("new_value_json", flat=True)
                )
            )
            for _status, index, _event_id in conflicts:
                self.assertNotIn(f"tri-party-race-{index}", retained)
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="loan_document_verification",
                versioned_entity_id=document_id,
            ).count(),
            expected,
        )
