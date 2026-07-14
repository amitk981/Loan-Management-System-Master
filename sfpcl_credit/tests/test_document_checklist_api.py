import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless

from django.core.exceptions import ValidationError
from django.db import IntegrityError, close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import (
    ApprovalCase,
    ApprovalCaseReadScopeGrant,
    ApprovalMatrixRule,
    SanctionCommittee,
    SanctionDecision,
)
from sfpcl_credit.approvals.modules.approval_case_projection import (
    refresh_approval_case_projection,
)
from sfpcl_credit.credit.models import (
    AppraisalReviewDecision,
    LoanAppraisalNote,
    RiskAssessment,
)
from sfpcl_credit.credit.modules.appraisal_workflow import (
    project_approval_case_review_facts,
)
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
)
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.members.models import CancelledCheque, Member
from sfpcl_credit.processes import sanction_completion
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class DocumentChecklistApiTests(TestCase):
    password = "ChecklistPass123!"

    def setUp(self):
        self.client = Client()
        self.actor = self._user(
            "compliance_team_member",
            "Checklist Compliance",
            "documents.checklist.read",
        )
        self.cfo = self._user("cfo", "Checklist CFO")
        self.director = self._user("director", "Checklist Director")
        self.second_director = self._user("director", "Checklist Second Director")
        decision_date = timezone.localdate()
        self.rule = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction",
            amount_min="0.00",
            amount_max="500000.00",
            required_approver_roles_json=["cfo", "director"],
            required_director_count=1,
            joint_approval_required_flag=True,
            register_required="credit_sanction_register",
            effective_from=decision_date,
            status="active",
            version_number="checklist-rule-v1",
        )
        self.committee = SanctionCommittee.objects.create(
            committee_name="Checklist Committee",
            cfo_user=self.cfo,
            director_1_user=self.director,
            director_2_user=self.second_director,
            board_meeting_reference="BM-CHECKLIST-2026",
            effective_from=decision_date,
            status="active",
            version_number="checklist-committee-v1",
        )
        self.application, self.case = self._approved_application(
            "001", holding_mode="physical", subsidiary=True
        )

    def test_approved_sanction_creates_ordered_applicability_once_with_evidence(self):
        CancelledCheque.objects.create(
            loan_application_id=self.application.pk,
            member=self.application.member,
            document_id="10000000-0000-0000-0000-000000000001",
            account_number_encrypted="synthetic-token",
            account_number_hash="synthetic-hash-001",
            account_number_last4="0001",
            ifsc="SYNTH000001",
            verification_status="verified",
            signature_mismatch_flag=True,
        )

        checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        first_updated_at = checklist.updated_at
        first_items = list(checklist.items.order_by("display_order"))

        self.assertEqual(
            [item.item_code for item in first_items],
            [
                "witness_pan_aadhaar",
                "cancelled_cheque",
                "blank_dated_cheque",
                "poa",
                "tri_party_agreement",
                "sh4",
                "cdsl_pledge",
                "term_sheet",
                "loan_agreement",
                "bank_verification_letter",
                "final_checklist",
            ],
        )
        by_code = {item.item_code: item for item in first_items}
        for code in (
            "witness_pan_aadhaar",
            "cancelled_cheque",
            "blank_dated_cheque",
            "poa",
            "tri_party_agreement",
            "sh4",
            "term_sheet",
            "loan_agreement",
            "bank_verification_letter",
            "final_checklist",
        ):
            self.assertTrue(by_code[code].required_flag, code)
            self.assertTrue(by_code[code].applicable_flag, code)
            self.assertEqual(by_code[code].completion_status, "pending", code)
        self.assertFalse(by_code["cdsl_pledge"].required_flag)
        self.assertFalse(by_code["cdsl_pledge"].applicable_flag)
        self.assertEqual(by_code["cdsl_pledge"].completion_status, "not_applicable")
        self.assertIsNone(by_code["cdsl_pledge"].applicability_blocker)

        creation_audit = AuditLog.objects.get(action="document_checklist.created")
        self.assertEqual(creation_audit.actor_user, self.actor)
        self.assertEqual(creation_audit.entity_id, checklist.pk)
        self.assertEqual(
            creation_audit.new_value_json["sanction_decision_id"],
            str(self.application.sanction_decision.pk),
        )
        creation_event = WorkflowEvent.objects.get(
            workflow_name="documentation_checklist"
        )
        self.assertEqual(creation_event.triggered_by_user, self.actor)
        self.assertEqual(creation_event.entity_id, checklist.pk)

        replay = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        replay.refresh_from_db()
        self.assertEqual(replay.pk, checklist.pk)
        self.assertEqual(replay.updated_at, first_updated_at)
        self.assertEqual(DocumentChecklist.objects.count(), 1)
        self.assertEqual(ChecklistItem.objects.count(), 11)
        self.assertEqual(AuditLog.objects.filter(entity_id=checklist.pk).count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(entity_id=checklist.pk).count(), 1)

    def test_share_mode_variants_and_missing_or_conflicting_facts_do_not_guess(self):
        demat_application, _ = self._approved_application(
            "002", holding_mode="demat", subsidiary=False
        )
        missing_application, _ = self._approved_application(
            "003", holding_mode=None, subsidiary=False
        )
        conflicting_application, _ = self._approved_application(
            "004", holding_mode="mixed", subsidiary=False
        )
        CancelledCheque.objects.create(
            loan_application_id=demat_application.pk,
            member=demat_application.member,
            document_id="10000000-0000-0000-0000-000000000002",
            account_number_encrypted="synthetic-token",
            account_number_hash="synthetic-hash-002",
            account_number_last4="0002",
            ifsc="SYNTH000002",
            verification_status="verified",
            signature_mismatch_flag=False,
        )

        for application in (demat_application, missing_application, conflicting_application):
            document_checklist.refresh_for_approved_sanction(
                actor=self.actor,
                application_id=application.pk,
                source_reason="sanction_approved",
            )

        demat = self._items(demat_application)
        self.assertFalse(demat["sh4"].applicable_flag)
        self.assertTrue(demat["cdsl_pledge"].applicable_flag)
        self.assertFalse(demat["tri_party_agreement"].applicable_flag)
        self.assertFalse(demat["bank_verification_letter"].applicable_flag)
        self.assertEqual(
            demat["bank_verification_letter"].applicability_source,
            "persisted_signature_match",
        )
        self.assertIsNone(demat["bank_verification_letter"].applicability_blocker)

        for application, blocker in (
            (missing_application, "shareholding_mode_missing"),
            (conflicting_application, "shareholding_mode_conflicting"),
        ):
            items = self._items(application)
            for code in ("sh4", "cdsl_pledge"):
                self.assertFalse(items[code].applicable_flag)
                self.assertFalse(items[code].required_flag)
                self.assertEqual(items[code].completion_status, "not_applicable")
                self.assertEqual(items[code].applicability_blocker, blocker)

    def test_partial_subsidiary_snapshot_stays_blocked(self):
        active_member = self.case.appraisal_facts_json["eligibility"][
            "active_member_snapshot"
        ]
        active_member.pop("supplied_to_stepdown_flag")
        self.case.save(update_fields=["appraisal_facts_json"])

        document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="partial_subsidiary_snapshot",
        )

        item = self._items(self.application)["tri_party_agreement"]
        self.assertFalse(item.applicable_flag)
        self.assertEqual(item.applicability_source, "subsidiary_route_source_missing")
        self.assertEqual(item.applicability_blocker, "subsidiary_route_source_missing")

    def test_real_applicability_change_records_old_and_new_facts(self):
        checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        self.case.appraisal_facts_json["shareholding"]["holding_mode"] = "demat"
        self.case.save(update_fields=["appraisal_facts_json"])

        document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="retained_shareholding_mode_corrected",
            request_meta={
                "request_id": "req-applicability-correction",
                "ip_address": "203.0.113.44",
                "user_agent": "Checklist Correction Test",
            },
        )

        changed = AuditLog.objects.get(
            action="document_checklist.applicability_changed", entity_id=checklist.pk
        )
        self.assertEqual(changed.new_value_json["source_reason"], "retained_shareholding_mode_corrected")
        self.assertEqual(
            changed.new_value_json["request_id"], "req-applicability-correction"
        )
        self.assertEqual(changed.new_value_json["actor_role_codes"], self.actor.role_codes())
        self.assertEqual(changed.new_value_json["actor_team_codes"], self.actor.team_codes())
        self.assertEqual(changed.ip_address, "203.0.113.44")
        self.assertEqual(changed.user_agent, "Checklist Correction Test")
        self.assertEqual(changed.old_value_json["items"]["sh4"]["applicable_flag"], True)
        self.assertEqual(changed.new_value_json["items"]["sh4"]["applicable_flag"], False)
        self.assertNotIn("loan_document_id", changed.old_value_json["items"]["sh4"])
        self.assertNotIn("loan_document_id", changed.new_value_json["items"]["sh4"])
        self.assertEqual(changed.old_value_json["items"]["cdsl_pledge"]["applicable_flag"], False)
        self.assertEqual(changed.new_value_json["items"]["cdsl_pledge"]["applicable_flag"], True)
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="documentation_checklist", entity_id=checklist.pk
            ).count(),
            2,
        )

    def test_refresh_does_not_mislabel_presentation_metadata_as_applicability(self):
        checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        item = checklist.items.get(item_code="term_sheet")
        item.item_label = "Retained presentation label"
        item.display_order = 77
        item.save(update_fields=["item_label", "display_order"])

        document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="unchanged_applicability_refresh",
        )

        item.refresh_from_db()
        self.assertEqual(item.item_label, "Retained presentation label")
        self.assertEqual(item.display_order, 77)
        self.assertFalse(
            AuditLog.objects.filter(
                entity_id=checklist.pk,
                action="document_checklist.applicability_changed",
            ).exists()
        )

    def test_cancelled_cheque_owner_fact_matrix_fails_closed(self):
        cases = {}
        for index, label in enumerate(
            ("missing", "pending", "verified_match", "verified_mismatch", "conflict", "malformed"),
            start=20,
        ):
            application, _ = self._approved_application(
                str(index), holding_mode="physical", subsidiary=False
            )
            cases[label] = application
        for index, (label, status, mismatch) in enumerate(
            (
                ("pending", "pending", False),
                ("verified_match", "verified", False),
                ("verified_mismatch", "verified", True),
                ("conflict", "verified", False),
                ("conflict", "verified", True),
                ("malformed", "verified", False),
            ),
            start=1,
        ):
            cheque = CancelledCheque.objects.create(
                loan_application_id=cases[label].pk,
                member=cases[label].member,
                document_id=f"30000000-0000-0000-0000-{index:012d}",
                account_number_encrypted=f"synthetic-token-{index}",
                account_number_hash=f"synthetic-hash-{index}",
                account_number_last4=f"{index:04d}",
                ifsc=f"SYNTH{index:06d}",
                verification_status=status,
                signature_mismatch_flag=mismatch,
            )
            if label == "malformed":
                CancelledCheque.objects.filter(pk=cheque.pk).update(
                    verification_status="malformed"
                )

        for application in cases.values():
            document_checklist.refresh_for_approved_sanction(
                actor=self.actor,
                application_id=application.pk,
                source_reason="cheque_fact_matrix",
            )

        expected = {
            "missing": (False, "signature_mismatch_source_missing"),
            "pending": (False, "signature_mismatch_source_unverified"),
            "verified_match": (False, None),
            "verified_mismatch": (True, None),
            "conflict": (False, "signature_mismatch_conflicting"),
            "malformed": (False, "signature_mismatch_source_malformed"),
        }
        for label, application in cases.items():
            item = self._items(application)["bank_verification_letter"]
            applicable, blocker = expected[label]
            self.assertEqual(item.applicable_flag, applicable, label)
            self.assertEqual(item.applicability_blocker, blocker, label)
        source = inspect.getsource(
            importlib.import_module(
                "sfpcl_credit.legal_documents.modules.document_checklist"
            )
        )
        self.assertNotIn("members.models", source)
        self.assertNotIn("CancelledCheque", source)

    def test_refresh_preserves_completion_owner_facts_and_conflicts_atomically(self):
        checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        verified_at = timezone.now() - timedelta(minutes=5)
        sh4 = checklist.items.get(item_code="sh4")
        sh4.completion_status = ChecklistItem.STATUS_COMPLETE
        sh4.verified_by_user = self.actor
        sh4.verified_at = verified_at
        sh4.remarks = "Physical SH-4 verified by its owning workflow."
        sh4.save()
        term_sheet = checklist.items.get(item_code="term_sheet")
        term_sheet.completion_status = ChecklistItem.STATUS_COMPLETE
        term_sheet.remarks = "Completed owner evidence without verification yet."
        term_sheet.save()
        checklist.checklist_status = DocumentChecklist.STATUS_CS_APPROVED
        checklist.remarks = "Checklist owner state."
        checklist.save()
        retained = {
            "item": ChecklistItem.objects.filter(pk=sh4.pk).values().get(),
            "completed_item": ChecklistItem.objects.filter(pk=term_sheet.pk)
            .values()
            .get(),
            "checklist": DocumentChecklist.objects.filter(pk=checklist.pk).values().get(),
            "audit_count": AuditLog.objects.count(),
            "workflow_count": WorkflowEvent.objects.count(),
        }

        document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="unchanged_replay",
        )
        self.assertEqual(
            ChecklistItem.objects.filter(pk=sh4.pk).values().get(), retained["item"]
        )
        self.assertEqual(
            ChecklistItem.objects.filter(pk=term_sheet.pk).values().get(),
            retained["completed_item"],
        )
        self.assertEqual(
            DocumentChecklist.objects.filter(pk=checklist.pk).values().get(),
            retained["checklist"],
        )
        self.case.appraisal_facts_json["shareholding"]["holding_mode"] = "demat"
        self.case.save(update_fields=["appraisal_facts_json"])

        with self.assertRaises(document_checklist.ChecklistApplicabilityConflict):
            document_checklist.refresh_for_approved_sanction(
                actor=self.actor,
                application_id=self.application.pk,
                source_reason="shareholding_correction",
            )

        self.assertEqual(
            ChecklistItem.objects.filter(pk=sh4.pk).values().get(), retained["item"]
        )
        self.assertEqual(
            ChecklistItem.objects.filter(pk=term_sheet.pk).values().get(),
            retained["completed_item"],
        )
        self.assertEqual(
            DocumentChecklist.objects.filter(pk=checklist.pk).values().get(),
            retained["checklist"],
        )
        self.assertEqual(AuditLog.objects.count(), retained["audit_count"])
        self.assertEqual(WorkflowEvent.objects.count(), retained["workflow_count"])

    def test_legacy_unverified_document_cannot_link_to_checklist_item(self):
        template_file = DocumentFile.objects.create(
            file_name="term-sheet.docx",
            storage_provider="local",
            storage_key="templates/term-sheet.docx",
            sensitivity_level="internal",
        )
        output_file = DocumentFile.objects.create(
            file_name="term-sheet.pdf",
            storage_provider="local",
            storage_key="generated/term-sheet.pdf",
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code="checklist-term-sheet-v1",
            template_name="Checklist Term Sheet",
            document_type="term_sheet",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=template_file,
            merge_fields_json=[],
            approval_status="approved",
            effective_from=timezone.localdate(),
        )
        generated = LoanDocument.objects.create(
            loan_application=self.application,
            document_type="term_sheet",
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=output_file,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
        )

        checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        item = checklist.items.get(item_code="term_sheet")
        self.assertIsNone(item.loan_document)
        self.assertEqual(item.completion_status, "pending")
        self.assertIsNone(item.verified_by_user_id)
        self.assertIsNone(item.verified_at)

        response = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
            **self._auth(self.actor),
        )
        self.assertEqual(response.status_code, 200, response.json())
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        term_sheet = next(row for row in data["items"] if row["item_code"] == "term_sheet")
        self.assertIsNone(term_sheet["loan_document_id"])
        self.assertEqual(term_sheet["completion_status"], "pending")
        flattened = str(response.json())
        for secret in (
            "generated/term-sheet.pdf",
            "templates/term-sheet.docx",
            "term-sheet.pdf",
            "download_url",
            "available_actions",
        ):
            self.assertNotIn(secret, flattened)

    def test_current_provenance_document_links_without_completing_item(self):
        checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        item = checklist.items.get(item_code="term_sheet")
        item.completion_status = ChecklistItem.STATUS_COMPLETE
        item.verified_by_user = self.actor
        item.verified_at = timezone.now() - timedelta(minutes=3)
        item.remarks = "Execution owner evidence remains authoritative."
        item.save()
        retained_completion = ChecklistItem.objects.filter(pk=item.pk).values().get()
        template_file = DocumentFile.objects.create(
            file_name="current-template.docx",
            storage_provider="local",
            storage_key="templates/current-template.docx",
            checksum_sha256="a" * 64,
            sensitivity_level="internal",
        )
        output_file = DocumentFile.objects.create(
            file_name="current-term-sheet.pdf",
            storage_provider="local",
            storage_key="generated/current-term-sheet.pdf",
            checksum_sha256="b" * 64,
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code="checklist-current-term-sheet-v1",
            template_name="Current Checklist Term Sheet",
            document_type="term_sheet",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=template_file,
            merge_fields_json=[],
            approval_status="approved",
            effective_from=timezone.localdate(),
        )
        current = LoanDocument.objects.create(
            loan_application=self.application,
            document_type="term_sheet",
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=output_file,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=output_file.pk,
            renderer_validated_checksum_sha256=output_file.checksum_sha256,
        )

        document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="current_renderer_output_available",
            request_meta={
                "request_id": "req-current-renderer-link",
                "ip_address": "203.0.113.45",
                "user_agent": "Checklist Linkage Test",
            },
        )

        item.refresh_from_db()
        self.assertEqual(item.loan_document, current)
        for field in (
            "completion_status",
            "verified_by_user_id",
            "verified_at",
            "remarks",
        ):
            self.assertEqual(getattr(item, field), retained_completion[field])
        linkage = AuditLog.objects.get(
            action="document_checklist.linkage_changed", entity_id=checklist.pk
        )
        self.assertIsNone(
            linkage.old_value_json["items"]["term_sheet"]["loan_document_id"]
        )
        self.assertEqual(
            linkage.new_value_json["items"]["term_sheet"]["loan_document_id"],
            str(current.pk),
        )
        self.assertEqual(
            set(linkage.old_value_json["items"]["term_sheet"]),
            {"loan_document_id"},
        )
        self.assertEqual(
            set(linkage.new_value_json["items"]["term_sheet"]),
            {"loan_document_id"},
        )
        self.assertEqual(linkage.new_value_json["request_id"], "req-current-renderer-link")
        self.assertEqual(linkage.new_value_json["actor_role_codes"], self.actor.role_codes())
        self.assertEqual(linkage.new_value_json["actor_team_codes"], self.actor.team_codes())
        self.assertEqual(linkage.ip_address, "203.0.113.45")
        self.assertEqual(linkage.user_agent, "Checklist Linkage Test")
        self.assertFalse(
            AuditLog.objects.filter(
                action="document_checklist.applicability_changed",
                entity_id=checklist.pk,
            ).exists()
        )

    def test_get_enforces_permission_and_source_authorised_object_scope(self):
        document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        plain = self._user("plain_checklist", "Plain Checklist")
        permission_only = self._user(
            "permission_only", "Permission Only", "documents.checklist.read"
        )
        committee = self._user(
            "director", "Attributable Director", "documents.checklist.read"
        )
        unrelated_committee = self._user(
            "director", "Unrelated Director", "documents.checklist.read"
        )
        company_secretary = self._user(
            "company_secretary", "Checklist Company Secretary", "documents.checklist.read"
        )
        auditor = self._user(
            "internal_auditor", "Checklist Auditor", "documents.checklist.read"
        )
        credit_manager = self._user(
            "credit_manager",
            "Checklist Credit Manager",
            "documents.checklist.read",
            "applications.loan_application.read",
        )
        ApprovalCaseReadScopeGrant.objects.create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        )
        self.case.required_approvers_json = [
            {"user_id": str(committee.pk), "role_code": "director"}
        ]
        self.case.save(update_fields=["required_approvers_json"])

        denied = (
            (plain, "FORBIDDEN"),
            (permission_only, "OBJECT_ACCESS_DENIED"),
            (unrelated_committee, "OBJECT_ACCESS_DENIED"),
        )
        for user, code in denied:
            with self.subTest(user=user.email):
                headers = self._auth(user)
                with CaptureQueriesContext(connection) as queries:
                    response = self.client.get(
                        f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
                        **headers,
                    )
                self.assertEqual(response.status_code, 403)
                assert_error_envelope(self, response.json(), code)
                self.assertFalse(
                    any('FROM "document_checklists"' in query["sql"] for query in queries),
                    [query["sql"] for query in queries],
                )

        for user in (
            self.actor,
            committee,
            company_secretary,
            credit_manager,
            auditor,
        ):
            with self.subTest(user=user.email):
                response = self.client.get(
                    f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
                    **self._auth(user),
                )
                self.assertEqual(response.status_code, 200, response.json())
                self.assertEqual(
                    response.json()["data"]["signature_status"],
                    {
                        "company_secretary": "pending",
                        "credit_manager": "pending",
                        "sanction_committee": "pending",
                        "senior_manager_finance": "not_applicable_until_disbursement",
                    },
                )

        unknown_id = "ffffffff-ffff-ffff-ffff-ffffffffffff"
        unknown_compliance = self.client.get(
            f"/api/v1/loan-applications/{unknown_id}/document-checklist/",
            **self._auth(self.actor),
        )
        self.assertEqual(unknown_compliance.status_code, 404)
        assert_error_envelope(self, unknown_compliance.json(), "NOT_FOUND")
        unknown_permission_only = self.client.get(
            f"/api/v1/loan-applications/{unknown_id}/document-checklist/",
            **self._auth(permission_only),
        )
        self.assertEqual(unknown_permission_only.status_code, 403)
        assert_error_envelope(
            self, unknown_permission_only.json(), "OBJECT_ACCESS_DENIED"
        )

        inactive_headers = self._auth(credit_manager)
        credit_manager.status = "inactive"
        credit_manager.save(update_fields=["status"])
        inactive = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
            **inactive_headers,
        )
        self.assertEqual(inactive.status_code, 401)

        self.assertEqual(AuditLog.objects.filter(entity_type="document_checklist").count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(entity_type="document_checklist").count(), 1)

    def test_non_approved_or_incoherent_cases_create_nothing(self):
        for index, (status, decision, coherent) in enumerate((
            (ApprovalCase.STATUS_PENDING, None, True),
            (ApprovalCase.STATUS_REJECTED, None, True),
            (ApprovalCase.STATUS_RETURNED, None, True),
            (ApprovalCase.STATUS_BLOCKED_CONFLICT, None, True),
            (ApprovalCase.STATUS_APPROVED, "sanctioned", False),
        )):
            application, case = self._application_case(
                f"blocked-{index}",
                case_status=status,
                coherent=coherent,
                holding_mode="physical",
                subsidiary=False,
            )
            if decision:
                self._decision(application, case)
            with self.subTest(status=status, coherent=coherent):
                with self.assertRaises(document_checklist.InvalidChecklistState):
                    document_checklist.refresh_for_approved_sanction(
                        actor=self.actor,
                        application_id=application.pk,
                        source_reason="sanction_approved",
                    )
        self.assertEqual(DocumentChecklist.objects.count(), 0)

    def test_invalid_direct_item_states_fail_validation_and_database_constraints(self):
        checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )
        invalid = ChecklistItem(
            document_checklist=checklist,
            item_code="invalid",
            item_label="Invalid",
            display_order=99,
            required_flag=True,
            applicable_flag=False,
            completion_status="pending",
            applicability_source="test",
        )
        with self.assertRaises(ValidationError):
            invalid.full_clean()
        with self.assertRaises(IntegrityError):
            ChecklistItem.objects.bulk_create([invalid])

    def test_dependency_direction_keeps_approvals_free_of_legal_imports(self):
        approval_actions = importlib.import_module(
            "sfpcl_credit.approvals.modules.approval_actions"
        )
        legal_checklist = importlib.import_module(
            "sfpcl_credit.legal_documents.modules.document_checklist"
        )
        completion = importlib.import_module(
            "sfpcl_credit.processes.sanction_completion"
        )
        self.assertNotIn("legal_documents", inspect.getsource(approval_actions))
        legal_read_source = inspect.getsource(legal_checklist.read_for_application)
        self.assertIn("document_checklist_access.resolve_read_access", legal_read_source)
        self.assertNotIn("role_codes", legal_read_source)
        self.assertNotIn("auth_service", legal_read_source)
        self.assertIn("document_checklist", inspect.getsource(completion))

    def _items(self, application):
        checklist = DocumentChecklist.objects.get(loan_application=application)
        return {item.item_code: item for item in checklist.items.all()}

    def _approved_application(self, suffix, *, holding_mode, subsidiary):
        application, case = self._application_case(
            suffix,
            case_status=ApprovalCase.STATUS_APPROVED,
            coherent=True,
            holding_mode=holding_mode,
            subsidiary=subsidiary,
        )
        self._decision(application, case)
        return application, case

    def _application_case(
        self, suffix, *, case_status, coherent, holding_mode, subsidiary
    ):
        member = Member.objects.create(
            member_number=f"MEM-CHECK-{suffix}",
            member_type="individual_farmer",
            legal_name=f"Checklist Borrower {suffix}",
            display_name=f"Checklist Borrower {suffix}",
            folio_number=f"FOL-CHECK-{suffix}",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        application = LoanApplication.objects.create(
            application_reference_number=f"LO-CHECK-{suffix}",
            member=member,
            borrower_type="individual_farmer",
            received_by_user=self.actor,
            created_by_user=self.actor,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Seasonal crop finance",
            purpose_category="crop_production",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=(
                LoanApplication.STATUS_APPROVED_BY_SANCTION
                if case_status == ApprovalCase.STATUS_APPROVED
                else LoanApplication.STATUS_SUBMITTED_TO_SANCTION
            ),
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
        )
        risk = RiskAssessment.objects.create(
            loan_application=application,
            market_risk_rating="low",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            assessed_by_user=self.actor,
        )
        calculated_at = timezone.now() - timedelta(hours=1)
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=self.actor,
            reviewed_by_user=self.actor,
            reviewed_at=timezone.now(),
            last_review_decision="reviewed",
            tat_due_at=timezone.now() + timedelta(days=1),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="10000000-0000-0000-0000-000000000001",
            loan_limit_assessment_id_snapshot="20000000-0000-0000-0000-000000000002",
            eligibility_snapshot_json={
                "eligibility_assessment_id": "10000000-0000-0000-0000-000000000001",
                "loan_application_id": str(application.pk),
                "overall_result": "eligible",
                "member_active_check": "pass",
                "default_check": "pass",
                "document_check": "pass",
                "terms_acceptance_check": "pass",
                "purpose_check": "pass",
                "nominee_check": "pass",
                "assessment_notes": "Eligible for checklist fixture.",
                "active_member_snapshot": {
                    "supplied_to_subsidiary_flag": subsidiary,
                    "supplied_to_stepdown_flag": False,
                },
                "assessed_by_user_id": str(self.actor.pk),
                "assessed_at": calculated_at.isoformat(),
            },
            loan_limit_snapshot_json={
                "loan_limit_assessment_id": "20000000-0000-0000-0000-000000000002",
                "loan_application_id": str(application.pk),
                "final_eligible_loan_amount": "400000.00",
                "exception_required_flag": False,
                "calculation_rule_version": "checklist-limit-v1",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Checklist Test Policy",
                "calculated_at": calculated_at.isoformat(),
            },
            prerequisite_provenance="verified",
            borrower_summary="No prior borrowing.",
            eligibility_summary="Eligible.",
            loan_limit_summary="Within limit.",
            recommended_amount="400000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Standard security.",
            repayment_capacity_notes="Adequate.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=note,
            decision="reviewed",
            review_comments="Immutable checklist test review.",
            reviewer_user=self.actor,
            decided_at=note.reviewed_at,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
        note = LoanAppraisalNote.objects.select_related("risk_assessment").get(
            pk=note.pk
        )
        decision_date = timezone.localdate()
        case = ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            appraisal_review_decision=review,
            submitted_by_user=self.actor,
            submission_remarks="Checklist facts.",
            approval_matrix_rule=self.rule,
            approval_matrix_rule_version=self.rule.version_number,
            sanction_committee=self.committee,
            sanction_committee_version=self.committee.version_number,
            required_approvers_json=[
                {
                    "role_code": "cfo",
                    "user_id": str(self.cfo.pk),
                    "full_name": self.cfo.full_name,
                },
                {
                    "role_code": "director",
                    "user_id": str(self.director.pk),
                    "full_name": self.director.full_name,
                },
            ],
            excluded_approvers_json=[],
            current_status=case_status,
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=application.pk,
            reason_for_approval="Approved for checklist.",
            closed_at=(timezone.now() if case_status != ApprovalCase.STATUS_PENDING else None),
            matrix_projection_json={
                "approval_matrix_rule_id": str(self.rule.pk),
                "version_number": self.rule.version_number,
                "decision_type": "loan_sanction",
                "amount": "400000.00",
                "amount_min": "0.00",
                "amount_max": "500000.00",
                "condition_code": None,
                "decision_date": decision_date.isoformat(),
                "required_approver_roles": ["cfo", "director"],
                "required_director_count": 1,
                "joint_approval_required": True,
                "register_required": "credit_sanction_register",
            },
            committee_projection_json={
                "sanction_committee_id": str(self.committee.pk),
                "version_number": self.committee.version_number,
                "decision_date": decision_date.isoformat(),
                "cfo_user_id": str(self.cfo.pk),
                "director_user_ids": [
                    str(self.director.pk),
                    str(self.second_director.pk),
                ],
            },
            loan_limit_provenance_json={
                **note.loan_limit_snapshot_json,
                "loan_limit_assessment_id": str(
                    note.loan_limit_assessment_id_snapshot
                ),
            },
            decision_date=decision_date,
            version=2,
        )
        case = ApprovalCase.objects.select_related(
            "loan_application", "loan_appraisal_note__risk_assessment"
        ).get(pk=case.pk)
        case.appraisal_facts_json = project_approval_case_review_facts(
            application=application,
            appraisal_note=note,
            review=review,
        )
        case.appraisal_facts_json["shareholding"] = {"holding_mode": holding_mode}
        case.save(update_fields=["appraisal_facts_json"])
        refresh_approval_case_projection(case)
        if not coherent:
            malformed = case.appraisal_facts_json
            malformed["borrower"].pop("name")
            case.appraisal_facts_json = malformed
            case.routing_snapshot_is_coherent = True
            case.save(
                update_fields=["appraisal_facts_json", "routing_snapshot_is_coherent"]
            )
        return application, case

    @staticmethod
    def _decision(application, case):
        return SanctionDecision.objects.create(
            loan_application=application,
            approval_case=case,
            decision="sanctioned",
            sanctioned_amount="400000.00",
            sanctioned_tenure_months=12,
            interest_rate_type="floating",
            security_required_summary="Standard security.",
            decision_reason="Approved.",
        )

    def _user(self, role_code, full_name, *permission_codes):
        role, _ = Role.objects.get_or_create(
            role_code=role_code,
            defaults={"role_name": full_name, "status": "active"},
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={"permission_name": code, "risk_level": "medium"},
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)
        user = User.objects.create(
            full_name=full_name,
            email=f"{role.role_code}-{User.objects.count()}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save()
        return user

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.json())
        return {
            "HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"
        }


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative checklist five-race requires PostgreSQL.",
)
class DocumentChecklistConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def test_five_final_sanction_attempts_persist_one_atomic_checklist_ledger(self):
        fixture = DocumentChecklistApiTests(methodName="test_approved_sanction_creates_ordered_applicability_once_with_evidence")
        fixture.setUp()
        application, case = fixture._application_case(
            "final-race",
            case_status=ApprovalCase.STATUS_PENDING,
            coherent=True,
            holding_mode="physical",
            subsidiary=True,
        )
        sanction_completion.approve_case(
            actor=fixture.cfo,
            case_id=case.pk,
            payload={"version": 2, "comments": "Seed first joint approval."},
            actor_permissions={"approvals.case.approve", "approvals.case.read"},
            request_meta={"request_id": "final-race-seed"},
        )
        actor_id = fixture.director.pk
        gate = Barrier(5)

        def approve(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=actor_id)
                gate.wait(timeout=10)
                try:
                    result = sanction_completion.approve_case(
                        actor=actor,
                        case_id=case.pk,
                        payload={
                            "version": 3,
                            "comments": f"Concurrent final sanction {index}.",
                        },
                        actor_permissions={
                            "approvals.case.approve",
                            "approvals.case.read",
                        },
                        request_meta={
                            "request_id": f"final-sanction-race-{index}",
                            "ip_address": f"203.0.113.{index + 1}",
                            "user_agent": "Checklist Final Race",
                        },
                    )
                    return "won", index, result["sanction_decision_id"]
                except Exception as exc:
                    from sfpcl_credit.approvals.modules import approval_actions

                    if isinstance(exc, approval_actions.ApprovalActionConflict):
                        return exc.code, index, None
                    raise
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(approve, index) for index in range(5)]
            results = [future.result(timeout=30) for future in futures]

        self.assertEqual([code for code, _, _ in results].count("won"), 1)
        self.assertEqual([code for code, _, _ in results].count("STALE_VERSION"), 4)
        self.assertEqual(
            SanctionDecision.objects.filter(loan_application=application).count(), 1
        )
        checklist = DocumentChecklist.objects.get(loan_application=application)
        self.assertEqual(
            ChecklistItem.objects.filter(document_checklist=checklist).count(), 11
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="document_checklist.created", entity_id=checklist.pk
            ).count(),
            1,
        )
        winner_code, winner_index, winner_decision_id = next(
            result for result in results if result[0] == "won"
        )
        self.assertEqual(winner_code, "won")
        creation = AuditLog.objects.get(
            action="document_checklist.created", entity_id=checklist.pk
        )
        self.assertEqual(
            creation.new_value_json["request_id"],
            f"final-sanction-race-{winner_index}",
        )
        self.assertEqual(
            creation.new_value_json["sanction_decision_id"], winner_decision_id
        )
        self.assertEqual(creation.ip_address, f"203.0.113.{winner_index + 1}")
        self.assertEqual(creation.user_agent, "Checklist Final Race")
