from decimal import Decimal
from uuid import uuid4

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class CreditAssessmentModelOwnershipMigrationTests(TransactionTestCase):
    migrate_from = [("applications", "0010_loanapplication_nominee"), ("credit", None)]
    migrate_to = [
        ("credit", "0001_credit_assessment_model_ownership"),
        ("workflows", "0001_canonical_workflow_event"),
    ]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        pre_move_state_targets = [
            node
            for node in self.executor.loader.graph.leaf_nodes()
            # Downstream configuration, legal-document, loan-account, monitoring, default,
            # recovery, closure, compliance, member-correction, SAP, and communications ownership
            # (including interest invoices) anchors current approval/application state and must not
            # outrun this historical pre-move projection.
            if node[0]
            not in {
                "credit",
                "approvals",
                "members",
                "loans",
                "sap_workflow",
                "disbursements",
                "communications",
                "legal_documents",
                "configurations",
                "interest",
                "monitoring",
                "defaults",
                "recovery",
                "closure",
                "compliance",
            }
        ]
        old_apps = self.executor.loader.project_state(pre_move_state_targets).apps
        self.identifiers = self._create_pre_move_rows(old_apps)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_forward_move_preserves_rows_relationships_and_evidence_references(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        moved_apps = self.executor.loader.project_state(self.migrate_to).apps

        with self.assertRaises(LookupError):
            moved_apps.get_model("applications", "EligibilityAssessment")
        with self.assertRaises(LookupError):
            moved_apps.get_model("applications", "LoanLimitAssessment")
        eligibility_model = moved_apps.get_model("credit", "EligibilityAssessment")
        loan_limit_model = moved_apps.get_model("credit", "LoanLimitAssessment")

        eligibility = eligibility_model.objects.get(
            eligibility_assessment_id=self.identifiers["eligibility_id"]
        )
        loan_limit = loan_limit_model.objects.get(
            loan_limit_assessment_id=self.identifiers["loan_limit_id"]
        )

        self.assertEqual(eligibility.loan_application_id, self.identifiers["application_id"])
        self.assertEqual(eligibility.assessed_by_user_id, self.identifiers["user_id"])
        self.assertEqual(loan_limit.loan_application_id, self.identifiers["application_id"])
        self.assertEqual(loan_limit.member_id, self.identifiers["member_id"])
        self.assertEqual(loan_limit.shareholding_id, self.identifiers["shareholding_id"])
        self.assertEqual(loan_limit.calculated_by_user_id, self.identifiers["user_id"])

        audit_model = moved_apps.get_model("identity", "AuditLog")
        workflow_model = moved_apps.get_model("workflows", "WorkflowEvent")
        self.assertEqual(
            audit_model.objects.get(audit_log_id=self.identifiers["audit_id"]).entity_id,
            self.identifiers["loan_limit_id"],
        )
        self.assertEqual(
            workflow_model.objects.get(
                workflow_event_id=self.identifiers["workflow_id"]
            ).entity_id,
            self.identifiers["loan_limit_id"],
        )

        self.assertEqual(eligibility_model._meta.db_table, "eligibility_assessments")
        self.assertEqual(loan_limit_model._meta.db_table, "loan_limit_assessments")

    def test_reverse_move_restores_application_state_without_changing_rows(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        self.executor = MigrationExecutor(connection)
        reverse_targets = [
            ("applications", "0010_loanapplication_nominee"),
            ("workflows", "0001_canonical_workflow_event"),
            ("credit", None),
        ]
        self.executor.migrate(reverse_targets)
        rolled_back_apps = self.executor.loader.project_state(reverse_targets[:2]).apps

        with self.assertRaises(LookupError):
            rolled_back_apps.get_model("credit", "EligibilityAssessment")
        with self.assertRaises(LookupError):
            rolled_back_apps.get_model("credit", "LoanLimitAssessment")
        eligibility_model = rolled_back_apps.get_model(
            "applications", "EligibilityAssessment"
        )
        loan_limit_model = rolled_back_apps.get_model("applications", "LoanLimitAssessment")

        eligibility = eligibility_model.objects.get(
            eligibility_assessment_id=self.identifiers["eligibility_id"]
        )
        loan_limit = loan_limit_model.objects.get(
            loan_limit_assessment_id=self.identifiers["loan_limit_id"]
        )
        self.assertEqual(eligibility.loan_application_id, self.identifiers["application_id"])
        self.assertEqual(eligibility.assessed_by_user_id, self.identifiers["user_id"])
        self.assertEqual(loan_limit.loan_application_id, self.identifiers["application_id"])
        self.assertEqual(loan_limit.member_id, self.identifiers["member_id"])
        self.assertEqual(loan_limit.shareholding_id, self.identifiers["shareholding_id"])
        self.assertEqual(loan_limit.calculated_by_user_id, self.identifiers["user_id"])

        audit_model = rolled_back_apps.get_model("identity", "AuditLog")
        workflow_model = rolled_back_apps.get_model("workflows", "WorkflowEvent")
        self.assertEqual(
            audit_model.objects.get(audit_log_id=self.identifiers["audit_id"]).entity_id,
            self.identifiers["loan_limit_id"],
        )
        self.assertEqual(
            workflow_model.objects.get(
                workflow_event_id=self.identifiers["workflow_id"]
            ).entity_id,
            self.identifiers["loan_limit_id"],
        )
        self.assertEqual(eligibility_model._meta.db_table, "eligibility_assessments")
        self.assertEqual(loan_limit_model._meta.db_table, "loan_limit_assessments")

    def _create_pre_move_rows(self, old_apps):
        Role = old_apps.get_model("identity", "Role")
        User = old_apps.get_model("identity", "User")
        Member = old_apps.get_model("members", "Member")
        Shareholding = old_apps.get_model("members", "Shareholding")
        LoanApplication = old_apps.get_model("applications", "LoanApplication")
        EligibilityAssessment = old_apps.get_model("applications", "EligibilityAssessment")
        LoanLimitAssessment = old_apps.get_model("applications", "LoanLimitAssessment")
        AuditLog = old_apps.get_model("identity", "AuditLog")
        WorkflowEvent = old_apps.get_model("workflows", "WorkflowEvent")

        role = Role.objects.create(role_code="migration_credit", role_name="Migration Credit")
        user = User.objects.create(
            full_name="Migration Proof User",
            email="migration-proof@sfpcl.example",
            primary_role=role,
            password_hash="not-a-real-password",
        )
        member = Member.objects.create(
            member_number="MEM-MIGRATION-PROOF",
            member_type="individual_farmer",
            legal_name="Migration Proof Member",
            display_name="Migration Proof Member",
            folio_number="FOL-MIGRATION-PROOF",
            membership_status="active",
            pan_encrypted="synthetic-pan-token",
            pan_hash="synthetic-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        shareholding = Shareholding.objects.create(
            member=member,
            folio_number=member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share=Decimal("1000.00"),
            pledged_share_count=0,
            available_share_count=100,
        )
        application = LoanApplication.objects.create(
            member=member,
            borrower_type="individual_farmer",
            received_by_user=user,
        )
        eligibility_id = uuid4()
        loan_limit_id = uuid4()
        EligibilityAssessment.objects.create(
            eligibility_assessment_id=eligibility_id,
            loan_application=application,
            member_active_check="pass",
            default_check="no_default",
            document_check="complete",
            terms_acceptance_check="accepted",
            purpose_check="agriculture_aligned",
            nominee_check="valid",
            overall_result="eligible",
            assessed_by_user=user,
        )
        LoanLimitAssessment.objects.create(
            loan_limit_assessment_id=loan_limit_id,
            loan_application=application,
            member=member,
            shareholding=shareholding,
            number_of_shares=100,
            valuation_per_share=Decimal("1000.00"),
            share_limit_percentage=Decimal("30.0000"),
            per_share_cap_amount=Decimal("200.00"),
            shareholding_based_limit_amount=Decimal("20000.00"),
            land_area_acres=Decimal("1.00"),
            scale_of_finance_per_acre_amount=Decimal("20000.00"),
            land_based_limit_amount=Decimal("20000.00"),
            final_eligible_loan_amount=Decimal("20000.00"),
            requested_amount=Decimal("20000.00"),
            amount_within_limit_flag=True,
            exception_required_flag=False,
            calculation_rule_version="migration-proof-v1",
            calculated_by_user=user,
        )
        audit = AuditLog.objects.create(
            actor_user=user,
            action="loan_limit.calculated",
            entity_type="loan_limit_assessment",
            entity_id=loan_limit_id,
        )
        workflow = WorkflowEvent.objects.create(
            workflow_name="loan_limit_assessment",
            entity_type="loan_limit_assessment",
            entity_id=loan_limit_id,
            to_state="calculated",
            triggered_by_user=user,
        )
        return {
            "eligibility_id": eligibility_id,
            "loan_limit_id": loan_limit_id,
            "application_id": application.loan_application_id,
            "member_id": member.member_id,
            "shareholding_id": shareholding.shareholding_id,
            "user_id": user.user_id,
            "audit_id": audit.audit_log_id,
            "workflow_id": workflow.workflow_event_id,
        }
