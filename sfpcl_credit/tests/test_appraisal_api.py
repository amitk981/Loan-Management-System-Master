from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from threading import Event, Lock
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4

from django.apps import apps
from django.db import close_old_connections, connection, connections
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.credit.models import EligibilityAssessment, LoanLimitAssessment
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
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
        self.assertEqual(
            appraisal["repayment_capacity_notes"],
            "Seasonal crop proceeds cover the proposed repayment schedule.",
        )
        self.assertEqual(
            appraisal["eligibility_snapshot"],
            {
                "eligibility_assessment_id": str(self.eligibility.pk),
                "loan_application_id": str(self.application.pk),
                "member_active_check": "pass",
                "default_check": "no_default",
                "document_check": "complete",
                "terms_acceptance_check": "accepted",
                "purpose_check": "agriculture_aligned",
                "nominee_check": "valid",
                "overall_result": "eligible",
                "assessment_notes": "All mandatory eligibility criteria passed.",
                "assessed_by_user_id": str(self.actor.pk),
                "assessed_at": timezone.localtime(self.eligibility.assessed_at).isoformat(),
            },
        )
        self.assertEqual(
            appraisal["loan_limit_snapshot"]["final_eligible_loan_amount"],
            "500000.00",
        )
        self.assertEqual(appraisal["prerequisite_provenance"], "verified")
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

    def test_public_appraisal_module_projects_disabled_and_enabled_resource_actions(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]

        snapshot = AppraisalWorkflow().get(
            actor=self.actor,
            application_id=self.application.pk,
        ).snapshot
        actions = {item["action_code"]: item for item in snapshot["available_actions"]}

        self.assertTrue(actions["credit.appraisal.update"]["enabled"])
        self.assertTrue(actions["credit.appraisal.submit_review"]["enabled"])
        self.assertFalse(actions["credit.appraisal.review"]["enabled"])
        self.assertEqual(actions["credit.appraisal.review"]["required_role"], "credit_manager")
        self.assertIsNotNone(actions["credit.appraisal.review"]["disabled_reason"])
        self.assertEqual(created["loan_appraisal_note_id"], snapshot["loan_appraisal_note_id"])

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

    def test_create_requires_non_blank_repayment_capacity_notes_without_writes(self):
        for invalid_notes in (None, "   "):
            payload = self._payload()
            if invalid_notes is None:
                payload.pop("repayment_capacity_notes")
            else:
                payload["repayment_capacity_notes"] = invalid_notes
            response = self.client.post(
                f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
                data=payload,
                content_type="application/json",
                headers=self._headers(),
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                "repayment_capacity_notes",
                response.json()["error"]["field_errors"],
            )
        self.assertEqual(apps.get_model("credit", "LoanAppraisalNote").objects.count(), 0)
        self.assertEqual(apps.get_model("credit", "RiskAssessment").objects.count(), 0)
        self.assertFalse(AuditLog.objects.filter(action__startswith="appraisal.").exists())
        self.assertFalse(WorkflowEvent.objects.filter(workflow_name="appraisal_note").exists())

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
        note = apps.get_model("credit", "LoanAppraisalNote").objects.get()
        self.assertEqual(
            note.submission_remarks,
            "Appraisal completed for Credit Manager review.",
        )
        audit = AuditLog.objects.get(action="appraisal.submitted_for_review")
        self.assertTrue(audit.new_value_json["submission_reason_exists"])
        self.assertEqual(
            audit.new_value_json["submission_reason_owner_id"],
            str(note.pk),
        )
        self.assertNotIn("remarks", audit.new_value_json)
        self.assertNotIn("Appraisal completed", str(audit.new_value_json))

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

    def test_credit_manager_reviews_submitted_appraisal_with_metadata_only_evidence(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
            data={"remarks": "Ready for independent review."},
            content_type="application/json",
            headers=self._headers(),
        )
        reviewer = self._user(
            "credit.manager@sfpcl.example",
            self._permission("credit.appraisal.review", "Review appraisal"),
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": reviewer.email, "password": "AppraisalPass123!"},
            content_type="application/json",
        )

        response = self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/",
            data={
                "decision": "reviewed",
                "review_comments": "Reviewed and recommended for Sanction Committee.",
            },
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {login.json()['data']['access_token']}",
                "X-Request-ID": "review-tracer-006f",
            },
        )

        self.assertEqual(response.status_code, 200)
        reviewed = response.json()["data"]
        self.assertEqual(reviewed["loan_appraisal_note_id"], created["loan_appraisal_note_id"])
        self.assertEqual(reviewed["loan_application_id"], str(self.application.pk))
        self.assertEqual(reviewed["appraisal_status"], "reviewed")
        self.assertEqual(reviewed["decision"], "reviewed")
        self.assertEqual(
            reviewed["review_comments"],
            "Reviewed and recommended for Sanction Committee.",
        )
        self.assertEqual(
            reviewed["reviewed_by"],
            {"user_id": str(reviewer.pk), "full_name": reviewer.full_name},
        )
        self.assertIsNotNone(reviewed["reviewed_at"])
        self.assertEqual(len(reviewed["review_history"]), 1)
        history = reviewed["review_history"][0]
        self.assertEqual(history["decision"], "reviewed")
        self.assertEqual(
            history["review_comments"],
            "Reviewed and recommended for Sanction Committee.",
        )

        audit = AuditLog.objects.get(action="appraisal.reviewed")
        self.assertEqual(audit.new_value_json["decision"], "reviewed")
        self.assertEqual(
            audit.new_value_json["appraisal_review_decision_id"],
            history["appraisal_review_decision_id"],
        )
        self.assertEqual(audit.new_value_json["request_id"], "review-tracer-006f")
        self.assertNotIn("review_comments", audit.new_value_json)
        self.assertNotIn("Sanction Committee", str(audit.new_value_json))
        workflow = WorkflowEvent.objects.get(
            workflow_name="appraisal_note",
            to_state="reviewed",
        )
        self.assertEqual(workflow.from_state, "review_pending")
        self.assertIn(history["appraisal_review_decision_id"], workflow.trigger_reason)
        self.assertNotIn("Sanction Committee", workflow.trigger_reason)
        self.assertNotIn("risk", workflow.trigger_reason.lower())

    def test_credit_manager_rejects_appraisal_and_creates_one_unsent_rejection_note(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
            data={"remarks": "Ready for a terminal credit decision."},
            content_type="application/json",
            headers=self._headers(),
        )
        reviewer, review_headers = self._credit_manager_headers()

        response = self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/",
            data={
                "decision": "rejected",
                "review_comments": "Independent credit review completed.",
                "rejection_reason_category": "eligibility",
                "detailed_reason": "Verified appraisal facts do not meet credit criteria.",
                "reapply_allowed_flag": True,
                "communication_mode": "email",
            },
            content_type="application/json",
            headers={**review_headers, "X-Request-ID": "reject-tracer-006f2"},
        )

        self.assertEqual(response.status_code, 200)
        rejected = response.json()["data"]
        self.assertEqual(rejected["appraisal_status"], "rejected")
        self.assertEqual(rejected["decision"], "rejected")
        rejection_note = rejected["rejection_note"]
        self.assertEqual(rejection_note["loan_application_id"], str(self.application.pk))
        self.assertEqual(rejection_note["rejection_stage"], "credit_assessment")
        self.assertEqual(rejection_note["rejection_reason_category"], "eligibility")
        self.assertEqual(rejection_note["note_status"], "draft")
        self.assertEqual(rejection_note["communication_status"], "not_sent")
        self.assertEqual(rejection_note["prepared_by_user_id"], str(reviewer.pk))
        self.assertIsNone(rejection_note["sent_at"])
        self.assertEqual(len(rejected["review_history"]), 1)
        rejection_history = rejected["review_history"][0]
        self.assertEqual(rejection_history["decision"], "rejected")
        self.assertEqual(
            rejection_history["review_comments"],
            "Independent credit review completed.",
        )

        rejection_note_model = apps.get_model("applications", "RejectionNote")
        self.assertEqual(rejection_note_model.objects.count(), 1)
        self.assertEqual(
            str(rejection_note_model.objects.get().rejection_note_id),
            rejection_note["rejection_note_id"],
        )
        appraisal_audit = AuditLog.objects.get(action="appraisal.rejected")
        self.assertEqual(
            appraisal_audit.new_value_json["rejection_note_id"],
            rejection_note["rejection_note_id"],
        )
        self.assertEqual(
            appraisal_audit.new_value_json["appraisal_review_decision_id"],
            rejection_history["appraisal_review_decision_id"],
        )
        self.assertEqual(appraisal_audit.new_value_json["request_id"], "reject-tracer-006f2")
        self.assertNotIn("review_comments", appraisal_audit.new_value_json)
        self.assertNotIn("detailed_reason", appraisal_audit.new_value_json)
        self.assertNotIn("credit criteria", str(appraisal_audit.new_value_json))
        self.assertEqual(
            AuditLog.objects.filter(action="applications.rejection_note.created").count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="appraisal_note",
                from_state="review_pending",
                to_state="rejected",
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                entity_type="rejection_note",
                to_state="draft",
            ).count(),
            1,
        )
        repeated = self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/",
            data={
                "decision": "rejected",
                "review_comments": "Attempted repeated rejection.",
                "rejection_reason_category": "eligibility",
                "detailed_reason": "This must not create a second note.",
                "reapply_allowed_flag": True,
                "communication_mode": "email",
            },
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(repeated.status_code, 409)
        self.assertEqual(rejection_note_model.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="appraisal.rejected").count(), 1)
        self.assertEqual(
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            1,
        )

    def test_rejected_review_requires_explicit_source_rejection_note_fields(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
            data={"remarks": "Ready for rejection validation."},
            content_type="application/json",
            headers=self._headers(),
        )
        _, review_headers = self._credit_manager_headers()
        workflow_count = WorkflowEvent.objects.count()

        response = self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/",
            data={
                "decision": "rejected",
                "review_comments": "Independent review complete.",
                "rejection_reason_category": "eligibility",
                "detailed_reason": "Credit criteria were not met.",
                "communication_mode": "email",
            },
            content_type="application/json",
            headers=review_headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertIn(
            "reapply_allowed_flag",
            response.json()["error"]["field_errors"],
        )
        note = apps.get_model("credit", "LoanAppraisalNote").objects.get()
        self.assertEqual(note.appraisal_status, "review_pending")
        self.assertIsNone(note.reviewed_by_user_id)
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 0)
        self.assertFalse(AuditLog.objects.filter(action="appraisal.rejected").exists())
        self.assertEqual(WorkflowEvent.objects.count(), workflow_count)

        invalid_payloads = (
            (
                {
                    "decision": "rejected",
                    "review_comments": "Independent review complete.",
                    "rejection_reason_category": "unknown_reason",
                    "detailed_reason": "Credit criteria were not met.",
                    "reapply_allowed_flag": True,
                    "communication_mode": "email",
                },
                "rejection_reason_category",
            ),
            (
                {
                    "decision": "rejected",
                    "review_comments": "Independent review complete.",
                    "rejection_reason_category": "eligibility",
                    "detailed_reason": "   ",
                    "reapply_allowed_flag": True,
                    "communication_mode": "email",
                },
                "detailed_reason",
            ),
            (
                {
                    "decision": "rejected",
                    "review_comments": "Independent review complete.",
                    "rejection_reason_category": "eligibility",
                    "detailed_reason": "Credit criteria were not met.",
                    "reapply_allowed_flag": True,
                    "communication_mode": "email",
                    "rejection_stage": "sanction_committee",
                },
                "rejection_stage",
            ),
        )
        for payload, expected_field in invalid_payloads:
            with self.subTest(expected_field=expected_field):
                invalid = self.client.post(
                    f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/",
                    data=payload,
                    content_type="application/json",
                    headers=review_headers,
                )
                self.assertEqual(invalid.status_code, 400)
                self.assertIn(expected_field, invalid.json()["error"]["field_errors"])
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 0)
        self.assertEqual(WorkflowEvent.objects.count(), workflow_count)

    def test_rejection_failures_roll_back_appraisal_note_and_all_success_evidence(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
            data={"remarks": "Frozen facts are ready for rejection."},
            content_type="application/json",
            headers=self._headers(),
        )
        _, review_headers = self._credit_manager_headers()
        review_url = f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/"
        payload = {
            "decision": "rejected",
            "review_comments": "Independent review complete.",
            "rejection_reason_category": "limit_issue",
            "detailed_reason": "The requested amount cannot be supported.",
            "reapply_allowed_flag": True,
            "communication_mode": "email",
        }
        note = apps.get_model("credit", "LoanAppraisalNote").objects.get()
        preserved = {
            "eligibility": note.eligibility_snapshot_json,
            "loan_limit": note.loan_limit_snapshot_json,
            "repayment": note.repayment_capacity_notes,
            "remarks": note.submission_remarks,
            "recommendation": note.recommendation,
            "tat_due_at": note.tat_due_at,
            "risk": note.risk_assessment.overall_risk_rating,
        }

        with patch(
            "sfpcl_credit.applications.services._audit_rejection_note",
            side_effect=RuntimeError("rejection audit unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "rejection audit unavailable"):
                self.client.post(
                    review_url,
                    data=payload,
                    content_type="application/json",
                    headers=review_headers,
                )
        note.refresh_from_db()
        self.assertEqual(note.appraisal_status, "review_pending")
        self.assertIsNone(note.reviewed_by_user_id)
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 0)
        self.assertEqual(
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            0,
        )
        self.assertFalse(AuditLog.objects.filter(action="appraisal.rejected").exists())

        with patch(
            "sfpcl_credit.credit.modules.appraisal_workflow.record_workflow_event",
            side_effect=RuntimeError("appraisal workflow unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "appraisal workflow unavailable"):
                self.client.post(
                    review_url,
                    data=payload,
                    content_type="application/json",
                    headers=review_headers,
                )
        note.refresh_from_db()
        self.assertEqual(note.appraisal_status, "review_pending")
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 0)
        self.assertEqual(
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            0,
        )
        self.assertFalse(AuditLog.objects.filter(action="appraisal.rejected").exists())
        self.assertFalse(
            AuditLog.objects.filter(action="applications.rejection_note.created").exists()
        )

        rejected = self.client.post(
            review_url,
            data=payload,
            content_type="application/json",
            headers=review_headers,
        ).json()["data"]
        self.assertEqual(rejected["eligibility_snapshot"], preserved["eligibility"])
        self.assertEqual(rejected["loan_limit_snapshot"], preserved["loan_limit"])
        note.refresh_from_db()
        self.assertEqual(note.repayment_capacity_notes, preserved["repayment"])
        self.assertEqual(note.submission_remarks, preserved["remarks"])
        self.assertEqual(note.recommendation, preserved["recommendation"])
        self.assertEqual(note.tat_due_at, preserved["tat_due_at"])
        self.assertEqual(note.risk_assessment.overall_risk_rating, preserved["risk"])

    def test_returned_appraisal_can_be_revised_resubmitted_and_reviewed(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        submit_url = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/"
            "submit-for-review/"
        )
        review_url = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/"
        )
        self.client.post(
            submit_url,
            data={"remarks": "Initial submission."},
            content_type="application/json",
            headers=self._headers(),
        )
        reviewer = self._user(
            "credit.manager@sfpcl.example",
            self._permission("credit.appraisal.review", "Review appraisal"),
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": reviewer.email, "password": "AppraisalPass123!"},
            content_type="application/json",
        )
        review_headers = {
            "Authorization": f"Bearer {login.json()['data']['access_token']}"
        }

        returned_response = self.client.post(
            review_url,
            data={
                "decision": "returned",
                "review_comments": "Clarify the seasonal repayment assumptions.",
            },
            content_type="application/json",
            headers=review_headers,
        )

        self.assertEqual(returned_response.status_code, 200)
        returned = returned_response.json()["data"]
        self.assertEqual(returned["appraisal_status"], "draft")
        self.assertEqual(returned["decision"], "returned")
        self.assertEqual(
            returned["review_comments"],
            "Clarify the seasonal repayment assumptions.",
        )
        returned_audit = AuditLog.objects.get(action="appraisal.returned")
        self.assertNotIn("review_comments", returned_audit.new_value_json)
        self.assertNotIn("seasonal repayment", str(returned_audit.new_value_json))

        revised = self.client.patch(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={
                "repayment_capacity_notes": (
                    "Seasonal crop proceeds and monthly deductions cover repayment."
                )
            },
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(revised.status_code, 200)
        resubmitted = self.client.post(
            submit_url,
            data={"remarks": "Repayment assumptions clarified."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(resubmitted.status_code, 200)
        self.assertEqual(resubmitted.json()["data"]["appraisal_status"], "review_pending")
        reviewed = self.client.post(
            review_url,
            data={"decision": "reviewed", "review_comments": "Clarification accepted."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(reviewed.status_code, 200)
        reviewed_data = reviewed.json()["data"]
        self.assertEqual(reviewed_data["appraisal_status"], "reviewed")
        self.assertEqual(reviewed_data["decision"], "reviewed")
        self.assertEqual(reviewed_data["review_comments"], "Clarification accepted.")
        self.assertEqual(
            [item["decision"] for item in reviewed_data["review_history"]],
            ["returned", "reviewed"],
        )
        self.assertEqual(
            [item["review_comments"] for item in reviewed_data["review_history"]],
            [
                "Clarify the seasonal repayment assumptions.",
                "Clarification accepted.",
            ],
        )
        self.assertEqual(
            [item["from_state"] for item in reviewed_data["review_history"]],
            ["review_pending", "review_pending"],
        )
        self.assertEqual(
            [item["to_state"] for item in reviewed_data["review_history"]],
            ["draft", "reviewed"],
        )
        self.assertTrue(
            all(
                item["reviewer"]
                == {"user_id": str(reviewer.pk), "full_name": reviewer.full_name}
                for item in reviewed_data["review_history"]
            )
        )
        self.assertTrue(
            all(item["history_provenance"] == "native" for item in reviewed_data["review_history"])
        )
        history_model = apps.get_model("credit", "AppraisalReviewDecision")
        persisted = list(history_model.objects.order_by("decided_at", "pk"))
        self.assertEqual(len(persisted), 2)
        original_return_time = persisted[0].decided_at
        original_return_reviewer = persisted[0].reviewer_user_id
        self.assertEqual(persisted[0].review_comments, "Clarify the seasonal repayment assumptions.")
        persisted[0].refresh_from_db()
        self.assertEqual(persisted[0].decided_at, original_return_time)
        self.assertEqual(persisted[0].reviewer_user_id, original_return_reviewer)
        self.assertEqual(persisted[0].review_comments, "Clarify the seasonal repayment assumptions.")
        self.assertEqual(AuditLog.objects.filter(action="appraisal.returned").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="appraisal.reviewed").count(), 1)

    def test_review_enforces_independent_permission_object_scope_and_maker_checker(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
            data={"remarks": "Ready for review."},
            content_type="application/json",
            headers=self._headers(),
        )
        review_url = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/"
        )
        workflow_count_before_denials = WorkflowEvent.objects.filter(
            workflow_name="appraisal_note"
        ).count()
        payload = {
            "decision": "rejected",
            "review_comments": "Independent review.",
            "rejection_reason_category": "eligibility",
            "detailed_reason": "The appraisal does not meet credit criteria.",
            "reapply_allowed_flag": True,
            "communication_mode": "email",
        }
        review_permission = self._permission(
            "credit.appraisal.review",
            "Review appraisal",
        )
        in_scope_non_manager = self._user(
            "delegated.reviewer@sfpcl.example",
            review_permission,
        )
        self.application.received_by_user = in_scope_non_manager
        self.application.save(update_fields=["received_by_user"])
        delegated_login = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": in_scope_non_manager.email,
                "password": "AppraisalPass123!",
            },
            content_type="application/json",
        )
        delegated_denied = self.client.post(
            review_url,
            data=payload,
            content_type="application/json",
            headers={
                "Authorization": (
                    f"Bearer {delegated_login.json()['data']['access_token']}"
                )
            },
        )
        self.assertEqual(delegated_denied.status_code, 403)
        self.assertEqual(
            delegated_denied.json()["error"]["code"],
            "FORBIDDEN",
        )
        self.assertEqual(
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            0,
        )
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 0)
        self.assertFalse(AuditLog.objects.filter(action="appraisal.rejected").exists())
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="appraisal_note").count(),
            workflow_count_before_denials,
        )
        maker_review_link = RolePermission.objects.create(
            role=self.actor.primary_role,
            permission=review_permission,
        )

        maker_denied = self.client.post(
            review_url,
            data=payload,
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(maker_denied.status_code, 403)
        self.assertEqual(maker_denied.json()["error"]["code"], "FORBIDDEN")

        maker_review_link.delete()
        missing_permission = self.client.post(
            review_url,
            data=payload,
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(missing_permission.status_code, 403)
        self.assertEqual(
            missing_permission.json()["error"]["code"],
            "FORBIDDEN",
        )

        non_manager_outsider = self._user(
            "other.reviewer@sfpcl.example",
            review_permission,
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": non_manager_outsider.email, "password": "AppraisalPass123!"},
            content_type="application/json",
        )
        out_of_scope = self.client.post(
            review_url,
            data=payload,
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {login.json()['data']['access_token']}"
            },
        )
        self.assertEqual(out_of_scope.status_code, 403)
        self.assertEqual(out_of_scope.json()["error"]["code"], "FORBIDDEN")
        note = apps.get_model("credit", "LoanAppraisalNote").objects.get()
        self.assertEqual(note.appraisal_status, "review_pending")
        self.assertFalse(
            AuditLog.objects.filter(
                action__in=(
                    "appraisal.reviewed",
                    "appraisal.returned",
                    "appraisal.rejected",
                )
            ).exists()
        )
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 0)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="appraisal_note").count(),
            workflow_count_before_denials,
        )

        credit_manager_role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
            is_system_role=True,
            status="active",
        )
        RolePermission.objects.create(
            role=credit_manager_role,
            permission=review_permission,
        )
        credit_manager = User.objects.create(
            full_name="Credit Manager",
            email="authority.credit-manager@sfpcl.example",
            status="active",
            primary_role=credit_manager_role,
        )
        credit_manager.set_password("AppraisalPass123!")
        credit_manager.save()
        manager_login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": credit_manager.email, "password": "AppraisalPass123!"},
            content_type="application/json",
        )
        manager_headers = {
            "Authorization": f"Bearer {manager_login.json()['data']['access_token']}"
        }
        LoanApplication.objects.filter(pk=self.application.pk).update(
            current_stage=LoanApplication.STAGE_INITIAL
        )
        manager_out_of_scope = self.client.post(
            review_url,
            data=payload,
            content_type="application/json",
            headers=manager_headers,
        )
        self.assertEqual(manager_out_of_scope.status_code, 403)
        self.assertEqual(
            manager_out_of_scope.json()["error"]["code"],
            "OBJECT_ACCESS_DENIED",
        )
        self.assertEqual(
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            0,
        )

        LoanApplication.objects.filter(pk=self.application.pk).update(
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT
        )
        manager_succeeds = self.client.post(
            review_url,
            data=payload,
            content_type="application/json",
            headers=manager_headers,
        )
        self.assertEqual(manager_succeeds.status_code, 200)
        self.assertEqual(manager_succeeds.json()["data"]["appraisal_status"], "rejected")
        self.assertEqual(
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            1,
        )

    def test_review_validates_payload_provenance_and_state_without_success_evidence(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        submit_url = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/"
            "submit-for-review/"
        )
        review_url = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/"
        )
        self.client.post(
            submit_url,
            data={"remarks": "Ready for validation checks."},
            content_type="application/json",
            headers=self._headers(),
        )
        _, review_headers = self._credit_manager_headers()

        invalid_payloads = (
            ({"decision": "returned", "review_comments": "   "}, "review_comments"),
            ({"decision": "approved", "review_comments": "Checked."}, "decision"),
            (
                {
                    "decision": "reviewed",
                    "review_comments": "Checked.",
                    "approval_case": "not-in-this-slice",
                },
                "approval_case",
            ),
        )
        for payload, expected_field in invalid_payloads:
            with self.subTest(expected_field=expected_field):
                response = self.client.post(
                    review_url,
                    data=payload,
                    content_type="application/json",
                    headers=review_headers,
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
                self.assertIn(expected_field, response.json()["error"]["field_errors"])

        note = apps.get_model("credit", "LoanAppraisalNote").objects.get()
        note.prerequisite_provenance = "legacy_unverified"
        note.save(update_fields=["prerequisite_provenance"])
        unverified = self.client.post(
            review_url,
            data={"decision": "reviewed", "review_comments": "Checked."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(unverified.status_code, 409)
        note.refresh_from_db()
        self.assertEqual(note.appraisal_status, "review_pending")

        note.prerequisite_provenance = "verified"
        note.appraisal_status = "draft"
        note.save(update_fields=["prerequisite_provenance", "appraisal_status"])
        draft_review = self.client.post(
            review_url,
            data={"decision": "reviewed", "review_comments": "Checked."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(draft_review.status_code, 409)
        self.assertFalse(
            AuditLog.objects.filter(
                action__in=("appraisal.reviewed", "appraisal.returned")
            ).exists()
        )

    def test_review_preserves_frozen_appraisal_facts_and_rolls_back_evidence_failure(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
            data={"remarks": "Snapshot facts are final for review."},
            content_type="application/json",
            headers=self._headers(),
        )
        _, review_headers = self._credit_manager_headers()
        review_url = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/review/"
        )

        self.eligibility.overall_result = EligibilityAssessment.OVERALL_INELIGIBLE
        self.eligibility.default_check = "default_found"
        self.eligibility.save(update_fields=["overall_result", "default_check"])
        self.loan_limit.final_eligible_loan_amount = Decimal("700000.00")
        self.loan_limit.exception_required_flag = True
        self.loan_limit.save(
            update_fields=["final_eligible_loan_amount", "exception_required_flag"]
        )
        note = apps.get_model("credit", "LoanAppraisalNote").objects.get()
        preserved = {
            "eligibility_snapshot": note.eligibility_snapshot_json,
            "loan_limit_snapshot": note.loan_limit_snapshot_json,
            "recommended_amount": note.recommended_amount,
            "tat_due_at": note.tat_due_at,
            "tat_status": note.tat_status,
            "repayment_capacity_notes": note.repayment_capacity_notes,
            "submission_remarks": note.submission_remarks,
            "recommendation": note.recommendation,
            "risk": {
                "overall": note.risk_assessment.overall_risk_rating,
                "notes": note.risk_assessment.risk_mitigation_notes,
            },
        }

        with patch(
            "sfpcl_credit.credit.modules.appraisal_workflow.record_workflow_event",
            side_effect=RuntimeError("workflow unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "workflow unavailable"):
                self.client.post(
                    review_url,
                    data={"decision": "reviewed", "review_comments": "Checked."},
                    content_type="application/json",
                    headers=review_headers,
                )
        note.refresh_from_db()
        self.assertEqual(note.appraisal_status, "review_pending")
        self.assertIsNone(note.reviewed_by_user_id)
        self.assertEqual(
            apps.get_model("credit", "AppraisalReviewDecision").objects.count(),
            0,
        )
        self.assertFalse(AuditLog.objects.filter(action="appraisal.reviewed").exists())

        response = self.client.post(
            review_url,
            data={"decision": "reviewed", "review_comments": "Checked."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(response.status_code, 200)
        reviewed = response.json()["data"]
        self.assertEqual(reviewed["eligibility_snapshot"], preserved["eligibility_snapshot"])
        self.assertEqual(reviewed["loan_limit_snapshot"], preserved["loan_limit_snapshot"])
        note.refresh_from_db()
        self.assertEqual(note.recommended_amount, preserved["recommended_amount"])
        self.assertEqual(note.tat_due_at, preserved["tat_due_at"])
        self.assertEqual(note.tat_status, preserved["tat_status"])
        self.assertEqual(note.repayment_capacity_notes, preserved["repayment_capacity_notes"])
        self.assertEqual(note.submission_remarks, preserved["submission_remarks"])
        self.assertEqual(note.recommendation, preserved["recommendation"])
        self.assertEqual(note.risk_assessment.overall_risk_rating, preserved["risk"]["overall"])
        self.assertEqual(note.risk_assessment.risk_mitigation_notes, preserved["risk"]["notes"])
        repeated = self.client.post(
            review_url,
            data={"decision": "returned", "review_comments": "Attempted repeat."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(repeated.status_code, 409)
        self.assertEqual(AuditLog.objects.filter(action="appraisal.reviewed").count(), 1)
        self.assertFalse(AuditLog.objects.filter(action="appraisal.returned").exists())
        locked_edit = self.client.patch(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data={"repayment_capacity_notes": "Attempted post-review edit."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(locked_edit.status_code, 409)

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
        actual = response.json()["data"]
        self.assertEqual(
            {key: value for key, value in actual.items() if key != "available_actions"},
            {key: value for key, value in expected.items() if key != "available_actions"},
        )
        actions = {item["action_code"]: item for item in actual["available_actions"]}
        self.assertEqual(
            set(actions),
            {
                "credit.appraisal.update",
                "revalidate_appraisal_prerequisites",
                "credit.appraisal.submit_review",
                "credit.appraisal.review",
                "credit.appraisal.submit_sanction",
            },
        )
        self.assertFalse(actions["credit.appraisal.review"]["enabled"])
        self.assertEqual(actions["credit.appraisal.review"]["required_role"], "credit_manager")

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

    def test_legacy_unverified_draft_requires_scoped_revalidation_before_submit(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        note_model = apps.get_model("credit", "LoanAppraisalNote")
        note = note_model.objects.get()
        original_recommendation = note.recommendation
        original_risk_id = note.risk_assessment_id
        note.prerequisite_provenance = "legacy_unverified"
        note.eligibility_snapshot_json = {}
        note.loan_limit_snapshot_json = {}
        note.save(
            update_fields=(
                "prerequisite_provenance",
                "eligibility_snapshot_json",
                "loan_limit_snapshot_json",
            )
        )

        submit_url = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/"
        )
        blocked = self.client.post(
            submit_url,
            data={"remarks": "Ready for review."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(blocked.status_code, 409)

        response = self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/revalidate-prerequisites/",
            data={},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        revalidated = response.json()["data"]
        self.assertEqual(revalidated["prerequisite_provenance"], "verified")
        note.refresh_from_db()
        self.assertEqual(note.recommendation, original_recommendation)
        self.assertEqual(note.risk_assessment_id, original_risk_id)
        audit = AuditLog.objects.get(action="appraisal.prerequisites_revalidated")
        self.assertEqual(
            audit.new_value_json["eligibility_assessment_id"],
            str(self.eligibility.pk),
        )
        self.assertNotIn("assessment_notes", str(audit.new_value_json))

        repeated_revalidation = self.client.post(
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/revalidate-prerequisites/",
            data={},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(repeated_revalidation.status_code, 409)
        self.assertEqual(
            AuditLog.objects.filter(action="appraisal.prerequisites_revalidated").count(),
            1,
        )

        submitted = self.client.post(
            submit_url,
            data={"remarks": "Ready for review."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(submitted.status_code, 200)

    def test_legacy_review_pending_revalidation_pins_facts_and_stays_pending(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        appraisal_id = created["loan_appraisal_note_id"]
        submitted = self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/submit-for-review/",
            data={"remarks": "Ready for review."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(submitted.status_code, 200)
        note = apps.get_model("credit", "LoanAppraisalNote").objects.get(pk=appraisal_id)
        note.prerequisite_provenance = "legacy_unverified"
        note.eligibility_snapshot_json = {}
        note.loan_limit_snapshot_json = {}
        note.save(
            update_fields=(
                "prerequisite_provenance",
                "eligibility_snapshot_json",
                "loan_limit_snapshot_json",
            )
        )

        response = self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/revalidate-prerequisites/",
            data={},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        remediated = response.json()["data"]
        self.assertEqual(remediated["appraisal_status"], "review_pending")
        self.assertEqual(remediated["prerequisite_provenance"], "verified")
        self.assertEqual(
            remediated["eligibility_snapshot"]["eligibility_assessment_id"],
            str(self.eligibility.pk),
        )
        audit = AuditLog.objects.get(action="appraisal.prerequisites_revalidated")
        self.assertEqual(audit.old_value_json["appraisal_status"], "review_pending")
        self.assertEqual(audit.new_value_json["appraisal_status"], "review_pending")
        self.assertNotIn("recommended_amount", str(audit.new_value_json))
        event = WorkflowEvent.objects.get(
            workflow_name="appraisal_note",
            entity_id=appraisal_id,
            trigger_reason="Appraisal prerequisite projections revalidated.",
        )
        self.assertEqual(event.from_state, "review_pending")
        self.assertEqual(event.to_state, "review_pending")

    def test_legacy_reviewed_revalidation_requires_fresh_review_before_sanction(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        appraisal_id = created["loan_appraisal_note_id"]
        submit_url = f"/api/v1/appraisal-notes/{appraisal_id}/submit-for-review/"
        review_url = f"/api/v1/appraisal-notes/{appraisal_id}/review/"
        self.client.post(
            submit_url,
            data={"remarks": "Ready for initial review."},
            content_type="application/json",
            headers=self._headers(),
        )
        reviewer, review_headers = self._credit_manager_headers()
        sanction_permission = self._permission(
            "credit.appraisal.submit_sanction",
            "Submit appraisal to sanction",
        )
        RolePermission.objects.create(
            role=reviewer.primary_role,
            permission=sanction_permission,
        )
        initially_reviewed = self.client.post(
            review_url,
            data={"decision": "reviewed", "review_comments": "Initial review."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(initially_reviewed.status_code, 200)
        note_model = apps.get_model("credit", "LoanAppraisalNote")
        history_model = apps.get_model("credit", "AppraisalReviewDecision")
        note = note_model.objects.get(pk=appraisal_id)
        original_history = list(
            history_model.objects.filter(loan_appraisal_note=note).values()
        )
        authored_facts = {
            "recommendation": note.recommendation,
            "repayment_capacity_notes": note.repayment_capacity_notes,
            "risk_assessment_id": note.risk_assessment_id,
            "tat_due_at": note.tat_due_at,
        }
        note.prerequisite_provenance = "legacy_unverified"
        note.eligibility_snapshot_json = {}
        note.loan_limit_snapshot_json = {}
        note.save(
            update_fields=(
                "prerequisite_provenance",
                "eligibility_snapshot_json",
                "loan_limit_snapshot_json",
            )
        )

        remediated_response = self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/revalidate-prerequisites/",
            data={},
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(remediated_response.status_code, 200)
        remediated = remediated_response.json()["data"]
        self.assertEqual(remediated["appraisal_status"], "draft")
        self.assertIsNone(remediated["decision"])
        self.assertIsNone(remediated["reviewed_by"])
        self.assertIsNone(remediated["reviewed_at"])
        self.assertIsNone(remediated["review_comments"])
        self.assertEqual(remediated["review_history"], initially_reviewed.json()["data"]["review_history"])
        note.refresh_from_db()
        self.assertEqual(note.recommendation, authored_facts["recommendation"])
        self.assertEqual(
            note.repayment_capacity_notes,
            authored_facts["repayment_capacity_notes"],
        )
        self.assertEqual(note.risk_assessment_id, authored_facts["risk_assessment_id"])
        self.assertEqual(note.tat_due_at, authored_facts["tat_due_at"])
        self.assertEqual(
            list(history_model.objects.filter(loan_appraisal_note=note).values()),
            original_history,
        )
        remediation_audit = AuditLog.objects.get(
            action="appraisal.prerequisites_revalidated"
        )
        self.assertEqual(remediation_audit.old_value_json["appraisal_status"], "reviewed")
        self.assertEqual(remediation_audit.new_value_json["appraisal_status"], "draft")
        self.assertTrue(remediation_audit.new_value_json["review_authority_invalidated"])
        self.assertNotIn("Initial review", str(remediation_audit.new_value_json))

        sanction_url = (
            f"/api/v1/loan-applications/{self.application.pk}/"
            "submit-to-sanction-committee/"
        )
        blocked = self.client.post(
            sanction_url,
            data={"remarks": "Must not reuse the old review."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(blocked.status_code, 409)
        self.assertFalse(apps.get_model("approvals", "ApprovalCase").objects.exists())

        resubmitted = self.client.post(
            submit_url,
            data={"remarks": "Revalidated facts ready for fresh review."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(resubmitted.status_code, 200)
        freshly_reviewed = self.client.post(
            review_url,
            data={"decision": "reviewed", "review_comments": "Fresh independent review."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(freshly_reviewed.status_code, 200)
        self.assertEqual(len(freshly_reviewed.json()["data"]["review_history"]), 2)
        sanctioned = self.client.post(
            sanction_url,
            data={"remarks": "Fresh review completed."},
            content_type="application/json",
            headers=review_headers,
        )
        self.assertEqual(sanctioned.status_code, 200)

    def test_revalidation_requires_both_scopes_and_rolls_back_workflow_failure(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        note_model = apps.get_model("credit", "LoanAppraisalNote")
        note = note_model.objects.get()
        note.prerequisite_provenance = "legacy_unverified"
        note.eligibility_snapshot_json = {}
        note.loan_limit_snapshot_json = {}
        note.save(
            update_fields=(
                "prerequisite_provenance",
                "eligibility_snapshot_json",
                "loan_limit_snapshot_json",
            )
        )
        endpoint = (
            f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/"
            "revalidate-prerequisites/"
        )

        update_link = RolePermission.objects.get(
            role=self.actor.primary_role,
            permission__permission_code="credit.appraisal.update",
        )
        update_permission = update_link.permission
        update_link.delete()
        denied_update = self.client.post(
            endpoint,
            data={},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(denied_update.status_code, 403)
        RolePermission.objects.create(role=self.actor.primary_role, permission=update_permission)

        risk_link = RolePermission.objects.get(
            role=self.actor.primary_role,
            permission__permission_code="credit.risk_assessment.manage",
        )
        risk_permission = risk_link.permission
        risk_link.delete()
        denied_risk = self.client.post(
            endpoint,
            data={},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(denied_risk.status_code, 403)
        RolePermission.objects.create(role=self.actor.primary_role, permission=risk_permission)

        with patch(
            "sfpcl_credit.credit.modules.appraisal_workflow.record_workflow_event",
            side_effect=RuntimeError("workflow unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "workflow unavailable"):
                self.client.post(
                    endpoint,
                    data={},
                    content_type="application/json",
                    headers=self._headers(),
                )
        note.refresh_from_db()
        self.assertEqual(note.prerequisite_provenance, "legacy_unverified")
        self.assertEqual(note.eligibility_snapshot_json, {})
        self.assertEqual(note.loan_limit_snapshot_json, {})
        self.assertFalse(
            AuditLog.objects.filter(action="appraisal.prerequisites_revalidated").exists()
        )

    def test_revalidation_rejects_malformed_scope_and_terminal_states_without_writes(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        appraisal_id = created["loan_appraisal_note_id"]
        endpoint = (
            f"/api/v1/appraisal-notes/{appraisal_id}/revalidate-prerequisites/"
        )
        note = apps.get_model("credit", "LoanAppraisalNote").objects.get(pk=appraisal_id)
        note.prerequisite_provenance = "legacy_unverified"
        note.eligibility_snapshot_json = {}
        note.loan_limit_snapshot_json = {}
        note.save(
            update_fields=(
                "prerequisite_provenance",
                "eligibility_snapshot_json",
                "loan_limit_snapshot_json",
            )
        )
        baseline = {
            "audit": AuditLog.objects.filter(
                action="appraisal.prerequisites_revalidated"
            ).count(),
            "workflow": WorkflowEvent.objects.filter(
                workflow_name="appraisal_note",
                trigger_reason="Appraisal prerequisite projections revalidated.",
            ).count(),
        }

        malformed = self.client.post(
            endpoint,
            data="{",
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(malformed.status_code, 400)
        self.assertEqual(malformed.json()["error"]["code"], "VALIDATION_ERROR")
        unknown = self.client.post(
            endpoint,
            data={"silently_bless": True},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(unknown.status_code, 400)
        self.assertIn("silently_bless", unknown.json()["error"]["field_errors"])

        outsider = self._user(
            "legacy.remediation.outsider@sfpcl.example",
            Permission.objects.get(permission_code="credit.appraisal.update"),
            Permission.objects.get(permission_code="credit.risk_assessment.manage"),
        )
        outsider_login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": outsider.email, "password": "AppraisalPass123!"},
            content_type="application/json",
        )
        denied = self.client.post(
            endpoint,
            data={},
            content_type="application/json",
            headers={
                "Authorization": (
                    f"Bearer {outsider_login.json()['data']['access_token']}"
                )
            },
        )
        self.assertIn(denied.status_code, {403, 404})

        for terminal_state in ("rejected", "submitted_to_sanction_committee"):
            with self.subTest(terminal_state=terminal_state):
                note.appraisal_status = terminal_state
                note.save(update_fields=["appraisal_status"])
                quarantined = self.client.post(
                    endpoint,
                    data={},
                    content_type="application/json",
                    headers=self._headers(),
                )
                self.assertEqual(quarantined.status_code, 409)
                self.assertIn(
                    "governed manual repair",
                    quarantined.json()["error"]["message"],
                )
                note.refresh_from_db()
                self.assertEqual(note.appraisal_status, terminal_state)
                self.assertEqual(note.prerequisite_provenance, "legacy_unverified")
                self.assertEqual(note.eligibility_snapshot_json, {})
                self.assertEqual(note.loan_limit_snapshot_json, {})

        self.assertEqual(
            AuditLog.objects.filter(
                action="appraisal.prerequisites_revalidated"
            ).count(),
            baseline["audit"],
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="appraisal_note",
                trigger_reason="Appraisal prerequisite projections revalidated.",
            ).count(),
            baseline["workflow"],
        )

    def test_reviewed_revalidation_rolls_back_authority_clear_on_evidence_failure(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        appraisal_id = created["loan_appraisal_note_id"]
        self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/submit-for-review/",
            data={"remarks": "Ready for review."},
            content_type="application/json",
            headers=self._headers(),
        )
        _, review_headers = self._credit_manager_headers()
        self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/review/",
            data={"decision": "reviewed", "review_comments": "Immutable review."},
            content_type="application/json",
            headers=review_headers,
        )
        note_model = apps.get_model("credit", "LoanAppraisalNote")
        history_model = apps.get_model("credit", "AppraisalReviewDecision")
        note = note_model.objects.get(pk=appraisal_id)
        note.prerequisite_provenance = "legacy_unverified"
        note.eligibility_snapshot_json = {}
        note.loan_limit_snapshot_json = {}
        note.save(
            update_fields=(
                "prerequisite_provenance",
                "eligibility_snapshot_json",
                "loan_limit_snapshot_json",
            )
        )
        endpoint = (
            f"/api/v1/appraisal-notes/{appraisal_id}/revalidate-prerequisites/"
        )
        preserved_history = list(
            history_model.objects.filter(loan_appraisal_note=note).values()
        )
        evidence_count = AuditLog.objects.filter(
            action="appraisal.prerequisites_revalidated"
        ).count()

        with patch.object(
            AuditLog.objects,
            "create",
            side_effect=RuntimeError("audit unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "audit unavailable"):
                self.client.post(
                    endpoint,
                    data={},
                    content_type="application/json",
                    headers=self._headers(),
                )
        note.refresh_from_db()
        self.assertEqual(note.appraisal_status, "reviewed")
        self.assertEqual(note.last_review_decision, "reviewed")
        self.assertEqual(note.review_comments, "Immutable review.")
        self.assertEqual(note.prerequisite_provenance, "legacy_unverified")
        self.assertEqual(note.eligibility_snapshot_json, {})
        self.assertEqual(note.loan_limit_snapshot_json, {})

        with patch(
            "sfpcl_credit.credit.modules.appraisal_workflow.record_workflow_event",
            side_effect=RuntimeError("workflow unavailable"),
        ):
            with self.assertRaisesMessage(RuntimeError, "workflow unavailable"):
                self.client.post(
                    endpoint,
                    data={},
                    content_type="application/json",
                    headers=self._headers(),
                )
        note.refresh_from_db()
        self.assertEqual(note.appraisal_status, "reviewed")
        self.assertEqual(note.last_review_decision, "reviewed")
        self.assertEqual(note.review_comments, "Immutable review.")
        self.assertEqual(note.prerequisite_provenance, "legacy_unverified")
        self.assertEqual(note.eligibility_snapshot_json, {})
        self.assertEqual(note.loan_limit_snapshot_json, {})
        self.assertEqual(
            list(history_model.objects.filter(loan_appraisal_note=note).values()),
            preserved_history,
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="appraisal.prerequisites_revalidated"
            ).count(),
            evidence_count,
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

    def test_same_uuid_prerequisite_replacement_cannot_change_frozen_appraisal(self):
        endpoint = f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/"
        created = self.client.post(
            endpoint,
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]

        self.eligibility.overall_result = EligibilityAssessment.OVERALL_INELIGIBLE
        self.eligibility.default_check = "default_found"
        self.eligibility.assessed_at = timezone.now()
        self.eligibility.save(
            update_fields=("overall_result", "default_check", "assessed_at")
        )
        self.loan_limit.final_eligible_loan_amount = "700000.00"
        self.loan_limit.amount_within_limit_flag = True
        self.loan_limit.exception_required_flag = False
        self.loan_limit.calculated_at = timezone.now()
        self.loan_limit.save(
            update_fields=(
                "final_eligible_loan_amount",
                "amount_within_limit_flag",
                "exception_required_flag",
                "calculated_at",
            )
        )

        read = self.client.get(endpoint, headers=self._headers()).json()["data"]
        self.assertEqual(read["eligibility_snapshot"], created["eligibility_snapshot"])
        self.assertEqual(read["loan_limit_snapshot"], created["loan_limit_snapshot"])
        self.assertEqual(read["eligibility_assessment_id"], str(self.eligibility.pk))
        self.assertEqual(read["loan_limit_assessment_id"], str(self.loan_limit.pk))

        update = self.client.patch(
            endpoint,
            data={"recommended_amount": "600000.00"},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(update.status_code, 400)
        self.assertIn("recommended_amount", update.json()["error"]["field_errors"])
        self.assertEqual(
            apps.get_model("credit", "LoanAppraisalNote").objects.get().recommended_amount,
            400000,
        )

    def test_update_revalidation_and_submit_failures_roll_back_all_writes(self):
        created = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        ).json()["data"]
        note_model = apps.get_model("credit", "LoanAppraisalNote")
        note = note_model.objects.get()

        with patch.object(AuditLog.objects, "create", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaisesMessage(RuntimeError, "audit unavailable"):
                self.client.patch(
                    f"/api/v1/loan-applications/{self.application.pk}/appraisal-note/",
                    data={"recommendation": "conditions"},
                    content_type="application/json",
                    headers=self._headers(),
                )
        note.refresh_from_db()
        self.assertEqual(note.recommendation, "approve")

        note.prerequisite_provenance = "legacy_unverified"
        note.save(update_fields=["prerequisite_provenance"])
        with patch.object(AuditLog.objects, "create", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaisesMessage(RuntimeError, "audit unavailable"):
                self.client.post(
                    f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/revalidate-prerequisites/",
                    data={},
                    content_type="application/json",
                    headers=self._headers(),
                )
        note.refresh_from_db()
        self.assertEqual(note.prerequisite_provenance, "legacy_unverified")

        note.prerequisite_provenance = "verified"
        note.save(update_fields=["prerequisite_provenance"])
        with patch.object(AuditLog.objects, "create", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaisesMessage(RuntimeError, "audit unavailable"):
                self.client.post(
                    f"/api/v1/appraisal-notes/{created['loan_appraisal_note_id']}/submit-for-review/",
                    data={"remarks": "Ready for review."},
                    content_type="application/json",
                    headers=self._headers(),
                )
        note.refresh_from_db()
        self.assertEqual(note.appraisal_status, "draft")
        self.assertEqual(note.submission_remarks, "")

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
            "repayment_capacity_notes": (
                "Seasonal crop proceeds cover the proposed repayment schedule."
            ),
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

    def _credit_manager_headers(self):
        reviewer = self._user(
            "credit.manager@sfpcl.example",
            self._permission("credit.appraisal.review", "Review appraisal"),
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": reviewer.email, "password": "AppraisalPass123!"},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200)
        return reviewer, {
            "Authorization": f"Bearer {login.json()['data']['access_token']}"
        }

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


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative appraisal concurrency proof requires PostgreSQL integration settings.",
)
class AppraisalConcurrencyTests(TransactionTestCase):
    setUp = AppraisalApiTests.setUp
    _payload = AppraisalApiTests._payload
    _permission = staticmethod(AppraisalApiTests._permission)
    _user = staticmethod(AppraisalApiTests._user)

    def test_rejected_review_serializes_before_stale_draft_patch_without_deadlock(self):
        from sfpcl_credit.credit.models import (
            AppraisalReviewDecision,
            LoanAppraisalNote,
        )
        from sfpcl_credit.credit.modules.appraisal_workflow import (
            AppraisalWorkflow,
            CreditModuleInvalidStateError,
        )

        workflow = AppraisalWorkflow()
        created = workflow.create_or_update(
            actor=self.actor,
            application_id=self.application.pk,
            payload=self._payload(),
            request_meta={"request_id": "concurrency-appraisal-created"},
        ).snapshot
        workflow.submit_for_review(
            actor=self.actor,
            appraisal_id=created["loan_appraisal_note_id"],
            payload={"remarks": "Ready for a competing terminal review."},
            request_meta={"request_id": "concurrency-appraisal-submitted"},
        )
        reviewer = self._user(
            "credit.manager@sfpcl.example",
            self._permission("credit.appraisal.review", "Review appraisal"),
        )
        review_locked = Event()
        patch_attempting = Event()
        patch_payload_entered = Event()
        release_review = Event()
        ordering = []
        ordering_lock = Lock()

        def record(step):
            with ordering_lock:
                ordering.append(step)

        class CoordinatedReviewPayload(dict):
            blocked = False

            def get(self, key, default=None):
                if key == "rejection_reason_category" and not self.blocked:
                    self.blocked = True
                    record("review_locked_application_and_appraisal")
                    review_locked.set()
                    if not release_review.wait(timeout=10):
                        raise AssertionError("Timed out waiting to release rejected review.")
                    record("review_released")
                return super().get(key, default)

        class CoordinatedPatchPayload(Mapping):
            values = {"recommendation": "conditions"}

            def __contains__(self, key):
                return key in self.values

            def __getitem__(self, key):
                return self.values[key]

            def __iter__(self):
                record("patch_locked_application")
                patch_payload_entered.set()
                return iter(self.values)

            def __len__(self):
                return len(self.values)

        rejection_payload = CoordinatedReviewPayload(
            {
                "decision": "rejected",
                "review_comments": "Independent terminal review completed.",
                "rejection_reason_category": "eligibility",
                "detailed_reason": "The appraisal does not meet credit criteria.",
                "reapply_allowed_flag": True,
                "communication_mode": "email",
            }
        )

        def reject():
            close_old_connections()
            try:
                thread_reviewer = User.objects.get(user_id=reviewer.pk)
                return AppraisalWorkflow().review(
                    actor=thread_reviewer,
                    appraisal_id=created["loan_appraisal_note_id"],
                    decision="rejected",
                    comments=rejection_payload["review_comments"],
                    payload_fields=rejection_payload,
                    request_meta={"request_id": "concurrency-rejection-winner"},
                ).snapshot
            finally:
                connections["default"].close()

        def stale_patch():
            close_old_connections()
            try:
                thread_actor = User.objects.get(user_id=self.actor.pk)
                record("patch_attempting_application_lock")
                patch_attempting.set()
                return AppraisalWorkflow().create_or_update(
                    actor=thread_actor,
                    application_id=self.application.pk,
                    payload=CoordinatedPatchPayload(),
                    partial=True,
                    request_meta={"request_id": "concurrency-stale-patch-loser"},
                ).snapshot
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            review_future = executor.submit(reject)
            review_locked.wait(timeout=10)
            patch_future = executor.submit(stale_patch)
            patch_attempting.wait(timeout=10)
            try:
                self.assertFalse(
                    patch_payload_entered.wait(timeout=0.5),
                    "Stale PATCH reached its payload while rejected review held the locks.",
                )
            finally:
                release_review.set()
            rejected = review_future.result(timeout=10)
            with self.assertRaises(CreditModuleInvalidStateError):
                patch_future.result(timeout=10)

        note = LoanAppraisalNote.objects.get(pk=created["loan_appraisal_note_id"])
        history = AppraisalReviewDecision.objects.get(loan_appraisal_note=note)
        rejection_note_model = apps.get_model("applications", "RejectionNote")
        self.assertEqual(note.appraisal_status, LoanAppraisalNote.STATUS_REJECTED)
        self.assertEqual(note.recommendation, "approve")
        self.assertEqual(rejected["appraisal_status"], "rejected")
        self.assertEqual(history.history_provenance, "native")
        self.assertEqual(history.from_state, "review_pending")
        self.assertEqual(history.to_state, "rejected")
        self.assertEqual(rejection_note_model.objects.count(), 1)
        appraisal_audit = AuditLog.objects.get(action="appraisal.rejected")
        self.assertEqual(
            appraisal_audit.new_value_json["appraisal_review_decision_id"],
            str(history.pk),
        )
        self.assertEqual(
            appraisal_audit.new_value_json["rejection_note_id"],
            str(rejection_note_model.objects.get().pk),
        )
        appraisal_event = WorkflowEvent.objects.get(
            workflow_name="appraisal_note",
            entity_id=note.pk,
            from_state="review_pending",
            to_state="rejected",
        )
        self.assertIn(str(history.pk), appraisal_event.trigger_reason)
        self.assertFalse(AuditLog.objects.filter(action="appraisal.updated").exists())
        self.assertEqual(
            ordering,
            [
                "review_locked_application_and_appraisal",
                "patch_attempting_application_lock",
                "review_released",
                "patch_locked_application",
            ],
        )
        print(f"database_backend={connection.vendor} ordering={' -> '.join(ordering)}")

    def test_duplicate_terminal_reviews_append_one_complete_decision_and_no_loser_evidence(self):
        from sfpcl_credit.credit.models import (
            AppraisalReviewDecision,
            LoanAppraisalNote,
        )
        from sfpcl_credit.credit.modules.appraisal_workflow import (
            AppraisalWorkflow,
            CreditModuleInvalidStateError,
        )

        workflow = AppraisalWorkflow()
        created = workflow.create_or_update(
            actor=self.actor,
            application_id=self.application.pk,
            payload=self._payload(),
            request_meta={"request_id": "duplicate-review-created"},
        ).snapshot
        workflow.submit_for_review(
            actor=self.actor,
            appraisal_id=created["loan_appraisal_note_id"],
            payload={"remarks": "Ready for an initial return."},
            request_meta={"request_id": "duplicate-review-first-submit"},
        )
        reviewer = self._user(
            "credit.manager@sfpcl.example",
            self._permission("credit.appraisal.review", "Review appraisal"),
        )
        workflow.review(
            actor=reviewer,
            appraisal_id=created["loan_appraisal_note_id"],
            decision="returned",
            comments="Clarify the repayment capacity evidence.",
            payload_fields={
                "decision": "returned",
                "review_comments": "Clarify the repayment capacity evidence.",
            },
            request_meta={"request_id": "duplicate-review-returned"},
        )
        workflow.create_or_update(
            actor=self.actor,
            application_id=self.application.pk,
            payload={"repayment_capacity_notes": "Clarified repayment evidence."},
            partial=True,
            request_meta={"request_id": "duplicate-review-revised"},
        )
        workflow.submit_for_review(
            actor=self.actor,
            appraisal_id=created["loan_appraisal_note_id"],
            payload={"remarks": "Clarification added for terminal review."},
            request_meta={"request_id": "duplicate-review-second-submit"},
        )
        history_fields = (
            "appraisal_review_decision_id",
            "decision",
            "review_comments",
            "reviewer_user_id",
            "decided_at",
            "from_state",
            "to_state",
            "history_provenance",
        )
        pre_race_history = list(
            AppraisalReviewDecision.objects.order_by(
                "decided_at", "appraisal_review_decision_id"
            ).values(*history_fields)
        )
        winner_locked = Event()
        loser_attempting = Event()
        loser_completed = Event()
        release_winner = Event()
        ordering = []
        ordering_lock = Lock()

        def record(step):
            with ordering_lock:
                ordering.append(step)

        class CoordinatedRejectionPayload(dict):
            blocked = False

            def get(self, key, default=None):
                if key == "rejection_reason_category" and not self.blocked:
                    self.blocked = True
                    record("winner_locked_application_appraisal_and_history")
                    winner_locked.set()
                    if not release_winner.wait(timeout=10):
                        raise AssertionError("Timed out waiting to release terminal review.")
                    record("winner_released")
                return super().get(key, default)

        rejection_payload = CoordinatedRejectionPayload(
            {
                "decision": "rejected",
                "review_comments": "Terminal rejection after independent review.",
                "rejection_reason_category": "limit_issue",
                "detailed_reason": "The clarified repayment evidence remains insufficient.",
                "reapply_allowed_flag": True,
                "communication_mode": "email",
            }
        )

        def reject():
            close_old_connections()
            try:
                thread_reviewer = User.objects.get(user_id=reviewer.pk)
                return AppraisalWorkflow().review(
                    actor=thread_reviewer,
                    appraisal_id=created["loan_appraisal_note_id"],
                    decision="rejected",
                    comments=rejection_payload["review_comments"],
                    payload_fields=rejection_payload,
                    request_meta={"request_id": "duplicate-review-rejection-winner"},
                ).snapshot
            finally:
                connections["default"].close()

        def duplicate_review():
            close_old_connections()
            try:
                thread_reviewer = User.objects.get(user_id=reviewer.pk)
                record("loser_attempting_application_lock")
                loser_attempting.set()
                return AppraisalWorkflow().review(
                    actor=thread_reviewer,
                    appraisal_id=created["loan_appraisal_note_id"],
                    decision="reviewed",
                    comments="This competing decision must not persist.",
                    payload_fields={
                        "decision": "reviewed",
                        "review_comments": "This competing decision must not persist.",
                    },
                    request_meta={"request_id": "duplicate-review-loser"},
                ).snapshot
            finally:
                loser_completed.set()
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            winner_future = executor.submit(reject)
            winner_locked.wait(timeout=10)
            loser_future = executor.submit(duplicate_review)
            loser_attempting.wait(timeout=10)
            try:
                self.assertFalse(
                    loser_completed.wait(timeout=0.5),
                    "Competing review completed before the winning transaction committed.",
                )
            finally:
                release_winner.set()
            rejected = winner_future.result(timeout=10)
            with self.assertRaises(CreditModuleInvalidStateError):
                loser_future.result(timeout=10)

        note = LoanAppraisalNote.objects.get(pk=created["loan_appraisal_note_id"])
        final_history = list(
            AppraisalReviewDecision.objects.order_by(
                "decided_at", "appraisal_review_decision_id"
            ).values(*history_fields)
        )
        winning_history = final_history[-1]
        rejection_note_model = apps.get_model("applications", "RejectionNote")
        self.assertEqual(final_history[:-1], pre_race_history)
        self.assertEqual(len(final_history), len(pre_race_history) + 1)
        self.assertEqual(note.appraisal_status, LoanAppraisalNote.STATUS_REJECTED)
        self.assertEqual(rejected["appraisal_status"], "rejected")
        self.assertEqual(winning_history["decision"], "rejected")
        self.assertEqual(winning_history["from_state"], "review_pending")
        self.assertEqual(winning_history["to_state"], "rejected")
        self.assertEqual(winning_history["history_provenance"], "native")
        self.assertEqual(rejection_note_model.objects.count(), 1)
        winning_audit = AuditLog.objects.get(
            action="appraisal.rejected",
            new_value_json__request_id="duplicate-review-rejection-winner",
        )
        self.assertEqual(
            winning_audit.new_value_json["appraisal_review_decision_id"],
            str(winning_history["appraisal_review_decision_id"]),
        )
        winning_event = WorkflowEvent.objects.get(
            workflow_name="appraisal_note",
            entity_id=note.pk,
            from_state="review_pending",
            to_state="rejected",
        )
        self.assertEqual(
            winning_event.trigger_reason,
            f"Appraisal review decision {winning_history['appraisal_review_decision_id']} "
            "recorded as rejected.",
        )
        self.assertEqual(winning_event.from_state, "review_pending")
        self.assertEqual(winning_event.to_state, "rejected")
        self.assertFalse(AuditLog.objects.filter(action="appraisal.reviewed").exists())
        self.assertFalse(
            WorkflowEvent.objects.filter(
                workflow_name="appraisal_note",
                to_state="reviewed",
            ).exists()
        )
        self.assertEqual(
            ordering,
            [
                "winner_locked_application_appraisal_and_history",
                "loser_attempting_application_lock",
                "winner_released",
            ],
        )
        print(f"database_backend={connection.vendor} ordering={' -> '.join(ordering)}")


class AppraisalSnapshotMigrationTests(TransactionTestCase):
    migrate_from = [("credit", "0002_riskassessment_loanappraisalnote")]
    migrate_to = [("credit", "0003_appraisal_prerequisite_snapshots")]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps
        self.ids = self._create_legacy_rows(old_apps)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_migration_copies_only_chronologically_proven_legacy_projections(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        migrated_apps = self.executor.loader.project_state(self.migrate_to).apps
        Appraisal = migrated_apps.get_model("credit", "LoanAppraisalNote")

        safe = Appraisal.objects.get(pk=self.ids["safe_appraisal_id"])
        self.assertEqual(safe.prerequisite_provenance, "verified")
        self.assertEqual(
            safe.eligibility_snapshot_json["eligibility_assessment_id"],
            str(self.ids["safe_eligibility_id"]),
        )
        self.assertEqual(
            safe.loan_limit_snapshot_json["final_eligible_loan_amount"],
            "20000.00",
        )
        self.assertEqual(
            safe.eligibility_snapshot_json["assessed_at"],
            timezone.localtime(self.ids["base_time"]).isoformat(),
        )
        self.assertEqual(
            safe.loan_limit_snapshot_json["calculated_at"],
            self.ids["base_time"].isoformat().replace("+00:00", "Z"),
        )

        ambiguous = Appraisal.objects.get(pk=self.ids["ambiguous_appraisal_id"])
        self.assertEqual(ambiguous.prerequisite_provenance, "legacy_unverified")
        self.assertEqual(ambiguous.eligibility_snapshot_json, {})
        self.assertEqual(ambiguous.loan_limit_snapshot_json, {})

    def _create_legacy_rows(self, old_apps):
        Role = old_apps.get_model("identity", "Role")
        User = old_apps.get_model("identity", "User")
        Member = old_apps.get_model("members", "Member")
        Application = old_apps.get_model("applications", "LoanApplication")
        Eligibility = old_apps.get_model("credit", "EligibilityAssessment")
        LoanLimit = old_apps.get_model("credit", "LoanLimitAssessment")
        Risk = old_apps.get_model("credit", "RiskAssessment")
        Appraisal = old_apps.get_model("credit", "LoanAppraisalNote")
        AuditLog = old_apps.get_model("identity", "AuditLog")

        role = Role.objects.create(role_code="legacy_appraisal", role_name="Legacy Appraisal")
        user = User.objects.create(
            full_name="Synthetic Migration User",
            email="legacy-appraisal@sfpcl.example",
            primary_role=role,
            password_hash="not-a-real-password",
        )
        base_time = timezone.now() - timedelta(days=3)
        identifiers = {"base_time": base_time}
        for label, member_suffix in (("safe", "SAFE"), ("ambiguous", "AMBIG")):
            member = Member.objects.create(
                member_number=f"MEM-APP-MIG-{member_suffix}",
                member_type="individual_farmer",
                legal_name=f"Synthetic {label} member",
                display_name=f"Synthetic {label} member",
                folio_number=f"FOL-APP-MIG-{member_suffix}",
                membership_status="active",
                kyc_status="verified",
                default_status="no_default",
            )
            application = Application.objects.create(
                member=member,
                borrower_type="individual_farmer",
                received_by_user=user,
                created_by_user=user,
            )
            eligibility = Eligibility.objects.create(
                loan_application=application,
                member_active_check="pass",
                default_check="no_default",
                document_check="complete",
                terms_acceptance_check="accepted",
                purpose_check="agriculture_aligned",
                nominee_check="valid",
                overall_result="eligible",
                assessment_notes="Synthetic eligibility proof.",
                assessed_by_user=user,
                assessed_at=base_time,
            )
            loan_limit = LoanLimit.objects.create(
                loan_application=application,
                member=member,
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
                calculation_rule_version="legacy-proof-v1",
                calculated_by_user=user,
                calculated_at=base_time,
            )
            risk = Risk.objects.create(
                loan_application=application,
                market_risk_rating="low",
                operational_risk_rating="low",
                borrower_risk_rating="low",
                overall_risk_rating="low",
                assessed_by_user=user,
                assessed_at=base_time,
            )
            appraisal = Appraisal.objects.create(
                loan_application=application,
                prepared_by_user=user,
                prepared_at=base_time + timedelta(hours=1),
                tat_due_at=base_time + timedelta(days=2),
                tat_status="within_tat",
                eligibility_assessment_id_snapshot=eligibility.pk,
                loan_limit_assessment_id_snapshot=loan_limit.pk,
                borrower_summary="Synthetic borrower summary.",
                eligibility_summary="Synthetic eligibility summary.",
                loan_limit_summary="Synthetic limit summary.",
                recommended_amount=Decimal("20000.00"),
                recommended_security_summary="Synthetic security.",
                risk_assessment=risk,
                recommendation="approve",
            )
            identifiers[f"{label}_appraisal_id"] = appraisal.pk
            identifiers[f"{label}_eligibility_id"] = eligibility.pk
            if label == "ambiguous":
                AuditLog.objects.create(
                    actor_user=user,
                    action="loan_limit.calculated",
                    entity_type="loan_limit_assessment",
                    entity_id=loan_limit.pk,
                    created_at=base_time + timedelta(hours=2),
                )
        return identifiers


class AppraisalHistoryHardeningMigrationTests(TransactionTestCase):
    migrate_from = [("credit", "0004_appraisal_review_facts")]
    migrate_to = [("credit", "0005_appraisalreviewdecision")]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps
        self.ids = self._create_hardening_fixtures(old_apps)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_forward_repair_requires_positive_exact_chronology_and_backfills_latest_only(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        migrated_apps = self.executor.loader.project_state(self.migrate_to).apps
        Appraisal = migrated_apps.get_model("credit", "LoanAppraisalNote")
        Decision = migrated_apps.get_model("credit", "AppraisalReviewDecision")

        expected = {
            "positive": "verified",
            "missing_eligibility_audit": "legacy_unverified",
            "missing_both_audits": "legacy_unverified",
            "later_eligibility_rerun": "legacy_unverified",
            "source_after_preparation": "legacy_unverified",
            "mismatched_application": "legacy_unverified",
            "existing_legacy_unverified": "legacy_unverified",
        }
        for label, provenance in expected.items():
            with self.subTest(label=label):
                appraisal = Appraisal.objects.get(pk=self.ids[label])
                self.assertEqual(appraisal.prerequisite_provenance, provenance)
                self.assertEqual(appraisal.eligibility_snapshot_json["untrusted"], label)
                self.assertEqual(appraisal.loan_limit_snapshot_json["untrusted"], label)

        decisions = list(Decision.objects.all())
        self.assertEqual(len(decisions), 1)
        decision = decisions[0]
        self.assertEqual(decision.loan_appraisal_note_id, self.ids["positive"])
        self.assertEqual(decision.decision, "reviewed")
        self.assertEqual(decision.review_comments, "Legacy latest review only.")
        self.assertEqual(decision.from_state, "review_pending")
        self.assertEqual(decision.to_state, "reviewed")
        self.assertEqual(decision.history_provenance, "legacy_latest_only")

    def test_reverse_drops_history_without_relabeling_unproven_provenance(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        migrated_apps = self.executor.loader.project_state(self.migrate_to).apps
        Appraisal = migrated_apps.get_model("credit", "LoanAppraisalNote")
        self.assertEqual(
            Appraisal.objects.get(pk=self.ids["missing_both_audits"]).prerequisite_provenance,
            "legacy_unverified",
        )

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        reversed_apps = self.executor.loader.project_state(self.migrate_from).apps
        ReversedAppraisal = reversed_apps.get_model("credit", "LoanAppraisalNote")
        self.assertEqual(
            ReversedAppraisal.objects.get(
                pk=self.ids["missing_both_audits"]
            ).prerequisite_provenance,
            "legacy_unverified",
        )
        with self.assertRaises(LookupError):
            reversed_apps.get_model("credit", "AppraisalReviewDecision")

    def _create_hardening_fixtures(self, old_apps):
        Role = old_apps.get_model("identity", "Role")
        UserModel = old_apps.get_model("identity", "User")
        MemberModel = old_apps.get_model("members", "Member")
        Application = old_apps.get_model("applications", "LoanApplication")
        Eligibility = old_apps.get_model("credit", "EligibilityAssessment")
        LoanLimit = old_apps.get_model("credit", "LoanLimitAssessment")
        Risk = old_apps.get_model("credit", "RiskAssessment")
        Appraisal = old_apps.get_model("credit", "LoanAppraisalNote")
        Audit = old_apps.get_model("identity", "AuditLog")

        role = Role.objects.create(role_code="migration_reviewer", role_name="Migration Reviewer")
        user = UserModel.objects.create(
            full_name="Synthetic Migration Reviewer",
            email="migration-reviewer@sfpcl.example",
            primary_role=role,
            password_hash="not-a-real-password",
        )
        base_time = timezone.now() - timedelta(days=5)
        prepared_at = base_time + timedelta(hours=2)
        identifiers = {}

        def create_case(
            label,
            *,
            eligibility_audit=True,
            loan_limit_audit=True,
            later_eligibility_audit=False,
            source_after=False,
            mismatch=False,
            provenance="verified",
            latest_review=False,
        ):
            suffix = label.upper().replace("_", "-")[:24]
            member = MemberModel.objects.create(
                member_number=f"MEM-HARD-{suffix}",
                member_type="individual_farmer",
                legal_name=f"Synthetic {label} member",
                display_name=f"Synthetic {label} member",
                folio_number=f"FOL-HARD-{suffix}",
                membership_status="active",
                kyc_status="verified",
                default_status="no_default",
            )
            application = Application.objects.create(
                member=member,
                borrower_type="individual_farmer",
                received_by_user=user,
                created_by_user=user,
            )
            source_application = application
            if mismatch:
                source_member = MemberModel.objects.create(
                    member_number=f"MEM-HARD-{suffix}-SRC",
                    member_type="individual_farmer",
                    legal_name=f"Synthetic {label} source member",
                    display_name=f"Synthetic {label} source member",
                    folio_number=f"FOL-HARD-{suffix}-SRC",
                    membership_status="active",
                    kyc_status="verified",
                    default_status="no_default",
                )
                source_application = Application.objects.create(
                    member=source_member,
                    borrower_type="individual_farmer",
                    received_by_user=user,
                    created_by_user=user,
                )
            source_time = prepared_at + timedelta(minutes=1) if source_after else base_time
            eligibility = Eligibility.objects.create(
                loan_application=source_application,
                member_active_check="pass",
                default_check="no_default",
                document_check="complete",
                terms_acceptance_check="accepted",
                purpose_check="agriculture_aligned",
                nominee_check="valid",
                overall_result="eligible",
                assessment_notes="Synthetic proof.",
                assessed_by_user=user,
                assessed_at=source_time,
            )
            loan_limit = LoanLimit.objects.create(
                loan_application=source_application,
                member=source_application.member,
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
                calculation_rule_version="legacy-proof-v1",
                calculated_by_user=user,
                calculated_at=source_time,
            )
            risk = Risk.objects.create(
                loan_application=application,
                market_risk_rating="low",
                operational_risk_rating="low",
                borrower_risk_rating="low",
                overall_risk_rating="low",
                assessed_by_user=user,
                assessed_at=base_time,
            )
            appraisal = Appraisal.objects.create(
                loan_application=application,
                prepared_by_user=user,
                reviewed_by_user=user if latest_review else None,
                prepared_at=prepared_at,
                reviewed_at=prepared_at + timedelta(minutes=30) if latest_review else None,
                review_comments="Legacy latest review only." if latest_review else "",
                last_review_decision="reviewed" if latest_review else "",
                tat_due_at=prepared_at + timedelta(days=2),
                tat_status="within_tat",
                eligibility_assessment_id_snapshot=eligibility.pk,
                loan_limit_assessment_id_snapshot=loan_limit.pk,
                eligibility_snapshot_json={"untrusted": label},
                loan_limit_snapshot_json={"untrusted": label},
                prerequisite_provenance=provenance,
                borrower_summary="Synthetic borrower summary.",
                eligibility_summary="Synthetic eligibility summary.",
                loan_limit_summary="Synthetic limit summary.",
                recommended_amount=Decimal("20000.00"),
                recommended_security_summary="Synthetic security.",
                repayment_capacity_notes="Synthetic repayment capacity.",
                risk_assessment=risk,
                recommendation="approve",
                appraisal_status="reviewed" if latest_review else "draft",
            )
            audit_time = base_time + timedelta(hours=1)
            if eligibility_audit:
                Audit.objects.create(
                    actor_user=user,
                    action="eligibility.assessed",
                    entity_type="eligibility_assessment",
                    entity_id=eligibility.pk,
                    created_at=audit_time,
                )
            if loan_limit_audit:
                Audit.objects.create(
                    actor_user=user,
                    action="loan_limit.calculated",
                    entity_type="loan_limit_assessment",
                    entity_id=loan_limit.pk,
                    created_at=audit_time,
                )
            if later_eligibility_audit:
                Audit.objects.create(
                    actor_user=user,
                    action="eligibility.assessed",
                    entity_type="eligibility_assessment",
                    entity_id=eligibility.pk,
                    created_at=prepared_at + timedelta(hours=1),
                )
            identifiers[label] = appraisal.pk

        create_case("positive", latest_review=True)
        create_case("missing_eligibility_audit", eligibility_audit=False)
        create_case("missing_both_audits", eligibility_audit=False, loan_limit_audit=False)
        create_case("later_eligibility_rerun", later_eligibility_audit=True)
        create_case("source_after_preparation", source_after=True)
        create_case("mismatched_application", mismatch=True)
        create_case("existing_legacy_unverified", provenance="legacy_unverified")
        return identifiers


class LegacyAppraisalRemediationMigrationTests(TransactionTestCase):
    migrate_from = [("credit", "0005_appraisalreviewdecision")]
    migrate_to = [("credit", "0006_legacy_appraisal_history_remediation")]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        self.old_apps = self.executor.loader.project_state(self.migrate_from).apps
        self.user = self._create_actor(self.old_apps)
        self.ids = {
            "returned_resubmitted": self._create_case(
                "returned-resubmitted",
                decision="returned",
                appraisal_status="review_pending",
                comments="Correct the repayment evidence.",
            ),
            "reviewed_submitted": self._create_case(
                "reviewed-submitted",
                decision="reviewed",
                appraisal_status="submitted_to_sanction_committee",
            ),
            "already_backfilled": self._create_case(
                "already-backfilled",
                decision="returned",
                appraisal_status="review_pending",
                existing_latest=True,
            ),
            "incomplete": self._create_case(
                "incomplete",
                decision="returned",
                appraisal_status="review_pending",
                comments="",
            ),
            "multiple_cycles": self._create_case(
                "multiple-cycles",
                decision="returned",
                appraisal_status="review_pending",
                existing_earlier=True,
            ),
            "verified_unrelated": self._create_case(
                "verified-unrelated",
                decision="returned",
                appraisal_status="review_pending",
                provenance="verified",
            ),
        }

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_forward_backfills_returned_projection_after_resubmission(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        migrated_apps = self.executor.loader.project_state(self.migrate_to).apps
        Decision = migrated_apps.get_model("credit", "AppraisalReviewDecision")

        decision = Decision.objects.get(
            loan_appraisal_note_id=self.ids["returned_resubmitted"]
        )
        self.assertEqual(decision.decision, "returned")
        self.assertEqual(decision.review_comments, "Correct the repayment evidence.")
        self.assertEqual(decision.from_state, "review_pending")
        self.assertEqual(decision.to_state, "draft")
        self.assertEqual(decision.history_provenance, "legacy_latest_only")

    def test_forward_is_selective_preserves_cycles_and_is_idempotent(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        migrated_apps = self.executor.loader.project_state(self.migrate_to).apps
        Decision = migrated_apps.get_model("credit", "AppraisalReviewDecision")

        reviewed = Decision.objects.get(
            loan_appraisal_note_id=self.ids["reviewed_submitted"]
        )
        self.assertEqual(reviewed.decision, "reviewed")
        self.assertEqual(reviewed.to_state, "reviewed")
        self.assertEqual(reviewed.history_provenance, "legacy_latest_only")
        self.assertEqual(
            Decision.objects.filter(
                loan_appraisal_note_id=self.ids["already_backfilled"]
            ).count(),
            1,
        )
        self.assertFalse(
            Decision.objects.filter(
                loan_appraisal_note_id=self.ids["incomplete"]
            ).exists()
        )
        multiple = Decision.objects.filter(
            loan_appraisal_note_id=self.ids["multiple_cycles"]
        ).order_by("decided_at")
        self.assertEqual(multiple.count(), 2)
        self.assertEqual(
            list(multiple.values_list("history_provenance", flat=True)),
            ["native", "legacy_latest_only"],
        )
        self.assertFalse(
            Decision.objects.filter(
                loan_appraisal_note_id=self.ids["verified_unrelated"]
            ).exists()
        )

        counts_before = {
            appraisal_id: Decision.objects.filter(
                loan_appraisal_note_id=appraisal_id
            ).count()
            for appraisal_id in self.ids.values()
        }
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        rerun_apps = self.executor.loader.project_state(self.migrate_to).apps
        RerunDecision = rerun_apps.get_model("credit", "AppraisalReviewDecision")
        self.assertEqual(
            {
                appraisal_id: RerunDecision.objects.filter(
                    loan_appraisal_note_id=appraisal_id
                ).count()
                for appraisal_id in self.ids.values()
            },
            counts_before,
        )

    def _create_actor(self, old_apps):
        Role = old_apps.get_model("identity", "Role")
        UserModel = old_apps.get_model("identity", "User")
        role = Role.objects.create(
            role_code="legacy_remediation_reviewer",
            role_name="Legacy Remediation Reviewer",
        )
        return UserModel.objects.create(
            full_name="Synthetic Legacy Reviewer",
            email="legacy-remediation@sfpcl.example",
            primary_role=role,
            password_hash="not-a-real-password",
        )

    def _create_case(
        self,
        label,
        *,
        decision,
        appraisal_status,
        comments="Legacy latest decision.",
        provenance="legacy_unverified",
        existing_latest=False,
        existing_earlier=False,
    ):
        old_apps = self.old_apps
        MemberModel = old_apps.get_model("members", "Member")
        Application = old_apps.get_model("applications", "LoanApplication")
        Risk = old_apps.get_model("credit", "RiskAssessment")
        Appraisal = old_apps.get_model("credit", "LoanAppraisalNote")
        Decision = old_apps.get_model("credit", "AppraisalReviewDecision")

        suffix = label.upper()
        member = MemberModel.objects.create(
            member_number=f"MEM-LEGACY-{suffix}",
            member_type="individual_farmer",
            legal_name=f"Synthetic {label} Member",
            display_name=f"Synthetic {label} Member",
            folio_number=f"FOL-LEGACY-{suffix}",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        application = Application.objects.create(
            member=member,
            borrower_type="individual_farmer",
            received_by_user=self.user,
            created_by_user=self.user,
        )
        decided_at = timezone.now() - timedelta(days=1)
        risk = Risk.objects.create(
            loan_application=application,
            market_risk_rating="low",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            assessed_by_user=self.user,
            assessed_at=decided_at,
        )
        appraisal = Appraisal.objects.create(
            loan_application=application,
            prepared_by_user=self.user,
            reviewed_by_user=self.user,
            reviewed_at=decided_at,
            review_comments=comments,
            last_review_decision=decision,
            tat_due_at=decided_at + timedelta(days=2),
            tat_status="within_tat",
            eligibility_assessment_id_snapshot=uuid4(),
            loan_limit_assessment_id_snapshot=uuid4(),
            eligibility_snapshot_json={},
            loan_limit_snapshot_json={},
            prerequisite_provenance=provenance,
            borrower_summary="Synthetic borrower summary.",
            eligibility_summary="Synthetic eligibility summary.",
            loan_limit_summary="Synthetic limit summary.",
            recommended_amount=Decimal("20000.00"),
            recommended_security_summary="Synthetic security.",
            repayment_capacity_notes="Synthetic repayment capacity.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=appraisal_status,
        )
        destination = {"returned": "draft", "reviewed": "reviewed", "rejected": "rejected"}[
            decision
        ]
        if existing_earlier:
            Decision.objects.create(
                loan_appraisal_note=appraisal,
                decision="returned",
                review_comments="Earlier immutable cycle.",
                reviewer_user=self.user,
                decided_at=decided_at - timedelta(days=1),
                from_state="review_pending",
                to_state="draft",
                history_provenance="native",
            )
        if existing_latest:
            Decision.objects.create(
                loan_appraisal_note=appraisal,
                decision=decision,
                review_comments=comments,
                reviewer_user=self.user,
                decided_at=decided_at,
                from_state="review_pending",
                to_state=destination,
                history_provenance="legacy_latest_only",
            )
        return appraisal.pk
