from datetime import timedelta
from unittest.mock import patch

from django.apps import apps
from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.credit.models import EligibilityAssessment, LoanLimitAssessment
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class AppraisalApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        permissions = [
            self._permission("applications.loan_application.read", "Read applications"),
            self._permission("credit.appraisal.create", "Create appraisal"),
            self._permission("credit.appraisal.update", "Update appraisal"),
            self._permission("credit.appraisal.submit_review", "Submit appraisal"),
            self._permission("credit.risk_assessment.manage", "Manage risk assessment"),
        ]
        self.actor = self._user("appraisal.owner@sfpcl.example", *permissions)
        self.member = Member.objects.create(
            member_number="MEM-APPRAISAL-001",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            membership_status="active",
            folio_number="FOL-APPRAISAL-001",
            kyc_status="verified",
            default_status="no_default",
        )
        self.received_at = timezone.now() - timedelta(hours=12)
        self.application = LoanApplication.objects.create(
            application_reference_number="LO00000601",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.actor,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Grape crop production",
            purpose_category="crop_production",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_REFERENCE_GENERATED,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
            created_at=self.received_at,
            created_by_user=self.actor,
        )
        self.eligibility = EligibilityAssessment.objects.create(
            loan_application=self.application,
            member_active_check=EligibilityAssessment.MEMBER_ACTIVE_PASS,
            default_check="no_default",
            document_check="complete",
            terms_acceptance_check="accepted",
            purpose_check="agriculture_aligned",
            nominee_check="valid",
            overall_result=EligibilityAssessment.OVERALL_ELIGIBLE,
            assessment_notes="All mandatory eligibility criteria passed.",
            assessed_by_user=self.actor,
        )
        self.loan_limit = LoanLimitAssessment.objects.create(
            loan_application=self.application,
            member=self.member,
            number_of_shares=1000,
            valuation_per_share="2000.00",
            share_limit_percentage="10.0000",
            per_share_cap_amount="500.00",
            shareholding_based_limit_amount="500000.00",
            land_area_acres="20.00",
            scale_of_finance_per_acre_amount="25000.00",
            land_based_limit_amount="500000.00",
            final_eligible_loan_amount="500000.00",
            requested_amount="400000.00",
            amount_within_limit_flag=True,
            exception_required_flag=False,
            calculation_rule_version="loan-policy-v1.0",
            calculated_by_user=self.actor,
        )

    def test_owner_creates_and_reads_appraisal_with_linked_risk_and_tat(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        appraisal = body["data"]
        self.assertEqual(appraisal["loan_application_id"], str(self.application.pk))
        self.assertEqual(
            appraisal["eligibility_assessment_id"],
            str(self.eligibility.pk),
        )
        self.assertEqual(
            appraisal["loan_limit_assessment_id"],
            str(self.loan_limit.pk),
        )
        self.assertEqual(appraisal["appraisal_status"], "draft")
        self.assertEqual(appraisal["tat_status"], "within_tat")
        self.assertEqual(appraisal["recommended_amount"], "400000.00")
        self.assertEqual(appraisal["risk_assessment"]["overall_risk_rating"], "low")
        self.assertEqual(
            appraisal["prepared_by"],
            {"user_id": str(self.actor.pk), "full_name": self.actor.full_name},
        )
        self.assertEqual(
            timezone.datetime.fromisoformat(appraisal["tat_due_at"]),
            self.received_at + timedelta(days=2),
        )

        read_response = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            headers=self._headers(),
        )
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.json()["data"], appraisal)

        appraisal_model = apps.get_model("credit", "LoanAppraisalNote")
        risk_model = apps.get_model("credit", "RiskAssessment")
        self.assertEqual(appraisal_model.objects.count(), 1)
        self.assertEqual(risk_model.objects.count(), 1)
        self.assertEqual(
            appraisal_model.objects.get().risk_assessment_id,
            risk_model.objects.get().pk,
        )
        audit = AuditLog.objects.get(action="appraisal.created")
        self.assertNotIn("borrower_summary", audit.new_value_json)
        self.assertNotIn("risk_mitigation_notes", audit.new_value_json)
        workflow = WorkflowEvent.objects.get(workflow_name="appraisal_note")
        self.assertNotIn("Active individual", workflow.trigger_reason)
        self.assertEqual(AuditLog.objects.filter(action__startswith="appraisal.").count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="appraisal_note").count(), 1)

    def test_patch_updates_only_supplied_draft_fields_and_preserves_due_time(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]

        response = self.client.patch(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={
                "recommendation": "conditions",
                "risk_assessment": {"overall_risk_rating": "medium"},
            },
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        updated = response.json()["data"]
        self.assertEqual(updated["recommendation"], "conditions")
        self.assertEqual(updated["risk_assessment"]["overall_risk_rating"], "medium")
        self.assertEqual(
            updated["risk_assessment"]["market_risk_rating"],
            created["risk_assessment"]["market_risk_rating"],
        )
        self.assertEqual(updated["borrower_summary"], created["borrower_summary"])
        self.assertEqual(updated["tat_due_at"], created["tat_due_at"])
        self.assertEqual(updated["prepared_at"], created["prepared_at"])
        self.assertEqual(AuditLog.objects.filter(action="appraisal.updated").count(), 1)

    def test_create_rejects_unknown_fields_without_success_evidence(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={**self._payload(), "commercial_score": 99},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("commercial_score", response.json()["error"]["field_errors"])
        self.assertEqual(apps.get_model("credit", "LoanAppraisalNote").objects.count(), 0)
        self.assertEqual(apps.get_model("credit", "RiskAssessment").objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="appraisal.").count(), 0)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="appraisal_note").count(), 0)

    def test_create_rejects_blank_required_summary(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={**self._payload(), "borrower_summary": "   "},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("borrower_summary", response.json()["error"]["field_errors"])

    def test_create_rejects_unknown_recommendation(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={**self._payload(), "recommendation": "refer"},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("recommendation", response.json()["error"]["field_errors"])

    def test_create_rejects_non_positive_amount_and_tenure(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={
                **self._payload(),
                "recommended_amount": "0.00",
                "recommended_tenure_months": 0,
            },
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        errors = response.json()["error"]["field_errors"]
        self.assertIn("recommended_amount", errors)
        self.assertIn("recommended_tenure_months", errors)

    def test_create_rejects_recommendation_above_non_exception_loan_limit(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={**self._payload(), "recommended_amount": "500000.01"},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("recommended_amount", response.json()["error"]["field_errors"])
        self.assertEqual(apps.get_model("credit", "LoanAppraisalNote").objects.count(), 0)

    def test_create_requires_eligible_and_loan_limit_snapshots(self):
        endpoint = f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/"
        self.eligibility.delete()
        missing_eligibility = self.client.post(
            endpoint,
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(missing_eligibility.status_code, 409)
        self.assertEqual(
            missing_eligibility.json()["error"]["code"],
            "INVALID_STATE_TRANSITION",
        )

        self.eligibility = EligibilityAssessment.objects.create(
            loan_application=self.application,
            member_active_check=EligibilityAssessment.MEMBER_ACTIVE_FAIL,
            default_check="no_default",
            document_check="complete",
            terms_acceptance_check="accepted",
            purpose_check="agriculture_aligned",
            nominee_check="valid",
            overall_result=EligibilityAssessment.OVERALL_INELIGIBLE,
            assessment_notes="Active membership evidence failed.",
            assessed_by_user=self.actor,
        )
        ineligible = self.client.post(
            endpoint,
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(ineligible.status_code, 409)

        self.eligibility.overall_result = EligibilityAssessment.OVERALL_ELIGIBLE
        self.eligibility.save(update_fields=["overall_result"])
        self.loan_limit.delete()
        missing_limit = self.client.post(
            endpoint,
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(missing_limit.status_code, 409)
        self.assertEqual(apps.get_model("credit", "LoanAppraisalNote").objects.count(), 0)
        self.assertEqual(apps.get_model("credit", "RiskAssessment").objects.count(), 0)

    def test_create_rejects_unknown_nested_risk_rating(self):
        payload = self._payload()
        payload["risk_assessment"] = {
            **payload["risk_assessment"],
            "market_risk_rating": "severe",
        }
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=payload,
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "risk_assessment.market_risk_rating",
            response.json()["error"]["field_errors"],
        )

    def test_create_rejects_non_text_risk_mitigation_notes(self):
        payload = self._payload()
        payload["risk_assessment"] = {
            **payload["risk_assessment"],
            "risk_mitigation_notes": ["not", "free text"],
        }
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=payload,
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "risk_assessment.risk_mitigation_notes",
            response.json()["error"]["field_errors"],
        )

    def test_submit_transitions_draft_once_and_locks_later_edits(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        endpoint = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/"
            "submit-for-review/"
        )

        response = self.client.post(
            endpoint,
            data={"remarks": "Appraisal completed for Credit Manager review."},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        submitted = response.json()["data"]
        self.assertEqual(submitted["appraisal_status"], "review_pending")
        self.assertEqual(submitted["tat_due_at"], created["tat_due_at"])
        self.assertEqual(submitted["prepared_at"], created["prepared_at"])
        self.assertEqual(AuditLog.objects.filter(action="appraisal.submitted_for_review").count(), 1)

        repeated = self.client.post(
            endpoint,
            data={"remarks": "Submit again."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(repeated.status_code, 409)
        patch = self.client.patch(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={"recommendation": "reject"},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(patch.status_code, 409)
        self.assertEqual(AuditLog.objects.filter(action="appraisal.submitted_for_review").count(), 1)

    def test_create_requires_only_appraisal_create_and_risk_manage_permissions(self):
        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission__permission_code="applications.loan_application.read",
        ).delete()

        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["appraisal_status"], "draft")

    def test_patch_requires_risk_manage_only_when_nested_risk_changes(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission__permission_code="credit.risk_assessment.manage",
        ).delete()
        endpoint = f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/"

        appraisal_only = self.client.patch(
            endpoint,
            data={"recommendation": "conditions"},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(appraisal_only.status_code, 200)
        self.assertEqual(
            appraisal_only.json()["data"]["risk_assessment"]["assessed_at"],
            created["risk_assessment"]["assessed_at"],
        )

        nested_risk = self.client.patch(
            endpoint,
            data={"risk_assessment": {"overall_risk_rating": "medium"}},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(nested_risk.status_code, 403)

    def test_permission_and_object_scope_denials_create_no_success_evidence(self):
        risk_permission = Permission.objects.get(
            permission_code="credit.risk_assessment.manage"
        )
        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission=risk_permission,
        ).delete()
        endpoint = f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/"
        no_risk_permission = self.client.post(
            endpoint,
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(no_risk_permission.status_code, 403)

        RolePermission.objects.create(role=self.actor.primary_role, permission=risk_permission)
        outsider = self._user(
            "appraisal.outsider@sfpcl.example",
            Permission.objects.get(permission_code="credit.appraisal.create"),
            risk_permission,
        )
        outsider.set_password("OutsiderPass123!")
        outsider.save()
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": outsider.email, "password": "OutsiderPass123!"},
            content_type="application/json",
        )
        out_of_scope = self.client.post(
            endpoint,
            data=self._payload(),
            content_type="application/json",
            headers={"Authorization": f"Bearer {login.json()['data']['access_token']}"},
        )
        self.assertEqual(out_of_scope.status_code, 403)
        self.assertEqual(out_of_scope.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
        self.assertEqual(apps.get_model("credit", "LoanAppraisalNote").objects.count(), 0)
        self.assertEqual(apps.get_model("credit", "RiskAssessment").objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="appraisal.").count(), 0)

    def test_create_update_and_submit_permissions_are_independent(self):
        create_link = RolePermission.objects.get(
            role=self.actor.primary_role,
            permission__permission_code="credit.appraisal.create",
        )
        create_permission = create_link.permission
        create_link.delete()
        endpoint = f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/"
        denied_create = self.client.post(
            endpoint,
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(denied_create.status_code, 403)

        RolePermission.objects.create(
            role=self.actor.primary_role,
            permission=create_permission,
        )
        created = self.client.post(
            endpoint,
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission__permission_code="credit.appraisal.update",
        ).delete()
        denied_update = self.client.patch(
            endpoint,
            data={"recommendation": "conditions"},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(denied_update.status_code, 403)

        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission__permission_code="credit.appraisal.submit_review",
        ).delete()
        denied_submit = self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
            data={"remarks": "Ready for review."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(denied_submit.status_code, 403)
        self.assertEqual(
            apps.get_model("credit", "LoanAppraisalNote").objects.get().appraisal_status,
            "draft",
        )

    def test_credit_manager_review_permission_can_read_credit_domain_appraisal(self):
        expected = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        review_permission = self._permission(
            "credit.appraisal.review",
            "Review appraisal",
        )
        credit_manager = self._user(
            "credit.manager@sfpcl.example",
            review_permission,
        )
        credit_manager.set_password("CreditManagerPass123!")
        credit_manager.save()
        login = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": credit_manager.email,
                "password": "CreditManagerPass123!",
            },
            content_type="application/json",
        )

        response = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            headers={"Authorization": f"Bearer {login.json()['data']['access_token']}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], expected)

    def test_submit_rejects_blank_remarks_without_transition_evidence(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]

        response = self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
            data={"remarks": "   "},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("remarks", response.json()["error"]["field_errors"])
        note = apps.get_model("credit", "LoanAppraisalNote").objects.get()
        self.assertEqual(note.appraisal_status, "draft")
        self.assertEqual(
            AuditLog.objects.filter(action="appraisal.submitted_for_review").count(),
            0,
        )

    def test_existing_exception_flag_allows_recommendation_above_stored_limit(self):
        self.loan_limit.exception_required_flag = True
        self.loan_limit.amount_within_limit_flag = False
        self.loan_limit.save(
            update_fields=["exception_required_flag", "amount_within_limit_flag"]
        )

        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={**self._payload(), "recommended_amount": "500000.01"},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["recommended_amount"], "500000.01")

    def test_tat_boundary_is_within_at_due_time_and_breached_after(self):
        fixed_now = timezone.now()
        self.application.created_at = fixed_now - timedelta(days=2)
        self.application.save(update_fields=["created_at"])
        endpoint = f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/"
        with patch(
            "sfpcl_credit.credit.modules.appraisal_workflow.timezone.now",
            return_value=fixed_now,
        ):
            at_due = self.client.post(
                endpoint,
                data=self._payload(),
                content_type="application/json",
                headers=self._headers(),
            )
        self.assertEqual(at_due.status_code, 200)
        self.assertEqual(at_due.json()["data"]["tat_status"], "within_tat")

        note_model = apps.get_model("credit", "LoanAppraisalNote")
        risk_model = apps.get_model("credit", "RiskAssessment")
        note = note_model.objects.get()
        risk = note.risk_assessment
        note.delete()
        risk.delete()
        with patch(
            "sfpcl_credit.credit.modules.appraisal_workflow.timezone.now",
            return_value=fixed_now + timedelta(microseconds=1),
        ):
            after_due = self.client.post(
                endpoint,
                data=self._payload(),
                content_type="application/json",
                headers=self._headers(),
            )
        self.assertEqual(after_due.status_code, 200)
        self.assertEqual(after_due.json()["data"]["tat_status"], "breached")

    def test_audit_failure_rolls_back_appraisal_risk_and_workflow(self):
        with patch.object(
            AuditLog.objects,
            "create",
            side_effect=RuntimeError("audit unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "audit unavailable"):
                self.client.post(
                    f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
                    data=self._payload(),
                    content_type="application/json",
                    headers=self._headers(),
                )

        self.assertEqual(apps.get_model("credit", "LoanAppraisalNote").objects.count(), 0)
        self.assertEqual(apps.get_model("credit", "RiskAssessment").objects.count(), 0)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="appraisal_note").count(), 0)

    def _payload(self):
        return {
            "borrower_summary": "Active individual farmer with verified KYC.",
            "eligibility_summary": "All mandatory eligibility criteria passed.",
            "loan_limit_summary": "Stored final eligible amount is INR 500,000.",
            "recommended_amount": "400000.00",
            "recommended_tenure_months": 12,
            "recommended_interest_type": "floating",
            "recommended_security_summary": "PoA, shares and blank-dated cheque.",
            "risk_assessment": {
                "market_risk_rating": "medium",
                "operational_risk_rating": "low",
                "borrower_risk_rating": "low",
                "overall_risk_rating": "low",
                "risk_mitigation_notes": "Produce deduction arrangement is available.",
            },
            "recommendation": "approve",
        }

    def _headers(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": self.actor.email, "password": "AppraisalPass123!"},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200)
        return {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    @staticmethod
    def _permission(code, name):
        return Permission.objects.create(
            permission_code=code,
            permission_name=name,
            module_name=code.split(".")[0],
            risk_level="high",
        )

    @staticmethod
    def _user(email, *permissions):
        role = Role.objects.create(
            role_code=email.split("@")[0].replace(".", "_"),
            role_name="Deputy Manager Finance",
            is_system_role=True,
            status="active",
        )
        for permission in permissions:
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name="Deputy Manager Finance",
            email=email,
            status="active",
            primary_role=role,
        )
        user.set_password("AppraisalPass123!")
        user.save()
        return user
