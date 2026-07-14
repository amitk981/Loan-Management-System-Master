import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless

from django.core.exceptions import ValidationError
from django.db import IntegrityError, close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import (
    ApprovalCase,
    ApprovalCaseReadScopeGrant,
    SanctionDecision,
)
from sfpcl_credit.credit.models import LoanAppraisalNote, RiskAssessment
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
)
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.members.models import CancelledCheque, Member
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
        )

        changed = AuditLog.objects.get(
            action="document_checklist.applicability_changed", entity_id=checklist.pk
        )
        self.assertEqual(changed.new_value_json["source_reason"], "retained_shareholding_mode_corrected")
        self.assertEqual(changed.old_value_json["items"]["sh4"]["applicable_flag"], True)
        self.assertEqual(changed.new_value_json["items"]["sh4"]["applicable_flag"], False)
        self.assertEqual(changed.old_value_json["items"]["cdsl_pledge"]["applicable_flag"], False)
        self.assertEqual(changed.new_value_json["items"]["cdsl_pledge"]["applicable_flag"], True)
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="documentation_checklist", entity_id=checklist.pk
            ).count(),
            2,
        )

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

        checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.actor,
            application_id=self.application.pk,
            source_reason="sanction_approved",
        )

        item = checklist.items.get(item_code="term_sheet")
        self.assertEqual(item.loan_document, current)
        self.assertEqual(item.completion_status, "pending")
        self.assertIsNone(item.verified_by_user_id)
        self.assertIsNone(item.verified_at)

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
                response = self.client.get(
                    f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
                    **self._auth(user),
                )
                self.assertEqual(response.status_code, 403)
                assert_error_envelope(self, response.json(), code)

        for user in (self.actor, committee, company_secretary, auditor):
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
        completion = importlib.import_module(
            "sfpcl_credit.processes.sanction_completion"
        )
        self.assertNotIn("legal_documents", inspect.getsource(approval_actions))
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
            eligibility_snapshot_json={"overall_result": "eligible"},
            loan_limit_snapshot_json={"final_eligible_loan_amount": "400000.00"},
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
        case = ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            submitted_by_user=self.actor,
            submission_remarks="Checklist facts.",
            current_status=case_status,
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=application.pk,
            reason_for_approval="Approved for checklist.",
            routing_snapshot_is_coherent=coherent,
            closed_at=(timezone.now() if case_status != ApprovalCase.STATUS_PENDING else None),
            appraisal_facts_json={
                "snapshot_schema_version": "approval-review-v3",
                "shareholding": {"holding_mode": holding_mode},
                "eligibility": {
                    "active_member_snapshot": {
                        "supplied_to_subsidiary_flag": subsidiary,
                        "supplied_to_stepdown_flag": False,
                    }
                },
            },
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

    def test_five_refreshes_persist_one_checklist_and_item_ledger(self):
        fixture = DocumentChecklistApiTests(methodName="test_approved_sanction_creates_ordered_applicability_once_with_evidence")
        fixture.setUp()
        application_id = fixture.application.pk
        actor_id = fixture.actor.pk
        gate = Barrier(5)

        def refresh(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=actor_id)
                gate.wait(timeout=10)
                checklist = document_checklist.refresh_for_approved_sanction(
                    actor=actor,
                    application_id=application_id,
                    source_reason=f"race-{index}",
                )
                return checklist.pk
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(refresh, index) for index in range(5)]
            ids = [future.result(timeout=20) for future in futures]

        self.assertEqual(len(set(ids)), 1)
        self.assertEqual(DocumentChecklist.objects.count(), 1)
        self.assertEqual(ChecklistItem.objects.count(), 11)
        self.assertEqual(
            AuditLog.objects.filter(action="document_checklist.created").count(), 1
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="document_checklist.applicability_changed"
            ).count(),
            0,
        )
