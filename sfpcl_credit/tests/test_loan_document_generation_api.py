import hashlib
import tempfile
import uuid
import zipfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch
from xml.etree import ElementTree

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision
from sfpcl_credit.credit.models import LoanAppraisalNote, RiskAssessment
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.legal_documents.modules import document_generation, document_renderer
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
)
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
        frozen_name = "Document Borrower – कृषक & Sons \\ Cooperative"
        self.case.appraisal_facts_json = {
            **self.case.appraisal_facts_json,
            "borrower": {
                **self.case.appraisal_facts_json["borrower"],
                "name": frozen_name,
            },
        }
        self.case.save(update_fields=["appraisal_facts_json"])
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

        from sfpcl_credit.legal_documents.models import LoanDocument

        retained = LoanDocument.objects.get(pk=body["data"]["loan_document_id"])
        self.assertEqual(retained.loan_application_id, self.application.pk)
        self.assertEqual(retained.document_template_id, self.template.pk)
        self.assertEqual(retained.document_id, retained.document.document_id)
        self.assertEqual(retained.generation_status, "generated")
        self.assertEqual(retained.execution_status, "pending")
        self.assertEqual(retained.verification_status, "pending")
        self.assertEqual(retained.document_category, "legal")
        self.assertEqual(retained.party_required, "borrower")
        output_bytes = (
            Path(settings.DOCUMENT_STORAGE_ROOT) / retained.document.storage_key
        ).read_bytes()
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(output_bytes), strict=True)
        self.assertGreaterEqual(len(reader.pages), 1)
        extracted = "\n".join(
            page.extract_text(extraction_mode="layout") or "" for page in reader.pages
        )
        self.assertIn("Approved Term Sheet", extracted)
        self.assertIn("SFPCL Approved Legal Template", extracted)
        self.assertIn("Retained legal footer", extracted)
        self.assertIn(frozen_name, extracted)
        self.assertIn("Amount (₹)", extracted)
        self.assertIn("400000.00", extracted)

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
        from sfpcl_credit.legal_documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(),
            0,
        )

    def test_pdf_wraps_long_legal_text_across_bounded_pages(self):
        long_name = "कृषक ₹ " + ("seasonal-crop-borrower " * 500)
        self.case.appraisal_facts_json = {
            **self.case.appraisal_facts_json,
            "borrower": {
                **self.case.appraisal_facts_json["borrower"],
                "name": long_name,
            },
        }
        self.case.save(update_fields=["appraisal_facts_json"])

        response = self._generate(output_format="pdf")

        self.assertEqual(response.status_code, 200, response.content)
        retained = LoanDocument.objects.get(pk=response.json()["data"]["loan_document_id"])
        output_bytes = (
            Path(settings.DOCUMENT_STORAGE_ROOT) / retained.document.storage_key
        ).read_bytes()
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(output_bytes), strict=True)
        self.assertGreaterEqual(len(reader.pages), 2)
        self.assertLessEqual(len(reader.pages), document_renderer.MAX_PDF_PAGES)
        extracted = " ".join(
            "\n".join(
                page.extract_text(extraction_mode="layout") or ""
                for page in reader.pages
            ).split()
        )
        self.assertIn("कृषक ₹", extracted)
        self.assertGreaterEqual(extracted.count("seasonal-crop-borrower"), 500)

    def test_term_sheet_word_output_contains_all_thirteen_authoritative_facts(self):
        frozen_borrower = "शेतकरी ₹ & Sons \\1"
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
            "borrower": {
                **self.case.appraisal_facts_json["borrower"],
                "name": frozen_borrower,
            },
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
        self.template.template_file = self._template_source_file(all_fields=True)
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
        self.template.save(update_fields=["merge_fields_json", "template_file"])

        response = self._generate(output_format="docx")

        self.assertEqual(response.status_code, 200, response.content)
        document = DocumentFile.objects.get(pk=response.json()["data"]["document_id"])
        output_path = Path(settings.DOCUMENT_STORAGE_ROOT) / document.storage_key
        with zipfile.ZipFile(output_path) as archive:
            self.assertIn("word/styles.xml", archive.namelist())
            self.assertIn("word/header1.xml", archive.namelist())
            self.assertIn("word/footer1.xml", archive.namelist())
            rendered = self._extract_docx_text(output_path.read_bytes())
        for expected in (
            "Approved Term Sheet",
            "Retained legal footer",
            frozen_borrower,
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
        from sfpcl_credit.legal_documents.models import LoanDocument

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
        self.assertEqual(
            item["renderer_validation_status"],
            LoanDocument.RENDERER_CURRENT_VALIDATED,
        )

    def test_legacy_unverified_row_conflicts_on_replay_and_is_labelled_in_list(self):
        legacy_rows = {}
        for output_format, content in (
            ("pdf", b"%PDF-1.4\nlegacy minimal output\n%%EOF"),
            ("docx", b"legacy plain text falsely named as a Word package"),
        ):
            stored = LocalDocumentStorage().store(
                ContentFile(content, name=f"legacy-term-sheet.{output_format}")
            )
            legacy_file = DocumentFile.objects.create(
                file_name=f"term-sheet-LO00000801.{output_format}",
                file_extension=f".{output_format}",
                mime_type=(
                    "application/pdf"
                    if output_format == "pdf"
                    else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ),
                file_size_bytes=stored.file_size_bytes,
                storage_provider=stored.storage_provider,
                storage_key=stored.storage_key,
                checksum_sha256=stored.checksum_sha256,
                uploaded_by_user=self.actor,
                sensitivity_level="confidential",
            )
            legacy_rows[output_format] = LoanDocument.objects.create(
                loan_application=self.application,
                document_type="term_sheet",
                document_category="legal",
                party_required="borrower",
                document_template=self.template,
                document=legacy_file,
                output_format=output_format,
                generation_status="generated",
                execution_status="executed",
                verification_status="verified",
                stamp_status="adequate",
                notarisation_status="completed",
                verified_by_user=self.actor,
                verified_at=timezone.now(),
            )
        checklist = DocumentChecklist.objects.create(loan_application=self.application)
        ChecklistItem.objects.create(
            document_checklist=checklist,
            loan_document=legacy_rows["pdf"],
            item_code="term_sheet",
            item_label="Term Sheet",
            display_order=1,
            required_flag=True,
            applicable_flag=True,
            completion_status="complete",
            applicability_source="retained_legacy_history",
            verified_by_user=self.actor,
            verified_at=timezone.now(),
        )
        evidence_before = (
            DocumentFile.objects.count(),
            AuditLog.objects.filter(action="documents.loan_document.generated").count(),
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(),
        )

        for output_format in ("pdf", "docx"):
            replay = self._generate(output_format=output_format)
            self.assertEqual(replay.status_code, 409, replay.content)
            self.assertEqual(replay.json()["error"]["code"], "CONFLICT")
            self.assertEqual(
                replay.json()["error"]["details"]["renderer_validation_status"],
                LoanDocument.RENDERER_LEGACY_UNVERIFIED,
            )
        listed = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/",
            **self._auth(),
        )
        self.assertEqual(listed.status_code, 200, listed.content)
        self.assertEqual(listed.json()["pagination"]["total_count"], 2)
        self.assertEqual(
            {row["renderer_validation_status"] for row in listed.json()["data"]},
            {LoanDocument.RENDERER_LEGACY_UNVERIFIED},
        )
        self.assertEqual(
            (
                DocumentFile.objects.count(),
                AuditLog.objects.filter(action="documents.loan_document.generated").count(),
                WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(),
            ),
            evidence_before,
        )

    def test_new_outputs_bind_current_provenance_to_reopened_stored_checksum(self):
        for output_format in ("docx", "pdf"):
            with self.subTest(output_format=output_format):
                generated = self._generate(output_format=output_format)
                self.assertEqual(generated.status_code, 200, generated.content)
                row = LoanDocument.objects.select_related("document").get(
                    pk=generated.json()["data"]["loan_document_id"]
                )
                stored_bytes = (
                    Path(settings.DOCUMENT_STORAGE_ROOT) / row.document.storage_key
                ).read_bytes()
                checksum = hashlib.sha256(stored_bytes).hexdigest()
                self.assertEqual(
                    row.renderer_contract_version, LoanDocument.RENDERER_CONTRACT_V1
                )
                self.assertEqual(row.renderer_validated_document_id, row.document_id)
                self.assertEqual(row.renderer_validated_checksum_sha256, checksum)
                self.assertEqual(row.document.checksum_sha256, checksum)
                self.assertEqual(
                    row.renderer_validation_status,
                    LoanDocument.RENDERER_CURRENT_VALIDATED,
                )
                if output_format == "docx":
                    extracted = self._extract_docx_text(stored_bytes)
                else:
                    from pypdf import PdfReader

                    extracted = "\n".join(
                        page.extract_text(extraction_mode="layout") or ""
                        for page in PdfReader(BytesIO(stored_bytes), strict=True).pages
                    )
                self.assertIn("Document Borrower", extracted)
                self.assertIn("400000.00", extracted)
                evidence_before_replay = (
                    DocumentFile.objects.count(),
                    LoanDocument.objects.count(),
                    AuditLog.objects.filter(
                        action="documents.loan_document.generated"
                    ).count(),
                    WorkflowEvent.objects.filter(
                        workflow_name="loan_document_generation"
                    ).count(),
                )
                replay = self._generate(output_format=output_format)
                self.assertEqual(replay.status_code, 200, replay.content)
                self.assertEqual(replay.json()["data"], generated.json()["data"])
                self.assertEqual(
                    (
                        DocumentFile.objects.count(),
                        LoanDocument.objects.count(),
                        AuditLog.objects.filter(
                            action="documents.loan_document.generated"
                        ).count(),
                        WorkflowEvent.objects.filter(
                            workflow_name="loan_document_generation"
                        ).count(),
                    ),
                    evidence_before_replay,
                )
                checklist_candidates = (
                    document_generation.legal_document_selector.latest_generated_metadata_by_type(
                        application_id=self.application.pk,
                        document_types=("term_sheet",),
                    )
                )
                self.assertEqual(checklist_candidates, {"term_sheet": row.pk})

    def test_renderer_provenance_is_immutable_while_lifecycle_fields_remain_updateable(self):
        generated = self._generate(output_format="docx")
        self.assertEqual(generated.status_code, 200, generated.content)
        row = LoanDocument.objects.get(pk=generated.json()["data"]["loan_document_id"])

        row.renderer_validated_checksum_sha256 = "f" * 64
        with self.assertRaises(ValidationError) as blocked:
            row.save(update_fields=["renderer_validated_checksum_sha256"])
        self.assertIn("renderer_provenance", blocked.exception.message_dict)

        with self.assertRaises(ValidationError):
            LoanDocument.objects.filter(pk=row.pk).update(
                renderer_validated_checksum_sha256="e" * 64
            )
        row.renderer_contract_version = "rewritten-contract"
        with self.assertRaises(ValidationError):
            LoanDocument.objects.bulk_update([row], ["renderer_contract_version"])

        row.refresh_from_db()
        row.execution_status = "executed"
        row.save(update_fields=["execution_status"])
        row.refresh_from_db()
        self.assertEqual(row.execution_status, "executed")
        self.assertEqual(
            row.renderer_validation_status, LoanDocument.RENDERER_CURRENT_VALIDATED
        )

    def test_unknown_or_missing_merge_fact_creates_no_file_metadata_or_evidence(self):
        for merge_field in ("unknown_legal_fact", "nominee_name"):
            with self.subTest(merge_field=merge_field):
                self.template.merge_fields_json = [merge_field]
                self.template.save(update_fields=["merge_fields_json"])
                response = self._generate()
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(merge_field, response.json()["error"]["field_errors"])
                from sfpcl_credit.legal_documents.models import LoanDocument

                self.assertEqual(LoanDocument.objects.count(), 0)
                self.assertEqual(DocumentFile.objects.count(), 1)
                self.assertEqual(
                    AuditLog.objects.filter(action="documents.loan_document.generated").count(), 0
                )

    def test_word_placeholder_contract_rejects_duplicate_undeclared_and_missing_fields(self):
        cases = (
            (["borrower_name", "borrower_name"], ["borrower_name"], "borrower_name"),
            (["borrower_name", "loan_amount"], ["borrower_name"], "template_file_id"),
            (["borrower_name"], ["borrower_name", "loan_amount"], "loan_amount"),
        )
        for fields, declared, expected_error in cases:
            with self.subTest(fields=fields, declared=declared):
                self.template.template_file = self._template_source_file(fields=fields)
                self.template.merge_fields_json = declared
                self.template.save(update_fields=["template_file", "merge_fields_json"])
                response = self._generate(output_format="docx")
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(
                    expected_error,
                    response.json()["error"]["field_errors"],
                )
        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(), 0
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(), 0
        )

    def test_renderer_rejects_every_bounded_input_class(self):
        content = self._genuine_docx_fixture(["borrower_name", "loan_amount"])
        merge_values = {"borrower_name": "Borrower", "loan_amount": "400000.00"}
        cases = (
            ("MAX_SOURCE_BYTES", 1),
            ("MAX_ARCHIVE_ENTRIES", 1),
            ("MAX_EXPANDED_BYTES", 1),
            ("MAX_ARCHIVE_ENTRY_BYTES", 1),
            ("MAX_COMPRESSION_RATIO", 1),
            ("MAX_XML_BYTES", 1),
            ("MAX_TEXT_CHARS", 1),
            ("MAX_PLACEHOLDERS", 1),
            ("MAX_REPLACEMENT_BYTES", 1),
            ("MAX_OUTPUT_BYTES", 1),
        )
        for limit_name, limit in cases:
            with self.subTest(limit=limit_name), patch.object(
                document_renderer, limit_name, limit
            ), self.assertRaises(ValidationError):
                document_renderer.render(
                    template_bytes=content,
                    merge_values=merge_values,
                    output_format="docx",
                )
        with patch.object(document_renderer, "MAX_EXPANDED_BYTES", 1):
            response = self._generate(output_format="docx")
        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("template_file_id", response.json()["error"]["field_errors"])
        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(), 0
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(), 0
        )

    def test_m05_writer_nullable_terms_block_full_term_sheet_with_zero_writes(self):
        decision = self.application.sanction_decision
        decision.interest_rate_value = None
        decision.repayment_date = None
        decision.penal_interest_rate = None
        decision.charges_json = {}
        decision.conditions_precedent = ""
        decision.save(
            update_fields=[
                "interest_rate_value", "repayment_date", "penal_interest_rate",
                "charges_json", "conditions_precedent",
            ]
        )
        self.template.template_file = self._template_source_file(all_fields=True)
        self.template.merge_fields_json = [
            "borrower_name", "loan_amount", "interest_rate", "repayment_date",
            "penal_interest_rate", "charges_and_fees", "dispute_resolution",
        ]
        self.template.save(update_fields=["template_file", "merge_fields_json"])

        response = self._generate(output_format="docx")

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            set(response.json()["error"]["field_errors"]),
            {
                "interest_rate", "repayment_date", "penal_interest_rate",
                "charges_and_fees", "dispute_resolution",
            },
        )
        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(), 0
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(), 0
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
        self.assertEqual(denied_without_permission.status_code, 403)
        self.assertEqual(denied_without_permission.json()["error"]["code"], "FORBIDDEN")

        from sfpcl_credit.legal_documents.models import LoanDocument

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

        from sfpcl_credit.legal_documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)

    def test_generate_read_and_object_scope_permissions_do_not_leak_authority(self):
        generated = self._generate()
        self.assertEqual(generated.status_code, 200, generated.content)
        direct_replay = document_generation.generate(
            actor=self.actor,
            application_id=self.application.pk,
            payload={
                "document_type": "term_sheet",
                "template_id": str(self.template.pk),
                "output_format": "pdf",
            },
            metadata=document_generation.RequestMetadata(
                request_id="req-direct-replay",
                ip_address="127.0.0.1",
                user_agent="test",
            ),
        )
        self.assertEqual(direct_replay, generated.json()["data"])

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

        outside_reader = self._user(
            "outside_reader",
            "documents.loan_document.read",
        )
        object_denied_read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/",
            **self._auth(outside_reader),
        )
        self.assertEqual(object_denied_read.status_code, 403, object_denied_read.content)
        self.assertEqual(
            object_denied_read.json()["error"]["code"],
            "OBJECT_ACCESS_DENIED",
        )

    def test_unknown_application_is_404_only_after_role_and_permission_authority(self):
        unknown_id = uuid.uuid4()
        authorised = self._user(
            "compliance_team_member",
            "documents.loan_document.generate",
            "documents.loan_document.read",
            "documents.template.file_reference",
        )
        authorised_generate = self.client.post(
            f"/api/v1/loan-applications/{unknown_id}/loan-documents/generate/",
            {},
            content_type="application/json",
            **self._auth(authorised),
        )
        authorised_list = self.client.get(
            f"/api/v1/loan-applications/{unknown_id}/loan-documents/",
            **self._auth(authorised),
        )
        for response in (authorised_generate, authorised_list):
            self.assertEqual(response.status_code, 404, response.content)
            self.assertEqual(response.json()["error"]["code"], "NOT_FOUND")

        no_permission = self._user("unknown_plain")
        unrelated_generator = self._user(
            "unknown_unrelated_generator",
            "documents.loan_document.generate",
            "documents.template.file_reference",
        )
        unrelated_reader = self._user(
            "unknown_unrelated_reader", "documents.loan_document.read"
        )
        denied_generate = (
            self.client.post(
                f"/api/v1/loan-applications/{unknown_id}/loan-documents/generate/",
                {},
                content_type="application/json",
                **self._auth(no_permission),
            ),
            self.client.post(
                f"/api/v1/loan-applications/{unknown_id}/loan-documents/generate/",
                {},
                content_type="application/json",
                **self._auth(unrelated_generator),
            ),
        )
        for response in denied_generate:
            self.assertEqual(response.status_code, 403, response.content)
        denied_list = self.client.get(
            f"/api/v1/loan-applications/{unknown_id}/loan-documents/",
            **self._auth(unrelated_reader),
        )
        self.assertEqual(denied_list.status_code, 403, denied_list.content)
        self.assertEqual(LoanDocument.objects.count(), 0)

    def test_direct_generation_enforces_application_object_scope_before_template_reads(self):
        outsider = self._user(
            "direct_outside_generator",
            "documents.loan_document.generate",
            "documents.template.file_reference",
        )

        with (
            patch.object(
                document_generation.document_templates,
                "resolve_borrower_template_variant",
            ) as variant_read,
            patch.object(
                document_generation.approval_facts,
                "resolve_for_generation",
            ) as approval_read,
            patch.object(
                document_generation.document_services,
                "resolve_template_source_reference",
            ) as file_read,
            patch.object(document_generation.LocalDocumentStorage, "store") as storage_write,
            self.assertRaises(document_generation.LegalDocumentAccessDenied) as denied,
        ):
            document_generation.generate(
                actor=outsider,
                application_id=self.application.pk,
                payload={
                    "document_type": "term_sheet",
                    "template_id": str(self.template.pk),
                    "output_format": "pdf",
                },
                metadata=document_generation.RequestMetadata(
                    request_id="req-direct-object-denied",
                    ip_address="127.0.0.1",
                    user_agent="test",
                ),
            )

        self.assertEqual(denied.exception.error_code, "OBJECT_ACCESS_DENIED")
        variant_read.assert_not_called()
        approval_read.assert_not_called()
        file_read.assert_not_called()
        storage_write.assert_not_called()
        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(),
            0,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(),
            0,
        )

    def test_direct_list_enforces_read_scope_before_selector_count_or_serialization(self):
        generated = self._generate()
        self.assertEqual(generated.status_code, 200, generated.content)
        outsider = self._user(
            "direct_outside_reader",
            "documents.loan_document.read",
        )

        with (
            patch.object(document_generation.legal_document_selector, "list_for_application") as selector,
            self.assertRaises(document_generation.LegalDocumentAccessDenied) as denied,
        ):
            document_generation.list_for_application(
                actor=outsider,
                application_id=self.application.pk,
                query_params={"page": "1", "page_size": "20"},
            )

        self.assertEqual(denied.exception.error_code, "OBJECT_ACCESS_DENIED")
        selector.assert_not_called()

    def test_direct_list_returns_exact_first_middle_final_and_empty_pages(self):
        generated_file = DocumentFile.objects.create(
            file_name="generated.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=10,
            storage_provider="local",
            storage_key="generated.pdf",
            checksum_sha256="0" * 64,
            uploaded_by_user=self.actor,
            sensitivity_level="confidential",
        )
        expected_newest_first = []
        for index in range(5):
            template = DocumentTemplate.objects.create(
                template_code=f"page_template_{index}",
                template_name=f"Page template {index}",
                document_type=f"page_document_{index}",
                borrower_type="individual_farmer",
                template_version=f"{index + 2}.0",
                template_file=self.template_file,
                merge_fields_json=[],
                approval_status=DocumentTemplate.STATUS_APPROVED,
                effective_from=timezone.localdate(),
            )
            row = LoanDocument.objects.create(
                loan_application=self.application,
                document_type=template.document_type,
                document_category="legal",
                party_required="borrower",
                document_template=template,
                document=generated_file,
                output_format="pdf",
                generation_status="generated",
                execution_status="pending",
                verification_status="pending",
            )
            LoanDocument.objects.filter(pk=row.pk).update(
                created_at=timezone.now() + timedelta(minutes=index)
            )
            expected_newest_first.insert(0, str(row.pk))

        pages = []
        for requested_page in (1, 2, 3, 99):
            rows, pagination = document_generation.list_for_application(
                actor=self.actor,
                application_id=self.application.pk,
                query_params={"page": str(requested_page), "page_size": "2"},
            )
            pages.append(([row["loan_document_id"] for row in rows], pagination))

        self.assertEqual(pages[0][0], expected_newest_first[:2])
        self.assertEqual(pages[1][0], expected_newest_first[2:4])
        self.assertEqual(pages[2][0], expected_newest_first[4:])
        self.assertEqual(pages[3][0], expected_newest_first[4:])
        self.assertEqual(
            [page[1]["page"] for page in pages],
            [1, 2, 3, 3],
        )
        for _, pagination in pages:
            self.assertEqual(pagination["page_size"], 2)
            self.assertEqual(pagination["total_count"], 5)
            self.assertEqual(pagination["total_pages"], 3)

        empty_application = LoanApplication.objects.create(
            application_reference_number="LO00000802",
            member=self.member,
            borrower_type="individual_farmer",
            received_by_user=self.actor,
            created_by_user=self.actor,
        )
        empty_rows, empty_pagination = document_generation.list_for_application(
            actor=self.actor,
            application_id=empty_application.pk,
            query_params={"page": "99", "page_size": "2"},
        )
        self.assertEqual(empty_rows, [])
        self.assertEqual(
            empty_pagination,
            {
                "page": 1,
                "page_size": 2,
                "total_count": 0,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
            },
        )

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
        from sfpcl_credit.legal_documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)

    def test_metadata_failure_removes_stored_bytes_and_all_success_evidence(self):
        storage = LocalDocumentStorage()
        before = set(Path(settings.DOCUMENT_STORAGE_ROOT).rglob("*"))
        with patch(
            "sfpcl_credit.legal_documents.modules.document_generation.DocumentFile.objects.create",
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
        from sfpcl_credit.legal_documents.models import LoanDocument

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
        from sfpcl_credit.legal_documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 1)

    def test_database_rejects_non_null_loan_account_until_epic_009_fk_exists(self):
        generated = self._generate()
        self.assertEqual(generated.status_code, 200, generated.content)
        retained = LoanDocument.objects.get(
            pk=generated.json()["data"]["loan_document_id"]
        )
        self.assertIsNone(retained.loan_account_id)

        retained.loan_account_id = uuid.uuid4()
        with self.assertRaises(IntegrityError), transaction.atomic():
            retained.save(update_fields=["loan_account_id"])

        retained.refresh_from_db()
        self.assertIsNone(retained.loan_account_id)

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

    def _template_source_file(self, *, all_fields=False, fields=None):
        body_fields = (
            [
                "borrower_name", "nominee_name", "witness_name", "shares_held",
                "facility", "loan_amount", "loan_purpose", "interest_rate",
                "interest_tenure", "repayment_date", "penal_interest_rate",
                "charges_and_fees", "security", "dispute_resolution",
            ]
            if all_fields
            else (fields or ["borrower_name", "loan_amount"])
        )
        stored = LocalDocumentStorage().store(
            ContentFile(
                self._genuine_docx_fixture(body_fields),
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

    @staticmethod
    def _genuine_docx_fixture(
        fields, title="Approved Term Sheet", footer="Retained legal footer"
    ):
        namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        relationships = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        labels = {
            "borrower_name": "Borrower", "nominee_name": "Nominee",
            "witness_name": "Witness", "shares_held": "Shares",
            "facility": "Facility", "loan_amount": "Amount (₹)",
            "loan_purpose": "Purpose", "interest_rate": "Interest",
            "interest_tenure": "Interest tenure", "repayment_date": "Repayment",
            "penal_interest_rate": "Penalty", "charges_and_fees": "Charges",
            "security": "Security", "dispute_resolution": "Disputes",
            "loan_account_number": "Loan account",
            "application_reference": "Application reference",
            "disbursed_amount": "Disbursed amount",
            "full_repayment_date": "Full repayment date",
            "issued_by": "Issued by",
            "issue_date": "Issue date",
        }
        rows = []
        for field in fields:
            placeholder = f"{{{{{field}}}}}"
            midpoint = len(placeholder) // 2
            rows.append(
                f'<w:tr><w:tc><w:p><w:r><w:t>{labels[field]}</w:t></w:r></w:p></w:tc>'
                f'<w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>{placeholder[:midpoint]}</w:t></w:r>'
                f'<w:r><w:t>{placeholder[midpoint:]}</w:t></w:r></w:p></w:tc></w:tr>'
            )
        document_xml = (
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:document xmlns:w="{namespace}" xmlns:r="{relationships}"><w:body>'
            f'<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>{title}</w:t></w:r></w:p>'
            f'<w:tbl>{"".join(rows)}</w:tbl><w:sectPr>'
            '<w:headerReference w:type="default" r:id="rId2"/>'
            '<w:footerReference w:type="default" r:id="rId3"/>'
            '</w:sectPr></w:body></w:document>'
        )
        output = BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                '<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
                '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
                '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
                '</Types>',
            )
            archive.writestr(
                "_rels/.rels",
                '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                '</Relationships>',
            )
            archive.writestr("word/document.xml", document_xml)
            archive.writestr(
                "word/_rels/document.xml.rels",
                '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>'
                '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
                '</Relationships>',
            )
            archive.writestr(
                "word/header1.xml",
                f'<?xml version="1.0"?><w:hdr xmlns:w="{namespace}"><w:p><w:r><w:t>SFPCL Approved Legal Template</w:t></w:r></w:p></w:hdr>',
            )
            archive.writestr(
                "word/footer1.xml",
                f'<?xml version="1.0"?><w:ftr xmlns:w="{namespace}"><w:p><w:r><w:t>{footer}</w:t></w:r></w:p></w:ftr>',
            )
            archive.writestr(
                "word/styles.xml",
                f'<?xml version="1.0"?><w:styles xmlns:w="{namespace}"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style></w:styles>',
            )
        return output.getvalue()

    @staticmethod
    def _extract_docx_text(content):
        texts = []
        with zipfile.ZipFile(BytesIO(content)) as archive:
            for name in archive.namelist():
                if name == "word/document.xml" or name.startswith(("word/header", "word/footer")):
                    root = ElementTree.fromstring(archive.read(name))
                    texts.extend(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
        return " ".join(texts)


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
        from sfpcl_credit.legal_documents.models import LoanDocument

        self.assertEqual(LoanDocument.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), 2)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(), 1
        )
