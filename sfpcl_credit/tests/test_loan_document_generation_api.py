import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import close_old_connections, connection
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision
from sfpcl_credit.credit.models import LoanAppraisalNote, RiskAssessment
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.documents.modules import document_generation
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member, Nominee, Shareholding
from sfpcl_credit.applications.models import Witness
from sfpcl_credit.tests.api_contracts import assert_pagination_shape, assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-loan-doc-tests-"))
class LoanDocumentGenerationApiTests(TestCase):
    password = "DocumentPass123!"

    def setUp(self):
        self.client = Client()
        self.actor = self._user(
            "compliance_generator",
            "documents.loan_document.generate",
            "documents.loan_document.read",
            "documents.template.file_reference",
        )
        self.member = Member.objects.create(
            member_number="MEM-DOC-001",
            member_type="individual_farmer",
            legal_name="Document Borrower",
            display_name="Document Borrower",
            folio_number="FOL-DOC-001",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="LO00000801",
            member=self.member,
            borrower_type="individual_farmer",
            received_by_user=self.actor,
            created_by_user=self.actor,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Seasonal crop working capital",
            purpose_category="crop_production",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
        )
        risk = RiskAssessment.objects.create(
            loan_application=self.application,
            market_risk_rating="low",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            assessed_by_user=self.actor,
        )
        note = LoanAppraisalNote.objects.create(
            loan_application=self.application,
            prepared_by_user=self.actor,
            reviewed_by_user=self.actor,
            reviewed_at=timezone.now(),
            last_review_decision="reviewed",
            tat_due_at=timezone.now() + timedelta(days=1),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="10000000-0000-0000-0000-000000000001",
            loan_limit_assessment_id_snapshot="20000000-0000-0000-0000-000000000002",
            eligibility_snapshot_json={"overall_result": "eligible"},
            loan_limit_snapshot_json={"final_eligible_loan_amount": "400000.00"},
            prerequisite_provenance="verified",
            borrower_summary="No prior borrowing.",
            eligibility_summary="Eligible.",
            loan_limit_summary="Within limit.",
            recommended_amount="400000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Standard member security package.",
            repayment_capacity_notes="Seasonal proceeds support repayment.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        case = ApprovalCase.objects.create(
            loan_application=self.application,
            loan_appraisal_note=note,
            submitted_by_user=self.actor,
            submission_remarks="Approved document source facts.",
            current_status=ApprovalCase.STATUS_APPROVED,
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=self.application.pk,
            reason_for_approval="Approved by sanction committee.",
            appraisal_facts_json={
                "snapshot_schema_version": "approval-review-v3",
                "borrower": {
                    "name": "Document Borrower",
                    "member_type": "individual_farmer",
                    "folio_number": "FOL-DOC-001",
                },
                "purpose": {"description": "Seasonal crop working capital"},
            },
        )
        self.case = case
        SanctionDecision.objects.create(
            loan_application=self.application,
            approval_case=case,
            decision="sanctioned",
            sanctioned_amount="400000.00",
            sanctioned_tenure_months=12,
            interest_rate_type="floating",
            interest_rate_value="9.5000",
            repayment_date=timezone.localdate() + timedelta(days=365),
            penal_interest_rate="2.0000",
            charges_json={"processing_fee": "1000.00"},
            security_required_summary="Standard member security package.",
            conditions_precedent="Disputes subject to Pune jurisdiction.",
            decision_reason="Approved terms.",
        )
        self.template_file = self._template_source_file()
        self.template = DocumentTemplate.objects.create(
            template_code="term_sheet_individual_v1",
            template_name="Term Sheet",
            document_type="term_sheet",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=self.template_file,
            merge_fields_json=["borrower_name", "loan_amount"],
            approval_status=DocumentTemplate.STATUS_APPROVED,
            effective_from=timezone.localdate() - timedelta(days=1),
        )

    def test_sanctioned_application_generates_retained_pdf_from_exact_template(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/generate/",
            {
                "document_type": "term_sheet",
                "template_id": str(self.template.pk),
                "output_format": "pdf",
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-generate-term-sheet",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(
            set(body["data"]),
            {
                "loan_document_id",
                "document_type",
                "generation_status",
                "document_id",
                "file_name",
            },
        )
        self.assertEqual(body["data"]["document_type"], "term_sheet")
        self.assertEqual(body["data"]["generation_status"], "generated")
        self.assertEqual(body["data"]["file_name"], "term-sheet-LO00000801.pdf")

        from sfpcl_credit.documents.models import LoanDocument

        retained = LoanDocument.objects.get(pk=body["data"]["loan_document_id"])
        self.assertEqual(retained.loan_application_id, self.application.pk)
        self.assertEqual(retained.document_template_id, self.template.pk)
        self.assertEqual(retained.document_id, retained.document.document_id)
        self.assertEqual(retained.generation_status, "generated")
        self.assertEqual(retained.execution_status, "pending")
        self.assertEqual(retained.verification_status, "pending")
        self.assertEqual(retained.document_category, "legal")
        self.assertEqual(retained.party_required, "borrower")

    def test_loan_agreement_requires_executed_term_sheet_for_same_application(self):
        agreement = DocumentTemplate.objects.create(
            template_code="loan_agreement_individual_v1",
            template_name="Loan Agreement",
            document_type="loan_agreement",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=self.template_file,
            merge_fields_json=["borrower_name", "loan_amount"],
            approval_status=DocumentTemplate.STATUS_APPROVED,
            effective_from=timezone.localdate() - timedelta(days=1),
        )

        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/generate/",
            {
                "document_type": "loan_agreement",
                "template_id": str(agreement.pk),
                "output_format": "pdf",
            },
            content_type="application/json",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        from sfpcl_credit.documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(),
            0,
        )

    def test_term_sheet_word_output_contains_all_thirteen_authoritative_facts(self):
        nominee = Nominee.objects.create(
            member=self.member,
            nominee_name="Nominated Member",
            gender="female",
            pan_encrypted="encrypted",
            pan_hash="nominee-pan",
            aadhaar_encrypted="encrypted",
            aadhaar_hash="nominee-aadhaar",
            kyc_status="verified",
        )
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=250,
            holding_mode="physical",
            available_share_count=250,
            status="active",
        )
        Witness.objects.create(
            loan_application=self.application,
            member=self.member,
            witness_name="Verified Witness",
            pan_encrypted="encrypted",
            pan_hash="witness-pan",
            aadhaar_encrypted="encrypted",
            aadhaar_hash="witness-aadhaar",
            verification_shareholding=shareholding,
            shareholder_verified_flag=True,
            verification_status="verified",
            verified_by_user=self.actor,
            verified_at=timezone.now(),
        )
        self.application.nominee = nominee
        self.application.save(update_fields=["nominee"])
        self.case.appraisal_facts_json = {
            **self.case.appraisal_facts_json,
            "nominee": {"nominee_id": str(nominee.pk), "name": nominee.nominee_name},
            "witness": {
                "witness_id": str(self.application.witnesses.get().pk),
                "name": "Verified Witness",
                "version": 1,
            },
            "shareholding": {
                "shareholding_id": str(shareholding.pk),
                "number_of_shares": 250,
            },
        }
        self.case.save(update_fields=["appraisal_facts_json"])
        nominee.nominee_name = "Mutable Nominee Name"
        nominee.save(update_fields=["nominee_name"])
        Witness.objects.filter(loan_application=self.application).update(
            witness_name="Mutable Witness Name"
        )
        shareholding.number_of_shares = 999
        shareholding.available_share_count = 999
        shareholding.save(update_fields=["number_of_shares", "available_share_count"])
        self.template.merge_fields_json = [
            "borrower_name",
            "nominee_name",
            "witness_name",
            "shares_held",
            "facility",
            "loan_amount",
            "loan_purpose",
            "interest_rate",
            "interest_tenure",
            "repayment_date",
            "penal_interest_rate",
            "charges_and_fees",
            "security",
            "dispute_resolution",
        ]
        self.template.save(update_fields=["merge_fields_json"])

        response = self._generate(output_format="docx")

        self.assertEqual(response.status_code, 200, response.content)
        document = DocumentFile.objects.get(pk=response.json()["data"]["document_id"])
        with zipfile.ZipFile(Path(settings.DOCUMENT_STORAGE_ROOT) / document.storage_key) as archive:
            rendered = archive.read("word/document.xml").decode()
        for expected in (
            "Approved Term Sheet",
            "Document Borrower",
            "Nominated Member",
            "Verified Witness",
            "250",
            "short_term",
            "400000.00",
            "Seasonal crop working capital",
            "9.5000 floating",
            "12",
            self.application.sanction_decision.repayment_date.isoformat(),
            "2.0000",
            "processing_fee",
            "Standard member security package.",
            "Disputes subject to Pune jurisdiction.",
        ):
            self.assertIn(expected, rendered)
        self.assertNotIn("{{", rendered)
        self.assertNotIn("Mutable Nominee Name", rendered)
        self.assertNotIn("Mutable Witness Name", rendered)
        self.assertNotIn("999", rendered)

    def test_exact_replay_returns_one_result_and_list_is_metadata_only(self):
        first = self._generate()
        second = self._generate()

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(first.json()["data"], second.json()["data"])
        from sfpcl_credit.documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(), 1
        )

        listed = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/",
            {"page": 1, "page_size": 1},
            **self._auth(),
        )
        self.assertEqual(listed.status_code, 200, listed.content)
        assert_pagination_shape(self, listed.json())
        self.assertEqual(listed.json()["pagination"]["total_count"], 1)
        item = listed.json()["data"][0]
        self.assertNotIn("download_url", item)
        self.assertNotIn("merge_fields", item)
        self.assertNotIn("borrower_name", item)
        self.assertEqual(item["template_version"], "1.0")

    def test_unknown_or_missing_merge_fact_creates_no_file_metadata_or_evidence(self):
        for merge_field in ("unknown_legal_fact", "nominee_name"):
            with self.subTest(merge_field=merge_field):
                self.template.merge_fields_json = [merge_field]
                self.template.save(update_fields=["merge_fields_json"])
                response = self._generate()
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(merge_field, response.json()["error"]["field_errors"])
                from sfpcl_credit.documents.models import LoanDocument

                self.assertEqual(LoanDocument.objects.count(), 0)
                self.assertEqual(DocumentFile.objects.count(), 1)
                self.assertEqual(
                    AuditLog.objects.filter(action="documents.loan_document.generated").count(), 0
                )

    def test_generation_requires_008a2_file_provenance_and_reference_permission(self):
        upload = AuditLog.objects.get(
            action="documents.file.uploaded", entity_id=self.template_file.pk
        )
        upload.new_value_json = {**upload.new_value_json, "document_category": "legal"}
        upload.save(update_fields=["new_value_json"])

        denied = self._generate()
        self.assertEqual(denied.status_code, 400, denied.content)
        self.assertIn("template_file_id", denied.json()["error"]["field_errors"])

        upload.new_value_json = {**upload.new_value_json, "document_category": "template_source"}
        upload.save(update_fields=["new_value_json"])
        permission = Permission.objects.get(
            permission_code="documents.template.file_reference"
        )
        RolePermission.objects.filter(
            role=self.actor.primary_role, permission=permission
        ).delete()
        denied_without_permission = self._generate()
        self.assertEqual(denied_without_permission.status_code, 400)
        self.assertIn(
            "template_file_id",
            denied_without_permission.json()["error"]["field_errors"],
        )

        from sfpcl_credit.documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)

    def test_unsafe_format_unsanctioned_state_and_unresolved_variant_fail_closed(self):
        unsafe = self._generate(output_format="html")
        self.assertEqual(unsafe.status_code, 400, unsafe.content)
        self.assertIn("output_format", unsafe.json()["error"]["field_errors"])

        self.application.application_status = LoanApplication.STATUS_SUBMITTED_TO_SANCTION
        self.application.save(update_fields=["application_status"])
        unsanctioned = self._generate()
        self.assertEqual(unsanctioned.status_code, 409, unsanctioned.content)
        self.assertEqual(unsanctioned.json()["error"]["code"], "INVALID_STATE_TRANSITION")

        self.application.application_status = LoanApplication.STATUS_APPROVED_BY_SANCTION
        self.application.borrower_type = "fpc"
        self.application.save(update_fields=["application_status", "borrower_type"])
        unresolved = self._generate()
        self.assertEqual(unresolved.status_code, 400, unresolved.content)
        self.assertIn("borrower_type", unresolved.json()["error"]["field_errors"])

        from sfpcl_credit.documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)

    def test_generate_read_and_object_scope_permissions_do_not_leak_authority(self):
        generated = self._generate()
        self.assertEqual(generated.status_code, 200, generated.content)

        generate_permission = Permission.objects.get(permission_code="documents.loan_document.generate")
        read_permission = Permission.objects.get(permission_code="documents.loan_document.read")
        RolePermission.objects.filter(role=self.actor.primary_role, permission=generate_permission).delete()
        for code in ("documents.template.manage", "documents.file.download"):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={"permission_name": code, "module_name": "documents", "risk_level": "high"},
            )
            RolePermission.objects.get_or_create(role=self.actor.primary_role, permission=permission)
        denied_generate = self._generate(output_format="docx")
        self.assertEqual(denied_generate.status_code, 403, denied_generate.content)
        self.assertEqual(denied_generate.json()["error"]["code"], "FORBIDDEN")

        readable = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/",
            **self._auth(),
        )
        self.assertEqual(readable.status_code, 200, readable.content)
        RolePermission.objects.filter(role=self.actor.primary_role, permission=read_permission).delete()
        denied_read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/",
            **self._auth(),
        )
        self.assertEqual(denied_read.status_code, 403, denied_read.content)
        self.assertEqual(denied_read.json()["error"]["code"], "FORBIDDEN")

        outsider = self._user(
            "outside_generator",
            "documents.loan_document.generate",
            "documents.template.file_reference",
        )
        object_denied = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/generate/",
            {"document_type": "term_sheet", "template_id": str(self.template.pk), "output_format": "docx"},
            content_type="application/json",
            **self._auth(outsider),
        )
        self.assertEqual(object_denied.status_code, 403, object_denied.content)
        self.assertEqual(object_denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

    def test_ineligible_template_states_fail_closed_before_rendering(self):
        cases = (
            {"approval_status": DocumentTemplate.STATUS_DRAFT},
            {"approval_status": DocumentTemplate.STATUS_RETIRED},
            {"effective_from": timezone.localdate() + timedelta(days=1)},
            {"effective_to": timezone.localdate() - timedelta(days=1)},
            {"document_type": "power_of_attorney"},
            {"borrower_type": "fpo"},
            {"template_file": None},
        )
        original = {
            "approval_status": self.template.approval_status,
            "effective_from": self.template.effective_from,
            "effective_to": self.template.effective_to,
            "document_type": self.template.document_type,
            "borrower_type": self.template.borrower_type,
            "template_file": self.template.template_file,
        }
        for overrides in cases:
            with self.subTest(overrides=overrides):
                for field, value in original.items():
                    setattr(self.template, field, value)
                for field, value in overrides.items():
                    setattr(self.template, field, value)
                self.template.save(update_fields=list(original))
                denied = self._generate(document_type="term_sheet")
                self.assertEqual(denied.status_code, 400, denied.content)
                self.assertIn("template_id", denied.json()["error"]["field_errors"])
        from sfpcl_credit.documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)

    def test_metadata_failure_removes_stored_bytes_and_all_success_evidence(self):
        storage = LocalDocumentStorage()
        before = set(Path(settings.DOCUMENT_STORAGE_ROOT).rglob("*"))
        with patch(
            "sfpcl_credit.documents.modules.document_generation.DocumentFile.objects.create",
            side_effect=RuntimeError("metadata write failed"),
        ):
            with self.assertRaisesRegex(RuntimeError, "metadata write failed"):
                document_generation.generate(
                    actor=self.actor,
                    application_id=self.application.pk,
                    payload={
                        "document_type": "term_sheet",
                        "template_id": str(self.template.pk),
                        "output_format": "pdf",
                    },
                    metadata=document_generation.RequestMetadata(
                        request_id="req-storage-failure", ip_address="127.0.0.1", user_agent="test"
                    ),
                    storage=storage,
                )
        self.assertEqual(set(Path(settings.DOCUMENT_STORAGE_ROOT).rglob("*")), before)
        from sfpcl_credit.documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(), 0
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(), 0
        )

    def test_missing_retained_template_source_bytes_fail_before_output_storage(self):
        source_path = Path(settings.DOCUMENT_STORAGE_ROOT) / self.template_file.storage_key
        source_path.unlink()

        denied = self._generate()

        self.assertEqual(denied.status_code, 400, denied.content)
        self.assertIn("template_file_id", denied.json()["error"]["field_errors"])
        from sfpcl_credit.documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)

    def _generate(self, *, output_format="pdf", template=None, document_type=None):
        template = template or self.template
        return self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/generate/",
            {
                "document_type": document_type or template.document_type,
                "template_id": str(template.pk),
                "output_format": output_format,
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-generate-term-sheet",
            **self._auth(),
        )

    def _user(self, role_code, *permission_codes):
        role = Role.objects.create(
            role_code=role_code,
            role_name="Compliance Generator",
            is_system_role=True,
            status="active",
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
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name="Compliance Generator",
            email=f"{role_code}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save(update_fields=["password_hash"])
        return user

    def _auth(self, user=None):
        user = user or self.actor
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"}

    def _template_source_file(self):
        stored = LocalDocumentStorage().store(
            ContentFile(
                (
                    "Approved Term Sheet\n"
                    "Borrower: {{borrower_name}}\nNominee: {{nominee_name}}\n"
                    "Witness: {{witness_name}}\nShares: {{shares_held}}\n"
                    "Facility: {{facility}}\nAmount: {{loan_amount}}\n"
                    "Purpose: {{loan_purpose}}\nInterest: {{interest_rate}}\n"
                    "Interest tenure: {{interest_tenure}}\nRepayment: {{repayment_date}}\n"
                    "Penalty: {{penal_interest_rate}}\nCharges: {{charges_and_fees}}\n"
                    "Security: {{security}}\nDisputes: {{dispute_resolution}}"
                ).encode(),
                name="term-sheet.docx",
            )
        )
        document = DocumentFile.objects.create(
            file_name="term-sheet.docx",
            file_extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=self.actor,
            sensitivity_level="internal",
        )
        AuditLog.objects.create(
            actor_user=self.actor,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=document.pk,
            new_value_json={
                "document_id": str(document.pk),
                "file_name": document.file_name,
                "file_extension": document.file_extension,
                "mime_type": document.mime_type,
                "file_size_bytes": document.file_size_bytes,
                "storage_provider": document.storage_provider,
                "storage_key": document.storage_key,
                "checksum_sha256": document.checksum_sha256,
                "sensitivity_level": document.sensitivity_level,
                "document_category": "template_source",
                "related_entity_type": "global",
                "related_entity_id": None,
            },
        )
        return document


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative loan-document replay race requires PostgreSQL.",
)
@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-loan-doc-race-"))
class LoanDocumentGenerationConcurrencyTests(TransactionTestCase):
    reset_sequences = True
    password = LoanDocumentGenerationApiTests.password
    setUp = LoanDocumentGenerationApiTests.setUp
    _user = LoanDocumentGenerationApiTests._user
    _template_source_file = LoanDocumentGenerationApiTests._template_source_file

    def test_five_identical_requests_retain_one_result_and_one_evidence_set(self):
        barrier = Barrier(5)
        actor_id = self.actor.pk
        application_id = self.application.pk
        payload = {
            "document_type": "term_sheet",
            "template_id": str(self.template.pk),
            "output_format": "pdf",
        }

        def generate(index):
            close_old_connections()
            actor = User.objects.get(pk=actor_id)
            barrier.wait()
            result = document_generation.generate(
                actor=actor,
                application_id=application_id,
                payload=payload,
                metadata=document_generation.RequestMetadata(
                    request_id=f"req-race-{index}", ip_address="127.0.0.1", user_agent="test"
                ),
            )
            close_old_connections()
            return result

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(generate, range(5)))

        self.assertEqual(len({row["loan_document_id"] for row in results}), 1)
        from sfpcl_credit.documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), 2)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(), 1
        )
