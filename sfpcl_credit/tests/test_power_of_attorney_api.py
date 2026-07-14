from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from threading import Barrier
from tempfile import TemporaryDirectory
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
    NotarisationRecord,
    PowerOfAttorney,
    SignatureRecord,
    SecurityPackage,
    StampDutyRecord,
)
from sfpcl_credit.members.models import Member, Nominee
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent
from sfpcl_credit.legal_documents.modules import power_of_attorney
from sfpcl_credit.legal_documents.modules import document_renderer
from sfpcl_credit.legal_documents.modules import signatures, stamp_notary


class PowerOfAttorneyApiTests(TestCase):
    password = "PowerOfAttorneyPass123!"

    def setUp(self):
        self.client = Client()
        self.document_storage = TemporaryDirectory()
        self.addCleanup(self.document_storage.cleanup)
        self.compliance = self._user(
            "compliance_team_member",
            "security.package.read",
            "security.package.create",
            "security.poa.manage",
            "documents.signature.record",
            "documents.stamp.record",
            "documents.notary.record",
        )
        self.member = Member.objects.create(
            member_number="MEM-POA-001",
            member_type="individual_farmer",
            legal_name="Power Borrower",
            display_name="Power Borrower",
            folio_number="FOL-POA-001",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        self.nominee = Nominee.objects.create(
            member=self.member,
            nominee_name="Power Nominee",
            gender="female",
            pan_encrypted="encrypted-pan",
            pan_hash="poa-pan-hash",
            aadhaar_encrypted="encrypted-aadhaar",
            aadhaar_hash="poa-aadhaar-hash",
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="LO-POA-001",
            member=self.member,
            nominee=self.nominee,
            borrower_type="individual_farmer",
            received_by_user=self.compliance,
            created_by_user=self.compliance,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
        )
        checklist = DocumentChecklist.objects.create(loan_application=self.application)
        self.poa_item = ChecklistItem.objects.create(
            document_checklist=checklist,
            item_code="poa",
            item_label="Power of Attorney",
            display_order=4,
            required_flag=True,
            applicable_flag=True,
            completion_status=ChecklistItem.STATUS_PENDING,
            applicability_source="source_always_required",
            remarks="Preserve checklist ownership.",
        )

    def test_package_refresh_is_replay_safe_and_preserves_checklist_truth(self):
        url = f"/api/v1/loan-applications/{self.application.pk}/security-package/refresh/"
        first = self.client.post(
            url,
            {},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-package-create",
            HTTP_USER_AGENT="PoA Test Agent",
            REMOTE_ADDR="203.0.113.40",
            **self._auth(self.compliance),
        )
        self.assertEqual(first.status_code, 200, first.content)
        assert_success_envelope(self, first.json())
        data = first.json()["data"]
        self.assertEqual(data["loan_application_id"], str(self.application.pk))
        self.assertEqual(data["security_status"], "pending")
        self.assertTrue(data["poa_required_flag"])
        self.assertFalse(data["security_ready_flag"])
        self.assertIsNone(data["power_of_attorney"])

        replay = self.client.post(url, {}, content_type="application/json", **self._auth(self.compliance))
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], data)
        self.assertEqual(AuditLog.objects.filter(action="security.package.created").count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="security_package").count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="security_package").count(), 1)
        audit = AuditLog.objects.get(action="security.package.created")
        self.assertEqual(audit.new_value_json["request_id"], "req-package-create")
        self.assertEqual(audit.ip_address, "203.0.113.40")

        self.poa_item.refresh_from_db()
        self.assertEqual(self.poa_item.completion_status, ChecklistItem.STATUS_PENDING)
        self.assertIsNone(self.poa_item.verified_by_user_id)
        self.assertEqual(self.poa_item.remarks, "Preserve checklist ownership.")

        read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/",
            **self._auth(self.compliance),
        )
        self.assertEqual(read.status_code, 200, read.content)
        self.assertEqual(read.json()["data"], data)

    def test_missing_manage_permission_denies_before_payload_and_writes_nothing(self):
        package = self._refresh_package()
        RolePermission.objects.filter(
            role=self.compliance.primary_role,
            permission__permission_code="security.poa.manage",
        ).delete()
        response = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/",
            {"status": "active"},
            content_type="application/json",
            **self._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(PowerOfAttorney.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="security.poa.").count(), 0)

    def test_missing_projection_target_rolls_back_poa_and_success_evidence(self):
        package = self._refresh_package()
        attorney = self._user("company_secretary", "security.poa.manage")
        document, stamp, notary = self._poa_evidence()
        self.poa_item.delete()
        response = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/",
            {
                "borrower_member_id": str(self.member.pk),
                "nominee_id": str(self.nominee.pk),
                "attorney_user_id": str(attorney.pk),
                "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
                "loan_document_id": str(document.pk),
                "stamp_duty_record_id": str(stamp.pk),
                "notarisation_record_id": str(notary.pk),
                "execution_status": "pending",
                "effective_from": None,
                "status": "draft",
            },
            content_type="application/json",
            **self._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(PowerOfAttorney.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="security.poa.").count(), 0)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 0)

    def test_compliance_prepares_one_replay_safe_draft_from_canonical_facts(self):
        package = self._refresh_package()
        attorney = self._user("company_secretary", "security.poa.manage")
        loan_document, stamp, notary = self._poa_evidence()
        payload = {
            "borrower_member_id": str(self.member.pk),
            "nominee_id": str(self.nominee.pk),
            "attorney_user_id": str(attorney.pk),
            "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
            "loan_document_id": str(loan_document.pk),
            "stamp_duty_record_id": str(stamp.pk),
            "notarisation_record_id": str(notary.pk),
            "execution_status": "pending",
            "effective_from": None,
            "status": "draft",
        }
        url = f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/"
        negated = self.client.post(
            url,
            {
                **payload,
                "purpose_summary": (
                    "Company Secretary must not initiate sale of shares on default."
                ),
            },
            content_type="application/json",
            **self._auth(self.compliance),
        )
        self.assertEqual(negated.status_code, 400, negated.content)
        self.assertEqual(PowerOfAttorney.objects.count(), 0)
        first = self.client.post(
            url,
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-poa-draft",
            **self._auth(self.compliance),
        )
        self.assertEqual(first.status_code, 200, first.content)
        assert_success_envelope(self, first.json())
        data = first.json()["data"]
        self.assertEqual(data["status"], "draft")
        self.assertEqual(data["execution_status"], "pending")
        self.assertEqual(data["prepared_by_user_id"], str(self.compliance.pk))
        self.assertIsNone(data["verified_by_user_id"])
        self.assertNotIn("document_download_url", data)

        replay = self.client.post(url, payload, content_type="application/json", **self._auth(self.compliance))
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], data)
        self.assertEqual(PowerOfAttorney.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="security.poa.created").count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 1)

        read = self.client.get(url, **self._auth(self.compliance))
        self.assertEqual(read.status_code, 200, read.content)
        self.assertEqual(read.json()["data"], data)
        self.poa_item.refresh_from_db()
        self.assertEqual(self.poa_item.completion_status, "pending")
        self.assertEqual(self.poa_item.poa_execution_status, "pending")
        self.assertEqual(self.poa_item.poa_status, "draft")

    def test_company_secretary_activates_only_with_current_maker_checker_and_signatures(self):
        package = self._refresh_package()
        attorney = self._user(
            "company_secretary", "security.poa.manage", "security.package.read",
            "documents.stamp.record", "documents.notary.record",
        )
        document, stamp, notary = self._poa_evidence()
        draft = {
            "borrower_member_id": str(self.member.pk),
            "nominee_id": str(self.nominee.pk),
            "attorney_user_id": str(attorney.pk),
            "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
            "loan_document_id": str(document.pk),
            "stamp_duty_record_id": str(stamp.pk),
            "notarisation_record_id": str(notary.pk),
            "execution_status": "pending",
            "effective_from": None,
            "status": "draft",
        }
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/",
            draft, content_type="application/json", **self._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        poa_id = created.json()["data"]["power_of_attorney_id"]

        stamp_notary.record_stamp(
            actor=attorney, loan_document_id=document.pk,
            payload={
                "stamp_paper_amount": "500.00", "stamp_type": "physical",
                "stamp_number": "MH-POA-001", "stamp_purchase_date": "2026-07-13",
                "executed_date": "2026-07-14", "status": "adequate",
                "remarks": "Verified through 008D2.",
            },
            metadata=stamp_notary.RequestMetadata("poa-stamp-verify", "", ""),
        )
        notary_evidence = self._notary_evidence()
        stamp_notary.record_notary(
            actor=attorney, loan_document_id=document.pk,
            payload={
                "notary_name": "Verified Notary",
                "notary_registration_number": "NOT-POA-001",
                "notarised_date": "2026-07-14", "status": "completed",
                "evidence_document_id": notary_evidence.pk,
                "remarks": "Verified through 008D2.",
            },
            metadata=stamp_notary.RequestMetadata("poa-notary-verify", "", ""),
        )
        signed_at = timezone.now()
        signature_rows = []
        for party_type, party_id, party_name in (
            ("borrower", self.member.pk, self.member.legal_name),
            ("nominee", self.nominee.pk, self.nominee.nominee_name),
        ):
            signatures.record(
                actor=self.compliance, loan_document_id=document.pk,
                payload={
                    "signer_party_type": party_type,
                    "signer_party_id": party_id,
                    "signer_name_snapshot": party_name,
                    "signature_method": "wet_ink", "signature_status": "signed",
                    "signed_at": signed_at.isoformat(), "signature_mismatch_flag": False,
                },
                metadata=signatures.RequestMetadata(
                    f"poa-{party_type}-signature", "", ""
                ),
            )
            signature_rows.append(SignatureRecord.objects.get(
                loan_document=document, signer_party_type=party_type
            ))
        for row in signature_rows:
            row.captured_by_user = None
            row.save(update_fields=["captured_by_user"])

        active = {**draft, "execution_status": "executed", "effective_from": "2026-07-14", "status": "active"}
        url = f"/api/v1/power-of-attorneys/{poa_id}/"
        legacy_denied = self.client.patch(
            url, active, content_type="application/json", **self._auth(attorney),
        )
        self.assertEqual(legacy_denied.status_code, 400, legacy_denied.content)
        self.assertEqual(
            VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 1
        )
        for row in signature_rows:
            row.captured_by_user = self.compliance
            row.save(update_fields=["captured_by_user"])
        Member.objects.filter(pk=self.member.pk).update(legal_name="Renamed Borrower")
        Nominee.objects.filter(pk=self.nominee.pk).update(nominee_name="Renamed Nominee")
        response = self.client.patch(
            url, active, content_type="application/json",
            HTTP_X_REQUEST_ID="req-poa-active", **self._auth(attorney),
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["execution_status"], "executed")
        self.assertEqual(data["verified_by_user_id"], str(attorney.pk))
        self.assertEqual(data["prepared_by_user_id"], str(self.compliance.pk))

        replay = self.client.patch(url, active, content_type="application/json", **self._auth(attorney))
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], data)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 2)
        self.assertEqual(AuditLog.objects.filter(action="security.poa.changed").count(), 1)
        self.poa_item.refresh_from_db()
        self.assertEqual(self.poa_item.completion_status, "pending")
        self.assertIsNone(self.poa_item.verified_by_user_id)
        self.assertEqual(self.poa_item.poa_execution_status, "executed")
        self.assertEqual(self.poa_item.poa_status, "active")
        package_read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/",
            **self._auth(attorney),
        )
        self.assertEqual(package_read.json()["data"]["security_status"], "pending")
        self.assertFalse(package_read.json()["data"]["security_ready_flag"])

        forbidden_state = self.client.patch(
            url, {**active, "status": "invoked"}, content_type="application/json",
            **self._auth(attorney),
        )
        self.assertEqual(forbidden_state.status_code, 400, forbidden_state.content)
        self.assertEqual(AuditLog.objects.filter(action="security.poa.changed").count(), 1)

    def _refresh_package(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/refresh/",
            {}, content_type="application/json", **self._auth(self.compliance)
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]

    def _poa_evidence(self):
        generation_tests = import_module(
            "sfpcl_credit.tests.test_loan_document_generation_api"
        )
        template_bytes = generation_tests.LoanDocumentGenerationApiTests._genuine_docx_fixture(
            ["borrower_name"]
        )
        rendered = document_renderer.render(
            template_bytes=template_bytes,
            merge_values={"borrower_name": self.member.legal_name},
            output_format="docx",
        )
        storage = LocalDocumentStorage(root=self.document_storage.name)
        stored_template = storage.store(
            SimpleUploadedFile("poa-template.docx", template_bytes)
        )
        template_file = DocumentFile.objects.create(
            file_name="poa-template.docx", file_extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=stored_template.file_size_bytes,
            storage_provider=stored_template.storage_provider,
            storage_key=stored_template.storage_key,
            checksum_sha256=stored_template.checksum_sha256,
            uploaded_by_user=self.compliance, sensitivity_level="internal",
        )
        stored_output = storage.store(
            SimpleUploadedFile("poa.docx", rendered.content)
        )
        generated_file = DocumentFile.objects.create(
            file_name="poa.docx", file_extension=".docx",
            mime_type=rendered.mime_type, file_size_bytes=stored_output.file_size_bytes,
            storage_provider=stored_output.storage_provider,
            storage_key=stored_output.storage_key,
            checksum_sha256=stored_output.checksum_sha256, uploaded_by_user=self.compliance,
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code="poa-workflow-v1", template_name="PoA Workflow",
            document_type="power_of_attorney", borrower_type="individual_farmer",
            template_version="1.0", template_file=template_file,
            approval_status="approved", effective_from="2026-01-01",
        )
        document = LoanDocument.objects.create(
            loan_application=self.application, document_type="power_of_attorney",
            document_category="legal", party_required="borrower_and_nominee",
            document_template=template, document=generated_file, output_format="docx",
            generation_status="generated", execution_status="pending",
            verification_status="pending", renderer_contract_version="legal-renderer-v1",
            renderer_validated_document_id=generated_file.pk,
            renderer_validated_checksum_sha256=generated_file.checksum_sha256,
        )
        self.poa_item.loan_document = document
        self.poa_item.save(update_fields=["loan_document"])
        stamp_notary.record_stamp(
            actor=self.compliance, loan_document_id=document.pk,
            payload={
                "stamp_paper_amount": "500.00", "stamp_type": "physical",
                "stamp_number": None, "stamp_purchase_date": None,
                "executed_date": None, "status": "pending",
                "remarks": "Prepared through 008D2.",
            },
            metadata=stamp_notary.RequestMetadata("poa-stamp-prepare", "", ""),
        )
        stamp_notary.record_notary(
            actor=self.compliance, loan_document_id=document.pk,
            payload={
                "notary_name": None, "notary_registration_number": None,
                "notarised_date": None, "status": "pending",
                "evidence_document_id": None, "remarks": "Prepared through 008D2.",
            },
            metadata=stamp_notary.RequestMetadata("poa-notary-prepare", "", ""),
        )
        stamp = StampDutyRecord.objects.get(loan_document=document)
        notary = NotarisationRecord.objects.get(loan_document=document)
        return document, stamp, notary

    def _notary_evidence(self):
        evidence = DocumentFile.objects.create(
            file_name="poa-notary-evidence.pdf", file_extension=".pdf",
            mime_type="application/pdf", file_size_bytes=8,
            storage_provider="local", storage_key="tests/poa-notary-evidence.pdf",
            checksum_sha256="7" * 64, uploaded_by_user=self.compliance,
            sensitivity_level="confidential",
        )
        AuditLog.objects.create(
            actor_user=self.compliance, actor_type="user",
            action="documents.file.uploaded", entity_type="document_file",
            entity_id=evidence.pk,
            new_value_json={
                "document_id": str(evidence.pk), "file_name": evidence.file_name,
                "file_extension": evidence.file_extension, "mime_type": evidence.mime_type,
                "file_size_bytes": evidence.file_size_bytes,
                "storage_provider": evidence.storage_provider,
                "storage_key": evidence.storage_key,
                "checksum_sha256": evidence.checksum_sha256,
                "sensitivity_level": evidence.sensitivity_level,
                "document_category": "legal", "related_entity_type": "application",
                "related_entity_id": str(self.application.pk),
            },
        )
        return evidence

    def _user(self, role_code, *permission_codes):
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_code.replace("_", " ").title(),
            status="active",
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "security",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=role.role_name,
            email=f"{role_code}@poa.example",
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


@skipUnless(connection.vendor == "postgresql", "PostgreSQL row-lock acceptance only")
class PowerOfAttorneyConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        compliance_role = Role.objects.create(
            role_code="compliance_team_member", role_name="Compliance", status="active"
        )
        permission = Permission.objects.create(
            permission_code="security.poa.manage", permission_name="Manage PoA",
            module_name="security", risk_level="critical",
        )
        RolePermission.objects.create(role=compliance_role, permission=permission)
        self.actor = User.objects.create(
            full_name="Concurrent Compliance", email="concurrent-compliance@poa.example",
            status="active", primary_role=compliance_role,
        )
        cs_role = Role.objects.create(
            role_code="company_secretary", role_name="Company Secretary", status="active"
        )
        self.attorney = User.objects.create(
            full_name="Concurrent Secretary", email="concurrent-cs@poa.example",
            status="active", primary_role=cs_role,
        )
        member = Member.objects.create(
            member_number="MEM-POA-RACE", member_type="individual_farmer",
            legal_name="Race Borrower", display_name="Race Borrower",
            folio_number="FOL-POA-RACE", membership_status="active",
            kyc_status="verified", default_status="no_default",
        )
        nominee = Nominee.objects.create(
            member=member, nominee_name="Race Nominee", gender="female",
            pan_encrypted="pan", pan_hash="race-pan", aadhaar_encrypted="aadhaar",
            aadhaar_hash="race-aadhaar",
        )
        application = LoanApplication.objects.create(
            member=member, nominee=nominee, borrower_type="individual_farmer",
            received_by_user=self.actor, created_by_user=self.actor,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
        )
        self.package = SecurityPackage.objects.create(loan_application=application)
        checklist = DocumentChecklist.objects.create(loan_application=application)
        generated = DocumentFile.objects.create(
            file_name="race-poa.pdf", file_extension=".pdf", mime_type="application/pdf",
            file_size_bytes=8, storage_provider="local", storage_key="tests/race-poa.pdf",
            checksum_sha256="9" * 64, uploaded_by_user=self.actor,
            sensitivity_level="confidential",
        )
        document = LoanDocument.objects.create(
            loan_application=application, document_type="power_of_attorney",
            document_category="legal", document=generated, output_format="pdf",
            generation_status="generated", execution_status="pending",
            verification_status="pending", renderer_contract_version="legal-renderer-v1",
            renderer_validated_document_id=generated.pk,
            renderer_validated_checksum_sha256=generated.checksum_sha256,
        )
        ChecklistItem.objects.create(
            document_checklist=checklist, loan_document=document, item_code="poa",
            item_label="Power of Attorney", display_order=4, required_flag=True,
            applicable_flag=True, completion_status="pending",
            applicability_source="source_always_required",
        )
        stamp = StampDutyRecord.objects.create(
            loan_document=document, stamp_paper_amount="500.00", stamp_type="physical",
            status="pending", prepared_by_user=self.actor,
        )
        notary = NotarisationRecord.objects.create(
            loan_document=document, status="pending", prepared_by_user=self.actor,
        )
        self.values = {
            "borrower_member_id": member.pk, "nominee_id": nominee.pk,
            "attorney_user_id": self.attorney.pk,
            "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
            "loan_document_id": document.pk, "stamp_duty_record_id": stamp.pk,
            "notarisation_record_id": notary.pk, "execution_status": "pending",
            "effective_from": None, "status": "draft",
        }

    def test_five_concurrent_exact_creates_retain_one_current_poa(self):
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = User.objects.get(pk=self.actor.pk)
            barrier.wait()
            result = power_of_attorney.create_poa(
                actor=actor, security_package_id=self.package.pk, values=self.values,
                metadata=power_of_attorney.RequestMetadata(f"race-create-{index}", "", ""),
            )
            close_old_connections()
            return result["power_of_attorney_id"]

        with ThreadPoolExecutor(max_workers=5) as pool:
            ids = list(pool.map(worker, range(5)))
        self.assertEqual(len(set(ids)), 1)
        self.assertEqual(PowerOfAttorney.objects.count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 1)

    def test_five_concurrent_draft_changes_retain_complete_history(self):
        power_of_attorney.create_poa(
            actor=self.actor, security_package_id=self.package.pk, values=self.values,
            metadata=power_of_attorney.RequestMetadata("race-seed", "", ""),
        )
        poa = PowerOfAttorney.objects.get()
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = User.objects.get(pk=self.actor.pk)
            values = {
                **self.values,
                "purpose_summary": (
                    f"Authorise Company Secretary to initiate sale of shares on default. Revision {index}."
                ),
            }
            barrier.wait()
            power_of_attorney.update_poa(
                actor=actor, power_of_attorney_id=poa.pk, values=values,
                metadata=power_of_attorney.RequestMetadata(f"race-change-{index}", "", ""),
            )
            close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            list(pool.map(worker, range(5)))
        self.assertEqual(PowerOfAttorney.objects.count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 6)
        self.assertEqual(AuditLog.objects.filter(entity_type="power_of_attorney").count(), 6)
