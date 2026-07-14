import uuid
from datetime import date

from django.test import Client, TestCase

from sfpcl_credit.applications.models import LoanApplication
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
from sfpcl_credit.members.models import Member
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
                "signer_party_type": "nominee",
                "signer_party_id": str(uuid.uuid4()),
                "signer_name_snapshot": "Ordinary Signed Nominee",
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
        self.assertEqual(data["mismatch_resolution_type"], "bank_verification_letter")
        self.assertEqual(data["mismatch_resolution_document_id"], str(bank_letter.document_id))
        self.assertEqual(data["mismatch_resolution_document_name"], "bank-letter.pdf")
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
            "signer_name_snapshot": "Frozen Borrower Name",
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
        self.assertEqual(history[0].new_value_json["signer_name_snapshot"], "Frozen Borrower Name")
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
        self.assertEqual(changed_capture.status_code, 409, changed_capture.content)
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
