import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, TransactionTestCase

from sfpcl_credit.applications.models import LoanApplication, Witness
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
    SignatureRecord,
    StampDutyRecord,
)
from sfpcl_credit.legal_documents.modules import signatures
from sfpcl_credit.legal_documents import serializers as legal_serializers
from sfpcl_credit.members.models import Member, Nominee
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class SignatureMismatchApiTests(TestCase):
    password = "SignaturePass123!"

    def setUp(self):
        self.client = Client()
        self.actor = self._user(
            "compliance_team_member",
            "documents.signature.record",
        )
        member = Member.objects.create(
            member_number="MEM-SIGN-001",
            member_type="individual_farmer",
            legal_name="Signature Test Borrower",
            display_name="Signature Test Borrower",
            folio_number="FOL-SIGN-001",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="LO-SIGN-001",
            member=member,
            borrower_type="individual_farmer",
            received_by_user=self.actor,
            created_by_user=self.actor,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
        )
        generated_file = DocumentFile.objects.create(
            file_name="agreement.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=8,
            storage_provider="local",
            storage_key="tests/agreement.pdf",
            checksum_sha256="a" * 64,
            uploaded_by_user=self.actor,
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code="signature-agreement-v1",
            template_name="Signature Agreement",
            document_type="loan_agreement",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=generated_file,
            approval_status="approved",
            effective_from="2026-01-01",
        )
        self.loan_document = LoanDocument.objects.create(
            loan_application=self.application,
            document_type="loan_agreement",
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=generated_file,
            output_format="pdf",
            generation_status=LoanDocument.GENERATION_GENERATED,
            execution_status=LoanDocument.EXECUTION_PENDING,
            verification_status=LoanDocument.VERIFICATION_PENDING,
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=generated_file.pk,
            renderer_validated_checksum_sha256=generated_file.checksum_sha256,
        )

    def test_compliance_records_pending_signature_with_attributable_evidence(self):
        response = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            {
                "signer_party_type": "borrower",
                "signer_party_id": str(self.application.member_id),
                "signer_name_snapshot": "Signature Test Borrower",
                "signature_method": "wet_ink",
                "signature_status": "pending",
                "signed_at": None,
                "signature_mismatch_flag": False,
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-signature-create",
            HTTP_USER_AGENT="Signature Test Agent",
            REMOTE_ADDR="203.0.113.30",
            **self._auth(self.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["data"]["signature_status"], "pending")
        self.assertEqual(payload["data"]["signer_name_snapshot"], "Signature Test Borrower")
        self.assertNotIn("storage_key", payload["data"])
        audit = AuditLog.objects.get(action="documents.signature.created")
        self.assertEqual(audit.actor_user, self.actor)
        self.assertEqual(audit.new_value_json["request_id"], "req-signature-create")
        self.assertEqual(audit.new_value_json["actor_role_codes"], ["compliance_team_member"])
        self.assertEqual(audit.ip_address, "203.0.113.30")
        self.assertEqual(audit.user_agent, "Signature Test Agent")
        self.assertEqual(
            VersionHistory.objects.filter(versioned_entity_type="signature_record").count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.get(workflow_name="loan_document_signature").to_state,
            "pending",
        )

    def test_verified_mismatch_atomically_changes_only_bank_letter_applicability(self):
        checklist = DocumentChecklist.objects.create(
            loan_application=self.application,
            remarks="Preserve checklist remarks.",
        )
        bank_item = ChecklistItem.objects.create(
            document_checklist=checklist,
            item_code="bank_verification_letter",
            item_label="Bank Verification Letter",
            display_order=10,
            required_flag=False,
            applicable_flag=False,
            completion_status=ChecklistItem.STATUS_NOT_APPLICABLE,
            applicability_source="persisted_signature_match",
            remarks="Preserve item remarks.",
        )

        response = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            {
                "signer_party_type": "borrower",
                "signer_party_id": str(self.application.member_id),
                "signer_name_snapshot": "Signature Test Borrower",
                "signature_method": "scanned",
                "signature_status": "mismatch",
                "signed_at": None,
                "signature_mismatch_flag": True,
            },
            content_type="application/json",
            **self._auth(self.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        checklist.refresh_from_db()
        bank_item.refresh_from_db()
        self.assertEqual(checklist.checklist_status, DocumentChecklist.STATUS_IN_PROGRESS)
        self.assertEqual(checklist.remarks, "Preserve checklist remarks.")
        self.assertTrue(bank_item.required_flag)
        self.assertTrue(bank_item.applicable_flag)
        self.assertEqual(bank_item.completion_status, ChecklistItem.STATUS_PENDING)
        self.assertEqual(bank_item.applicability_source, "verified_signature_mismatch")
        self.assertIsNone(bank_item.applicability_blocker)
        self.assertEqual(bank_item.remarks, "Preserve item remarks.")

        ordinary_signed = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            {
                "signer_party_type": "user",
                "signer_party_id": str(self.actor.pk),
                "signer_name_snapshot": self.actor.full_name,
                "signature_method": "wet_ink",
                "signature_status": "signed",
                "signed_at": "2026-06-22T11:00:00Z",
                "signature_mismatch_flag": False,
            },
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(ordinary_signed.status_code, 200, ordinary_signed.content)
        bank_item.refresh_from_db()
        self.assertTrue(bank_item.applicable_flag)
        self.assertEqual(bank_item.applicability_source, "verified_signature_mismatch")

    def test_unresolved_mismatch_cannot_be_cleared_by_same_signer_capture(self):
        checklist = DocumentChecklist.objects.create(loan_application=self.application)
        bank_item = ChecklistItem.objects.create(
            document_checklist=checklist,
            item_code="bank_verification_letter",
            item_label="Bank Verification Letter",
            display_order=10,
            required_flag=False,
            applicable_flag=False,
            completion_status=ChecklistItem.STATUS_NOT_APPLICABLE,
            applicability_source="persisted_signature_match",
        )
        url = f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/"
        mismatch_payload = {
            "signer_party_type": "borrower",
            "signer_party_id": str(self.application.member_id),
            "signer_name_snapshot": "Signature Test Borrower",
            "signature_method": "wet_ink",
            "signature_status": "mismatch",
            "signed_at": None,
            "signature_mismatch_flag": True,
        }
        first = self.client.post(
            url,
            mismatch_payload,
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(first.status_code, 200, first.content)
        ledger_counts = (
            AuditLog.objects.filter(action__startswith="documents.signature.").count(),
            VersionHistory.objects.filter(
                versioned_entity_type="signature_record"
            ).count(),
            WorkflowEvent.objects.filter(
                workflow_name="loan_document_signature"
            ).count(),
        )

        changed = self.client.post(
            url,
            {
                **mismatch_payload,
                "signature_status": "signed",
                "signed_at": "2026-06-22T11:00:00Z",
                "signature_mismatch_flag": False,
            },
            content_type="application/json",
            **self._auth(self.actor),
        )

        self.assertEqual(changed.status_code, 400, changed.content)
        self.assertEqual(
            changed.json()["error"]["code"], "SIGNATURE_MISMATCH_UNRESOLVED"
        )
        signature = SignatureRecord.objects.get(pk=first.json()["data"]["signature_record_id"])
        bank_item.refresh_from_db()
        self.assertEqual(signature.signature_status, "mismatch")
        self.assertTrue(signature.signature_mismatch_flag)
        self.assertIsNone(signature.mismatch_resolution_type)
        self.assertTrue(bank_item.applicable_flag)
        self.assertEqual(
            (
                AuditLog.objects.filter(
                    action__startswith="documents.signature."
                ).count(),
                VersionHistory.objects.filter(
                    versioned_entity_type="signature_record"
                ).count(),
                WorkflowEvent.objects.filter(
                    workflow_name="loan_document_signature"
                ).count(),
            ),
            ledger_counts,
        )

        replay = self.client.post(
            url,
            mismatch_payload,
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(
            (
                AuditLog.objects.filter(
                    action__startswith="documents.signature."
                ).count(),
                VersionHistory.objects.filter(
                    versioned_entity_type="signature_record"
                ).count(),
                WorkflowEvent.objects.filter(
                    workflow_name="loan_document_signature"
                ).count(),
            ),
            ledger_counts,
        )

    def test_capture_rejects_noncanonical_borrower_identity_without_writes(self):
        response = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            {
                "signer_party_type": "borrower",
                "signer_party_id": str(uuid.uuid4()),
                "signer_name_snapshot": "Caller Supplied Borrower",
                "signature_method": "wet_ink",
                "signature_status": "pending",
                "signed_at": None,
                "signature_mismatch_flag": False,
            },
            content_type="application/json",
            **self._auth(self.actor),
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(
            response.json()["error"]["field_errors"]["signer_party_id"],
            "Signer was not found for this application.",
        )
        self.assertFalse(SignatureRecord.objects.exists())
        self.assertFalse(
            AuditLog.objects.filter(action__startswith="documents.signature.").exists()
        )

    def test_http_serializer_and_direct_module_share_strict_capture_contract(self):
        payload = {
            "signer_party_type": "borrower",
            "signer_party_id": str(self.application.member_id),
            "signer_name_snapshot": "Signature Test Borrower",
            "signature_method": "wet_ink",
            "signature_status": "signed",
            "signed_at": "2026-06-22T10:30:00Z",
            "signature_mismatch_flag": False,
        }
        typed = legal_serializers.SignatureRecordRequest.parse(payload)
        direct = signatures.record(
            actor=self.actor,
            loan_document_id=self.loan_document.pk,
            payload=typed,
            metadata=signatures.RequestMetadata("direct-capture", "", "test"),
        )
        http = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            payload,
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(http.status_code, 200, http.content)
        self.assertEqual(http.json()["data"], direct)

        malformed = {**payload, "signed_at": "2026-06-22T10:30:00"}
        invalid_http = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            malformed,
            content_type="application/json",
            **self._auth(self.actor),
        )
        with self.assertRaises(ValidationError) as direct_error:
            signatures.record(
                actor=self.actor,
                loan_document_id=self.loan_document.pk,
                payload=malformed,
                metadata=signatures.RequestMetadata("invalid-direct", "", "test"),
            )
        self.assertEqual(invalid_http.status_code, 400, invalid_http.content)
        self.assertEqual(
            invalid_http.json()["error"]["field_errors"],
            signatures.validation_field_errors(direct_error.exception),
        )

    def test_canonical_nominee_witness_and_user_identities_are_frozen(self):
        nominee = Nominee.objects.create(
            member=self.application.member,
            loan_application_id=self.application.pk,
            nominee_name="Canonical Nominee",
            gender="female",
            pan_encrypted="encrypted-pan",
            pan_hash="nominee-pan-hash",
            aadhaar_encrypted="encrypted-aadhaar",
            aadhaar_hash="nominee-aadhaar-hash",
            kyc_status="verified",
        )
        self.application.nominee = nominee
        self.application.save(update_fields=["nominee"])
        witness = Witness.objects.create(
            loan_application=self.application,
            member=self.application.member,
            witness_name="Canonical Witness",
            pan_encrypted="encrypted-pan",
            pan_hash="witness-pan-hash",
            aadhaar_encrypted="encrypted-aadhaar",
            aadhaar_hash="witness-aadhaar-hash",
        )
        identities = (
            ("nominee", nominee.pk, nominee.nominee_name),
            ("witness", witness.pk, witness.witness_name),
            ("user", self.actor.pk, self.actor.full_name),
        )

        for party_type, party_id, name in identities:
            response = self.client.post(
                f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
                {
                    "signer_party_type": party_type,
                    "signer_party_id": str(party_id),
                    "signer_name_snapshot": name,
                    "signature_method": "wet_ink",
                    "signature_status": "pending",
                    "signed_at": None,
                    "signature_mismatch_flag": False,
                },
                content_type="application/json",
                **self._auth(self.actor),
            )
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(response.json()["data"]["signer_name_snapshot"], name)

        self.assertEqual(SignatureRecord.objects.count(), 3)

    def test_exact_replay_uses_frozen_name_after_canonical_owner_changes(self):
        url = f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/"
        payload = {
            "signer_party_type": "borrower",
            "signer_party_id": str(self.application.member_id),
            "signer_name_snapshot": "Signature Test Borrower",
            "signature_method": "wet_ink",
            "signature_status": "pending",
            "signed_at": None,
            "signature_mismatch_flag": False,
        }
        first = self.client.post(
            url, payload, content_type="application/json", **self._auth(self.actor)
        )
        self.assertEqual(first.status_code, 200, first.content)
        self.application.member.legal_name = "Changed Canonical Borrower"
        self.application.member.save(update_fields=["legal_name"])

        replay = self.client.post(
            url, payload, content_type="application/json", **self._auth(self.actor)
        )
        changed_name = self.client.post(
            url,
            {**payload, "signer_name_snapshot": "Changed Canonical Borrower"},
            content_type="application/json",
            **self._auth(self.actor),
        )

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(changed_name.status_code, 400, changed_name.content)
        record = SignatureRecord.objects.get()
        self.assertEqual(record.signer_name_snapshot, "Signature Test Borrower")

    def test_mismatch_resolution_requires_a_distinct_immutable_capture_maker(self):
        mismatch = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            {
                "signer_party_type": "borrower",
                "signer_party_id": str(self.application.member_id),
                "signer_name_snapshot": "Signature Test Borrower",
                "signature_method": "wet_ink",
                "signature_status": "mismatch",
                "signed_at": None,
                "signature_mismatch_flag": True,
            },
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(mismatch.status_code, 200, mismatch.content)
        signature = SignatureRecord.objects.get(
            pk=mismatch.json()["data"]["signature_record_id"]
        )
        self.assertEqual(signature.captured_by_user_id, self.actor.pk)
        bank_letter = self._legal_document(
            "bank_verification_letter", "same-maker-bank-letter.pdf", "e", self.actor
        )
        company_secretary = self._user(
            "company_secretary", "documents.signature.resolve_mismatch"
        )
        self.actor.primary_role = company_secretary.primary_role
        self.actor.save(update_fields=["primary_role"])

        response = self.client.post(
            f"/api/v1/signature-records/{signature.pk}/resolve-mismatch/",
            {
                "mismatch_resolution_type": "bank_verification_letter",
                "mismatch_resolution_document_id": str(bank_letter.pk),
                "remarks": "Role changed but identity did not.",
            },
            content_type="application/json",
            **self._auth(self.actor),
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            response.json()["error"]["field_errors"],
            {"mismatch_resolution_type": "The capture maker and resolver must be different users."},
        )
        signature.refresh_from_db()
        self.assertIsNone(signature.mismatch_resolution_type)
        self.assertFalse(
            AuditLog.objects.filter(
                action="documents.signature.mismatch_resolved"
            ).exists()
        )

    def test_latest_material_signature_editor_becomes_maker_and_cannot_resolve(self):
        url = f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/"
        pending = {
            "signer_party_type": "borrower",
            "signer_party_id": str(self.application.member_id),
            "signer_name_snapshot": "Signature Test Borrower",
            "signature_method": "wet_ink",
            "signature_status": "pending",
            "signed_at": None,
            "signature_mismatch_flag": False,
        }
        first = self.client.post(
            url, pending, content_type="application/json", **self._auth(self.actor)
        )
        self.assertEqual(first.status_code, 200, first.content)
        second_maker = self._user("signature_handoff_editor")
        second_maker.primary_role = self.actor.primary_role
        second_maker.save(update_fields=["primary_role"])
        mismatch = self.client.post(
            url,
            {
                **pending,
                "signature_status": "mismatch",
                "signature_mismatch_flag": True,
            },
            content_type="application/json",
            **self._auth(second_maker),
        )
        self.assertEqual(mismatch.status_code, 200, mismatch.content)
        record = SignatureRecord.objects.get(pk=first.json()["data"]["signature_record_id"])
        self.assertEqual(record.captured_by_user_id, second_maker.pk)

        secretary = self._user(
            "company_secretary", "documents.signature.resolve_mismatch"
        )
        second_maker.primary_role = secretary.primary_role
        second_maker.save(update_fields=["primary_role"])
        denied = self.client.post(
            f"/api/v1/signature-records/{record.pk}/resolve-mismatch/",
            {
                "mismatch_resolution_type": "bank_verification_letter",
                "mismatch_resolution_document_id": str(uuid.uuid4()),
                "remarks": "Must fail before evidence lookup.",
            },
            content_type="application/json",
            **self._auth(second_maker),
        )
        self.assertEqual(denied.status_code, 400, denied.content)
        self.assertEqual(
            denied.json()["error"]["field_errors"],
            {
                "mismatch_resolution_type": (
                    "The capture maker and resolver must be different users."
                )
            },
        )
        history = list(
            VersionHistory.objects.filter(versioned_entity_type="signature_record")
            .order_by("created_at")
            .values_list("old_value_json", "new_value_json")
        )
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0][1]["captured_by_user_id"], str(self.actor.pk))
        self.assertEqual(history[1][0]["captured_by_user_id"], str(self.actor.pk))
        self.assertEqual(history[1][1]["captured_by_user_id"], str(second_maker.pk))

    def test_authorized_resolution_hides_unknown_and_wrong_stage_signature_ids(self):
        signature = SignatureRecord.objects.create(
            loan_document=self.loan_document,
            signer_party_type="borrower",
            signer_party_id=self.application.member_id,
            signer_name_snapshot="Signature Test Borrower",
            signature_method="wet_ink",
            signature_status="mismatch",
            signature_mismatch_flag=True,
            captured_by_user=self.actor,
            verified_by_user=self.actor,
            verified_at="2026-06-22T10:00:00Z",
        )
        self.application.application_status = LoanApplication.STATUS_DRAFT
        self.application.save(update_fields=["application_status"])
        resolver = self._user(
            "company_secretary", "documents.signature.resolve_mismatch"
        )
        payload = {
            "mismatch_resolution_type": "bank_verification_letter",
            "mismatch_resolution_document_id": str(uuid.uuid4()),
            "remarks": None,
        }

        wrong_stage = self.client.post(
            f"/api/v1/signature-records/{signature.pk}/resolve-mismatch/",
            payload,
            content_type="application/json",
            **self._auth(resolver),
        )
        unknown = self.client.post(
            f"/api/v1/signature-records/{uuid.uuid4()}/resolve-mismatch/",
            payload,
            content_type="application/json",
            **self._auth(resolver),
        )

        self.assertEqual(wrong_stage.status_code, 404, wrong_stage.content)
        self.assertEqual(unknown.status_code, 404, unknown.content)
        self.assertEqual(wrong_stage.json()["error"], unknown.json()["error"])
        self.assertFalse(
            AuditLog.objects.filter(
                action="documents.signature.mismatch_resolved"
            ).exists()
        )

    def test_company_secretary_resolves_mismatch_with_retained_bank_letter_metadata(self):
        checklist = DocumentChecklist.objects.create(loan_application=self.application)
        bank_item = ChecklistItem.objects.create(
            document_checklist=checklist,
            item_code="bank_verification_letter",
            item_label="Bank Verification Letter",
            display_order=10,
            required_flag=False,
            applicable_flag=False,
            completion_status=ChecklistItem.STATUS_NOT_APPLICABLE,
            applicability_source="persisted_signature_match",
        )
        mismatch = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            {
                "signer_party_type": "borrower",
                "signer_party_id": str(self.application.member_id),
                "signer_name_snapshot": "Signature Test Borrower",
                "signature_method": "wet_ink",
                "signature_status": "mismatch",
                "signed_at": None,
                "signature_mismatch_flag": True,
            },
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(mismatch.status_code, 200, mismatch.content)
        signature_id = mismatch.json()["data"]["signature_record_id"]
        bank_letter = self._legal_document(
            "bank_verification_letter", "bank-letter.pdf", "b", self.actor
        )
        resolver = self._user(
            "company_secretary",
            "documents.signature.resolve_mismatch",
        )

        response = self.client.post(
            f"/api/v1/signature-records/{signature_id}/resolve-mismatch/",
            {
                "mismatch_resolution_type": "bank_verification_letter",
                "mismatch_resolution_document_id": str(bank_letter.document_id),
                "remarks": "Signed and stamped bank letter inspected.",
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-signature-resolve",
            **self._auth(resolver),
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
        self.assertEqual(data["entity_type"], "signature_record")
        self.assertEqual(data["entity_id"], signature_id)
        self.assertEqual(data["previous_status"], "mismatch")
        self.assertEqual(data["new_status"], "resolved")
        self.assertIsNotNone(data["workflow_event_id"])
        self.assertEqual(data["available_actions"], [])
        self.assertNotIn("storage_key", data)
        bank_item.refresh_from_db()
        self.assertFalse(bank_item.applicable_flag)
        self.assertFalse(bank_item.required_flag)
        self.assertEqual(bank_item.completion_status, ChecklistItem.STATUS_NOT_APPLICABLE)
        self.assertEqual(
            bank_item.applicability_source,
            "verified_signature_match_or_resolution",
        )
        resolution_audit = AuditLog.objects.get(
            action="documents.signature.mismatch_resolved"
        )
        self.assertEqual(resolution_audit.actor_user, resolver)
        self.assertEqual(resolution_audit.new_value_json["request_id"], "req-signature-resolve")
        signature = SignatureRecord.objects.get(pk=signature_id)
        self.assertEqual(
            data["workflow_event_id"],
            str(signature.mismatch_resolution_workflow_event_id),
        )
        self.assertEqual(
            signature.mismatch_resolution_document_id,
            bank_letter.document_id,
        )
        direct_replay = signatures.resolve_mismatch(
            actor=resolver,
            signature_record_id=signature_id,
            payload=legal_serializers.SignatureMismatchResolutionRequest.parse(
                {
                    "mismatch_resolution_type": "bank_verification_letter",
                    "mismatch_resolution_document_id": str(bank_letter.document_id),
                    "remarks": "Signed and stamped bank letter inspected.",
                }
            ),
            metadata=signatures.RequestMetadata("direct-replay", "", "test"),
        )
        self.assertEqual(direct_replay, data)
        self.assertEqual(
            AuditLog.objects.filter(
                action="documents.signature.mismatch_resolved"
            ).count(),
            1,
        )

    def test_resolution_rolls_back_when_completed_bank_letter_would_be_reversed(self):
        checklist = DocumentChecklist.objects.create(loan_application=self.application)
        bank_item = ChecklistItem.objects.create(
            document_checklist=checklist,
            item_code="bank_verification_letter",
            item_label="Bank Verification Letter",
            display_order=10,
            required_flag=True,
            applicable_flag=True,
            completion_status=ChecklistItem.STATUS_COMPLETE,
            applicability_source="verified_signature_mismatch",
            verified_by_user=self.actor,
            verified_at="2026-06-22T10:00:00Z",
            remarks="Completed evidence must survive.",
        )
        signature = SignatureRecord.objects.create(
            loan_document=self.loan_document,
            signer_party_type="borrower",
            signer_party_id=self.application.member_id,
            signer_name_snapshot="Signature Test Borrower",
            signature_method="wet_ink",
            signature_status="mismatch",
            signature_mismatch_flag=True,
            captured_by_user=self.actor,
            verified_by_user=self.actor,
            verified_at="2026-06-22T10:00:00Z",
        )
        bank_letter = self._legal_document(
            "bank_verification_letter", "completed-bank-letter.pdf", "c", self.actor
        )
        resolver = self._user(
            "company_secretary",
            "documents.signature.resolve_mismatch",
        )

        response = self.client.post(
            f"/api/v1/signature-records/{signature.pk}/resolve-mismatch/",
            {
                "mismatch_resolution_type": "bank_verification_letter",
                "mismatch_resolution_document_id": str(bank_letter.pk),
                "remarks": "Correction requires the owning checklist workflow.",
            },
            content_type="application/json",
            **self._auth(resolver),
        )

        self.assertEqual(response.status_code, 409, response.content)
        signature.refresh_from_db()
        bank_item.refresh_from_db()
        self.assertIsNone(signature.mismatch_resolution_type)
        self.assertEqual(bank_item.completion_status, ChecklistItem.STATUS_COMPLETE)
        self.assertTrue(bank_item.applicable_flag)
        self.assertEqual(bank_item.remarks, "Completed evidence must survive.")
        self.assertFalse(
            AuditLog.objects.filter(action="documents.signature.mismatch_resolved").exists()
        )

    def test_capture_replay_change_and_invalid_combinations_are_zero_write_safe(self):
        url = f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/"
        payload = {
            "signer_party_type": "borrower",
            "signer_party_id": str(self.application.member_id),
            "signer_name_snapshot": "Signature Test Borrower",
            "signature_method": "wet_ink",
            "signature_status": "pending",
            "signed_at": None,
            "signature_mismatch_flag": False,
        }
        first = self.client.post(url, payload, content_type="application/json", **self._auth(self.actor))
        replay = self.client.post(url, payload, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])
        self.assertEqual(SignatureRecord.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.signature.").count(), 1)

        payload.update(
            signature_status="signed",
            signed_at="2026-06-22T10:30:00Z",
        )
        changed = self.client.post(url, payload, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(changed.status_code, 200, changed.content)
        self.assertEqual(changed.json()["data"]["signature_record_id"], first.json()["data"]["signature_record_id"])
        self.assertEqual(changed.json()["data"]["signed_at"], "2026-06-22T10:30:00Z")
        history = list(
            VersionHistory.objects.filter(versioned_entity_type="signature_record").order_by("created_at")
        )
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].new_value_json["signer_name_snapshot"], "Signature Test Borrower")
        self.assertEqual(history[1].old_value_json["signature_status"], "pending")

        payload.update(signature_status="pending", signature_mismatch_flag=True)
        invalid = self.client.post(url, payload, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(invalid.status_code, 400, invalid.content)
        self.assertEqual(SignatureRecord.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.signature.").count(), 2)

    def test_resolution_requires_source_approved_evidence_and_exact_replay_is_zero_write(self):
        signature = SignatureRecord.objects.create(
            loan_document=self.loan_document,
            signer_party_type="borrower",
            signer_party_id=self.application.member_id,
            signer_name_snapshot="Signature Test Borrower",
            signature_method="wet_ink",
            signature_status="mismatch",
            signature_mismatch_flag=True,
            captured_by_user=self.actor,
            verified_by_user=self.actor,
            verified_at="2026-06-22T10:00:00Z",
        )
        resolver = self._user("company_secretary", "documents.signature.resolve_mismatch")
        wrong_type = self.loan_document.document
        url = f"/api/v1/signature-records/{signature.pk}/resolve-mismatch/"
        payload = {
            "mismatch_resolution_type": "borrower_declaration",
            "mismatch_resolution_document_id": str(wrong_type.pk),
            "remarks": "Wrong type.",
        }
        wrong = self.client.post(url, payload, content_type="application/json", **self._auth(resolver))
        self.assertEqual(wrong.status_code, 409, wrong.content)

        declaration_file = self._legal_document(
            "borrower_declaration", "borrower-declaration.pdf", "d", self.actor
        )
        declaration = LoanDocument.objects.get(document=declaration_file)
        unstamped = {**payload, "mismatch_resolution_document_id": str(declaration_file.pk)}
        rejected = self.client.post(url, unstamped, content_type="application/json", **self._auth(resolver))
        self.assertEqual(rejected.status_code, 409, rejected.content)
        StampDutyRecord.objects.create(
            loan_document=declaration,
            stamp_paper_amount="500.00",
            stamp_type="physical",
            stamp_number="DECL-500",
            stamp_purchase_date=date(2026, 6, 20),
            executed_date=date(2026, 6, 22),
            prepared_by_user=self.actor,
            verified_by_user=resolver,
            status="adequate",
            remarks="Non-judicial stamp verified.",
        )
        accepted_payload = {
            **unstamped,
            "remarks": "Stamped borrower declaration inspected.",
        }
        accepted = self.client.post(url, accepted_payload, content_type="application/json", **self._auth(resolver))
        replay = self.client.post(url, accepted_payload, content_type="application/json", **self._auth(resolver))
        self.assertEqual(accepted.status_code, 200, accepted.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(accepted.json()["data"], replay.json()["data"])
        self.assertEqual(AuditLog.objects.filter(action="documents.signature.mismatch_resolved").count(), 1)

        capture_url = f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/"
        original_capture = {
            "signer_party_type": "borrower",
            "signer_party_id": str(self.application.member_id),
            "signer_name_snapshot": "Signature Test Borrower",
            "signature_method": "wet_ink",
            "signature_status": "mismatch",
            "signed_at": None,
            "signature_mismatch_flag": True,
        }
        capture_replay = self.client.post(
            capture_url,
            original_capture,
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(capture_replay.status_code, 200, capture_replay.content)
        self.assertEqual(
            capture_replay.json()["data"]["mismatch_resolution_type"],
            "borrower_declaration",
        )
        changed_capture = self.client.post(
            capture_url,
            {**original_capture, "signer_name_snapshot": "Changed live name"},
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(changed_capture.status_code, 400, changed_capture.content)
        signature.refresh_from_db()
        self.assertEqual(signature.signer_name_snapshot, "Signature Test Borrower")
        self.assertEqual(signature.mismatch_resolution_type, "borrower_declaration")

        changed_payload = {**accepted_payload, "remarks": "Attempt to replace history."}
        changed = self.client.post(url, changed_payload, content_type="application/json", **self._auth(resolver))
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(AuditLog.objects.filter(action="documents.signature.mismatch_resolved").count(), 1)

    def test_action_specific_roles_and_unrelated_targets_are_nondisclosing_and_zero_write(self):
        company_secretary = self._user("company_secretary", "documents.signature.record")
        record_response = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            {
                "signer_party_type": "borrower",
                "signer_party_id": str(self.application.member_id),
                "signer_name_snapshot": "Signature Test Borrower",
                "signature_method": "wet_ink",
                "signature_status": "pending",
                "signed_at": None,
                "signature_mismatch_flag": False,
            },
            content_type="application/json",
            **self._auth(company_secretary),
        )
        self.assertEqual(record_response.status_code, 403, record_response.content)

        mismatch = SignatureRecord.objects.create(
            loan_document=self.loan_document,
            signer_party_type="borrower",
            signer_party_id=self.application.member_id,
            signer_name_snapshot="Signature Test Borrower",
            signature_method="wet_ink",
            signature_status="mismatch",
            signature_mismatch_flag=True,
            verified_by_user=self.actor,
            verified_at="2026-06-22T10:00:00Z",
        )
        compliance_resolver = self._user(
            "compliance_resolver_test",
            "documents.signature.resolve_mismatch",
        )
        denied = self.client.post(
            f"/api/v1/signature-records/{mismatch.pk}/resolve-mismatch/",
            {
                "mismatch_resolution_type": "bank_verification_letter",
                "mismatch_resolution_document_id": str(uuid.uuid4()),
                "remarks": None,
            },
            content_type="application/json",
            **self._auth(compliance_resolver),
        )
        self.assertEqual(denied.status_code, 403, denied.content)

        self.application.application_status = LoanApplication.STATUS_DRAFT
        self.application.save(update_fields=["application_status"])
        stage_denied = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/signatures/",
            {
                "signer_party_type": "borrower",
                "signer_party_id": str(self.application.member_id),
                "signer_name_snapshot": "Signature Test Borrower",
                "signature_method": "wet_ink",
                "signature_status": "pending",
                "signed_at": None,
                "signature_mismatch_flag": False,
            },
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(stage_denied.status_code, 403, stage_denied.content)
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.signature.").count(), 0)

    def _user(self, role_code, *permission_codes):
        role, _ = Role.objects.get_or_create(
            role_code=role_code,
            defaults={
                "role_name": role_code.replace("_", " ").title(),
                "status": "active",
            },
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "documents",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)
        user = User.objects.create(
            full_name=role.role_name,
            email=f"signature-{User.objects.count() + 1}@example.com",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save(update_fields=["password_hash"])
        return user

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"}

    def _legal_document(self, document_type, file_name, checksum_character, actor):
        document = DocumentFile.objects.create(
            file_name=file_name,
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=8,
            storage_provider="local",
            storage_key=f"tests/{file_name}",
            checksum_sha256=checksum_character * 64,
            uploaded_by_user=actor,
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code=f"signature-{document_type}-{DocumentTemplate.objects.count() + 1}",
            template_name=document_type.replace("_", " ").title(),
            document_type=document_type,
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=document,
            approval_status="approved",
            effective_from="2026-01-01",
        )
        LoanDocument.objects.create(
            loan_application=self.application,
            document_type=document_type,
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=document,
            output_format="pdf",
            generation_status=LoanDocument.GENERATION_GENERATED,
            execution_status=LoanDocument.EXECUTION_PENDING,
            verification_status=LoanDocument.VERIFICATION_PENDING,
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=document.pk,
            renderer_validated_checksum_sha256=document.checksum_sha256,
        )
        return document


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative signature five-worker races require PostgreSQL.",
)
class SignatureConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = SignatureMismatchApiTests(
            methodName="test_compliance_records_pending_signature_with_attributable_evidence"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_five_capture_workers_retain_one_current_outcome_and_ledger(self):
        barrier = Barrier(5)
        actor_id = self.fixture.actor.pk
        loan_document_id = self.fixture.loan_document.pk
        payload = {
            "signer_party_type": "borrower",
            "signer_party_id": str(self.fixture.application.member_id),
            "signer_name_snapshot": "Signature Test Borrower",
            "signature_method": "wet_ink",
            "signature_status": "mismatch",
            "signed_at": None,
            "signature_mismatch_flag": True,
        }

        def capture(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=actor_id)
                barrier.wait()
                return signatures.record(
                    actor=actor,
                    loan_document_id=loan_document_id,
                    payload=payload,
                    metadata=signatures.RequestMetadata(
                        f"capture-race-{index}",
                        f"203.0.113.{index + 20}",
                        f"capture-worker-{index}",
                    ),
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(capture, range(5)))

        self.assertEqual(len({row["signature_record_id"] for row in results}), 1)
        current = SignatureRecord.objects.get()
        self.assertEqual(current.signature_status, "mismatch")
        self.assertEqual(current.captured_by_user_id, actor_id)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.signature.created").count(), 1
        )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="signature_record"
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="loan_document_signature"
            ).count(),
            1,
        )

    def test_five_resolution_workers_retain_one_winner_and_action_identity(self):
        maker = self.fixture.actor
        signature = signatures.record(
            actor=maker,
            loan_document_id=self.fixture.loan_document.pk,
            payload={
                "signer_party_type": "borrower",
                "signer_party_id": str(self.fixture.application.member_id),
                "signer_name_snapshot": "Signature Test Borrower",
                "signature_method": "wet_ink",
                "signature_status": "mismatch",
                "signed_at": None,
                "signature_mismatch_flag": True,
            },
            metadata=signatures.RequestMetadata("resolution-seed", "", "race"),
        )
        bank_letter = self.fixture._legal_document(
            "bank_verification_letter", "resolution-race.pdf", "f", maker
        )
        resolver = self.fixture._user(
            "company_secretary", "documents.signature.resolve_mismatch"
        )
        barrier = Barrier(5)

        def resolve(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=resolver.pk)
                barrier.wait()
                try:
                    result = signatures.resolve_mismatch(
                        actor=actor,
                        signature_record_id=signature["signature_record_id"],
                        payload={
                            "mismatch_resolution_type": "bank_verification_letter",
                            "mismatch_resolution_document_id": str(bank_letter.pk),
                            "remarks": f"resolution-worker-{index}",
                        },
                        metadata=signatures.RequestMetadata(
                            f"resolution-race-{index}",
                            f"203.0.113.{index + 30}",
                            f"resolution-worker-{index}",
                        ),
                    )
                    return "won", result
                except signatures.InvalidState as exc:
                    return "lost", str(exc)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(resolve, range(5)))

        winners = [result for outcome, result in results if outcome == "won"]
        losers = [result for outcome, result in results if outcome == "lost"]
        self.assertEqual(len(winners), 1)
        self.assertEqual(len(losers), 4)
        current = SignatureRecord.objects.get(pk=signature["signature_record_id"])
        self.assertEqual(current.mismatch_resolution_type, "bank_verification_letter")
        self.assertEqual(
            winners[0]["workflow_event_id"],
            str(current.mismatch_resolution_workflow_event_id),
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="documents.signature.mismatch_resolved"
            ).count(),
            1,
        )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="signature_record"
            ).count(),
            2,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="loan_document_signature"
            ).count(),
            2,
        )
