from uuid import uuid4
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from sfpcl_credit.applications.models import ApplicationDocument, EligibilityAssessment, LoanApplication
from sfpcl_credit.configurations.models import LoanPolicyConfig
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import CancelledCheque, CropPlan, LandHolding, Member, Nominee
from sfpcl_credit.workflows.models import WorkflowEvent


APPLICATION_READ_PERMISSION = "applications.loan_application.read"
ELIGIBILITY_RUN_PERMISSION = "credit.eligibility.run"


class CreditEligibilityModuleTests(TestCase):
    def setUp(self):
        self.actor = self._user(
            "credit.module.actor@sfpcl.example",
            self._permission(APPLICATION_READ_PERMISSION, "View applications"),
            self._permission(ELIGIBILITY_RUN_PERMISSION, "Run eligibility assessment"),
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
            resolve_effective_loan_policy,
        )
        from sfpcl_credit.credit.modules.common import CreditModuleValidationError

        self._active_loan_policy(policy_version="loan-policy-v1.0")
        self._active_loan_policy(policy_version="loan-policy-v1.1")

        with self.assertRaises(CreditModuleValidationError) as raised:
            resolve_effective_loan_policy(calculation_date=timezone.localdate())

        self.assertEqual(
            raised.exception.field_errors,
            {
                "loan_policy_config": (
                    "Exactly one active loan policy must apply on calculation_date."
                )
            },
        )

    def test_application_layer_uses_only_public_credit_and_configuration_seams(self):
        import sfpcl_credit.applications.services as application_services
        import sfpcl_credit.applications.views as application_views
        from sfpcl_credit.configurations.modules.configuration_resolver import (
            resolve_effective_loan_policy,
        )
        from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule

        self.assertIs(application_views.EligibilityAssessmentModule, EligibilityAssessmentModule)
        self.assertIs(
            application_services.resolve_effective_loan_policy,
            resolve_effective_loan_policy,
        )
        forbidden_names = """
            get_eligibility_assessment eligibility_run_invalid_state_message
            run_eligibility_assessment serialize_eligibility_assessment _active_member_check
            _source_backed_eligibility_checks _eligibility_assessment_notes
            _audit_eligibility_assessment _eligibility_assessment_audit_snapshot
            _effective_loan_policy
        """.split()
        for forbidden_name in forbidden_names:
            self.assertFalse(
                hasattr(application_services, forbidden_name),
                f"applications.services must not expose credit helper {forbidden_name}",
            )

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
