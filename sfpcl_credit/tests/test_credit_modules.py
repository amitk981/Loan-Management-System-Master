import ast
from contextlib import ExitStack
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Event, Lock
from unittest import skipUnless
from uuid import uuid4
from unittest.mock import patch

from django.db import close_old_connections, connection, connections
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.applications.models import (
    ApplicationDocument,
    LoanApplication,
)
from sfpcl_credit.configurations.models import LoanPolicyConfig
from sfpcl_credit.credit.models import EligibilityAssessment, LoanLimitAssessment
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import (
    CancelledCheque,
    CropPlan,
    IndividualMemberProfile,
    LandHolding,
    Member,
    Nominee,
    ProduceSupplyRecord,
    Shareholding,
)
from sfpcl_credit.workflows.models import WorkflowEvent


APPLICATION_READ_PERMISSION = "applications.loan_application.read"
ELIGIBILITY_RUN_PERMISSION = "credit.eligibility.run"
LOAN_LIMIT_CALCULATE_PERMISSION = "credit.loan_limit.calculate"


class CreditEligibilityModuleTests(TestCase):
    def setUp(self):
        self.actor = self._user(
            "credit.module.actor@sfpcl.example",
            self._permission(APPLICATION_READ_PERMISSION, "View applications"),
            self._permission(ELIGIBILITY_RUN_PERMISSION, "Run eligibility assessment"),
            self._permission(LOAN_LIMIT_CALCULATE_PERMISSION, "Calculate loan limit"),
        )
        self.member = Member.objects.create(
            member_number="MEM-CREDIT-MODULE",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            folio_number="FOL-CREDIT-MODULE",
            membership_status="active",
            pan_encrypted="member-pan-token",
            pan_hash="member-pan-hash",
            aadhaar_encrypted="member-aadhaar-token",
            aadhaar_hash="member-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
            active_member_status="active",
            active_member_verified_at=timezone.now(),
        )
        IndividualMemberProfile.objects.create(
            member=self.member, first_name="Ramesh", last_name="Patil",
            services_availed_flag=True,
        )
        for year in ("2022-23", "2023-24", "2024-25", "2025-26"):
            ProduceSupplyRecord.objects.create(
                member=self.member, financial_year=year,
                supplied_to_entity_type="sfpcl", supply_route="direct",
                evidence_reference=f"ERP-CREDIT-{year}",
                captured_by_user=self.actor, verified_flag=True,
                verified_by_user=self.actor, verified_at=timezone.now(),
            )
        self.land = LandHolding.objects.create(
            member=self.member,
            document_type="7_12_extract",
            survey_number="123/4",
            village="Niphad",
            area_acres="5.00",
            document_id=uuid4(),
            verification_status="verified",
            verified_by_user=self.actor,
            verified_at=timezone.now(),
        )
        self.crop = CropPlan.objects.create(
            member=self.member,
            crop_type="grapes",
            season="FY2026 Kharif",
            planned_area_acres="5.00",
            estimated_cost_amount="100000.00",
            loan_purpose_alignment="agriculture_aligned",
            document_id=uuid4(),
            verification_status="verified",
            verified_by_user=self.actor,
            verified_at=timezone.now(),
        )
        self.nominee = Nominee.objects.create(
            member=self.member,
            nominee_name="Sita Patil",
            age_at_application=42,
            gender="female",
            relationship_to_borrower="Spouse",
            pan_encrypted="nominee-pan-token",
            pan_hash="nominee-pan-hash",
            aadhaar_encrypted="nominee-aadhaar-token",
            aadhaar_hash="nominee-aadhaar-hash",
            kyc_status="verified",
            minor_flag=False,
        )
        cheque = CancelledCheque.objects.create(
            member=self.member,
            document_id=uuid4(),
            account_number_encrypted="cheque-token",
            account_number_hash="cheque-hash",
            account_number_last4="9012",
            ifsc="HDFC0001234",
            branch_name="Nashik Road",
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="LO00000999",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.actor,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Crop production loan for grape cultivation",
            purpose_category="crop_production",
            nominee=self.nominee,
            loan_type_requested="short_term",
            land_holding=self.land,
            crop_plan=self.crop,
            cancelled_cheque=cheque,
            terms_acceptance_flag=True,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_REFERENCE_GENERATED,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            submitted_at=timezone.now(),
            submitted_by_user=self.actor,
            created_by_user=self.actor,
        )
        self.crop.loan_application_id = self.application.loan_application_id
        self.crop.save(update_fields=["loan_application_id"])
        self.nominee.loan_application_id = self.application.loan_application_id
        self.nominee.save(update_fields=["loan_application_id"])
        self._verified_required_documents()

    def test_eligible_assessment_runs_through_source_named_module_interface(self):
        from sfpcl_credit.credit.modules.eligibility_assessment import (
            EligibilityAssessmentModule,
            EligibilityAssessmentResult,
        )

        result = EligibilityAssessmentModule().run(
            actor=self.actor,
            application_id=self.application.loan_application_id,
            request_meta={
                "request_id": "req-credit-module-eligibility",
                "ip_address": "127.0.0.1",
                "user_agent": "credit-module-test",
            },
        )

        self.assertIsInstance(result, EligibilityAssessmentResult)
        self.assertEqual(result.snapshot["overall_result"], "eligible")
        self.assertEqual(result.snapshot["document_check"], "complete")
        self.assertEqual(result.snapshot["nominee_check"], "valid")
        self.assertEqual(
            AuditLog.objects.get(action="eligibility.assessed").new_value_json["request_id"],
            "req-credit-module-eligibility",
        )
        self.assertTrue(
            WorkflowEvent.objects.filter(
                workflow_name="eligibility_assessment",
                entity_id=self.application.loan_application_id,
            ).exists()
        )

    def test_eligibility_action_and_write_share_the_locked_transition_evaluation(self):
        from sfpcl_credit.credit.modules.common import CreditModuleInvalidStateError
        from sfpcl_credit.credit.modules.eligibility_assessment import (
            EligibilityAssessmentModule,
            evaluate_eligibility_run,
        )

        LoanApplication.objects.filter(pk=self.application.pk).update(
            completeness_status=LoanApplication.COMPLETENESS_INCOMPLETE
        )
        self.application.refresh_from_db()
        evaluation = evaluate_eligibility_run(self.application)

        self.assertFalse(evaluation.allowed)
        self.assertEqual(
            evaluation.reason,
            "Eligibility assessment requires complete application documentation.",
        )
        with self.assertRaisesMessage(CreditModuleInvalidStateError, evaluation.reason):
            EligibilityAssessmentModule().run(
                actor=self.actor,
                application_id=self.application.loan_application_id,
            )
        self.assertFalse(AuditLog.objects.filter(action="eligibility.assessed").exists())
        self.assertFalse(WorkflowEvent.objects.filter(workflow_name="eligibility_assessment").exists())

    def test_ineligible_assessment_returns_source_backed_blockers(self):
        from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule

        self.member.default_status = "default_found"
        self.member.save(update_fields=["default_status"])

        result = EligibilityAssessmentModule().run(
            actor=self.actor,
            application_id=self.application.loan_application_id,
        )

        self.assertEqual(result.snapshot["overall_result"], "ineligible")
        self.assertEqual(result.snapshot["default_check"], "default_found")
        self.assertIn("BR-008", result.snapshot["assessment_notes"])

    def test_pending_assessment_preserves_manual_evidence_result(self):
        from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule

        self.member.active_member_status = "pending"
        self.member.active_member_verified_at = None
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        self.member.individual_profile.services_availed_flag = False
        self.member.individual_profile.save(update_fields=["services_availed_flag"])

        result = EligibilityAssessmentModule().run(
            actor=self.actor,
            application_id=self.application.loan_application_id,
        )

        self.assertEqual(result.snapshot["overall_result"], "pending_manual_evidence")
        self.assertEqual(result.snapshot["member_active_check"], "manual_evidence_required")
        self.assertIn("BR-004 through BR-007", result.snapshot["assessment_notes"])

    def test_audit_failure_rolls_back_assessment_and_workflow_event(self):
        from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule

        with patch.object(AuditLog.objects, "create", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaisesMessage(RuntimeError, "audit unavailable"):
                EligibilityAssessmentModule().run(
                    actor=self.actor,
                    application_id=self.application.loan_application_id,
                )

        self.assertFalse(
            EligibilityAssessment.objects.filter(loan_application=self.application).exists()
        )
        self.assertFalse(
            WorkflowEvent.objects.filter(
                workflow_name="eligibility_assessment",
                entity_id=self.application.loan_application_id,
            ).exists()
        )

    def test_configuration_resolver_returns_the_single_effective_board_policy(self):
        from sfpcl_credit.configurations.modules.configuration_resolver import (
            resolve_effective_loan_policy,
        )

        policy = self._active_loan_policy()

        resolved = resolve_effective_loan_policy(calculation_date=timezone.localdate())

        self.assertEqual(resolved.loan_policy_config_id, policy.loan_policy_config_id)

    def test_configuration_resolver_rejects_overlapping_effective_policies(self):
        from sfpcl_credit.configurations.modules.configuration_resolver import (
            ConfigurationResolutionError,
            resolve_effective_loan_policy,
        )

        self._active_loan_policy(policy_version="loan-policy-v1.0")
        self._active_loan_policy(policy_version="loan-policy-v1.1")

        with self.assertRaises(ConfigurationResolutionError) as raised:
            resolve_effective_loan_policy(calculation_date=timezone.localdate())

        self.assertEqual(
            raised.exception.field_errors,
            {
                "loan_policy_config": (
                    "Exactly one active loan policy must apply on calculation_date."
                )
            },
        )

    def test_static_import_boundary_routes_loan_limit_and_appraisal_through_credit_modules(self):
        package_root = Path(__file__).resolve().parents[1]
        services_source = (package_root / "applications" / "services.py").read_text()
        views_source = (package_root / "applications" / "views.py").read_text()
        services_tree = ast.parse(services_source)
        views_tree = ast.parse(views_source)
        resolver_tree = ast.parse(
            (
                package_root
                / "configurations"
                / "modules"
                / "configuration_resolver.py"
            ).read_text()
        )
        appraisal_path = (
            package_root / "credit" / "modules" / "appraisal_workflow.py"
        )
        calculator_source = (
            package_root / "credit" / "modules" / "loan_limit_calculator.py"
        ).read_text()
        calculator_tree = ast.parse(calculator_source)

        service_definitions = {
            node.name
            for node in services_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        self.assertTrue(
            {
                "calculate_loan_limit",
                "serialize_loan_limit_assessment",
                "_audit_loan_limit_assessment",
                "_loan_limit_assessment_audit_snapshot",
            }.isdisjoint(service_definitions)
        )
        self.assertFalse(any("appraisal" in name for name in service_definitions))
        self.assertFalse(
            self._imports_from(services_tree, "sfpcl_credit.credit")
        )
        self.assertEqual(
            self._missing_required_imports(
                views_source,
                {
                    "sfpcl_credit.credit.modules.appraisal_workflow.AppraisalWorkflow",
                    "sfpcl_credit.credit.modules.loan_limit_calculator.LoanLimitCalculator",
                },
            ),
            set(),
        )
        self.assertFalse(
            self._imports_from(resolver_tree, "sfpcl_credit.credit")
            or self._imports_from(resolver_tree, "sfpcl_credit.applications")
        )
        self.assertFalse(
            self._imports_from(
                calculator_tree,
                "sfpcl_credit.configurations.models",
            )
        )
        self.assertTrue(appraisal_path.is_file())
        appraisal_source = appraisal_path.read_text()
        appraisal_tree = ast.parse(appraisal_source)
        for source in (services_source, views_source, appraisal_source):
            self.assertFalse(self._credit_boundary_violations(source))
        self.assertFalse(
            self._credit_boundary_violations(calculator_source)
            - {"direct credit assessment model access"}
        )
        self.assertFalse(
            self._imports_from(appraisal_tree, "sfpcl_credit.applications.services")
        )
        self.assertIn("AppraisalWorkflow().review(", views_source)
        self.assertFalse(
            self._imports_from_module(
                appraisal_tree,
                "sfpcl_credit.credit.models",
            )
            & {
                ("EligibilityAssessment", None),
                ("LoanLimitAssessment", None),
            }
        )
        self.assertEqual(
            self._missing_required_imports(
                appraisal_source,
                {
                    "sfpcl_credit.credit.modules.eligibility_assessment.EligibilityAssessmentModule",
                    "sfpcl_credit.credit.modules.loan_limit_calculator.LoanLimitCalculator",
                },
            ),
            set(),
        )
        appraisal_class = next(
            node for node in appraisal_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "AppraisalWorkflow"
        )
        self.assertTrue(
            {
                "create_or_update",
                "get",
                "submit_for_review",
                "revalidate_prerequisites",
                "review",
                "prepare_sanction_handoff",
            }
            .issubset(
                {
                    node.name
                    for node in appraisal_class.body
                    if isinstance(node, ast.FunctionDef)
                }
            )
        )
        self.assertIn(
            "AppraisalWorkflow",
            {
                node.name
                for node in appraisal_tree.body
                if isinstance(node, ast.ClassDef)
            },
        )

    def test_boundary_import_inspection_resolves_package_alias_imports(self):
        tree = ast.parse(
            "import sfpcl_credit.credit.models as credit_models\n"
        )

        self.assertEqual(
            self._imports_from_module(
                tree,
                "sfpcl_credit.credit.models",
            ),
            {("sfpcl_credit.credit.models", "credit_models")},
        )

    def test_boundary_fixture_rejects_package_level_concrete_model_access(self):
        source = """
from sfpcl_credit.credit import models as credit_models

assessment = credit_models.LoanLimitAssessment
"""

        self.assertEqual(
            self._credit_boundary_violations(source),
            {"direct credit assessment model access"},
        )

    def test_boundary_fixtures_reject_direct_aliased_policy_and_private_access(self):
        fixtures = {
            "direct assessment": (
                "from sfpcl_credit.credit.models import LoanLimitAssessment\n",
                {"direct credit assessment model access"},
            ),
            "aliased assessment": (
                "from sfpcl_credit.credit.models import EligibilityAssessment as Current\n",
                {"direct credit assessment model access"},
            ),
            "package policy": (
                "from sfpcl_credit.configurations import models as configs\n"
                "policy = configs.LoanPolicyConfig\n",
                {"direct loan policy model access"},
            ),
            "aliased policy": (
                "from sfpcl_credit.configurations.models import LoanPolicyConfig as Policy\n",
                {"direct loan policy model access"},
            ),
            "private calculator helper": (
                "from sfpcl_credit.credit.modules.loan_limit_calculator import _projection as project\n",
                {"private loan-limit module access"},
            ),
        }

        for label, (source, expected) in fixtures.items():
            with self.subTest(label=label):
                self.assertEqual(self._credit_boundary_violations(source), expected)

    def test_boundary_fixture_requires_public_imports_and_allows_extra_methods(self):
        required = {
            "sfpcl_credit.credit.modules.appraisal_workflow.AppraisalWorkflow",
            "sfpcl_credit.credit.modules.eligibility_assessment.EligibilityAssessmentModule",
            "sfpcl_credit.credit.modules.loan_limit_calculator.LoanLimitCalculator",
        }
        missing_source = "from sfpcl_credit.credit.modules import appraisal_workflow\n"
        public_source = """
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow as Workflow
from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule
import sfpcl_credit.credit.modules.loan_limit_calculator as calculator

workflow = Workflow
eligibility = EligibilityAssessmentModule
loan_limit = calculator.LoanLimitCalculator

class AppraisalWorkflow:
    def create_or_update(self): pass
    def get(self): pass
    def submit_for_review(self): pass
    def review(self): pass
    def additional_public_refactor(self): pass
"""

        self.assertEqual(
            self._missing_required_imports(missing_source, required),
            required,
        )
        self.assertEqual(
            self._missing_required_imports(public_source, required),
            set(),
        )
        workflow_tree = ast.parse(public_source).body[-1]
        public_methods = {
            node.name
            for node in workflow_tree.body
            if isinstance(node, ast.FunctionDef)
        }
        self.assertTrue(
            {"create_or_update", "get", "submit_for_review", "review"}.issubset(
                public_methods
            )
        )

    def test_loan_limit_calculates_through_module_with_one_public_audit_projection(self):
        from sfpcl_credit.configurations.modules.configuration_resolver import (
            resolve_effective_loan_policy,
        )
        from sfpcl_credit.credit.modules.loan_limit_calculator import (
            LoanLimitAssessmentResult,
            LoanLimitSnapshot,
        )

        calculator, shareholding, policy = self._calculator_fixture()
        IndividualMemberProfile.objects.update_or_create(
            member=self.member,
            defaults={"first_name": "Ramesh", "last_name": "Patil", "land_area_under_cultivation_acres": "5.0", "services_availed_flag": True},
        )
        locked_models = (
            LoanApplication, EligibilityAssessment, LoanLimitAssessment, Shareholding,
            LandHolding, CropPlan, IndividualMemberProfile,
        )
        with ExitStack() as stack:
            locks = {
                model: stack.enter_context(
                    patch.object(model.objects, "select_for_update", wraps=model.objects.select_for_update)
                )
                for model in locked_models
            }
            resolver = stack.enter_context(patch(
                "sfpcl_credit.credit.modules.loan_limit_calculator.resolve_effective_loan_policy",
                wraps=resolve_effective_loan_policy,
            ))
            result = calculator.calculate_for_application(
                actor=self.actor,
                application_id=self.application.loan_application_id,
                payload=self._loan_limit_payload(shareholding),
                request_meta={"request_id": "req-credit-module-loan-limit"},
            )

        self.assertIsInstance(result, LoanLimitAssessmentResult)
        self.assertIsInstance(result.projection, LoanLimitSnapshot)
        self.assertEqual(result.snapshot["calculation_rule_version"], policy.policy_version)
        self.assertEqual(result.snapshot["shareholding_based_limit_amount"], "20000.00")
        self.assertEqual(result.snapshot["land_based_limit_amount"], "100000.00")
        self.assertEqual(result.snapshot["final_eligible_loan_amount"], "20000.00")
        self.assertTrue(result.snapshot["exception_required_flag"])
        self.assertEqual(
            result.snapshot["warnings"][0]["code"],
            "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
        )
        public_shared = dict(result.snapshot)
        public_shared.pop("warnings")
        public_shared.pop("available_actions")
        audit_snapshot = AuditLog.objects.get(action="loan_limit.calculated").new_value_json
        self.assertEqual(audit_snapshot.pop("request_id"), "req-credit-module-loan-limit")
        self.assertEqual(audit_snapshot, public_shared)
        resolver.assert_called_once_with(
            calculation_date=timezone.localdate(),
            for_update=True,
        )
        for model, lock in locks.items():
            self.assertTrue(lock.called, f"{model.__name__} must be locked")

    def test_calculator_rolls_back_snapshot_and_workflow_when_audit_fails(self):
        calculator, shareholding, _policy = self._calculator_fixture()

        with patch.object(AuditLog.objects, "create", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaisesMessage(RuntimeError, "audit unavailable"):
                calculator.calculate_for_application(
                    actor=self.actor,
                    application_id=self.application.loan_application_id,
                    payload=self._loan_limit_payload(shareholding),
                )

        self.assertFalse(
            LoanLimitAssessment.objects.filter(loan_application=self.application).exists()
        )
        self.assertFalse(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").exists()
        )

    def test_failed_module_rerun_preserves_snapshot_and_success_evidence(self):
        from sfpcl_credit.credit.modules.common import CreditModuleValidationError

        calculator, shareholding, _policy = self._calculator_fixture()
        original = calculator.calculate_for_application(
            actor=self.actor,
            application_id=self.application.loan_application_id,
            payload=self._loan_limit_payload(shareholding),
        ).snapshot
        audit_count = AuditLog.objects.filter(action="loan_limit.calculated").count()
        workflow_count = WorkflowEvent.objects.filter(
            workflow_name="loan_limit_assessment"
        ).count()
        self.crop.planned_area_acres = "4.00"
        self.crop.save(update_fields=["planned_area_acres"])

        with self.assertRaises(CreditModuleValidationError) as raised:
            calculator.calculate_for_application(
                actor=self.actor,
                application_id=self.application.loan_application_id,
                payload=self._loan_limit_payload(shareholding),
            )

        self.assertEqual(
            raised.exception.field_errors,
            {"cultivated_acreage": "CULTIVATED_ACREAGE_UNRESOLVED"},
        )
        self.assertEqual(
            calculator.get_assessment(
                actor=self.actor,
                application_id=self.application.loan_application_id,
            ).snapshot,
            original,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="loan_limit.calculated").count(),
            audit_count,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            workflow_count,
        )

    def test_land_lower_equal_and_below_boundaries_preserve_assessment_uuid(self):
        calculator, shareholding, _policy = self._calculator_fixture(
            shareholding_overrides={
                "number_of_shares": 1000,
                "available_share_count": 1000,
            },
            policy_overrides={"per_share_cap_amount": None},
        )
        self.application.required_loan_amount = "100000.00"
        self.application.save(update_fields=["required_loan_amount"])

        equal = calculator.calculate_for_application(
            actor=self.actor,
            application_id=self.application.loan_application_id,
            payload=self._loan_limit_payload(
                shareholding,
                requested_amount="100000.00",
            ),
        ).snapshot
        self.application.required_loan_amount = "90000.00"
        self.application.save(update_fields=["required_loan_amount"])
        below = calculator.calculate_for_application(
            actor=self.actor,
            application_id=self.application.loan_application_id,
            payload=self._loan_limit_payload(
                shareholding,
                requested_amount="90000.00",
            ),
        ).snapshot

        self.assertEqual(equal["shareholding_based_limit_amount"], "200000.00")
        self.assertEqual(equal["land_based_limit_amount"], "100000.00")
        self.assertEqual(equal["final_eligible_loan_amount"], "100000.00")
        self.assertTrue(equal["amount_within_limit_flag"])
        self.assertTrue(below["amount_within_limit_flag"])
        self.assertFalse(below["exception_required_flag"])
        self.assertEqual(
            below["loan_limit_assessment_id"],
            equal["loan_limit_assessment_id"],
        )

    def test_module_rejects_unverified_and_unlinked_cultivation_sources(self):
        from sfpcl_credit.credit.modules.common import CreditModuleValidationError

        calculator, shareholding, _policy = self._calculator_fixture()
        cases = (
            (self.land, "verification_status", "pending", "land_holding_ids"),
            (self.land, "verification_status", "rejected", "land_holding_ids"),
            (self.crop, "verification_status", "pending", "crop_plan_id"),
            (self.crop, "verification_status", "rejected", "crop_plan_id"),
            (self.crop, "loan_application_id", None, "crop_plan_id"),
            (self.crop, "loan_application_id", uuid4(), "crop_plan_id"),
        )
        for source, field, invalid_value, error_field in cases:
            with self.subTest(source=source.__class__.__name__, value=invalid_value):
                original = getattr(source, field)
                setattr(source, field, invalid_value)
                source.save(update_fields=[field])
                with self.assertRaises(CreditModuleValidationError) as raised:
                    calculator.calculate_for_application(
                        actor=self.actor,
                        application_id=self.application.loan_application_id,
                        payload=self._loan_limit_payload(shareholding),
                    )
                self.assertIn(error_field, raised.exception.field_errors)
                setattr(source, field, original)
                source.save(update_fields=[field])

    def test_calculator_translates_ambiguous_policy_at_credit_seam(self):
        from sfpcl_credit.credit.modules.common import CreditModuleValidationError

        calculator, shareholding, _policy = self._calculator_fixture()
        self._active_loan_policy(policy_version="loan-policy-v1.1")

        with self.assertRaises(CreditModuleValidationError) as raised:
            calculator.calculate_for_application(
                actor=self.actor,
                application_id=self.application.loan_application_id,
                payload=self._loan_limit_payload(shareholding),
            )

        self.assertIn("loan_policy_config", raised.exception.field_errors)

    @staticmethod
    def _imports_from(tree, module_prefix):
        return any(
            (
                isinstance(node, ast.ImportFrom)
                and (node.module or "").startswith(module_prefix)
            )
            or (
                isinstance(node, ast.Import)
                and any(alias.name.startswith(module_prefix) for alias in node.names)
            )
            for node in ast.walk(tree)
        )

    @staticmethod
    def _imports_from_module(tree, module_name):
        imported_members = {
            (alias.name, alias.asname)
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module == module_name
            for alias in node.names
        }
        imported_modules = {
            (alias.name, alias.asname)
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name == module_name
        }
        return imported_members | imported_modules

    @classmethod
    def _credit_boundary_violations(cls, source):
        references = cls._resolved_import_references(ast.parse(source))
        violations = set()
        concrete_assessments = {
            "sfpcl_credit.credit.models.EligibilityAssessment",
            "sfpcl_credit.credit.models.LoanLimitAssessment",
        }
        if references & concrete_assessments:
            violations.add("direct credit assessment model access")
        if "sfpcl_credit.configurations.models.LoanPolicyConfig" in references:
            violations.add("direct loan policy model access")
        if any(
            reference.startswith(
                "sfpcl_credit.credit.modules.loan_limit_calculator._"
            )
            for reference in references
        ):
            violations.add("private loan-limit module access")
        return violations

    @classmethod
    def _missing_required_imports(cls, source, required):
        references = cls._resolved_import_references(ast.parse(source))
        return set(required) - references

    @staticmethod
    def _resolved_import_references(tree):
        aliases = {}
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    local_name = alias.asname or alias.name.split(".")[0]
                    target = alias.name if alias.asname else local_name
                    aliases[local_name] = target
                    imported.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    target = f"{module}.{alias.name}" if module else alias.name
                    aliases[alias.asname or alias.name] = target
                    imported.add(target)

        references = set(imported)
        for node in ast.walk(tree):
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name) and current.id in aliases:
                references.add(
                    ".".join([aliases[current.id], *reversed(parts)])
                )
        return references

    def _verified_required_documents(self):
        document_types = """
            loan_application_form borrower_pan borrower_aadhaar_ovd nominee_pan
            nominee_aadhaar_ovd share_certificate_copy land_document_7_12 crop_plan
            six_month_bank_statement
        """.split()
        for document_type in document_types:
            document_file = DocumentFile.objects.create(
                file_name=f"{document_type}.pdf",
                file_extension=".pdf",
                mime_type="application/pdf",
                file_size_bytes=256,
                storage_provider="local",
                storage_key=f"document-files/private/{document_type}.pdf",
                checksum_sha256=f"{document_type}-hash",
                uploaded_by_user=self.actor,
                sensitivity_level="restricted",
            )
            ApplicationDocument.objects.create(
                loan_application=self.application,
                document_type=document_type,
                party_type="borrower",
                party_id=self.member.member_id,
                document_file=document_file,
                required_flag=True,
                submission_status=ApplicationDocument.SUBMISSION_SUBMITTED,
                verification_status=ApplicationDocument.VERIFICATION_VERIFIED,
                verified_by_user=self.actor,
                verified_at=timezone.now(),
                created_by_user=self.actor,
            )

    def _shareholding(self, **overrides):
        values = {
            "member": self.member,
            "folio_number": self.member.folio_number,
            "number_of_shares": 100,
            "holding_mode": "physical",
            "valuation_per_share": "2000.00",
            "valuation_effective_date": timezone.localdate(),
            "pledged_share_count": 0,
            "available_share_count": 100,
            "status": "active",
        }
        values.update(overrides)
        return Shareholding.objects.create(**values)

    def _calculator_fixture(
        self,
        *,
        shareholding_overrides=None,
        policy_overrides=None,
    ):
        from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule
        from sfpcl_credit.credit.modules.loan_limit_calculator import LoanLimitCalculator

        EligibilityAssessmentModule().run(
            actor=self.actor,
            application_id=self.application.loan_application_id,
        )
        shareholding = self._shareholding(**(shareholding_overrides or {}))
        policy = self._active_loan_policy(**(policy_overrides or {}))
        return LoanLimitCalculator(), shareholding, policy

    def _loan_limit_payload(self, shareholding, **overrides):
        values = {
            "shareholding_id": str(shareholding.shareholding_id),
            "land_holding_ids": [str(self.land.land_holding_id)],
            "crop_plan_id": str(self.crop.crop_plan_id),
            "requested_amount": "400000.00",
            "calculation_date": timezone.localdate().isoformat(),
        }
        values.update(overrides)
        return values

    @staticmethod
    def _permission(code, name):
        return Permission.objects.create(
            permission_code=code,
            permission_name=name,
            module_name=code.split(".")[0],
            risk_level="high",
        )

    @staticmethod
    def _active_loan_policy(**overrides):
        values = {
            "policy_name": "Board-approved member loan policy",
            "policy_version": "loan-policy-v1.0",
            "effective_from": timezone.localdate(),
            "short_term_duration_months": 12,
            "approval_threshold_amount": "500000.00",
            "share_limit_percentage": "10.0000",
            "per_share_cap_amount": "200.00",
            "default_scale_of_finance_per_acre_amount": "20000.00",
            "interest_rate_type": "floating",
            "rekyc_frequency_months": 24,
            "record_retention_years": 8,
            "grace_period_months": 3,
            "non_intentional_extension_months": 3,
            "board_approval_reference": "BOARD/2026/006D2A",
            "status": LoanPolicyConfig.STATUS_ACTIVE,
        }
        values.update(overrides)
        return LoanPolicyConfig.objects.create(**values)

    @staticmethod
    def _user(email, *permissions):
        role = Role.objects.create(
            role_code=email.split("@")[0].replace(".", "_"),
            role_name=email,
            is_system_role=True,
            status="active",
        )
        for permission in permissions:
            RolePermission.objects.create(role=role, permission=permission)
        return User.objects.create(
            full_name=email,
            email=email,
            status="active",
            primary_role=role,
        )


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative loan-limit concurrency proof requires the PostgreSQL integration settings.",
)
class LoanLimitConcurrencyTests(TransactionTestCase):
    setUp = CreditEligibilityModuleTests.setUp
    _verified_required_documents = CreditEligibilityModuleTests._verified_required_documents
    _shareholding = CreditEligibilityModuleTests._shareholding
    _calculator_fixture = CreditEligibilityModuleTests._calculator_fixture
    _loan_limit_payload = CreditEligibilityModuleTests._loan_limit_payload
    _permission = staticmethod(CreditEligibilityModuleTests._permission)
    _active_loan_policy = staticmethod(CreditEligibilityModuleTests._active_loan_policy)
    _user = staticmethod(CreditEligibilityModuleTests._user)

    def test_competing_valid_reruns_serialize_complete_snapshots_and_evidence(self):
        from sfpcl_credit.credit.modules.loan_limit_calculator import LoanLimitCalculator

        calculator, first_shareholding, _policy = self._calculator_fixture()
        initial = calculator.calculate_for_application(
            actor=self.actor,
            application_id=self.application.loan_application_id,
            payload=self._loan_limit_payload(first_shareholding),
            request_meta={"request_id": "concurrency-initial"},
        ).snapshot
        second_shareholding = self._shareholding(
            folio_number="FOL-CREDIT-MODULE-SECOND",
            number_of_shares=250,
            available_share_count=250,
        )
        initial_audit_count = AuditLog.objects.filter(
            action="loan_limit.calculated"
        ).count()
        initial_workflow_count = WorkflowEvent.objects.filter(
            workflow_name="loan_limit_assessment"
        ).count()
        first_locked = Barrier(2)
        second_attempting = Barrier(2)
        release_first = Event()
        second_payload_entered = Event()
        ordering = []
        ordering_lock = Lock()

        def record(step):
            with ordering_lock:
                ordering.append(step)

        def first_payload():
            record("first_locked_application")
            first_locked.wait(timeout=10)
            if not release_first.wait(timeout=10):
                raise AssertionError("Timed out waiting to release the first calculation.")
            record("first_released")
            return self._loan_limit_payload(first_shareholding)

        def second_payload():
            record("second_locked_application")
            second_payload_entered.set()
            return self._loan_limit_payload(second_shareholding)

        def calculate(payload, request_id, attempted_barrier=None):
            close_old_connections()
            try:
                actor = User.objects.get(user_id=self.actor.user_id)
                if attempted_barrier is not None:
                    record("second_attempting_application_lock")
                    attempted_barrier.wait(timeout=10)
                return LoanLimitCalculator().calculate_for_application(
                    actor=actor,
                    application_id=self.application.loan_application_id,
                    payload=payload,
                    request_meta={"request_id": request_id},
                ).snapshot
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            first_future = executor.submit(
                calculate,
                first_payload,
                "concurrency-first",
            )
            first_locked.wait(timeout=10)
            second_future = executor.submit(
                calculate,
                second_payload,
                "concurrency-second",
                second_attempting,
            )
            second_attempting.wait(timeout=10)
            try:
                self.assertFalse(
                    second_payload_entered.wait(timeout=0.5),
                    "The second calculation reached its payload before the first committed.",
                )
            finally:
                release_first.set()
            first = first_future.result(timeout=10)
            second = second_future.result(timeout=10)

        assessment = LoanLimitAssessment.objects.get(
            loan_application=self.application
        )
        final = calculator.get_assessment(
            actor=self.actor,
            application_id=self.application.loan_application_id,
        ).snapshot
        self.assertEqual(LoanLimitAssessment.objects.count(), 1)
        self.assertEqual(
            str(assessment.loan_limit_assessment_id),
            initial["loan_limit_assessment_id"],
        )
        self.assertEqual(first["shareholding_id"], str(first_shareholding.shareholding_id))
        self.assertEqual(first["number_of_shares"], 100)
        self.assertEqual(first["shareholding_based_limit_amount"], "20000.00")
        self.assertEqual(second["shareholding_id"], str(second_shareholding.shareholding_id))
        self.assertEqual(second["number_of_shares"], 250)
        self.assertEqual(second["shareholding_based_limit_amount"], "50000.00")
        self.assertEqual(final, second)
        self.assertEqual(
            AuditLog.objects.filter(action="loan_limit.calculated").count(),
            initial_audit_count + 2,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            initial_workflow_count + 2,
        )
        final_audit = AuditLog.objects.filter(
            action="loan_limit.calculated",
            entity_id=assessment.loan_limit_assessment_id,
        ).latest("created_at")
        audit_projection = dict(final_audit.new_value_json)
        self.assertEqual(audit_projection.pop("request_id"), "concurrency-second")
        final_projection = dict(final)
        final_projection.pop("warnings")
        final_projection.pop("available_actions")
        self.assertEqual(audit_projection, final_projection)
        self.assertEqual(
            ordering,
            [
                "first_locked_application",
                "second_attempting_application_lock",
                "first_released",
                "second_locked_application",
            ],
        )
        print(f"database_backend={connection.vendor} ordering={' -> '.join(ordering)}")

    def test_competing_valid_and_invalid_calculations_preserve_valid_snapshot(self):
        from sfpcl_credit.credit.modules.common import CreditModuleValidationError
        from sfpcl_credit.credit.modules.loan_limit_calculator import LoanLimitCalculator

        calculator, shareholding, _policy = self._calculator_fixture()
        valid_locked = Barrier(2)
        invalid_attempting = Barrier(2)
        release_valid = Event()
        invalid_payload_entered = Event()
        ordering = []
        ordering_lock = Lock()

        def record(step):
            with ordering_lock:
                ordering.append(step)

        def valid_payload():
            record("valid_locked_application")
            valid_locked.wait(timeout=10)
            if not release_valid.wait(timeout=10):
                raise AssertionError("Timed out waiting to release the valid calculation.")
            record("valid_released")
            return self._loan_limit_payload(shareholding)

        def invalid_payload():
            record("invalid_locked_application")
            invalid_payload_entered.set()
            return self._loan_limit_payload(
                shareholding,
                requested_amount="1.00",
            )

        def calculate(payload, request_id, attempted_barrier=None):
            close_old_connections()
            try:
                actor = User.objects.get(user_id=self.actor.user_id)
                if attempted_barrier is not None:
                    record("invalid_attempting_application_lock")
                    attempted_barrier.wait(timeout=10)
                return LoanLimitCalculator().calculate_for_application(
                    actor=actor,
                    application_id=self.application.loan_application_id,
                    payload=payload,
                    request_meta={"request_id": request_id},
                ).snapshot
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            valid_future = executor.submit(
                calculate,
                valid_payload,
                "concurrency-valid",
            )
            valid_locked.wait(timeout=10)
            invalid_future = executor.submit(
                calculate,
                invalid_payload,
                "concurrency-invalid",
                invalid_attempting,
            )
            invalid_attempting.wait(timeout=10)
            try:
                self.assertFalse(
                    invalid_payload_entered.wait(timeout=0.5),
                    "The invalid calculation reached its payload before the valid commit.",
                )
            finally:
                release_valid.set()
            valid = valid_future.result(timeout=10)
            with self.assertRaises(CreditModuleValidationError) as raised:
                invalid_future.result(timeout=10)

        self.assertEqual(
            raised.exception.field_errors,
            {
                "requested_amount": (
                    "Requested amount must match the loan application requested amount."
                )
            },
        )
        final = calculator.get_assessment(
            actor=self.actor,
            application_id=self.application.loan_application_id,
        ).snapshot
        self.assertEqual(final, valid)
        self.assertEqual(LoanLimitAssessment.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="loan_limit.calculated").count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            1,
        )
        only_audit = AuditLog.objects.get(action="loan_limit.calculated")
        self.assertEqual(only_audit.entity_id, LoanLimitAssessment.objects.get().pk)
        self.assertEqual(only_audit.new_value_json["request_id"], "concurrency-valid")
        self.assertEqual(
            ordering,
            [
                "valid_locked_application",
                "invalid_attempting_application_lock",
                "valid_released",
                "invalid_locked_application",
            ],
        )
        print(f"database_backend={connection.vendor} ordering={' -> '.join(ordering)}")
