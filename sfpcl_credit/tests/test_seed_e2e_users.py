from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase

from sfpcl_credit.applications.models import ApplicationDocument, LoanApplication
from sfpcl_credit.configurations.models import LoanPolicyConfig
from sfpcl_credit.credit.models import EligibilityAssessment
from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission, User
from sfpcl_credit.members.models import CropPlan, LandHolding, Member, Shareholding
from sfpcl_credit.workflows.models import WorkflowEvent


TRACER_PERMISSION = "tracer.lifecycle.run"
TRACER_EMAIL = "e2e.tracer@sfpcl.example"
ZERO_EMAIL = "e2e.zero@sfpcl.example"
E2E_PASSWORD = "E2eTracer123!"
EPIC_006_FINANCE_EMAIL = "e2e.credit.finance@sfpcl.example"
EPIC_006_MANAGER_EMAIL = "e2e.credit.manager@sfpcl.example"
EPIC_006_REFERENCE = "LOE2E00601"


class SeedE2eUsersTests(TestCase):
    """The Playwright suite needs deterministic staff users created by backend
    dev/test setup (slice 002EY req 8, 9, 14), not by frontend fixtures."""

    def test_seed_refuses_without_explicit_e2e_guard(self):
        with self.assertRaisesMessage(CommandError, "SFPCL_ALLOW_E2E_SEED=true"):
            call_command("seed_e2e_users")

        self.assertFalse(User.objects.filter(email=TRACER_EMAIL).exists())
        self.assertFalse(User.objects.filter(email=ZERO_EMAIL).exists())

    def _login_access_token(self, email):
        client = Client()
        response = client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": E2E_PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return client, response.json()["data"]["access_token"]

    def _seed_e2e_users(self):
        with patch.dict(
            "os.environ",
            {"SFPCL_DEBUG": "true", "SFPCL_ALLOW_E2E_SEED": "true"},
        ):
            call_command("seed_e2e_users")

    def test_seed_creates_active_tracer_staff_with_single_tracer_permission(self):
        self._seed_e2e_users()

        tracer_user = User.objects.get(email=TRACER_EMAIL)
        self.assertEqual(tracer_user.status, "active")
        self.assertTrue(tracer_user.check_password(E2E_PASSWORD))
        self.assertEqual(tracer_user.primary_role.status, "active")

        permission_codes = list(
            Permission.objects.filter(
                role_permissions__role=tracer_user.primary_role
            ).values_list("permission_code", flat=True)
        )
        self.assertEqual(permission_codes, [TRACER_PERMISSION])

    def test_seed_creates_zero_permission_staff(self):
        self._seed_e2e_users()

        zero_user = User.objects.get(email=ZERO_EMAIL)
        self.assertEqual(zero_user.status, "active")
        self.assertEqual(zero_user.primary_role.role_code, "it_head")
        self.assertFalse(
            RolePermission.objects.filter(role=zero_user.primary_role).exists()
        )

    def test_seed_is_idempotent(self):
        self._seed_e2e_users()
        self._seed_e2e_users()

        self.assertEqual(User.objects.filter(email=TRACER_EMAIL).count(), 1)
        self.assertEqual(User.objects.filter(email=ZERO_EMAIL).count(), 1)
        self.assertEqual(
            RolePermission.objects.filter(
                role__role_code="e2e_tracer",
                permission__permission_code=TRACER_PERMISSION,
            ).count(),
            1,
        )

    def test_me_exposes_exactly_the_tracer_permission_for_the_tracer_user(self):
        self._seed_e2e_users()
        client, access_token = self._login_access_token(TRACER_EMAIL)

        response = client.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["permissions"], [TRACER_PERMISSION])
        self.assertEqual(data["available_actions"], [TRACER_PERMISSION])

    def test_me_exposes_no_permissions_for_the_zero_permission_user(self):
        self._seed_e2e_users()
        client, access_token = self._login_access_token(ZERO_EMAIL)

        response = client.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["permissions"], [])
        self.assertEqual(data["available_actions"], [])

    def test_seed_creates_idempotent_epic_006_browser_fixture(self):
        call_command("seed_role_catalogue")
        self._seed_e2e_users()
        self._seed_e2e_users()

        finance = User.objects.get(email=EPIC_006_FINANCE_EMAIL)
        manager = User.objects.get(email=EPIC_006_MANAGER_EMAIL)
        self.assertEqual(finance.primary_role.role_code, "deputy_manager_finance")
        self.assertEqual(manager.primary_role.role_code, "credit_manager")
        self.assertTrue(finance.check_password(E2E_PASSWORD))
        self.assertTrue(manager.check_password(E2E_PASSWORD))
        finance_permissions = set(
            Permission.objects.filter(role_permissions__role=finance.primary_role)
            .values_list("permission_code", flat=True)
        )
        manager_permissions = set(
            Permission.objects.filter(role_permissions__role=manager.primary_role)
            .values_list("permission_code", flat=True)
        )
        self.assertIn("credit.appraisal.submit_sanction", finance_permissions)
        self.assertTrue(
            {
                "members.member.read",
                "members.member.create",
                "members.member.update",
                "members.witness.read",
                "members.witness.create",
            }.issubset(finance_permissions)
        )
        self.assertTrue(
            {
                "members.member.read",
                "members.member.identity_change.approve",
            }.issubset(manager_permissions)
        )

        application = LoanApplication.objects.select_related("member", "nominee").get(
            application_reference_number=EPIC_006_REFERENCE
        )
        self.assertEqual(application.application_status, "reference_generated")
        self.assertEqual(application.current_stage, "credit_assessment")
        self.assertEqual(application.completeness_status, "complete")
        self.assertEqual(application.created_by_user, finance)
        self.assertEqual(application.member.active_member_status, "active")
        self.assertFalse(application.nominee.minor_flag)
        self.assertEqual(
            ApplicationDocument.objects.filter(
                loan_application=application, verification_status="verified"
            ).count(),
            9,
        )
        self.assertEqual(
            EligibilityAssessment.objects.get(
                loan_application=application
            ).overall_result,
            "pending",
        )
        self.assertEqual(Member.objects.filter(member_number="MEM-E2E-006").count(), 1)
        witness_member = Member.objects.get(member_number="MEM-E2E-006-W")
        self.assertNotEqual(witness_member, application.member)
        self.assertEqual(witness_member.kyc_status, "verified")
        self.assertEqual(witness_member.legal_name, "Epic 006 Browser Witness")
        self.assertEqual(
            Shareholding.objects.filter(
                member=witness_member,
                status="active",
                number_of_shares__gt=0,
            ).count(),
            1,
        )
        self.assertEqual(Shareholding.objects.filter(member=application.member).count(), 1)
        self.assertEqual(LandHolding.objects.filter(member=application.member).count(), 1)
        self.assertEqual(CropPlan.objects.filter(member=application.member).count(), 1)
        self.assertEqual(LoanPolicyConfig.objects.filter(status="active").count(), 1)

    def test_seeded_witness_capture_is_independent_of_borrower_reverification(self):
        call_command("seed_role_catalogue")
        self._seed_e2e_users()
        application = LoanApplication.objects.get(
            application_reference_number=EPIC_006_REFERENCE
        )
        application.member.kyc_status = "pending"
        application.member.save(update_fields=["kyc_status"])
        witness_member = Member.objects.get(member_number="MEM-E2E-006-W")

        response = self.client.post(
            f"/api/v1/loan-applications/{application.pk}/witnesses/",
            data={
                "member_id": str(witness_member.pk),
                "witness_name": witness_member.legal_name,
                "pan": "ABCDE1234F",
                "aadhaar": "123412341234",
            },
            content_type="application/json",
            headers=self._auth_headers(EPIC_006_FINANCE_EMAIL),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"]["member_id"], str(witness_member.pk)
        )

    def test_seeded_fixture_completes_real_two_role_http_path(self):
        call_command("seed_role_catalogue")
        self._seed_e2e_users()
        application = LoanApplication.objects.get(application_reference_number=EPIC_006_REFERENCE)
        finance = self._auth_headers(EPIC_006_FINANCE_EMAIL)

        eligibility = self.client.post(
            f"/api/v1/loan-applications/{application.pk}/eligibility-assessment/run/",
            data={}, content_type="application/json", headers=finance,
        ).json()["data"]
        self.assertEqual(eligibility["overall_result"], "eligible")
        limit_response = self.client.post(
            f"/api/v1/loan-applications/{application.pk}/loan-limit-assessment/calculate/",
            data={
                "shareholding_id": str(Shareholding.objects.get(member=application.member).pk),
                "land_holding_ids": [str(LandHolding.objects.get(member=application.member).pk)],
                "crop_plan_id": str(CropPlan.objects.get(member=application.member).pk),
                "requested_amount": "15000.00", "calculation_date": "2026-07-11",
            }, content_type="application/json", headers=finance,
        )
        self.assertEqual(limit_response.status_code, 200, limit_response.content)
        limit = limit_response.json()["data"]
        writable = {
            "borrower_summary": "Verified synthetic member and complete application.",
            "eligibility_summary": "All stored eligibility checks passed.",
            "loan_limit_summary": "Requested amount is within the frozen limit.",
            "recommended_amount": "15000.00", "recommended_tenure_months": 12,
            "recommended_interest_type": "floating",
            "recommended_security_summary": "Existing verified synthetic security facts.",
            "repayment_capacity_notes": "Synthetic crop proceeds cover repayment.",
            "risk_assessment": {
                "market_risk_rating": "low", "operational_risk_rating": "low",
                "borrower_risk_rating": "low", "overall_risk_rating": "low",
                "risk_mitigation_notes": "Monitor the stored synthetic crop cycle.",
            },
            "recommendation": "approve",
        }
        create = self.client.post(
            f"/api/v1/loan-applications/{application.pk}/appraisal-note/",
            data=writable, content_type="application/json", headers=finance,
        )
        self.assertEqual(create.status_code, 200, create.content)
        appraisal = create.json()["data"]
        self.assertEqual(appraisal["eligibility_assessment_id"], eligibility["eligibility_assessment_id"])
        self.assertEqual(appraisal["loan_limit_assessment_id"], limit["loan_limit_assessment_id"])
        appraisal_id = appraisal["loan_appraisal_note_id"]
        patch_response = self.client.patch(
            f"/api/v1/loan-applications/{application.pk}/appraisal-note/",
            data=writable, content_type="application/json", headers=finance,
        )
        self.assertEqual(patch_response.status_code, 200, patch_response.content)
        submit = self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/submit-for-review/",
            data={"remarks": "Ready for independent review."},
            content_type="application/json", headers=finance,
        )
        self.assertEqual(submit.status_code, 200, submit.content)

        manager = self._auth_headers(EPIC_006_MANAGER_EMAIL)
        review = self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/review/",
            data={"decision": "reviewed", "review_comments": "Independent review complete."},
            content_type="application/json", headers=manager,
        )
        self.assertEqual(review.status_code, 200, review.content)
        decision_id = review.json()["data"]["review_history"][-1]["appraisal_review_decision_id"]
        sanction_url = f"/api/v1/loan-applications/{application.pk}/submit-to-sanction-committee/"
        sanction_response = self.client.post(
            sanction_url, data={"remarks": "Reviewed package ready for committee."},
            content_type="application/json", headers=manager,
        )
        self.assertEqual(sanction_response.status_code, 200, sanction_response.content)
        sanction = sanction_response.json()["data"]
        self.assertEqual(sanction["loan_appraisal_note_id"], appraisal_id)
        self.assertEqual(sanction["appraisal_review_decision_id"], decision_id)
        self.assertEqual(sanction["submission_status"], "pending")
        counts = (
            AuditLog.objects.filter(action="appraisal.submitted_to_sanction").count(),
            WorkflowEvent.objects.filter(workflow_name="sanction_submission").count(),
        )
        repeated = self.client.post(
            sanction_url, data={"remarks": "Must remain one pending case."},
            content_type="application/json", headers=manager,
        )
        self.assertEqual(repeated.status_code, 409, repeated.content)
        self.assertEqual(counts, (
            AuditLog.objects.filter(action="appraisal.submitted_to_sanction").count(),
            WorkflowEvent.objects.filter(workflow_name="sanction_submission").count(),
        ))
        evidence = " ".join(
            str(value)
            for audit in AuditLog.objects.filter(action__in=(
                "eligibility.assessed", "loan_limit.calculated",
                "appraisal.submitted_for_review", "appraisal.reviewed",
                "appraisal.submitted_to_sanction",
            ))
            for value in (audit.old_value_json, audit.new_value_json)
        )
        for private_text in (
            writable["borrower_summary"], writable["risk_assessment"]["risk_mitigation_notes"],
            "Independent review complete.", "Reviewed package ready for committee.",
        ):
            self.assertNotIn(private_text, evidence)

    def _auth_headers(self, email):
        _client, token = self._login_access_token(email)
        return {"Authorization": f"Bearer {token}"}
