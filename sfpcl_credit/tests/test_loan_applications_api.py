import json
from uuid import uuid4

from django.test import Client, TestCase
from django.apps import apps
from django.utils import timezone

from sfpcl_credit.configurations.models import LoanPolicyConfig
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, PortalAccount, Role, RolePermission, User
from sfpcl_credit.members.models import (
    BankAccount,
    CancelledCheque,
    CropPlan,
    IndividualMemberProfile,
    LandHolding,
    Member,
    Nominee,
    ProduceSupplyRecord,
    Shareholding,
)
from sfpcl_credit.tests.api_contracts import (
    assert_available_actions_shape,
    assert_error_envelope,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


APPLICATION_READ_PERMISSION = "applications.loan_application.read"
APPLICATION_CREATE_PERMISSION = "applications.loan_application.create"
APPLICATION_UPDATE_PERMISSION = "applications.loan_application.update"
APPLICATION_SUBMIT_PERMISSION = "applications.loan_application.submit"
APPLICATION_COMPLETE_CHECK_PERMISSION = "applications.loan_application.complete_check"
APPLICATION_RETURN_DEFICIENCY_PERMISSION = "applications.loan_application.return_deficiency"
APPLICATION_DEFICIENCY_RESOLVE_PERMISSION = "applications.deficiency.resolve"
APPLICATION_REJECTION_NOTE_CREATE_PERMISSION = "applications.rejection_note.create"
APPLICATION_DOCUMENT_UPLOAD_PERMISSION = "applications.document.upload"
APPLICATION_DOCUMENT_VERIFY_PERMISSION = "applications.document.verify"
ELIGIBILITY_RUN_PERMISSION = "credit.eligibility.run"
LOAN_LIMIT_CALCULATE_PERMISSION = "credit.loan_limit.calculate"


def without_detail_metadata(data):
    return {key: value for key, value in data.items() if key not in {"assigned_owner", "available_actions"}}


class LoanApplicationDraftApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.read_permission = self._permission(APPLICATION_READ_PERMISSION, "View applications")
        self.create_permission = self._permission(
            APPLICATION_CREATE_PERMISSION,
            "Create loan application",
        )
        self.update_permission = self._permission(
            APPLICATION_UPDATE_PERMISSION,
            "Update draft application",
        )
        self.submit_permission = self._permission(
            APPLICATION_SUBMIT_PERMISSION,
            "Submit loan application",
        )
        self.complete_check_permission = self._permission(
            APPLICATION_COMPLETE_CHECK_PERMISSION,
            "Mark completeness result",
        )
        self.return_deficiency_permission = self._permission(
            APPLICATION_RETURN_DEFICIENCY_PERMISSION,
            "Return application with deficiencies",
        )
        self.deficiency_resolve_permission = self._permission(
            APPLICATION_DEFICIENCY_RESOLVE_PERMISSION,
            "Resolve application deficiencies",
        )
        self.rejection_note_create_permission = self._permission(
            APPLICATION_REJECTION_NOTE_CREATE_PERMISSION,
            "Create application rejection note",
        )
        self.document_upload_permission = self._permission(
            APPLICATION_DOCUMENT_UPLOAD_PERMISSION,
            "Upload application documents",
        )
        self.document_verify_permission = self._permission(
            APPLICATION_DOCUMENT_VERIFY_PERMISSION,
            "Verify application documents",
        )
        self.eligibility_run_permission = self._permission(
            ELIGIBILITY_RUN_PERMISSION,
            "Run eligibility assessment",
        )
        self.loan_limit_calculate_permission = self._permission(
            LOAN_LIMIT_CALCULATE_PERMISSION,
            "Calculate loan limit",
        )
        self.creator = self._user(
            "applications.creator@sfpcl.example",
            "CreatorPass123!",
            self.read_permission,
            self.create_permission,
            self.update_permission,
            self.submit_permission,
            self.complete_check_permission,
            self.return_deficiency_permission,
            self.deficiency_resolve_permission,
            self.rejection_note_create_permission,
            self.document_upload_permission,
            self.document_verify_permission,
            self.eligibility_run_permission,
            self.loan_limit_calculate_permission,
        )
        self.unrelated_actor = self._user(
            "applications.unrelated@sfpcl.example",
            "UnrelatedPass123!",
            self.read_permission,
            self.update_permission,
            self.submit_permission,
            self.complete_check_permission,
            self.return_deficiency_permission,
            self.deficiency_resolve_permission,
            self.rejection_note_create_permission,
            self.document_upload_permission,
            self.eligibility_run_permission,
            self.loan_limit_calculate_permission,
        )
        self.reader = self._user(
            "applications.reader@sfpcl.example",
            "ReaderPass123!",
            self.read_permission,
        )
        self.plain = self._user("applications.plain@sfpcl.example", "PlainPass123!")
        self.member = self._member("005A", "Ramesh Patil")
        self.other_member = self._member("005A-OTHER", "Sita Farms")
        IndividualMemberProfile.objects.create(
            member=self.member, first_name="Ramesh", last_name="Patil",
            services_availed_flag=True,
        )
        for year in ("2022-23", "2023-24", "2024-25", "2025-26"):
            ProduceSupplyRecord.objects.create(
                member=self.member, financial_year=year,
                supplied_to_entity_type="sfpcl", supply_route="direct",
                evidence_reference=f"ERP-APPLICATION-{year}",
                captured_by_user=self.creator, verified_flag=True,
                verified_by_user=self.creator, verified_at=timezone.now(),
            )
        self.nominee = self._create_nominee(None)
        self.land = LandHolding.objects.create(
            member=self.member,
            document_type="7_12_extract",
            survey_number="123/4",
            village="Niphad",
            area_acres="5.00",
            document_id=uuid4(),
            verification_status="verified",
            verified_by_user=self.creator,
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
            verified_by_user=self.creator,
            verified_at=timezone.now(),
        )
        self.cheque = CancelledCheque.objects.create(
            member=self.member,
            document_id=uuid4(),
            account_number_encrypted="cheque-token-123456789012",
            account_number_hash="cheque-hash-123456789012",
            account_number_last4="9012",
            ifsc="HDFC0001234",
            branch_name="Nashik Road",
        )
        self.bank = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.member.member_id,
            account_holder_name="Ramesh Patil",
            account_number_encrypted="bank-token-123456789012",
            account_number_hash="bank-hash-123456789012",
            account_number_last4="9012",
            ifsc="HDFC0001234",
            bank_name="HDFC Bank",
            branch_name="Nashik Road",
            cancelled_cheque=self.cheque,
        )

    def test_create_and_read_draft_returns_metadata_only_response_and_audit(self):
        response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-create-loan-draft",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["meta"]["request_id"], "req-create-loan-draft")
        draft = body["data"]
        self.assertEqual(draft["application_status"], "draft")
        self.assertEqual(draft["current_stage"], "initial_loan_request")
        self.assertIsNone(draft["application_reference_number"])
        self.assertEqual(draft["member"]["member_id"], str(self.member.member_id))
        self.assertEqual(draft["member"]["display_name"], "Ramesh Patil")
        self.assertEqual(draft["required_loan_amount"], "400000.00")
        self.assertEqual(draft["requested_tenure_months"], 12)
        self.assertEqual(draft["declared_purpose"], "Crop production loan for grape cultivation")
        self.assertEqual(draft["purpose_category"], "crop_production")
        self.assertEqual(draft["land_holding"]["land_holding_id"], str(self.land.land_holding_id))
        self.assertEqual(draft["crop_plan"]["crop_plan_id"], str(self.crop.crop_plan_id))
        self.assertEqual(draft["bank_account"]["bank_account_id"], str(self.bank.bank_account_id))
        self.assertEqual(draft["bank_account"]["account_holder_name"], "Ramesh Patil")
        self.assertEqual(draft["bank_account"]["account_number"]["masked"], "********9012")
        self.assertFalse(draft["bank_account"]["account_number"]["can_view_full"])
        self.assertEqual(
            draft["cancelled_cheque"]["cancelled_cheque_id"],
            str(self.cheque.cancelled_cheque_id),
        )

        read_response = self.client.get(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(read_response.status_code, 200)
        read_body = read_response.json()
        assert_success_envelope(self, read_body)
        self.assertEqual(without_detail_metadata(read_body["data"]), draft)

        audit = AuditLog.objects.filter(action="applications.loan_application.created").get()
        self.assertEqual(audit.entity_type, "loan_application")
        self.assertEqual(str(audit.entity_id), draft["loan_application_id"])
        self.assertEqual(audit.new_value_json["member_id"], str(self.member.member_id))
        self.assertEqual(audit.new_value_json["bank_account_id"], str(self.bank.bank_account_id))
        self.assertEqual(audit.new_value_json["masked_bank_account_number"], "********9012")

        workflow_event = WorkflowEvent.objects.filter(entity_type="loan_application").get()
        self.assertEqual(str(workflow_event.entity_id), draft["loan_application_id"])
        self.assertEqual(workflow_event.workflow_name, "loan_application")
        self.assertIsNone(workflow_event.from_state)
        self.assertEqual(workflow_event.to_state, "draft")

        flattened = f"{body} {audit.new_value_json}"
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("cheque-token-123456789012", flattened)
        self.assertNotIn("cheque-hash-123456789012", flattened)
        self.assertNotIn("123456789012", flattened)
        self.assertNotIn('"holder_name"', json.dumps(body))

    def test_staff_application_detail_returns_neutral_owner_and_authorized_actions(self):
        create_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        application_id = create_response.json()["data"]["loan_application_id"]

        response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertIsNone(body["data"]["assigned_owner"])
        assert_available_actions_shape(self, body["data"]["available_actions"])
        self.assertEqual(
            body["data"]["available_actions"],
            [
                {
                    "action_code": "submit",
                    "label": "Submit Application",
                    "enabled": True,
                    "disabled_reason": None,
                    "required_permission": APPLICATION_SUBMIT_PERMISSION,
                    "required_role": None,
                }
            ],
        )


    def test_staff_create_and_detail_persist_safe_same_member_nominee_selection(self):
        response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        nominee = response.json()["data"]["nominee"]
        self.assertEqual(
            nominee,
            {
                "nominee_id": str(self.nominee.nominee_id),
                "nominee_name": "Sita Patil",
                "age_at_application": 42,
                "minor_flag": False,
                "kyc_status": "verified",
                "relationship_to_borrower": "Spouse",
                "signature_required_flag": True,
            },
        )
        self.assertNotIn("pan", nominee)
        self.assertNotIn("aadhaar", nominee)

        application_id = response.json()["data"]["loan_application_id"]
        detail = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["data"]["nominee"], nominee)
        self.assertEqual(
            str(
                apps.get_model("applications", "LoanApplication")
                .objects.get(pk=application_id)
                .nominee_id
            ),
            str(self.nominee.nominee_id),
        )

    def test_invalid_nominee_selections_create_no_application_or_success_evidence(self):
        cross_member = self._create_nominee(None, member=self.other_member)
        minor = self._create_nominee(None, minor_flag=True)
        missing_age = self._create_nominee(
            None,
            age_at_application=None,
            date_of_birth=None,
        )
        baseline = {
            "applications": apps.get_model("applications", "LoanApplication").objects.count(),
            "audits": AuditLog.objects.filter(
                action="applications.loan_application.created"
            ).count(),
            "workflows": WorkflowEvent.objects.filter(
                entity_type="loan_application"
            ).count(),
        }

        for nominee_id in (
            cross_member.nominee_id,
            minor.nominee_id,
            missing_age.nominee_id,
            uuid4(),
        ):
            with self.subTest(nominee_id=nominee_id):
                response = self.client.post(
                    "/api/v1/loan-applications/",
                    data=self._draft_payload(nominee_id=str(nominee_id)),
                    content_type="application/json",
                    headers=self._headers(
                        "applications.creator@sfpcl.example", "CreatorPass123!"
                    ),
                )
                self.assertEqual(response.status_code, 400)
                assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
                self.assertIn("nominee_id", response.json()["error"]["field_errors"])
                self.assertEqual(
                    apps.get_model("applications", "LoanApplication").objects.count(),
                    baseline["applications"],
                )
                self.assertEqual(
                    AuditLog.objects.filter(
                        action="applications.loan_application.created"
                    ).count(),
                    baseline["audits"],
                )
                self.assertEqual(
                    WorkflowEvent.objects.filter(entity_type="loan_application").count(),
                    baseline["workflows"],
                )

    def test_invalid_staff_nominee_patch_preserves_serialized_detail_and_success_evidence(self):
        cross_member = self._create_nominee(None, member=self.other_member)
        minor = self._create_nominee(None, minor_flag=True)
        missing_age = self._create_nominee(
            None,
            age_at_application=None,
            date_of_birth=None,
        )
        created = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(created.status_code, 200)
        application_id = created.json()["data"]["loan_application_id"]
        before = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        ).json()["data"]
        baseline = {
            "audits": AuditLog.objects.filter(
                action="applications.loan_application.updated",
                entity_id=application_id,
            ).count(),
            "workflows": WorkflowEvent.objects.filter(entity_id=application_id).count(),
        }

        for nominee_id in (
            cross_member.nominee_id,
            minor.nominee_id,
            missing_age.nominee_id,
            uuid4(),
        ):
            with self.subTest(nominee_id=nominee_id):
                response = self.client.patch(
                    f"/api/v1/loan-applications/{application_id}/",
                    data={"nominee_id": str(nominee_id)},
                    content_type="application/json",
                    headers=self._headers(
                        "applications.creator@sfpcl.example", "CreatorPass123!"
                    ),
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("nominee_id", response.json()["error"]["field_errors"])
                after = self.client.get(
                    f"/api/v1/loan-applications/{application_id}/",
                    headers=self._headers(
                        "applications.creator@sfpcl.example", "CreatorPass123!"
                    ),
                ).json()["data"]
                self.assertEqual(after, before)
                self.assertEqual(
                    AuditLog.objects.filter(
                        action="applications.loan_application.updated",
                        entity_id=application_id,
                    ).count(),
                    baseline["audits"],
                )
                self.assertEqual(
                    WorkflowEvent.objects.filter(entity_id=application_id).count(),
                    baseline["workflows"],
                )

    def test_draft_selects_nominee_then_submits_but_missing_selection_is_blocked(self):
        create = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(nominee_id=None),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create.status_code, 200)
        application_id = create.json()["data"]["loan_application_id"]

        blocked = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(blocked.status_code, 400)
        self.assertIn("nominee_id", blocked.json()["error"]["field_errors"])
        self.assertFalse(
            AuditLog.objects.filter(
                action="applications.loan_application.submitted",
                entity_id=application_id,
            ).exists()
        )
        self.assertFalse(
            WorkflowEvent.objects.filter(entity_id=application_id, to_state="submitted").exists()
        )

        selected = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/",
            data={"nominee_id": str(self.nominee.nominee_id)},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(selected.status_code, 200)
        self.assertEqual(
            selected.json()["data"]["nominee"]["nominee_id"],
            str(self.nominee.nominee_id),
        )
        submitted = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(submitted.json()["data"]["application_status"], "submitted")

    def test_completeness_read_and_pass_block_legacy_null_nominee_without_evidence(self):
        application_id = self._create_and_submit_application()
        application = apps.get_model("applications", "LoanApplication").objects.get(
            pk=application_id
        )
        application.nominee = None
        application.save(update_fields=["nominee"])
        self._verify_required_application_documents(application_id)

        workbench = self.client.get(
            f"/api/v1/loan-applications/{application_id}/completeness-check/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(workbench.status_code, 200)
        self.assertEqual(workbench.json()["data"]["nominee_selection_status"], "pending")
        self.assertIsNone(workbench.json()["data"]["nominee"])
        self.assertFalse(workbench.json()["data"]["can_generate_reference"])

        passed = self.client.post(
            f"/api/v1/loan-applications/{application_id}/completeness-check/pass/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(passed.status_code, 400)
        self.assertIn("nominee_id", passed.json()["error"]["field_errors"])
        self.assertFalse(
            apps.get_model("applications", "LoanRequestRegisterEntry")
            .objects.filter(loan_application_id=application_id)
            .exists()
        )

    def test_list_applications_supports_staff_pagination_filtering_search_and_ordering(self):
        first_id = self._create_and_submit_application()
        second_id = self._create_and_submit_application(
            declared_purpose="Farm pond repair",
            purpose_category="agriculture_activity",
            required_loan_amount="250000.00",
        )
        second_model = apps.get_model("applications", "LoanApplication").objects.get(
            pk=second_id
        )
        second_model.application_status = "incomplete_returned"
        second_model.completeness_status = "incomplete"
        second_model.save(update_fields=["application_status", "completeness_status"])

        response = self.client.get(
            "/api/v1/loan-applications/"
            "?search=Ramesh&application_status=incomplete_returned&ordering=-application_date&page=1&page_size=1",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["pagination"]["page"], 1)
        self.assertEqual(body["pagination"]["page_size"], 1)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(len(body["data"]), 1)
        item = body["data"][0]
        self.assertEqual(item["loan_application_id"], second_id)
        self.assertEqual(item["application_reference_number"], None)
        self.assertEqual(item["member"]["display_name"], "Ramesh Patil")
        self.assertEqual(item["member"]["folio_number"], "FOL-005A")
        self.assertEqual(item["required_loan_amount"], "250000.00")
        self.assertEqual(item["application_status"], "incomplete_returned")
        self.assertEqual(item["completeness_status"], "incomplete")
        self.assertIsNone(item["assigned_owner"])
        self.assertEqual(item["tat"]["status"], "blocked")

        flattened = json.dumps(body)
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn(first_id, flattened)

    def test_loan_request_register_list_returns_generated_reference_rows(self):
        application_id = self._create_and_submit_application()
        self._verify_required_application_documents(application_id)
        generate_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/completeness-check/pass/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(generate_response.status_code, 200)

        response = self.client.get(
            "/api/v1/loan-request-register/?search=LO00000001&page=1&page_size=20",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        row = body["data"][0]
        self.assertEqual(row["loan_application_id"], application_id)
        self.assertEqual(row["application_reference_number"], "LO00000001")
        self.assertEqual(row["borrower_name"], "Ramesh Patil")
        self.assertEqual(row["folio_number"], "FOL-005A")
        self.assertEqual(row["requested_amount"], "400000.00")
        self.assertEqual(row["register_status"], "reference_generated")

    def test_eligibility_assessment_run_and_read_persists_manual_evidence_active_member_result(self):
        self.member.individual_profile.services_availed_flag = False
        self.member.individual_profile.save(update_fields=["services_availed_flag"])
        application_id = self._reference_generated_application(terms_acceptance_flag=True)

        run_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-run-eligibility",
            },
        )

        self.assertEqual(run_response.status_code, 200)
        body = run_response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["meta"]["request_id"], "req-run-eligibility")
        assessment = body["data"]
        self.assertEqual(assessment["loan_application_id"], application_id)
        self.assertEqual(assessment["member_active_check"], "manual_evidence_required")
        self.assertEqual(assessment["default_check"], "no_default")
        self.assertEqual(assessment["document_check"], "complete")
        self.assertEqual(assessment["terms_acceptance_check"], "accepted")
        self.assertEqual(assessment["purpose_check"], "agriculture_aligned")
        self.assertEqual(assessment["nominee_check"], "valid")
        self.assertEqual(assessment["overall_result"], "pending_manual_evidence")
        self.assertIn("BR-004", assessment["assessment_notes"])
        self.assertEqual(assessment["assessed_by_user_id"], str(self.creator.user_id))
        self.assertIsNotNone(assessment["assessed_at"])

        read_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(read_response.status_code, 200)
        assert_success_envelope(self, read_response.json())
        self.assertEqual(read_response.json()["data"], assessment)

        assessment_model = apps.get_model("credit", "EligibilityAssessment")
        self.assertEqual(assessment_model.objects.filter(loan_application_id=application_id).count(), 1)
        audit = AuditLog.objects.filter(action="eligibility.assessed").get()
        self.assertEqual(audit.entity_type, "eligibility_assessment")
        self.assertEqual(str(audit.new_value_json["loan_application_id"]), application_id)
        self.assertEqual(audit.new_value_json["member_active_check"], "manual_evidence_required")
        workflow = WorkflowEvent.objects.filter(
            entity_type="loan_application",
            entity_id=application_id,
            to_state="eligibility_assessed",
        ).get()
        self.assertEqual(workflow.workflow_name, "eligibility_assessment")

    def test_eligibility_assessment_uses_existing_verified_active_member_facts_when_available(self):
        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        application_id = self._reference_generated_application(terms_acceptance_flag=True)
        application = apps.get_model("applications", "LoanApplication").objects.get(
            pk=application_id
        )
        application.nominee = None
        application.save(update_fields=["nominee"])

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["data"]["member_active_check"], "pass")
        self.assertEqual(body["data"]["default_check"], "no_default")
        self.assertEqual(body["data"]["document_check"], "complete")
        self.assertEqual(body["data"]["terms_acceptance_check"], "accepted")
        self.assertEqual(body["data"]["purpose_check"], "agriculture_aligned")
        self.assertEqual(body["data"]["nominee_check"], "pending")
        self.assertEqual(body["data"]["overall_result"], "pending_manual_evidence")
        active_snapshot = body["data"]["active_member_snapshot"]
        self.assertEqual(active_snapshot["member_type"], "individual_farmer")
        self.assertEqual(active_snapshot["member_active_check"], "pass")
        self.assertEqual(active_snapshot["continuous_supply_years"], 4)
        self.assertEqual(len(active_snapshot["supply_rows"]), 4)
        self.assertTrue(all(row["qualifying"] for row in active_snapshot["supply_rows"]))
        self.assertIsNotNone(active_snapshot["result_id"])
        self.assertIsNotNone(active_snapshot["calculated_as_of_date"])
        self.assertIn(
            "Application-specific nominee selection is pending",
            body["data"]["assessment_notes"],
        )

        ProduceSupplyRecord.objects.all().delete()
        read_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.json()["data"]["active_member_snapshot"], active_snapshot)

    def test_eligibility_assessment_marks_application_eligible_when_all_source_checks_pass(self):
        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        application_id = self._reference_generated_application(terms_acceptance_flag=True)
        Nominee.objects.create(
            member=self.member,
            loan_application_id=application_id,
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
        self._create_nominee(application_id, minor_flag=True)

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["data"]["member_active_check"], "pass")
        self.assertEqual(body["data"]["default_check"], "no_default")
        self.assertEqual(body["data"]["document_check"], "complete")
        self.assertEqual(body["data"]["terms_acceptance_check"], "accepted")
        self.assertEqual(body["data"]["purpose_check"], "agriculture_aligned")
        self.assertEqual(body["data"]["nominee_check"], "valid")
        self.assertEqual(body["data"]["overall_result"], "eligible")

    def test_eligibility_uses_dob_to_reject_legacy_selected_minor(self):
        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        application_id = self._reference_generated_application(terms_acceptance_flag=True)
        self.nominee.age_at_application = None
        self.nominee.date_of_birth = timezone.localdate().replace(
            year=timezone.localdate().year - 17
        )
        self.nominee.save(update_fields=["age_at_application", "date_of_birth"])

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["nominee_check"], "minor")
        self.assertEqual(response.json()["data"]["overall_result"], "ineligible")

    def test_eligibility_assessment_marks_blockers_ineligible_without_advancing_application(self):
        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.default_status = "existing_default"
        self.member.save(
            update_fields=[
                "active_member_status",
                "active_member_verified_at",
                "default_status",
            ]
        )
        application_id = self._reference_generated_application(
            terms_acceptance_flag=True,
            purpose_category="working_capital",
        )
        self._create_nominee(application_id, minor_flag=True, age_at_application=16)
        application_document = apps.get_model("applications", "ApplicationDocument").objects.get(
            loan_application_id=application_id,
            document_type="land_document_7_12",
        )
        reject_document_response = self.client.post(
            f"/api/v1/application-documents/{application_document.application_document_id}/verify/",
            data={"verification_status": "rejected", "remarks": "Not accepted."},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(reject_document_response.status_code, 200)

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["data"]["default_check"], "default_found")
        self.assertEqual(body["data"]["document_check"], "incomplete")
        self.assertEqual(body["data"]["terms_acceptance_check"], "accepted")
        self.assertEqual(body["data"]["purpose_check"], "non_agriculture")
        self.assertEqual(body["data"]["nominee_check"], "valid")
        self.assertEqual(body["data"]["overall_result"], "ineligible")
        self.assertIn("BR-008", body["data"]["assessment_notes"])
        self.assertNotIn("BR-009", body["data"]["assessment_notes"])
        self.assertIn("BR-013/BR-014", body["data"]["assessment_notes"])
        self.assertIn("BR-018", body["data"]["assessment_notes"])

        detail_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(detail_response.status_code, 200)
        detail = detail_response.json()["data"]
        self.assertEqual(detail["application_status"], "reference_generated")
        self.assertEqual(detail["current_stage"], "credit_assessment")

    def test_eligibility_assessment_missing_terms_is_ineligible(self):
        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        application_id = self._reference_generated_application(terms_acceptance_flag=False)
        self._create_nominee(application_id)

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["data"]["terms_acceptance_check"], "pending")
        self.assertEqual(body["data"]["overall_result"], "ineligible")
        self.assertIn("S15 terms acceptance is pending", body["data"]["assessment_notes"])

    def test_eligibility_assessment_rerun_updates_existing_assessment(self):
        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        application_id = self._reference_generated_application(terms_acceptance_flag=True)
        self._create_nominee(application_id)

        first_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(first_response.status_code, 200)
        self.member.default_status = "existing_default"
        self.member.save(update_fields=["default_status"])
        second_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(
            first_response.json()["data"]["eligibility_assessment_id"],
            second_response.json()["data"]["eligibility_assessment_id"],
        )
        self.assertEqual(second_response.json()["data"]["default_check"], "default_found")
        self.assertEqual(second_response.json()["data"]["overall_result"], "ineligible")
        assessment_model = apps.get_model("credit", "EligibilityAssessment")
        self.assertEqual(assessment_model.objects.filter(loan_application_id=application_id).count(), 1)

    def test_eligibility_assessment_denials_and_invalid_state_create_no_success_evidence(self):
        draft_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_response.status_code, 200)
        draft_id = draft_response.json()["data"]["loan_application_id"]

        invalid_state = self.client.post(
            f"/api/v1/loan-applications/{draft_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(invalid_state.status_code, 409)
        assert_error_envelope(self, invalid_state.json(), "INVALID_STATE_TRANSITION")

        application_id = self._reference_generated_application()
        no_permission = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")

        out_of_scope = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.unrelated@sfpcl.example", "UnrelatedPass123!"),
        )
        self.assertEqual(out_of_scope.status_code, 403)
        assert_error_envelope(self, out_of_scope.json(), "OBJECT_ACCESS_DENIED")

        assessment_model = apps.get_model("credit", "EligibilityAssessment")
        self.assertEqual(assessment_model.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="eligibility.assessed").count(), 0)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="eligibility_assessment").count(),
            0,
        )

    def test_loan_limit_calculation_stores_source_backed_lower_of_two_result(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        policy = self._active_loan_policy(
            share_limit_percentage="10.0000",
            per_share_cap_amount="200.00",
        )

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/calculate/",
            data={
                "shareholding_id": str(shareholding.shareholding_id),
                "land_holding_ids": [str(self.land.land_holding_id)],
                "crop_plan_id": str(self.crop.crop_plan_id),
                "requested_amount": "400000.00",
                "calculation_date": timezone.localdate().isoformat(),
            },
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-calculate-loan-limit",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["meta"]["request_id"], "req-calculate-loan-limit")
        assessment = body["data"]
        self.assertEqual(assessment["loan_application_id"], application_id)
        self.assertEqual(assessment["member_id"], str(self.member.member_id))
        self.assertEqual(assessment["shareholding_id"], str(shareholding.shareholding_id))
        self.assertEqual(assessment["number_of_shares"], 100)
        self.assertEqual(assessment["valuation_per_share"], "2000.00")
        self.assertEqual(assessment["share_limit_percentage"], "10.0000")
        self.assertEqual(assessment["per_share_cap_amount"], "200.00")
        self.assertEqual(assessment["shareholding_based_limit_amount"], "20000.00")
        self.assertEqual(assessment["land_area_acres"], "5.00")
        self.assertEqual(assessment["scale_of_finance_per_acre_amount"], "20000.00")
        self.assertEqual(assessment["land_based_limit_amount"], "100000.00")
        self.assertEqual(assessment["final_eligible_loan_amount"], "20000.00")
        self.assertEqual(assessment["requested_amount"], "400000.00")
        self.assertFalse(assessment["amount_within_limit_flag"])
        self.assertTrue(assessment["exception_required_flag"])
        self.assertEqual(assessment["calculation_rule_version"], policy.policy_version)
        self.assertEqual(
            assessment["configuration_source"]["loan_policy_config_id"],
            str(policy.loan_policy_config_id),
        )
        self.assertEqual(
            assessment["warnings"],
            [
                {
                    "code": "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
                    "message": "Requested amount exceeds final eligible loan amount.",
                }
            ],
        )
        self.assertIsNotNone(assessment["calculated_at"])

        loan_limit_model = apps.get_model("credit", "LoanLimitAssessment")
        self.assertEqual(loan_limit_model.objects.filter(loan_application_id=application_id).count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 1)
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="loan_limit_assessment",
                entity_id=application_id,
            ).count(),
            1,
        )

    def test_loan_limit_blocks_unresolved_cultivated_acreage_without_success_evidence(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        self.land.area_acres = "20.00"
        self.land.verification_status = "verified"
        self.land.verified_by_user = self.creator
        self.land.verified_at = timezone.now()
        self.land.save()
        self.crop.planned_area_acres = "5.00"
        self.crop.loan_application_id = application_id
        self.crop.verification_status = "verified"
        self.crop.verified_by_user = self.creator
        self.crop.verified_at = timezone.now()
        self.crop.save()
        IndividualMemberProfile.objects.update_or_create(
            member=self.member,
            defaults={"first_name": "Ramesh", "last_name": "Patil", "land_area_under_cultivation_acres": "5.00", "services_availed_flag": True},
        )
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        self._active_loan_policy(
            share_limit_percentage="10.0000",
            per_share_cap_amount="200.00",
        )

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/calculate/",
            data={
                "shareholding_id": str(shareholding.shareholding_id),
                "land_holding_ids": [str(self.land.land_holding_id)],
                "crop_plan_id": str(self.crop.crop_plan_id),
                "requested_amount": "400000.00",
                "calculation_date": timezone.localdate().isoformat(),
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        assert_error_envelope(self, body, "VALIDATION_ERROR")
        self.assertEqual(
            body["error"]["field_errors"]["cultivated_acreage"],
            "CULTIVATED_ACREAGE_UNRESOLVED",
        )
        loan_limit_model = apps.get_model("credit", "LoanLimitAssessment")
        self.assertEqual(loan_limit_model.objects.filter(loan_application_id=application_id).count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 0)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            0,
        )

    def test_loan_limit_accepts_decimal_equivalent_cultivated_acreage_sources(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        self.land.area_acres = "5"
        self.land.save()
        self.crop.planned_area_acres = "5.0"
        self.crop.save()
        IndividualMemberProfile.objects.update_or_create(
            member=self.member,
            defaults={"first_name": "Ramesh", "last_name": "Patil", "land_area_under_cultivation_acres": "5.00", "services_availed_flag": True},
        )
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        self._active_loan_policy(
            share_limit_percentage="10.0000",
            per_share_cap_amount="200.00",
        )

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/calculate/",
            data={
                "shareholding_id": str(shareholding.shareholding_id),
                "land_holding_ids": [str(self.land.land_holding_id)],
                "crop_plan_id": str(self.crop.crop_plan_id),
                "requested_amount": "400000.00",
                "calculation_date": timezone.localdate().isoformat(),
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        assert_success_envelope(self, response.json())
        assessment = response.json()["data"]
        self.assertEqual(assessment["land_area_acres"], "5.00")
        self.assertEqual(assessment["land_based_limit_amount"], "100000.00")

    def test_loan_limit_uses_selected_land_and_crop_plan_when_profile_acreage_is_null(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        IndividualMemberProfile.objects.update_or_create(
            member=self.member,
            defaults={"first_name": "Ramesh", "last_name": "Patil", "land_area_under_cultivation_acres": None, "services_availed_flag": True},
        )
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        self._active_loan_policy(
            share_limit_percentage="10.0000",
            per_share_cap_amount="200.00",
        )

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/calculate/",
            data={
                "shareholding_id": str(shareholding.shareholding_id),
                "land_holding_ids": [str(self.land.land_holding_id)],
                "crop_plan_id": str(self.crop.crop_plan_id),
                "requested_amount": "400000.00",
                "calculation_date": timezone.localdate().isoformat(),
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        assert_success_envelope(self, response.json())
        self.assertEqual(response.json()["data"]["land_area_acres"], "5.00")

    def test_loan_limit_failed_cultivated_acreage_rerun_preserves_existing_snapshot(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        self._active_loan_policy(
            share_limit_percentage="10.0000",
            per_share_cap_amount="200.00",
        )
        endpoint = f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/"
        payload = {
            "shareholding_id": str(shareholding.shareholding_id),
            "land_holding_ids": [str(self.land.land_holding_id)],
            "crop_plan_id": str(self.crop.crop_plan_id),
            "requested_amount": "400000.00",
            "calculation_date": timezone.localdate().isoformat(),
        }
        first = self.client.post(
            f"{endpoint}calculate/",
            data=payload,
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(first.status_code, 200)
        stored_snapshot = first.json()["data"]
        self.crop.planned_area_acres = "4.00"
        self.crop.save()

        failed = self.client.post(
            f"{endpoint}calculate/",
            data=payload,
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(failed.status_code, 400)
        assert_error_envelope(self, failed.json(), "VALIDATION_ERROR")
        self.assertEqual(
            failed.json()["error"]["field_errors"]["cultivated_acreage"],
            "CULTIVATED_ACREAGE_UNRESOLVED",
        )
        read = self.client.get(
            endpoint,
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(read.status_code, 200)
        self.assertEqual(read.json()["data"], stored_snapshot)
        loan_limit_model = apps.get_model("credit", "LoanLimitAssessment")
        self.assertEqual(loan_limit_model.objects.filter(loan_application_id=application_id).count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 1)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            1,
        )

    def test_loan_limit_rejects_unverified_or_unlinked_cultivation_facts_without_evidence(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        pending_land = LandHolding.objects.create(
            member=self.member,
            document_type="7_12_extract",
            survey_number="124/1",
            village="Niphad",
            area_acres="5.00",
            document_id=uuid4(),
            verification_status="pending",
        )
        rejected_land = LandHolding.objects.create(
            member=self.member,
            document_type="7_12_extract",
            survey_number="124/2",
            village="Niphad",
            area_acres="5.00",
            document_id=uuid4(),
            verification_status="rejected",
        )
        pending_crop = CropPlan.objects.create(
            member=self.member,
            loan_application_id=application_id,
            crop_type="grapes",
            season="FY2026 Rabi",
            planned_area_acres="5.00",
            estimated_cost_amount="100000.00",
            loan_purpose_alignment="agriculture_aligned",
            document_id=uuid4(),
            verification_status="pending",
        )
        unlinked_crop = CropPlan.objects.create(
            member=self.member,
            crop_type="grapes",
            season="FY2026 Summer",
            planned_area_acres="5.00",
            estimated_cost_amount="100000.00",
            loan_purpose_alignment="agriculture_aligned",
            document_id=uuid4(),
            verification_status="verified",
            verified_by_user=self.creator,
            verified_at=timezone.now(),
        )
        wrong_application_crop = CropPlan.objects.create(
            member=self.member,
            loan_application_id=uuid4(),
            crop_type="grapes",
            season="FY2026 Late",
            planned_area_acres="5.00",
            estimated_cost_amount="100000.00",
            loan_purpose_alignment="agriculture_aligned",
            document_id=uuid4(),
            verification_status="verified",
            verified_by_user=self.creator,
            verified_at=timezone.now(),
        )
        self._active_loan_policy(
            share_limit_percentage="10.0000",
            per_share_cap_amount="200.00",
        )
        endpoint = (
            f"/api/v1/loan-applications/{application_id}/"
            "loan-limit-assessment/calculate/"
        )
        base_payload = {
            "shareholding_id": str(shareholding.shareholding_id),
            "land_holding_ids": [str(self.land.land_holding_id)],
            "crop_plan_id": str(self.crop.crop_plan_id),
            "requested_amount": "400000.00",
            "calculation_date": timezone.localdate().isoformat(),
        }
        cases = [
            ({"land_holding_ids": [str(pending_land.land_holding_id)]}, "land_holding_ids"),
            ({"land_holding_ids": [str(rejected_land.land_holding_id)]}, "land_holding_ids"),
            ({"crop_plan_id": str(pending_crop.crop_plan_id)}, "crop_plan_id"),
            ({"crop_plan_id": str(unlinked_crop.crop_plan_id)}, "crop_plan_id"),
            ({"crop_plan_id": str(wrong_application_crop.crop_plan_id)}, "crop_plan_id"),
        ]
        for override, expected_field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    endpoint,
                    data={**base_payload, **override},
                    content_type="application/json",
                    headers=self._headers(
                        "applications.creator@sfpcl.example",
                        "CreatorPass123!",
                    ),
                )
                self.assertEqual(response.status_code, 400)
                assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
                self.assertIn(expected_field, response.json()["error"]["field_errors"])

        loan_limit_model = apps.get_model("credit", "LoanLimitAssessment")
        self.assertEqual(loan_limit_model.objects.filter(loan_application_id=application_id).count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 0)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            0,
        )

    def test_loan_limit_read_returns_immutable_stored_snapshot_without_evidence(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        policy = self._active_loan_policy(
            share_limit_percentage="10.0000",
            per_share_cap_amount="200.00",
        )
        endpoint = (
            f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/"
        )
        calculate = self.client.post(
            f"{endpoint}calculate/",
            data={
                "shareholding_id": str(shareholding.shareholding_id),
                "land_holding_ids": [str(self.land.land_holding_id)],
                "crop_plan_id": str(self.crop.crop_plan_id),
                "requested_amount": "400000.00",
                "calculation_date": timezone.localdate().isoformat(),
            },
            content_type="application/json",
            headers=self._headers(
                "applications.creator@sfpcl.example",
                "CreatorPass123!",
            ),
        )
        self.assertEqual(calculate.status_code, 200)
        stored_snapshot = calculate.json()["data"]

        Shareholding.objects.filter(pk=shareholding.pk).update(
            number_of_shares=999,
            valuation_per_share="9999.00",
            available_share_count=999,
        )
        LandHolding.objects.filter(pk=self.land.pk).update(area_acres="99.00")
        CropPlan.objects.filter(pk=self.crop.pk).update(planned_area_acres="99.00")
        application_model = apps.get_model("applications", "LoanApplication")
        application_model.objects.filter(pk=application_id).update(
            required_loan_amount="10000.00"
        )
        LoanPolicyConfig.objects.filter(pk=policy.pk).update(
            policy_name="Mutated policy name",
            policy_version="mutated-v99",
            board_approval_reference="BOARD-MUTATED",
            share_limit_percentage="99.0000",
            per_share_cap_amount="9999.00",
            default_scale_of_finance_per_acre_amount="9999.00",
        )

        read = self.client.get(
            endpoint,
            headers={
                **self._headers(
                    "applications.creator@sfpcl.example",
                    "CreatorPass123!",
                ),
                "X-Request-ID": "req-read-loan-limit-snapshot",
            },
        )

        self.assertEqual(read.status_code, 200)
        assert_success_envelope(self, read.json())
        self.assertEqual(
            read.json()["meta"]["request_id"],
            "req-read-loan-limit-snapshot",
        )
        self.assertEqual(read.json()["data"], stored_snapshot)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 1)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            1,
        )

        rerun = self.client.post(
            f"{endpoint}calculate/",
            data={
                "shareholding_id": str(shareholding.shareholding_id),
                "land_holding_ids": [str(self.land.land_holding_id)],
                "crop_plan_id": str(self.crop.crop_plan_id),
                "requested_amount": "10000.00",
                "calculation_date": timezone.localdate().isoformat(),
            },
            content_type="application/json",
            headers=self._headers(
                "applications.creator@sfpcl.example",
                "CreatorPass123!",
            ),
        )
        self.assertEqual(rerun.status_code, 200)
        replacement_snapshot = rerun.json()["data"]
        self.assertEqual(
            replacement_snapshot["loan_limit_assessment_id"],
            stored_snapshot["loan_limit_assessment_id"],
        )
        self.assertEqual(replacement_snapshot["number_of_shares"], 999)
        self.assertEqual(replacement_snapshot["land_area_acres"], "99.00")
        self.assertEqual(replacement_snapshot["requested_amount"], "10000.00")
        self.assertEqual(replacement_snapshot["calculation_rule_version"], "mutated-v99")
        self.assertEqual(
            replacement_snapshot["configuration_source"],
            {
                "type": "loan_policy_config",
                "loan_policy_config_id": str(policy.loan_policy_config_id),
                "policy_name": "Mutated policy name",
                "board_approval_reference": "BOARD-MUTATED",
            },
        )
        reread = self.client.get(
            endpoint,
            headers=self._headers(
                "applications.creator@sfpcl.example",
                "CreatorPass123!",
            ),
        )
        self.assertEqual(reread.status_code, 200)
        self.assertEqual(reread.json()["data"], replacement_snapshot)
        rerun_audit = (
            AuditLog.objects.filter(action="loan_limit.calculated")
            .order_by("-created_at")
            .first()
        )
        self.assertEqual(rerun_audit.old_value_json["number_of_shares"], 100)
        self.assertEqual(rerun_audit.new_value_json["number_of_shares"], 999)
        self.assertEqual(
            rerun_audit.old_value_json["configuration_source"]["policy_name"],
            policy.policy_name,
        )
        self.assertEqual(
            rerun_audit.new_value_json["configuration_source"]["policy_name"],
            "Mutated policy name",
        )
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 2)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            2,
        )

        rerun_payload = {
            "shareholding_id": str(shareholding.shareholding_id),
            "land_holding_ids": [str(self.land.land_holding_id)],
            "crop_plan_id": str(self.crop.crop_plan_id),
            "requested_amount": "10000.00",
            "calculation_date": timezone.localdate().isoformat(),
        }
        eligibility_model = apps.get_model("credit", "EligibilityAssessment")
        eligibility_model.objects.filter(loan_application_id=application_id).update(
            overall_result="ineligible"
        )
        invalid_state = self.client.post(
            f"{endpoint}calculate/",
            data=rerun_payload,
            content_type="application/json",
            headers=self._headers(
                "applications.creator@sfpcl.example",
                "CreatorPass123!",
            ),
        )
        self.assertEqual(invalid_state.status_code, 409)
        assert_error_envelope(
            self,
            invalid_state.json(),
            "INVALID_STATE_TRANSITION",
        )
        eligibility_model.objects.filter(loan_application_id=application_id).update(
            overall_result="eligible"
        )

        missing_source = self.client.post(
            f"{endpoint}calculate/",
            data={**rerun_payload, "shareholding_id": str(uuid4())},
            content_type="application/json",
            headers=self._headers(
                "applications.creator@sfpcl.example",
                "CreatorPass123!",
            ),
        )
        self.assertEqual(missing_source.status_code, 400)
        assert_error_envelope(self, missing_source.json(), "VALIDATION_ERROR")

        permission_denied = self.client.post(
            f"{endpoint}calculate/",
            data=rerun_payload,
            content_type="application/json",
            headers=self._headers(
                "applications.reader@sfpcl.example",
                "ReaderPass123!",
            ),
        )
        self.assertEqual(permission_denied.status_code, 403)
        assert_error_envelope(
            self,
            permission_denied.json(),
            "PERMISSION_DENIED",
        )

        object_scope_denied = self.client.post(
            f"{endpoint}calculate/",
            data=rerun_payload,
            content_type="application/json",
            headers=self._headers(
                "applications.unrelated@sfpcl.example",
                "UnrelatedPass123!",
            ),
        )
        self.assertEqual(object_scope_denied.status_code, 403)
        assert_error_envelope(
            self,
            object_scope_denied.json(),
            "OBJECT_ACCESS_DENIED",
        )

        preserved = self.client.get(
            endpoint,
            headers=self._headers(
                "applications.creator@sfpcl.example",
                "CreatorPass123!",
            ),
        )
        self.assertEqual(preserved.status_code, 200)
        self.assertEqual(preserved.json()["data"], replacement_snapshot)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 2)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            2,
        )

    def test_loan_limit_read_enforces_read_permission_scope_and_missing_snapshot(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        endpoint = (
            f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/"
        )

        unauthenticated = self.client.get(endpoint)
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        no_permission = self.client.get(
            endpoint,
            headers=self._headers("applications.plain@sfpcl.example", "PlainPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")

        out_of_scope = self.client.get(
            endpoint,
            headers=self._headers(
                "applications.unrelated@sfpcl.example",
                "UnrelatedPass123!",
            ),
        )
        self.assertEqual(out_of_scope.status_code, 403)
        assert_error_envelope(self, out_of_scope.json(), "OBJECT_ACCESS_DENIED")

        missing = self.client.get(
            endpoint,
            headers=self._headers(
                "applications.creator@sfpcl.example",
                "CreatorPass123!",
            ),
        )
        self.assertEqual(missing.status_code, 404)
        assert_error_envelope(self, missing.json(), "NOT_FOUND")
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 0)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            0,
        )

    def test_loan_limit_equal_and_below_boundaries_update_one_assessment(self):
        application_id = self._eligible_application(required_loan_amount="20000.00")
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        self._active_loan_policy(
            share_limit_percentage="10.0000",
            per_share_cap_amount="200.00",
        )
        endpoint = (
            f"/api/v1/loan-applications/{application_id}/"
            "loan-limit-assessment/calculate/"
        )
        payload = {
            "shareholding_id": str(shareholding.shareholding_id),
            "land_holding_ids": [str(self.land.land_holding_id)],
            "crop_plan_id": str(self.crop.crop_plan_id),
            "requested_amount": "20000.00",
            "calculation_date": timezone.localdate().isoformat(),
        }
        first = self.client.post(
            endpoint,
            data=payload,
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(first.status_code, 200)
        first_result = first.json()["data"]
        self.assertTrue(first_result["amount_within_limit_flag"])
        self.assertFalse(first_result["exception_required_flag"])
        self.assertEqual(first_result["warnings"], [])

        application_model = apps.get_model("applications", "LoanApplication")
        application_model.objects.filter(loan_application_id=application_id).update(
            required_loan_amount="15000.00"
        )
        payload["requested_amount"] = "15000.00"
        second = self.client.post(
            endpoint,
            data=payload,
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(second.status_code, 200)
        second_result = second.json()["data"]
        self.assertEqual(
            second_result["loan_limit_assessment_id"],
            first_result["loan_limit_assessment_id"],
        )
        self.assertEqual(second_result["requested_amount"], "15000.00")
        self.assertTrue(second_result["amount_within_limit_flag"])
        self.assertFalse(second_result["exception_required_flag"])
        loan_limit_model = apps.get_model("credit", "LoanLimitAssessment")
        self.assertEqual(loan_limit_model.objects.filter(loan_application_id=application_id).count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 2)

    def test_loan_limit_blocks_pending_ineligible_and_missing_policy_without_success_evidence(self):
        self.member.individual_profile.services_availed_flag = False
        self.member.individual_profile.save(update_fields=["services_availed_flag"])
        application_id = self._reference_generated_application(terms_acceptance_flag=True)
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        endpoint = (
            f"/api/v1/loan-applications/{application_id}/"
            "loan-limit-assessment/calculate/"
        )
        payload = {
            "shareholding_id": str(shareholding.shareholding_id),
            "land_holding_ids": [str(self.land.land_holding_id)],
            "crop_plan_id": str(self.crop.crop_plan_id),
            "requested_amount": "400000.00",
            "calculation_date": timezone.localdate().isoformat(),
        }
        eligibility_endpoint = (
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/"
        )
        pending = self.client.post(
            eligibility_endpoint,
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(pending.status_code, 200)
        self.assertEqual(pending.json()["data"]["overall_result"], "pending_manual_evidence")
        pending_calculation = self.client.post(
            endpoint,
            data=payload,
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(pending_calculation.status_code, 409)
        assert_error_envelope(
            self,
            pending_calculation.json(),
            "INVALID_STATE_TRANSITION",
        )

        self.member.default_status = "existing_default"
        self.member.save(update_fields=["default_status"])
        ineligible = self.client.post(
            eligibility_endpoint,
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(ineligible.status_code, 200)
        self.assertEqual(ineligible.json()["data"]["overall_result"], "ineligible")
        ineligible_calculation = self.client.post(
            endpoint,
            data=payload,
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(ineligible_calculation.status_code, 409)
        assert_error_envelope(
            self,
            ineligible_calculation.json(),
            "INVALID_STATE_TRANSITION",
        )

        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.default_status = "no_default"
        self.member.save(
            update_fields=[
                "active_member_status",
                "active_member_verified_at",
                "default_status",
            ]
        )
        self.member.individual_profile.services_availed_flag = True
        self.member.individual_profile.save(update_fields=["services_availed_flag"])
        self._create_nominee(application_id)
        eligible = self.client.post(
            eligibility_endpoint,
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(eligible.status_code, 200)
        self.assertEqual(eligible.json()["data"]["overall_result"], "eligible")
        missing_policy = self.client.post(
            endpoint,
            data=payload,
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(missing_policy.status_code, 400)
        assert_error_envelope(self, missing_policy.json(), "VALIDATION_ERROR")
        self.assertIn("loan_policy_config", missing_policy.json()["error"]["field_errors"])

        self._active_loan_policy()
        unresolved_policy = self.client.post(
            endpoint,
            data=payload,
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(unresolved_policy.status_code, 400)
        assert_error_envelope(self, unresolved_policy.json(), "VALIDATION_ERROR")
        self.assertIn(
            "loan_policy_config",
            unresolved_policy.json()["error"]["field_errors"],
        )

        loan_limit_model = apps.get_model("credit", "LoanLimitAssessment")
        self.assertEqual(loan_limit_model.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 0)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            0,
        )

    def test_loan_limit_rejects_missing_and_cross_member_source_facts_without_evidence(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        other_shareholding = Shareholding.objects.create(
            member=self.other_member,
            folio_number=self.other_member.folio_number,
            number_of_shares=50,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=50,
            status="active",
        )
        other_land = LandHolding.objects.create(
            member=self.other_member,
            document_type="7_12_extract",
            survey_number="999/1",
            village="Pune",
            area_acres="3.00",
            document_id=uuid4(),
        )
        other_crop = CropPlan.objects.create(
            member=self.other_member,
            crop_type="onion",
            season="FY2026 Kharif",
            planned_area_acres="3.00",
            estimated_cost_amount="60000.00",
            loan_purpose_alignment="agriculture_aligned",
            document_id=uuid4(),
        )
        self._active_loan_policy(share_limit_percentage="10.0000")
        endpoint = (
            f"/api/v1/loan-applications/{application_id}/"
            "loan-limit-assessment/calculate/"
        )
        base_payload = {
            "shareholding_id": str(shareholding.shareholding_id),
            "land_holding_ids": [str(self.land.land_holding_id)],
            "crop_plan_id": str(self.crop.crop_plan_id),
            "requested_amount": "400000.00",
            "calculation_date": timezone.localdate().isoformat(),
        }
        cases = [
            ({"shareholding_id": str(uuid4())}, "shareholding_id"),
            ({"land_holding_ids": []}, "land_holding_ids"),
            ({"crop_plan_id": str(uuid4())}, "crop_plan_id"),
            (
                {"shareholding_id": str(other_shareholding.shareholding_id)},
                "shareholding_id",
            ),
            ({"land_holding_ids": [str(other_land.land_holding_id)]}, "land_holding_ids"),
            ({"crop_plan_id": str(other_crop.crop_plan_id)}, "crop_plan_id"),
        ]
        for override, expected_field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    endpoint,
                    data={**base_payload, **override},
                    content_type="application/json",
                    headers=self._headers(
                        "applications.creator@sfpcl.example",
                        "CreatorPass123!",
                    ),
                )
                self.assertEqual(response.status_code, 400)
                assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
                self.assertIn(expected_field, response.json()["error"]["field_errors"])

        loan_limit_model = apps.get_model("credit", "LoanLimitAssessment")
        self.assertEqual(loan_limit_model.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 0)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            0,
        )

    def test_loan_limit_permission_and_object_scope_denials_create_no_success_evidence(self):
        application_id = self._eligible_application(required_loan_amount="400000.00")
        endpoint = (
            f"/api/v1/loan-applications/{application_id}/"
            "loan-limit-assessment/calculate/"
        )

        unauthenticated = self.client.post(
            endpoint,
            data={},
            content_type="application/json",
        )
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        no_permission = self.client.post(
            endpoint,
            data={},
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")

        out_of_scope = self.client.post(
            endpoint,
            data={},
            content_type="application/json",
            headers=self._headers(
                "applications.unrelated@sfpcl.example",
                "UnrelatedPass123!",
            ),
        )
        self.assertEqual(out_of_scope.status_code, 403)
        assert_error_envelope(self, out_of_scope.json(), "OBJECT_ACCESS_DENIED")

        loan_limit_model = apps.get_model("credit", "LoanLimitAssessment")
        self.assertEqual(loan_limit_model.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="loan_limit.calculated").count(), 0)
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_limit_assessment").count(),
            0,
        )

    def test_loan_limit_per_share_cap_policy_uses_land_limit_when_lower(self):
        application_id = self._eligible_application(required_loan_amount="100000.00")
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=1000,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=1000,
            status="active",
        )
        self._active_loan_policy(per_share_cap_amount="200.00")

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/calculate/",
            data={
                "shareholding_id": str(shareholding.shareholding_id),
                "land_holding_ids": [str(self.land.land_holding_id)],
                "crop_plan_id": str(self.crop.crop_plan_id),
                "requested_amount": "100000.00",
                "calculation_date": timezone.localdate().isoformat(),
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        assessment = response.json()["data"]
        self.assertIsNone(assessment["share_limit_percentage"])
        self.assertEqual(assessment["per_share_cap_amount"], "200.00")
        self.assertEqual(assessment["shareholding_based_limit_amount"], "200000.00")
        self.assertEqual(assessment["land_based_limit_amount"], "100000.00")
        self.assertEqual(assessment["final_eligible_loan_amount"], "100000.00")
        self.assertTrue(assessment["amount_within_limit_flag"])
        self.assertFalse(assessment["exception_required_flag"])

    def test_submit_draft_transitions_to_submitted_and_records_metadata_only_evidence(self):
        create_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        draft = create_response.json()["data"]

        response = self.client.post(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/submit/",
            data={"submission_notes": "Application form signed by applicant."},
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-submit-loan-application",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        submitted = body["data"]
        self.assertEqual(submitted["loan_application_id"], draft["loan_application_id"])
        self.assertEqual(submitted["application_status"], "submitted")
        self.assertEqual(submitted["current_stage"], "initial_loan_request")
        self.assertEqual(submitted["completeness_status"], "not_started")
        self.assertIsNone(submitted["application_reference_number"])
        self.assertIsNotNone(submitted["submitted_at"])
        self.assertEqual(submitted["submitted_by_user_id"], str(self.creator.user_id))
        self.assertEqual(submitted["bank_account"]["account_holder_name"], "Ramesh Patil")
        self.assertEqual(submitted["bank_account"]["account_number"]["masked"], "********9012")
        self.assertFalse(submitted["bank_account"]["account_number"]["can_view_full"])

        read_response = self.client.get(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(without_detail_metadata(read_response.json()["data"]), submitted)

        audit = AuditLog.objects.filter(action="applications.loan_application.submitted").get()
        self.assertEqual(str(audit.entity_id), draft["loan_application_id"])
        self.assertEqual(audit.old_value_json["application_status"], "draft")
        self.assertEqual(audit.new_value_json["application_status"], "submitted")
        self.assertEqual(audit.new_value_json["request_id"], "req-submit-loan-application")
        self.assertEqual(audit.new_value_json["masked_bank_account_number"], "********9012")

        workflow_event = WorkflowEvent.objects.filter(
            entity_type="loan_application",
            from_state="draft",
            to_state="submitted",
        ).get()
        self.assertEqual(str(workflow_event.entity_id), draft["loan_application_id"])
        self.assertEqual(workflow_event.workflow_name, "loan_application")

        flattened = f"{body} {audit.old_value_json} {audit.new_value_json}"
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("cheque-token-123456789012", flattened)
        self.assertNotIn("cheque-hash-123456789012", flattened)
        self.assertNotIn("123456789012", flattened)

    def test_generate_reference_after_completeness_pass_creates_register_and_metadata_only_evidence(self):
        create_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        draft = create_response.json()["data"]
        submit_response = self.client.post(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(submit_response.status_code, 200)

        response = self.client.post(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-generate-reference",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        generated = body["data"]
        self.assertEqual(generated["application_reference_number"], "LO00000001")
        self.assertEqual(generated["application_status"], "reference_generated")
        self.assertEqual(generated["current_stage"], "credit_assessment")
        self.assertEqual(generated["completeness_status"], "complete")
        self.assertEqual(
            generated["loan_request_register_entry"]["application_reference_number"],
            "LO00000001",
        )
        self.assertEqual(
            generated["loan_request_register_entry"]["loan_application_id"],
            draft["loan_application_id"],
        )
        self.assertEqual(
            generated["loan_request_register_entry"]["member_id"],
            str(self.member.member_id),
        )
        self.assertEqual(generated["loan_request_register_entry"]["borrower_name"], "Ramesh Patil")
        self.assertEqual(generated["loan_request_register_entry"]["folio_number"], "FOL-005A")
        self.assertEqual(generated["loan_request_register_entry"]["requested_amount"], "400000.00")

        read_response = self.client.get(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(without_detail_metadata(read_response.json()["data"]), generated)

        register_model = apps.get_model("applications", "LoanRequestRegisterEntry")
        register_entry = register_model.objects.get(
            loan_application_id=draft["loan_application_id"]
        )
        self.assertEqual(register_entry.application_reference_number, "LO00000001")
        self.assertEqual(str(register_entry.member_id), str(self.member.member_id))

        audit = AuditLog.objects.filter(
            action="applications.loan_application.reference_generated"
        ).get()
        self.assertEqual(audit.old_value_json["application_reference_number"], None)
        self.assertEqual(audit.new_value_json["application_reference_number"], "LO00000001")
        self.assertEqual(audit.new_value_json["loan_request_register_entry_id"], str(register_entry.pk))
        self.assertEqual(audit.new_value_json["request_id"], "req-generate-reference")

        workflow_event = WorkflowEvent.objects.filter(
            entity_type="loan_application",
            from_state="submitted",
            to_state="reference_generated",
        ).get()
        self.assertEqual(str(workflow_event.entity_id), draft["loan_application_id"])

        flattened = f"{body} {audit.old_value_json} {audit.new_value_json}"
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("cheque-token-123456789012", flattened)
        self.assertNotIn("cheque-hash-123456789012", flattened)
        self.assertNotIn("123456789012", flattened)

    def test_reference_generation_enforces_sequence_permission_state_and_duplicate_guards(self):
        first_id = self._create_and_submit_application()
        second_id = self._create_and_submit_application(
            declared_purpose="Crop production loan for onion cultivation",
            required_loan_amount="250000.00",
        )

        first = self.client.post(
            f"/api/v1/loan-applications/{first_id}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        second = self.client.post(
            f"/api/v1/loan-applications/{second_id}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()["data"]["application_reference_number"], "LO00000001")
        self.assertEqual(second.json()["data"]["application_reference_number"], "LO00000002")

        duplicate = self.client.post(
            f"/api/v1/loan-applications/{first_id}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(duplicate.status_code, 409)
        assert_error_envelope(self, duplicate.json(), "INVALID_STATE_TRANSITION")

        draft_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(declared_purpose="Draft only request"),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_response.status_code, 200)
        draft_id = draft_response.json()["data"]["loan_application_id"]
        draft_generate = self.client.post(
            f"/api/v1/loan-applications/{draft_id}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_generate.status_code, 409)
        assert_error_envelope(self, draft_generate.json(), "INVALID_STATE_TRANSITION")

        missing_application = self.client.post(
            f"/api/v1/loan-applications/{uuid4()}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(missing_application.status_code, 404)
        assert_error_envelope(self, missing_application.json(), "NOT_FOUND")

        no_permission = self.client.post(
            f"/api/v1/loan-applications/{second_id}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")

        register_model = apps.get_model("applications", "LoanRequestRegisterEntry")
        self.assertEqual(register_model.objects.count(), 2)
        self.assertEqual(
            AuditLog.objects.filter(
                action="applications.loan_application.reference_generated"
            ).count(),
            2,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                entity_type="loan_application",
                to_state="reference_generated",
            ).count(),
            2,
        )

    def test_patch_updates_allowed_draft_fields_and_rejects_cross_member_references(self):
        create_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        application_id = create_response.json()["data"]["loan_application_id"]
        other_bank = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.other_member.member_id,
            account_holder_name="Sita Farms",
            account_number_encrypted="other-bank-token-999900001111",
            account_number_hash="other-bank-hash-999900001111",
            account_number_last4="1111",
            ifsc="SBIN0000456",
        )

        bad_response = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/",
            data={"bank_account_id": str(other_bank.bank_account_id)},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(bad_response.status_code, 400)
        bad_body = bad_response.json()
        assert_error_envelope(self, bad_body, "VALIDATION_ERROR")
        self.assertIn("bank_account_id", bad_body["error"]["field_errors"])

        good_response = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/",
            data={
                "required_loan_amount": "450000.00",
                "requested_tenure_months": 18,
                "declared_purpose": "Updated crop production loan purpose",
                "borrower_request_notes": "Updated notes",
            },
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-update-loan-draft",
            },
        )

        self.assertEqual(good_response.status_code, 200)
        body = good_response.json()
        assert_success_envelope(self, body)
        draft = body["data"]
        self.assertEqual(draft["loan_application_id"], application_id)
        self.assertEqual(draft["member"]["member_id"], str(self.member.member_id))
        self.assertEqual(draft["required_loan_amount"], "450000.00")
        self.assertEqual(draft["requested_tenure_months"], 18)
        self.assertEqual(draft["declared_purpose"], "Updated crop production loan purpose")
        self.assertEqual(draft["borrower_request_notes"], "Updated notes")
        self.assertEqual(draft["bank_account"]["bank_account_id"], str(self.bank.bank_account_id))

        update_audit = AuditLog.objects.filter(
            action="applications.loan_application.updated"
        ).get()
        self.assertEqual(str(update_audit.entity_id), application_id)
        self.assertEqual(update_audit.new_value_json["required_loan_amount"], "450000.00")
        self.assertEqual(update_audit.new_value_json["request_id"], "req-update-loan-draft")
        self.assertEqual(WorkflowEvent.objects.filter(entity_type="loan_application").count(), 1)

    def test_unrelated_same_permission_user_is_object_access_denied_without_side_effects(self):
        create_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        application_id = create_response.json()["data"]["loan_application_id"]
        unrelated_headers = self._headers(
            "applications.unrelated@sfpcl.example",
            "UnrelatedPass123!",
        )

        denied_read = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=unrelated_headers,
        )
        self.assertEqual(denied_read.status_code, 403)
        assert_error_envelope(self, denied_read.json(), "OBJECT_ACCESS_DENIED")

        denied_patch = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/",
            data={"borrower_request_notes": "Unrelated actor edit attempt"},
            content_type="application/json",
            headers=unrelated_headers,
        )
        self.assertEqual(denied_patch.status_code, 403)
        assert_error_envelope(self, denied_patch.json(), "OBJECT_ACCESS_DENIED")

        denied_submit = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=unrelated_headers,
        )
        self.assertEqual(denied_submit.status_code, 403)
        assert_error_envelope(self, denied_submit.json(), "OBJECT_ACCESS_DENIED")
        self.assertEqual(
            AuditLog.objects.filter(action="applications.loan_application.updated").count(),
            0,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="applications.loan_application.submitted").count(),
            0,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                entity_type="loan_application",
                to_state="submitted",
            ).count(),
            0,
        )

        submit_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(submit_response.status_code, 200)

        denied_reference = self.client.post(
            f"/api/v1/loan-applications/{application_id}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=unrelated_headers,
        )
        self.assertEqual(denied_reference.status_code, 403)
        assert_error_envelope(self, denied_reference.json(), "OBJECT_ACCESS_DENIED")

        register_model = apps.get_model("applications", "LoanRequestRegisterEntry")
        sequence_model = apps.get_model("applications", "SystemSequence")
        self.assertEqual(register_model.objects.count(), 0)
        self.assertEqual(sequence_model.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action="applications.loan_application.reference_generated"
            ).count(),
            0,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                entity_type="loan_application",
                to_state="reference_generated",
            ).count(),
            0,
        )

    def test_credit_manager_can_read_credit_assessment_application_by_domain_scope(self):
        application_id = self._create_and_submit_application()
        generate_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(generate_response.status_code, 200)
        credit_manager = self._user(
            "applications.credit.manager@sfpcl.example",
            "CreditManagerPass123!",
            self.read_permission,
            role_code="credit_manager",
        )

        read_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers(credit_manager.email, "CreditManagerPass123!"),
        )

        self.assertEqual(read_response.status_code, 200)
        body = read_response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["data"]["loan_application_id"], application_id)
        self.assertEqual(body["data"]["current_stage"], "credit_assessment")

    def test_application_document_checklist_upload_and_verify_are_metadata_only(self):
        application_id = self._create_and_submit_application()

        checklist_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/document-checklist/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(checklist_response.status_code, 200)
        checklist_body = checklist_response.json()
        assert_success_envelope(self, checklist_body)
        checklist_codes = {item["document_type"] for item in checklist_body["data"]["items"]}
        self.assertEqual(
            checklist_codes,
            {
                "loan_application_form",
                "borrower_pan",
                "borrower_aadhaar_ovd",
                "nominee_pan",
                "nominee_aadhaar_ovd",
                "share_certificate_copy",
                "land_document_7_12",
                "crop_plan",
                "six_month_bank_statement",
            },
        )
        for item in checklist_body["data"]["items"]:
            self.assertTrue(item["required_flag"])
            self.assertEqual(item["submission_status"], "pending")
            self.assertEqual(item["verification_status"], "pending")

        document_file = self._document_file()
        upload_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "party_id": str(self.member.member_id),
                "document_file_id": str(document_file.document_id),
                "remarks": "PAN copy received at branch.",
            },
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-app-doc-upload",
            },
        )

        self.assertEqual(upload_response.status_code, 200)
        upload_body = upload_response.json()
        assert_success_envelope(self, upload_body)
        uploaded = upload_body["data"]
        self.assertEqual(uploaded["loan_application_id"], application_id)
        self.assertEqual(uploaded["document_type"], "borrower_pan")
        self.assertEqual(uploaded["party_type"], "borrower")
        self.assertEqual(uploaded["party_id"], str(self.member.member_id))
        self.assertEqual(uploaded["document_file"]["document_id"], str(document_file.document_id))
        self.assertEqual(uploaded["document_file"]["file_name"], "borrower-pan.pdf")
        self.assertEqual(uploaded["submission_status"], "submitted")
        self.assertEqual(uploaded["verification_status"], "pending")
        self.assertEqual(uploaded["version_number"], 1)

        list_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()["data"]["items"], [uploaded])

        upload_audit = AuditLog.objects.filter(
            action="applications.application_document.attached"
        ).get()
        self.assertEqual(upload_audit.entity_type, "application_document")
        self.assertEqual(str(upload_audit.entity_id), uploaded["application_document_id"])
        self.assertEqual(upload_audit.new_value_json["loan_application_id"], application_id)
        self.assertEqual(upload_audit.new_value_json["document_type"], "borrower_pan")
        self.assertEqual(upload_audit.new_value_json["party_type"], "borrower")
        self.assertEqual(upload_audit.new_value_json["document_file_id"], str(document_file.document_id))
        self.assertEqual(upload_audit.new_value_json["request_id"], "req-app-doc-upload")

        verify_response = self.client.post(
            f"/api/v1/application-documents/{uploaded['application_document_id']}/verify/",
            data={"verification_status": "verified", "remarks": "PAN name matches member profile."},
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-app-doc-verify",
            },
        )

        self.assertEqual(verify_response.status_code, 200)
        verified = verify_response.json()["data"]
        self.assertEqual(verified["verification_status"], "verified")
        self.assertEqual(verified["verified_by_user_id"], str(self.creator.user_id))
        self.assertIsNotNone(verified["verified_at"])
        self.assertEqual(verified["remarks"], "PAN name matches member profile.")

        verify_audit = AuditLog.objects.filter(
            action="applications.application_document.verified"
        ).get()
        self.assertEqual(str(verify_audit.entity_id), uploaded["application_document_id"])
        self.assertEqual(verify_audit.old_value_json["verification_status"], "pending")
        self.assertEqual(verify_audit.new_value_json["verification_status"], "verified")
        self.assertEqual(verify_audit.new_value_json["request_id"], "req-app-doc-verify")

        refreshed_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/document-checklist/refresh/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(refreshed_response.status_code, 200)
        refreshed_pan = [
            item
            for item in refreshed_response.json()["data"]["items"]
            if item["document_type"] == "borrower_pan"
        ][0]
        self.assertEqual(refreshed_pan["submission_status"], "submitted")
        self.assertEqual(refreshed_pan["verification_status"], "verified")
        self.assertEqual(refreshed_pan["latest_application_document_id"], uploaded["application_document_id"])

        flattened = (
            f"{checklist_body} {upload_body} {verify_response.json()} "
            f"{upload_audit.new_value_json} {verify_audit.new_value_json}"
        )
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("doc-hash-secret", flattened)
        self.assertNotIn("document-files/private/borrower-pan.pdf", flattened)

    def test_completeness_workbench_read_returns_checklist_status_without_side_effects(self):
        application_id = self._create_and_submit_application()
        document_file = self._document_file()
        upload_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "party_id": str(self.member.member_id),
                "document_file_id": str(document_file.document_id),
                "remarks": "PAN copy received but not verified yet.",
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(upload_response.status_code, 200)
        first_pan_id = upload_response.json()["data"]["application_document_id"]
        verify_first_pan = self.client.post(
            f"/api/v1/application-documents/{first_pan_id}/verify/",
            data={"verification_status": "verified"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(verify_first_pan.status_code, 200)
        rejected_pan_file = self._document_file(file_name="borrower-pan-rejected.pdf")
        rejected_pan_upload = self.client.post(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "party_id": str(self.member.member_id),
                "document_file_id": str(rejected_pan_file.document_id),
                "remarks": "Newer PAN copy has a mismatch.",
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(rejected_pan_upload.status_code, 200)
        rejected_pan_id = rejected_pan_upload.json()["data"]["application_document_id"]
        reject_latest_pan = self.client.post(
            f"/api/v1/application-documents/{rejected_pan_id}/verify/",
            data={"verification_status": "rejected", "remarks": "Name mismatch."},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(reject_latest_pan.status_code, 200)

        response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/completeness-check/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        workbench = body["data"]
        self.assertEqual(workbench["loan_application_id"], application_id)
        self.assertEqual(workbench["application_status"], "submitted")
        self.assertFalse(workbench["can_generate_reference"])
        self.assertIsNone(workbench["application_reference_number"])
        items_by_type = {
            item["document_type"]: item for item in workbench["required_checklist_items"]
        }
        self.assertEqual(
            set(items_by_type),
            {
                "loan_application_form",
                "borrower_pan",
                "borrower_aadhaar_ovd",
                "nominee_pan",
                "nominee_aadhaar_ovd",
                "share_certificate_copy",
                "land_document_7_12",
                "crop_plan",
                "six_month_bank_statement",
            },
        )
        self.assertEqual(items_by_type["borrower_pan"]["submission_status"], "submitted")
        self.assertEqual(items_by_type["borrower_pan"]["verification_status"], "rejected")
        self.assertEqual(items_by_type["borrower_pan"]["latest_version_number"], 2)
        self.assertEqual(
            items_by_type["borrower_pan"]["latest_application_document_id"],
            rejected_pan_id,
        )
        self.assertEqual(items_by_type["borrower_pan"]["reason_code"], "not_verified")
        self.assertFalse(items_by_type["borrower_pan"]["complete"])
        self.assertEqual(items_by_type["crop_plan"]["reason_code"], "missing_metadata")
        self.assertFalse(items_by_type["crop_plan"]["complete"])
        self.assertIn("borrower_pan", workbench["blocking_document_types"])
        self.assertIn("crop_plan", workbench["blocking_document_types"])

        register_model = apps.get_model("applications", "LoanRequestRegisterEntry")
        sequence_model = apps.get_model("applications", "SystemSequence")
        self.assertEqual(register_model.objects.count(), 0)
        self.assertEqual(sequence_model.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action="applications.loan_application.reference_generated"
            ).count(),
            0,
        )

    def test_completeness_read_projects_resource_actions_from_write_validators(self):
        application_id = self._create_and_submit_application()

        blocked_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/completeness-check/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(blocked_response.status_code, 200)
        blocked_actions = {
            action["action_code"]: action
            for action in blocked_response.json()["data"]["available_actions"]
        }
        self.assertEqual(
            set(blocked_actions),
            {"pass_completeness", "return_with_deficiencies", "resolve_deficiency", "create_rejection_note"},
        )
        assert_available_actions_shape(self, list(blocked_actions.values()))
        self.assertFalse(blocked_actions["pass_completeness"]["enabled"])
        self.assertIn("document", blocked_actions["pass_completeness"]["disabled_reason"].lower())
        self.assertTrue(blocked_actions["return_with_deficiencies"]["enabled"])
        self.assertFalse(blocked_actions["resolve_deficiency"]["enabled"])
        self.assertTrue(blocked_actions["create_rejection_note"]["enabled"])

        apps.get_model("applications", "LoanApplication").objects.filter(
            loan_application_id=application_id
        ).update(received_by_user=self.reader)
        reader_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/completeness-check/",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertTrue(all(
            not action["enabled"]
            for action in reader_response.json()["data"]["available_actions"]
        ))

        self._verify_required_application_documents(application_id)
        ready_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/completeness-check/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        ready_actions = {
            action["action_code"]: action
            for action in ready_response.json()["data"]["available_actions"]
        }
        self.assertTrue(ready_actions["pass_completeness"]["enabled"])
        self.assertFalse(ready_actions["return_with_deficiencies"]["enabled"])

        deficiencies_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/deficiencies/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        deficiency_actions = {
            action["action_code"]: action
            for action in deficiencies_response.json()["data"]["available_actions"]
        }
        self.assertFalse(deficiency_actions["resolve_deficiency"]["enabled"])

        returned_id = self._create_and_submit_application(declared_purpose="Action projection return")
        returned = self.client.post(
            f"/api/v1/loan-applications/{returned_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please correct the missing document.",
                "items": [{"item_code": "borrower_pan"}],
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(returned.status_code, 200)
        returned_read = self.client.get(
            f"/api/v1/loan-applications/{returned_id}/deficiencies/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        returned_actions = {
            action["action_code"]: action
            for action in returned_read.json()["data"]["available_actions"]
        }
        self.assertTrue(returned_actions["resolve_deficiency"]["enabled"])
        self.assertFalse(returned_actions["return_with_deficiencies"]["enabled"])

        rejected_id = self._create_and_submit_application(declared_purpose="Action projection rejection")
        rejected = self.client.post(
            f"/api/v1/loan-applications/{rejected_id}/rejection-note/",
            data=self._rejection_note_payload(rejection_stage="completeness"),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(rejected.status_code, 200)
        rejected_read = self.client.get(
            f"/api/v1/loan-applications/{rejected_id}/completeness-check/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        rejected_actions = {
            action["action_code"]: action
            for action in rejected_read.json()["data"]["available_actions"]
        }
        self.assertFalse(rejected_actions["create_rejection_note"]["enabled"])
        self.assertIn("already has", rejected_actions["create_rejection_note"]["disabled_reason"])

    def test_completeness_actions_use_distinct_six_field_authority_contract(self):
        return_only_actor = self._user(
            "applications.return-only@sfpcl.example",
            "ReturnOnlyPass123!",
            self.read_permission,
            self.return_deficiency_permission,
            role_code="deputy_manager_finance",
        )
        application_id = self._create_and_submit_application(
            declared_purpose="Distinct completeness authority projection"
        )
        apps.get_model("applications", "LoanApplication").objects.filter(
            loan_application_id=application_id
        ).update(received_by_user=return_only_actor)

        response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/completeness-check/",
            headers=self._headers(
                "applications.return-only@sfpcl.example",
                "ReturnOnlyPass123!",
            ),
        )

        self.assertEqual(response.status_code, 200)
        actions = {
            action["action_code"]: action
            for action in response.json()["data"]["available_actions"]
        }
        self.assertEqual(
            {code: action["required_permission"] for code, action in actions.items()},
            {
                "pass_completeness": APPLICATION_COMPLETE_CHECK_PERMISSION,
                "return_with_deficiencies": APPLICATION_RETURN_DEFICIENCY_PERMISSION,
                "resolve_deficiency": APPLICATION_DEFICIENCY_RESOLVE_PERMISSION,
                "create_rejection_note": APPLICATION_REJECTION_NOTE_CREATE_PERMISSION,
            },
        )
        self.assertEqual(
            {code: action["required_role"] for code, action in actions.items()},
            {
                "pass_completeness": "deputy_manager_finance",
                "return_with_deficiencies": "deputy_manager_finance",
                "resolve_deficiency": "deputy_manager_finance",
                "create_rejection_note": "credit_manager",
            },
        )
        self.assertEqual(
            {code for code, action in actions.items() if action["enabled"]},
            {"return_with_deficiencies"},
        )

    def test_each_completeness_permission_projects_and_invokes_only_its_own_action(self):
        actors = {
            "pass_completeness": self._user(
                "applications.pass-only@sfpcl.example",
                "PassOnlyPass123!",
                self.read_permission,
                self.complete_check_permission,
            ),
            "return_with_deficiencies": self._user(
                "applications.return-matrix@sfpcl.example",
                "ReturnMatrixPass123!",
                self.read_permission,
                self.return_deficiency_permission,
            ),
            "resolve_deficiency": self._user(
                "applications.resolve-only@sfpcl.example",
                "ResolveOnlyPass123!",
                self.read_permission,
                self.deficiency_resolve_permission,
            ),
            "create_rejection_note": self._user(
                "applications.reject-only@sfpcl.example",
                "RejectOnlyPass123!",
                self.read_permission,
                self.rejection_note_create_permission,
            ),
        }
        passwords = {
            "pass_completeness": "PassOnlyPass123!",
            "return_with_deficiencies": "ReturnMatrixPass123!",
            "resolve_deficiency": "ResolveOnlyPass123!",
            "create_rejection_note": "RejectOnlyPass123!",
        }

        applications_by_action = {}
        pass_id = self._create_and_submit_application(declared_purpose="Pass-only authority")
        self._verify_required_application_documents(pass_id)
        applications_by_action["pass_completeness"] = (pass_id, None)

        return_id = self._create_and_submit_application(declared_purpose="Return-only authority")
        applications_by_action["return_with_deficiencies"] = (return_id, None)

        resolve_id = self._create_and_submit_application(declared_purpose="Resolve-only authority")
        returned = self.client.post(
            f"/api/v1/loan-applications/{resolve_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please replace the missing PAN copy.",
                "items": [{"item_code": "borrower_pan"}],
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(returned.status_code, 200)
        resolve_deficiency_id = returned.json()["data"]["items"][0]["deficiency_id"]
        applications_by_action["resolve_deficiency"] = (resolve_id, resolve_deficiency_id)

        reject_id = self._create_and_submit_application(declared_purpose="Reject-only authority")
        applications_by_action["create_rejection_note"] = (reject_id, None)

        loan_application_model = apps.get_model("applications", "LoanApplication")
        deficiency_model = apps.get_model("applications", "ApplicationDeficiency")
        rejection_note_model = apps.get_model("applications", "RejectionNote")
        register_model = apps.get_model("applications", "LoanRequestRegisterEntry")

        for action_code, actor in actors.items():
            with self.subTest(action_code=action_code):
                application_id, deficiency_id = applications_by_action[action_code]
                loan_application_model.objects.filter(
                    loan_application_id=application_id
                ).update(received_by_user=actor)
                headers = self._headers(actor.email, passwords[action_code])
                read = self.client.get(
                    f"/api/v1/loan-applications/{application_id}/completeness-check/",
                    headers=headers,
                )
                self.assertEqual(read.status_code, 200)
                enabled = {
                    action["action_code"]
                    for action in read.json()["data"]["available_actions"]
                    if action["enabled"]
                }
                self.assertEqual(enabled, {action_code})

                action_requests = {
                    "pass_completeness": (
                        f"/api/v1/loan-applications/{application_id}/completeness-check/pass/",
                        {},
                    ),
                    "return_with_deficiencies": (
                        f"/api/v1/loan-applications/{application_id}/return-with-deficiencies/",
                        {
                            "communication_mode": "email",
                            "message": "Please supply the missing PAN copy.",
                            "items": [{"item_code": "borrower_pan"}],
                        },
                    ),
                    "resolve_deficiency": (
                        f"/api/v1/deficiencies/{deficiency_id or uuid4()}/resolve/",
                        {"resolution_notes": "Replacement PAN verified."},
                    ),
                    "create_rejection_note": (
                        f"/api/v1/loan-applications/{application_id}/rejection-note/",
                        self._rejection_note_payload(rejection_stage="completeness"),
                    ),
                }
                own_path, own_payload = action_requests[action_code]
                own_response = self.client.post(
                    own_path,
                    data=own_payload,
                    content_type="application/json",
                    headers=headers,
                )
                self.assertEqual(own_response.status_code, 200)

                application = loan_application_model.objects.get(
                    loan_application_id=application_id
                )
                evidence_before_denials = (
                    application.application_status,
                    application.application_reference_number,
                    AuditLog.objects.count(),
                    WorkflowEvent.objects.count(),
                    deficiency_model.objects.count(),
                    rejection_note_model.objects.count(),
                    register_model.objects.count(),
                )
                for denied_code, (path, payload) in action_requests.items():
                    if denied_code == action_code:
                        continue
                    denied = self.client.post(
                        path,
                        data=payload,
                        content_type="application/json",
                        headers=headers,
                    )
                    self.assertEqual(denied.status_code, 403)
                    assert_error_envelope(self, denied.json(), "PERMISSION_DENIED")

                application.refresh_from_db()
                self.assertEqual(
                    (
                        application.application_status,
                        application.application_reference_number,
                        AuditLog.objects.count(),
                        WorkflowEvent.objects.count(),
                        deficiency_model.objects.count(),
                        rejection_note_model.objects.count(),
                        register_model.objects.count(),
                    ),
                    evidence_before_denials,
                )

    def test_completeness_pass_requires_verified_checklist_then_generates_reference(self):
        application_id = self._create_and_submit_application()
        self._verify_required_application_documents(application_id)

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/completeness-check/pass/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-completeness-pass",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        generated = body["data"]
        self.assertEqual(generated["application_reference_number"], "LO00000001")
        self.assertEqual(generated["application_status"], "reference_generated")
        self.assertEqual(generated["current_stage"], "credit_assessment")
        self.assertEqual(generated["completeness_status"], "complete")
        self.assertEqual(
            generated["loan_request_register_entry"]["application_reference_number"],
            "LO00000001",
        )
        self.assertEqual(
            generated["loan_request_register_entry"]["loan_application_id"],
            application_id,
        )

        audit = AuditLog.objects.filter(
            action="applications.loan_application.reference_generated"
        ).get()
        self.assertEqual(audit.new_value_json["request_id"], "req-completeness-pass")
        workflow_event = WorkflowEvent.objects.filter(
            entity_type="loan_application",
            from_state="submitted",
            to_state="reference_generated",
        ).get()
        self.assertEqual(str(workflow_event.entity_id), application_id)

        flattened = f"{body} {audit.old_value_json} {audit.new_value_json}"
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("doc-hash-secret", flattened)
        self.assertNotIn("document-files/private", flattened)

    def test_completeness_pass_blocks_incomplete_draft_and_duplicate_without_partial_side_effects(self):
        incomplete_id = self._create_and_submit_application()

        incomplete_response = self.client.post(
            f"/api/v1/loan-applications/{incomplete_id}/completeness-check/pass/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(incomplete_response.status_code, 400)
        incomplete_body = incomplete_response.json()
        assert_error_envelope(self, incomplete_body, "VALIDATION_ERROR")
        failing_items = incomplete_body["error"]["field_errors"]["required_checklist_items"]
        self.assertIn(
            {
                "document_type": "borrower_pan",
                "reason_code": "missing_metadata",
                "submission_status": "pending",
                "verification_status": "pending",
            },
            failing_items,
        )
        self.assertIn(
            {
                "document_type": "six_month_bank_statement",
                "reason_code": "missing_metadata",
                "submission_status": "pending",
                "verification_status": "pending",
            },
            failing_items,
        )
        register_model = apps.get_model("applications", "LoanRequestRegisterEntry")
        sequence_model = apps.get_model("applications", "SystemSequence")
        self.assertEqual(register_model.objects.count(), 0)
        self.assertEqual(sequence_model.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action="applications.loan_application.reference_generated"
            ).count(),
            0,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(to_state="reference_generated").count(),
            0,
        )

        draft_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(declared_purpose="Draft completeness attempt"),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_response.status_code, 200)
        draft_id = draft_response.json()["data"]["loan_application_id"]
        draft_pass = self.client.post(
            f"/api/v1/loan-applications/{draft_id}/completeness-check/pass/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_pass.status_code, 409)
        assert_error_envelope(self, draft_pass.json(), "INVALID_STATE_TRANSITION")
        self.assertEqual(register_model.objects.count(), 0)
        self.assertEqual(sequence_model.objects.count(), 0)

        complete_id = self._create_and_submit_application(
            declared_purpose="Complete application for duplicate guard"
        )
        self._verify_required_application_documents(complete_id)
        first_pass = self.client.post(
            f"/api/v1/loan-applications/{complete_id}/completeness-check/pass/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(first_pass.status_code, 200)
        duplicate_pass = self.client.post(
            f"/api/v1/loan-applications/{complete_id}/completeness-check/pass/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(duplicate_pass.status_code, 409)
        assert_error_envelope(self, duplicate_pass.json(), "INVALID_STATE_TRANSITION")
        self.assertEqual(register_model.objects.count(), 1)
        self.assertEqual(sequence_model.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(
                action="applications.loan_application.reference_generated"
            ).count(),
            1,
        )

    def test_return_with_deficiencies_creates_open_records_from_blocking_checklist_items(self):
        application_id = self._create_and_submit_application()
        document_file = self._document_file(file_name="borrower-pan-rejected.pdf")
        upload_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "party_id": str(self.member.member_id),
                "document_file_id": str(document_file.document_id),
                "remarks": "PAN copy has a mismatch.",
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(upload_response.status_code, 200)
        application_document_id = upload_response.json()["data"]["application_document_id"]
        reject_response = self.client.post(
            f"/api/v1/application-documents/{application_document_id}/verify/",
            data={"verification_status": "rejected", "remarks": "Name mismatch."},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(reject_response.status_code, 200)

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please submit corrected documents to proceed.",
                "items": [
                    {
                        "item_code": "borrower_pan",
                        "remarks": "PAN name does not match the member profile.",
                    },
                    {
                        "item_code": "six_month_bank_statement",
                        "remarks": "Recent bank statement is missing.",
                    },
                ],
            },
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-return-deficiencies",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        data = body["data"]
        self.assertEqual(data["loan_application_id"], application_id)
        self.assertEqual(data["application_status"], "incomplete_returned")
        self.assertEqual(data["completeness_status"], "incomplete")
        self.assertEqual(data["current_stage"], "initial_loan_request")
        self.assertIsNone(data["application_reference_number"])
        self.assertEqual(data["communication_mode"], "email")
        self.assertEqual(data["message"], "Please submit corrected documents to proceed.")
        self.assertEqual(
            [item["item_code"] for item in data["items"]],
            ["borrower_pan", "six_month_bank_statement"],
        )
        self.assertEqual(data["items"][0]["deficiency_type"], "not_verified")
        self.assertEqual(data["items"][0]["resolution_status"], "open")
        self.assertEqual(data["items"][0]["raised_by_user_id"], str(self.creator.user_id))
        self.assertIsNotNone(data["items"][0]["raised_at"])
        self.assertEqual(data["items"][1]["deficiency_type"], "missing_document")
        self.assertEqual(data["items"][1]["source_reason_code"], "missing_metadata")

        list_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/deficiencies/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()["data"]["items"], data["items"])

        deficiency_model = apps.get_model("applications", "ApplicationDeficiency")
        self.assertEqual(
            deficiency_model.objects.filter(loan_application_id=application_id).count(),
            2,
        )
        application_model = apps.get_model("applications", "LoanApplication")
        persisted_application = application_model.objects.get(loan_application_id=application_id)
        self.assertEqual(persisted_application.application_status, "incomplete_returned")
        self.assertEqual(persisted_application.completeness_status, "incomplete")
        self.assertEqual(persisted_application.current_stage, "initial_loan_request")
        register_model = apps.get_model("applications", "LoanRequestRegisterEntry")
        sequence_model = apps.get_model("applications", "SystemSequence")
        self.assertEqual(register_model.objects.count(), 0)
        self.assertEqual(sequence_model.objects.count(), 0)

        audit = AuditLog.objects.filter(
            action="applications.loan_application.returned_with_deficiencies"
        ).get()
        self.assertEqual(str(audit.entity_id), application_id)
        self.assertEqual(audit.old_value_json["application_status"], "submitted")
        self.assertEqual(audit.new_value_json["application_status"], "incomplete_returned")
        self.assertEqual(audit.new_value_json["completeness_status"], "incomplete")
        self.assertEqual(
            audit.new_value_json["deficiency_item_codes"],
            ["borrower_pan", "six_month_bank_statement"],
        )
        self.assertEqual(audit.new_value_json["request_id"], "req-return-deficiencies")
        workflow_event = WorkflowEvent.objects.filter(
            entity_type="loan_application",
            trigger_reason="Application returned with completeness deficiencies.",
        ).get()
        self.assertEqual(str(workflow_event.entity_id), application_id)
        self.assertEqual(workflow_event.from_state, "submitted")
        self.assertEqual(workflow_event.to_state, "incomplete_returned")

        detail_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(
            detail_response.json()["data"]["application_status"],
            "incomplete_returned",
        )

        repeat_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please correct the returned items.",
                "items": [{"item_code": "borrower_pan"}],
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(repeat_response.status_code, 409)
        assert_error_envelope(self, repeat_response.json(), "INVALID_STATE_TRANSITION")
        self.assertEqual(
            deficiency_model.objects.filter(loan_application_id=application_id).count(),
            2,
        )
        self.assertEqual(register_model.objects.count(), 0)
        self.assertEqual(sequence_model.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action="applications.loan_application.returned_with_deficiencies"
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                entity_type="loan_application",
                trigger_reason="Application returned with completeness deficiencies.",
            ).count(),
            1,
        )

        flattened = f"{body} {list_response.json()} {audit.old_value_json} {audit.new_value_json}"
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("doc-hash-secret", flattened)
        self.assertNotIn("document-files/private", flattened)

    def test_return_with_deficiencies_enforces_validation_state_permission_and_scope(self):
        application_id = self._create_and_submit_application()

        empty_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please correct the returned items.",
                "items": [],
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(empty_response.status_code, 400)
        assert_error_envelope(self, empty_response.json(), "VALIDATION_ERROR")
        self.assertIn("items", empty_response.json()["error"]["field_errors"])

        arbitrary_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please correct the returned items.",
                "items": [{"item_code": "invented_item"}],
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(arbitrary_response.status_code, 400)
        assert_error_envelope(self, arbitrary_response.json(), "VALIDATION_ERROR")
        self.assertEqual(
            arbitrary_response.json()["error"]["field_errors"]["items"][0]["item_code"],
            "Must match a current blocking completeness checklist item.",
        )

        draft_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(declared_purpose="Draft deficiency attempt"),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_response.status_code, 200)
        draft_id = draft_response.json()["data"]["loan_application_id"]
        draft_return = self.client.post(
            f"/api/v1/loan-applications/{draft_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please correct the returned items.",
                "items": [{"item_code": "borrower_pan"}],
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_return.status_code, 409)
        assert_error_envelope(self, draft_return.json(), "INVALID_STATE_TRANSITION")

        complete_id = self._create_and_submit_application(
            declared_purpose="Complete application for deficiency invalid state"
        )
        self._verify_required_application_documents(complete_id)
        pass_response = self.client.post(
            f"/api/v1/loan-applications/{complete_id}/completeness-check/pass/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(pass_response.status_code, 200)
        reference_return = self.client.post(
            f"/api/v1/loan-applications/{complete_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please correct the returned items.",
                "items": [{"item_code": "borrower_pan"}],
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(reference_return.status_code, 409)
        assert_error_envelope(self, reference_return.json(), "INVALID_STATE_TRANSITION")

        no_permission = self.client.post(
            f"/api/v1/loan-applications/{application_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please correct the returned items.",
                "items": [{"item_code": "borrower_pan"}],
            },
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")

        unrelated_headers = self._headers(
            "applications.unrelated@sfpcl.example",
            "UnrelatedPass123!",
        )
        scope_denied = self.client.post(
            f"/api/v1/loan-applications/{application_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please correct the returned items.",
                "items": [{"item_code": "borrower_pan"}],
            },
            content_type="application/json",
            headers=unrelated_headers,
        )
        self.assertEqual(scope_denied.status_code, 403)
        assert_error_envelope(self, scope_denied.json(), "OBJECT_ACCESS_DENIED")

        deficiency_model = apps.get_model("applications", "ApplicationDeficiency")
        self.assertEqual(deficiency_model.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action="applications.loan_application.returned_with_deficiencies"
            ).count(),
            0,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                trigger_reason="Application returned with completeness deficiencies."
            ).count(),
            0,
        )

    def test_rejection_note_create_and_send_records_metadata_only_staff_evidence(self):
        application_id = self._create_and_submit_application()

        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-create-rejection-note",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        note = body["data"]
        self.assertEqual(note["loan_application_id"], application_id)
        self.assertEqual(note["rejection_stage"], "credit_assessment")
        self.assertEqual(note["rejection_reason_category"], "eligibility")
        self.assertEqual(note["detailed_reason"], "Borrower does not meet active member criteria.")
        self.assertTrue(note["reapply_allowed_flag"])
        self.assertEqual(note["communication_mode"], "email")
        self.assertEqual(note["note_status"], "draft")
        self.assertEqual(note["prepared_by_user_id"], str(self.creator.user_id))
        self.assertIsNotNone(note["created_at"])
        self.assertIsNone(note["sent_at"])

        rejection_note_model = apps.get_model("applications", "RejectionNote")
        self.assertEqual(rejection_note_model.objects.filter(loan_application_id=application_id).count(), 1)
        application_model = apps.get_model("applications", "LoanApplication")
        persisted_application = application_model.objects.get(loan_application_id=application_id)
        self.assertEqual(persisted_application.application_status, "submitted")
        self.assertIsNone(persisted_application.application_reference_number)
        self.assertEqual(apps.get_model("applications", "LoanRequestRegisterEntry").objects.count(), 0)
        self.assertEqual(apps.get_model("applications", "SystemSequence").objects.count(), 0)

        create_audit = AuditLog.objects.filter(
            action="applications.rejection_note.created"
        ).get()
        self.assertEqual(str(create_audit.entity_id), note["rejection_note_id"])
        self.assertEqual(create_audit.entity_type, "rejection_note")
        self.assertEqual(create_audit.new_value_json["loan_application_id"], application_id)
        self.assertEqual(create_audit.new_value_json["note_status"], "draft")
        self.assertEqual(create_audit.new_value_json["request_id"], "req-create-rejection-note")
        create_event = WorkflowEvent.objects.filter(
            entity_type="rejection_note",
            to_state="draft",
        ).get()
        self.assertEqual(str(create_event.entity_id), note["rejection_note_id"])

        send_response = self.client.post(
            f"/api/v1/rejection-notes/{note['rejection_note_id']}/send/",
            data={"recipient_email": "borrower@example.com", "message_override": None},
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-send-rejection-note",
            },
        )

        self.assertEqual(send_response.status_code, 200)
        send_body = send_response.json()
        assert_success_envelope(self, send_body)
        sent_note = send_body["data"]
        self.assertEqual(sent_note["rejection_note_id"], note["rejection_note_id"])
        self.assertEqual(sent_note["note_status"], "sent")
        self.assertEqual(sent_note["sent_by_user_id"], str(self.creator.user_id))
        self.assertIsNotNone(sent_note["sent_at"])
        self.assertIsNone(sent_note["communication_id"])
        self.assertEqual(apps.get_model("applications", "LoanRequestRegisterEntry").objects.count(), 0)
        self.assertEqual(apps.get_model("applications", "SystemSequence").objects.count(), 0)

        send_audit = AuditLog.objects.filter(action="applications.rejection_note.sent").get()
        self.assertEqual(str(send_audit.entity_id), note["rejection_note_id"])
        self.assertEqual(send_audit.old_value_json["note_status"], "draft")
        self.assertEqual(send_audit.new_value_json["note_status"], "sent")
        self.assertEqual(send_audit.new_value_json["request_id"], "req-send-rejection-note")
        send_event = WorkflowEvent.objects.filter(
            entity_type="rejection_note",
            from_state="draft",
            to_state="sent",
        ).get()
        self.assertEqual(str(send_event.entity_id), note["rejection_note_id"])

        flattened = (
            f"{body} {send_body} {create_audit.new_value_json} "
            f"{send_audit.old_value_json} {send_audit.new_value_json}"
        )
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("doc-hash-secret", flattened)
        self.assertNotIn("document-files/private", flattened)

    def test_staff_application_detail_returns_nullable_rejection_note_without_portal_exposure_or_read_audit(self):
        application_id = self._create_and_submit_application()

        absent_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(absent_response.status_code, 200)
        absent_body = absent_response.json()
        assert_success_envelope(self, absent_body)
        self.assertIsNone(absent_body["data"]["rejection_note"])

        create_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        note = create_response.json()["data"]

        detail_response = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(detail_response.status_code, 200)
        detail_body = detail_response.json()
        assert_success_envelope(self, detail_body)
        detail_note = detail_body["data"]["rejection_note"]
        self.assertEqual(detail_note["rejection_note_id"], note["rejection_note_id"])
        self.assertEqual(detail_note["note_status"], "draft")
        self.assertEqual(detail_note["rejection_stage"], "credit_assessment")
        self.assertEqual(detail_note["rejection_reason_category"], "eligibility")
        self.assertTrue(detail_note["reapply_allowed_flag"])
        self.assertEqual(detail_note["prepared_by_user_id"], str(self.creator.user_id))
        self.assertEqual(detail_note["communication_mode"], "email")
        self.assertIsNone(detail_note["communication_id"])
        self.assertIsNone(detail_note["sent_by_user_id"])
        self.assertIsNone(detail_note["sent_at"])
        self.assertNotIn("detailed_reason", detail_note)
        self.assertEqual(detail_body["data"]["application_status"], "submitted")
        self.assertEqual(detail_body["data"]["available_actions"], [])

        scope_denied = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers=self._headers("applications.unrelated@sfpcl.example", "UnrelatedPass123!"),
        )
        self.assertEqual(scope_denied.status_code, 403)
        assert_error_envelope(self, scope_denied.json(), "OBJECT_ACCESS_DENIED")
        self.assertNotIn("rejection_note", json.dumps(scope_denied.json()))

        portal_detail = self.client.get(
            f"/api/v1/portal/applications/{application_id}/",
            headers={"Authorization": f"Bearer {self._portal_token()}"},
        )
        self.assertEqual(portal_detail.status_code, 200)
        portal_body = portal_detail.json()
        assert_success_envelope(self, portal_body)
        self.assertNotIn("rejection_note", portal_body["data"])

        self.assertEqual(AuditLog.objects.filter(action="applications.rejection_note.created").count(), 1)
        self.assertFalse(AuditLog.objects.filter(action="applications.loan_application.read").exists())
        self.assertEqual(WorkflowEvent.objects.filter(entity_type="rejection_note").count(), 1)

    def test_rejection_note_create_and_send_enforce_staff_permissions_and_object_scope(self):
        application_id = self._create_and_submit_application()

        no_permission = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")

        scope_denied = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers=self._headers("applications.unrelated@sfpcl.example", "UnrelatedPass123!"),
        )
        self.assertEqual(scope_denied.status_code, 403)
        assert_error_envelope(self, scope_denied.json(), "OBJECT_ACCESS_DENIED")

        portal_token = self._portal_token()
        portal_denied = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers={"Authorization": f"Bearer {portal_token}"},
        )
        self.assertEqual(portal_denied.status_code, 403)
        assert_error_envelope(self, portal_denied.json(), "PERMISSION_DENIED")

        create_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        note_id = create_response.json()["data"]["rejection_note_id"]

        portal_send_denied = self.client.post(
            f"/api/v1/rejection-notes/{note_id}/send/",
            data={"recipient_email": "borrower@example.com", "message_override": None},
            content_type="application/json",
            headers={"Authorization": f"Bearer {portal_token}"},
        )
        self.assertEqual(portal_send_denied.status_code, 403)
        assert_error_envelope(self, portal_send_denied.json(), "PERMISSION_DENIED")

        suspended_token = self._portal_token(email="suspended.portal@sfpcl.example")
        suspended_account = PortalAccount.objects.get(user__email="suspended.portal@sfpcl.example")
        suspended_account.status = PortalAccount.STATUS_SUSPENDED
        suspended_account.save(update_fields=["status"])
        suspended_create = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers={"Authorization": f"Bearer {suspended_token}"},
        )
        self.assertEqual(suspended_create.status_code, 401)
        assert_error_envelope(self, suspended_create.json(), "INVALID_TOKEN")
        suspended_send = self.client.post(
            f"/api/v1/rejection-notes/{note_id}/send/",
            data={"recipient_email": "borrower@example.com", "message_override": None},
            content_type="application/json",
            headers={"Authorization": f"Bearer {suspended_token}"},
        )
        self.assertEqual(suspended_send.status_code, 401)
        assert_error_envelope(self, suspended_send.json(), "INVALID_TOKEN")

        rejection_note_model = apps.get_model("applications", "RejectionNote")
        self.assertEqual(rejection_note_model.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="applications.rejection_note.created").count(),
            1,
        )
        self.assertFalse(AuditLog.objects.filter(action="applications.rejection_note.sent").exists())
        self.assertEqual(WorkflowEvent.objects.filter(entity_type="rejection_note").count(), 1)

    def test_rejection_note_validation_state_and_duplicate_guards_have_no_side_effects(self):
        application_id = self._create_and_submit_application()

        invalid_payload = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data={
                "rejection_stage": "",
                "rejection_reason_category": "invented",
                "detailed_reason": "",
                "reapply_allowed_flag": "yes",
                "communication_mode": "fax",
                "unexpected": "value",
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(invalid_payload.status_code, 400)
        assert_error_envelope(self, invalid_payload.json(), "VALIDATION_ERROR")
        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 0)

        draft_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(declared_purpose="Draft rejection note attempt"),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_response.status_code, 200)
        draft_id = draft_response.json()["data"]["loan_application_id"]
        draft_rejection = self.client.post(
            f"/api/v1/loan-applications/{draft_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_rejection.status_code, 409)
        assert_error_envelope(self, draft_rejection.json(), "INVALID_STATE_TRANSITION")

        referenced_id = self._create_and_submit_application(
            declared_purpose="Reference generated rejection note attempt"
        )
        reference_response = self.client.post(
            f"/api/v1/loan-applications/{referenced_id}/generate-reference/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(reference_response.status_code, 200)
        referenced_rejection = self.client.post(
            f"/api/v1/loan-applications/{referenced_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(referenced_rejection.status_code, 409)
        assert_error_envelope(self, referenced_rejection.json(), "INVALID_STATE_TRANSITION")

        create_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        note_id = create_response.json()["data"]["rejection_note_id"]
        duplicate_create = self.client.post(
            f"/api/v1/loan-applications/{application_id}/rejection-note/",
            data=self._rejection_note_payload(detailed_reason="Duplicate attempt."),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(duplicate_create.status_code, 409)
        assert_error_envelope(self, duplicate_create.json(), "INVALID_STATE_TRANSITION")

        send_response = self.client.post(
            f"/api/v1/rejection-notes/{note_id}/send/",
            data={"recipient_email": "borrower@example.com", "message_override": None},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(send_response.status_code, 200)
        duplicate_send = self.client.post(
            f"/api/v1/rejection-notes/{note_id}/send/",
            data={"recipient_email": "borrower@example.com", "message_override": None},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(duplicate_send.status_code, 400)
        assert_error_envelope(self, duplicate_send.json(), "VALIDATION_ERROR")

        self.assertEqual(apps.get_model("applications", "RejectionNote").objects.count(), 1)
        self.assertEqual(apps.get_model("applications", "LoanRequestRegisterEntry").objects.count(), 1)
        self.assertEqual(apps.get_model("applications", "SystemSequence").objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="applications.rejection_note.created").count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="applications.rejection_note.sent").count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(entity_type="rejection_note").count(),
            2,
        )

    def test_deficiency_resolve_closes_open_item_with_metadata_only_evidence(self):
        application_id = self._create_and_submit_application()
        return_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/return-with-deficiencies/",
            data={
                "communication_mode": "email",
                "message": "Please submit corrected documents to proceed.",
                "items": [{"item_code": "borrower_pan", "remarks": "PAN is missing."}],
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(return_response.status_code, 200)
        deficiency_id = return_response.json()["data"]["items"][0]["deficiency_id"]

        response = self.client.post(
            f"/api/v1/deficiencies/{deficiency_id}/resolve/",
            data={"resolution_notes": "Borrower uploaded replacement PAN and it was verified."},
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-resolve-deficiency",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        item = body["data"]
        self.assertEqual(item["deficiency_id"], deficiency_id)
        self.assertEqual(item["resolution_status"], "resolved")
        self.assertEqual(item["resolution_notes"], "Borrower uploaded replacement PAN and it was verified.")
        self.assertEqual(item["resolved_by_user_id"], str(self.creator.user_id))
        self.assertIsNotNone(item["resolved_at"])

        duplicate_resolve = self.client.post(
            f"/api/v1/deficiencies/{deficiency_id}/resolve/",
            data={"resolution_notes": "Duplicate resolution attempt."},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(duplicate_resolve.status_code, 400)
        assert_error_envelope(self, duplicate_resolve.json(), "VALIDATION_ERROR")

        no_permission = self.client.post(
            f"/api/v1/deficiencies/{deficiency_id}/resolve/",
            data={"resolution_notes": "Reader should not resolve."},
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")

        audit = AuditLog.objects.filter(action="applications.deficiency.resolved").get()
        self.assertEqual(str(audit.entity_id), deficiency_id)
        self.assertEqual(audit.new_value_json["resolution_status"], "resolved")
        self.assertEqual(audit.new_value_json["request_id"], "req-resolve-deficiency")
        workflow_event = WorkflowEvent.objects.filter(entity_type="application_deficiency").get()
        self.assertEqual(str(workflow_event.entity_id), deficiency_id)
        self.assertEqual(workflow_event.from_state, "open")
        self.assertEqual(workflow_event.to_state, "resolved")

        flattened = f"{body} {audit.old_value_json} {audit.new_value_json}"
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("doc-hash-secret", flattened)
        self.assertNotIn("document-files/private", flattened)

    def test_completeness_workbench_and_pass_enforce_permissions_and_object_scope(self):
        application_id = self._create_and_submit_application()

        missing_application = self.client.get(
            f"/api/v1/loan-applications/{uuid4()}/completeness-check/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(missing_application.status_code, 404)
        assert_error_envelope(self, missing_application.json(), "NOT_FOUND")

        no_read = self.client.get(
            f"/api/v1/loan-applications/{application_id}/completeness-check/",
            headers=self._headers("applications.plain@sfpcl.example", "PlainPass123!"),
        )
        self.assertEqual(no_read.status_code, 403)
        assert_error_envelope(self, no_read.json(), "PERMISSION_DENIED")

        no_complete = self.client.post(
            f"/api/v1/loan-applications/{application_id}/completeness-check/pass/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_complete.status_code, 403)
        assert_error_envelope(self, no_complete.json(), "PERMISSION_DENIED")

        unrelated_headers = self._headers(
            "applications.unrelated@sfpcl.example",
            "UnrelatedPass123!",
        )
        denied_read = self.client.get(
            f"/api/v1/loan-applications/{application_id}/completeness-check/",
            headers=unrelated_headers,
        )
        self.assertEqual(denied_read.status_code, 403)
        assert_error_envelope(self, denied_read.json(), "OBJECT_ACCESS_DENIED")

        denied_pass = self.client.post(
            f"/api/v1/loan-applications/{application_id}/completeness-check/pass/",
            data={"completeness_result": "complete"},
            content_type="application/json",
            headers=unrelated_headers,
        )
        self.assertEqual(denied_pass.status_code, 403)
        assert_error_envelope(self, denied_pass.json(), "OBJECT_ACCESS_DENIED")

        register_model = apps.get_model("applications", "LoanRequestRegisterEntry")
        sequence_model = apps.get_model("applications", "SystemSequence")
        self.assertEqual(register_model.objects.count(), 0)
        self.assertEqual(sequence_model.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action="applications.loan_application.reference_generated"
            ).count(),
            0,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(to_state="reference_generated").count(),
            0,
        )

    def test_application_document_endpoints_enforce_permissions_scope_and_version_history(self):
        application_id = self._create_and_submit_application()
        document_file = self._document_file()

        missing_application = self.client.get(
            f"/api/v1/loan-applications/{uuid4()}/document-checklist/",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(missing_application.status_code, 404)
        assert_error_envelope(self, missing_application.json(), "NOT_FOUND")

        no_read = self.client.get(
            f"/api/v1/loan-applications/{application_id}/document-checklist/",
            headers=self._headers("applications.plain@sfpcl.example", "PlainPass123!"),
        )
        self.assertEqual(no_read.status_code, 403)
        assert_error_envelope(self, no_read.json(), "PERMISSION_DENIED")

        no_upload = self.client.post(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "document_file_id": str(document_file.document_id),
            },
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_upload.status_code, 403)
        assert_error_envelope(self, no_upload.json(), "PERMISSION_DENIED")

        unrelated_headers = self._headers(
            "applications.unrelated@sfpcl.example",
            "UnrelatedPass123!",
        )
        denied_upload = self.client.post(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "document_file_id": str(document_file.document_id),
            },
            content_type="application/json",
            headers=unrelated_headers,
        )
        self.assertEqual(denied_upload.status_code, 403)
        assert_error_envelope(self, denied_upload.json(), "OBJECT_ACCESS_DENIED")
        application_document_model = apps.get_model("applications", "ApplicationDocument")
        self.assertEqual(application_document_model.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="applications.application_document.attached").count(),
            0,
        )

        first_upload = self.client.post(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "document_file_id": str(document_file.document_id),
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(first_upload.status_code, 200)
        second_file = self._document_file(file_name="borrower-pan-v2.pdf")
        second_upload = self.client.post(
            f"/api/v1/loan-applications/{application_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "document_file_id": str(second_file.document_id),
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(second_upload.status_code, 200)
        self.assertEqual(first_upload.json()["data"]["version_number"], 1)
        self.assertEqual(second_upload.json()["data"]["version_number"], 2)
        self.assertEqual(application_document_model.objects.count(), 2)
        self.assertEqual(
            AuditLog.objects.filter(action="applications.application_document.attached").count(),
            2,
        )

        draft_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(declared_purpose="Draft document attempt"),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_response.status_code, 200)
        draft_id = draft_response.json()["data"]["loan_application_id"]
        draft_upload = self.client.post(
            f"/api/v1/loan-applications/{draft_id}/application-documents/",
            data={
                "document_type": "borrower_pan",
                "party_type": "borrower",
                "document_file_id": str(document_file.document_id),
            },
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_upload.status_code, 400)
        assert_error_envelope(self, draft_upload.json(), "VALIDATION_ERROR")

        unknown_document = self.client.post(
            f"/api/v1/application-documents/{uuid4()}/verify/",
            data={"verification_status": "verified"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(unknown_document.status_code, 404)
        assert_error_envelope(self, unknown_document.json(), "NOT_FOUND")

    def test_submit_enforces_permissions_required_facts_and_draft_only_transition(self):
        draft_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_response.status_code, 200)
        application_id = draft_response.json()["data"]["loan_application_id"]

        no_submit_permission = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_submit_permission.status_code, 403)
        assert_error_envelope(self, no_submit_permission.json(), "PERMISSION_DENIED")

        missing_application = self.client.post(
            f"/api/v1/loan-applications/{uuid4()}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(missing_application.status_code, 404)
        assert_error_envelope(self, missing_application.json(), "NOT_FOUND")

        incomplete_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(
                required_loan_amount="",
                declared_purpose="",
                purpose_category="",
            ),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(incomplete_response.status_code, 200)
        incomplete_id = incomplete_response.json()["data"]["loan_application_id"]
        incomplete_submit = self.client.post(
            f"/api/v1/loan-applications/{incomplete_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(incomplete_submit.status_code, 400)
        incomplete_body = incomplete_submit.json()
        assert_error_envelope(self, incomplete_body, "VALIDATION_ERROR")
        self.assertIn("required_loan_amount", incomplete_body["error"]["field_errors"])
        self.assertIn("declared_purpose", incomplete_body["error"]["field_errors"])
        self.assertIn("purpose_category", incomplete_body["error"]["field_errors"])

        first_submit = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(first_submit.status_code, 200)

        second_submit = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(second_submit.status_code, 409)
        assert_error_envelope(self, second_submit.json(), "INVALID_STATE_TRANSITION")

        patch_submitted = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/",
            data={"borrower_request_notes": "Attempt edit after submit"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(patch_submitted.status_code, 400)
        patch_body = patch_submitted.json()
        assert_error_envelope(self, patch_body, "VALIDATION_ERROR")
        self.assertIn("application_status", patch_body["error"]["field_errors"])

    def test_draft_endpoints_enforce_permissions_and_validation(self):
        unauthenticated = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
        )
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        no_create = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_create.status_code, 403)
        assert_error_envelope(self, no_create.json(), "PERMISSION_DENIED")

        plain = self.client.get(
            f"/api/v1/loan-applications/{uuid4()}/",
            headers=self._headers("applications.plain@sfpcl.example", "PlainPass123!"),
        )
        self.assertEqual(plain.status_code, 403)
        assert_error_envelope(self, plain.json(), "PERMISSION_DENIED")

        cases = [
            ({"member_id": str(uuid4())}, "member_id"),
            ({"member_id": "not-a-uuid"}, "member_id"),
            ({"required_loan_amount": "0"}, "required_loan_amount"),
            ({"required_loan_amount": "-1.00"}, "required_loan_amount"),
            ({"land_holding_id": "not-a-uuid"}, "land_holding_id"),
            ({"crop_plan_id": "not-a-uuid"}, "crop_plan_id"),
            ({"bank_account_id": "not-a-uuid"}, "bank_account_id"),
            ({"cancelled_cheque_id": "not-a-uuid"}, "cancelled_cheque_id"),
        ]
        for override, field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    "/api/v1/loan-applications/",
                    data=self._draft_payload(**override),
                    content_type="application/json",
                    headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                )
                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, "VALIDATION_ERROR")
                self.assertIn(field, body["error"]["field_errors"])

    def test_epic_006_cross_role_happy_path_reaches_one_pending_sanction_case(self):
        appraisal_permissions = [
            self._permission("credit.appraisal.create", "Create appraisal"),
            self._permission("credit.appraisal.update", "Update appraisal"),
            self._permission("credit.appraisal.submit_review", "Submit appraisal review"),
            self._permission("credit.risk_assessment.manage", "Manage risk assessment"),
        ]
        self.creator.primary_role.role_code = "deputy_manager_finance"
        self.creator.primary_role.role_name = "Deputy Manager Finance"
        self.creator.primary_role.save(update_fields=["role_code", "role_name"])
        for permission in appraisal_permissions:
            RolePermission.objects.create(role=self.creator.primary_role, permission=permission)
        review_permission = self._permission("credit.appraisal.review", "Review appraisal")
        sanction_permission = self._permission(
            "credit.appraisal.submit_sanction", "Submit appraisal to sanction"
        )
        reviewer = self._user(
            "credit.manager.tracer@sfpcl.example",
            "CreditManagerTracer123!",
            self.read_permission,
            review_permission,
            role_code="credit_manager",
        )

        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        application_id = self._reference_generated_application(
            terms_acceptance_flag=True,
            required_loan_amount="15000.00",
        )
        self._create_nominee(application_id)
        preparer_headers = self._headers(
            "applications.creator@sfpcl.example", "CreatorPass123!"
        )
        eligibility_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={}, content_type="application/json", headers=preparer_headers,
        )
        self.assertEqual(eligibility_response.status_code, 200)
        eligibility = eligibility_response.json()["data"]
        self.assertEqual(eligibility["overall_result"], "eligible")

        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            valuation_per_share="2000.00",
            valuation_effective_date=timezone.localdate(),
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        self._active_loan_policy(
            share_limit_percentage="10.0000", per_share_cap_amount="200.00"
        )
        limit_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/calculate/",
            data={
                "shareholding_id": str(shareholding.shareholding_id),
                "land_holding_ids": [str(self.land.land_holding_id)],
                "crop_plan_id": str(self.crop.crop_plan_id),
                "requested_amount": "15000.00",
                "calculation_date": timezone.localdate().isoformat(),
            },
            content_type="application/json",
            headers=preparer_headers,
        )
        self.assertEqual(limit_response.status_code, 200)
        loan_limit = limit_response.json()["data"]
        self.assertTrue(loan_limit["amount_within_limit_flag"])
        self.assertFalse(loan_limit["exception_required_flag"])

        writable = {
            "borrower_summary": "Verified member and complete application.",
            "eligibility_summary": "All stored eligibility checks passed.",
            "loan_limit_summary": "Requested amount is within the frozen limit.",
            "recommended_amount": "15000.00",
            "recommended_tenure_months": 12,
            "recommended_interest_type": "floating",
            "recommended_security_summary": "Existing verified security facts reviewed.",
            "repayment_capacity_notes": "Seasonal crop proceeds cover repayment.",
            "risk_assessment": {
                "market_risk_rating": "low",
                "operational_risk_rating": "low",
                "borrower_risk_rating": "low",
                "overall_risk_rating": "low",
                "risk_mitigation_notes": "Monitor the stored crop cycle.",
            },
            "recommendation": "approve",
        }
        create_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/appraisal-note/",
            data=writable, content_type="application/json", headers=preparer_headers,
        )
        self.assertEqual(create_response.status_code, 200)
        appraisal = create_response.json()["data"]
        self.assertEqual(appraisal["eligibility_assessment_id"], eligibility["eligibility_assessment_id"])
        self.assertEqual(appraisal["loan_limit_assessment_id"], loan_limit["loan_limit_assessment_id"])
        appraisal_id = appraisal["loan_appraisal_note_id"]

        patch_response = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/appraisal-note/",
            data=writable, content_type="application/json", headers=preparer_headers,
        )
        self.assertEqual(patch_response.status_code, 200)
        submit_review = self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/submit-for-review/",
            data={"remarks": "Ready for independent review."},
            content_type="application/json", headers=preparer_headers,
        )
        self.assertEqual(submit_review.status_code, 200)

        RolePermission.objects.create(role=reviewer.primary_role, permission=sanction_permission)
        reviewer_headers = self._headers(
            "credit.manager.tracer@sfpcl.example", "CreditManagerTracer123!"
        )
        premature_sanction = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit-to-sanction-committee/",
            data={"remarks": "Reviewed state must not be bypassed."},
            content_type="application/json", headers=reviewer_headers,
        )
        self.assertEqual(premature_sanction.status_code, 409)
        self.assertEqual(
            premature_sanction.json()["error"]["code"], "INVALID_STATE_TRANSITION"
        )
        RolePermission.objects.filter(
            role=reviewer.primary_role, permission=sanction_permission
        ).delete()

        preparer_review = self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/review/",
            data={"decision": "reviewed", "review_comments": "Must be denied."},
            content_type="application/json", headers=preparer_headers,
        )
        self.assertEqual(preparer_review.status_code, 403)
        reviewer_headers = self._headers(
            "credit.manager.tracer@sfpcl.example", "CreditManagerTracer123!"
        )
        reviewed_response = self.client.post(
            f"/api/v1/appraisal-notes/{appraisal_id}/review/",
            data={"decision": "reviewed", "review_comments": "Independent review complete."},
            content_type="application/json", headers=reviewer_headers,
        )
        self.assertEqual(reviewed_response.status_code, 200)
        reviewed = reviewed_response.json()["data"]
        decision_id = reviewed["review_history"][-1]["appraisal_review_decision_id"]

        sanction_url = f"/api/v1/loan-applications/{application_id}/submit-to-sanction-committee/"
        review_only_denied = self.client.post(
            sanction_url,
            data={"remarks": "Permission boundary proof."},
            content_type="application/json", headers=reviewer_headers,
        )
        self.assertEqual(review_only_denied.status_code, 403)
        RolePermission.objects.create(role=reviewer.primary_role, permission=sanction_permission)
        reviewer_headers = self._headers(
            "credit.manager.tracer@sfpcl.example", "CreditManagerTracer123!"
        )
        sanction_response = self.client.post(
            sanction_url,
            data={"remarks": "Reviewed package ready for committee."},
            content_type="application/json", headers=reviewer_headers,
        )
        self.assertEqual(sanction_response.status_code, 200)
        sanction = sanction_response.json()["data"]
        self.assertEqual(sanction["loan_application_id"], str(application_id))
        self.assertEqual(sanction["loan_appraisal_note_id"], appraisal_id)
        self.assertEqual(sanction["appraisal_review_decision_id"], decision_id)
        self.assertEqual(sanction["submission_status"], "pending")
        self.assertFalse(sanction["exception_required_flag"])
        self.assertEqual(sanction["application_status"], "submitted_to_sanction_committee")
        self.assertEqual(sanction["appraisal_status"], "submitted_to_sanction_committee")

        readback = self.client.get(
            f"/api/v1/loan-applications/{application_id}/sanction-case/",
            headers=reviewer_headers,
        )
        self.assertEqual(readback.status_code, 200)
        self.assertEqual(readback.json()["data"], sanction)
        approval_case_model = apps.get_model("approvals", "ApprovalCase")
        counts = (
            approval_case_model.objects.count(),
            AuditLog.objects.filter(action="appraisal.submitted_to_sanction").count(),
            WorkflowEvent.objects.filter(workflow_name="sanction_submission").count(),
        )
        repeated = self.client.post(
            sanction_url,
            data={"remarks": "Must remain idempotent."},
            content_type="application/json", headers=reviewer_headers,
        )
        self.assertEqual(repeated.status_code, 409)
        self.assertEqual(repeated.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(
            counts,
            (
                approval_case_model.objects.count(),
                AuditLog.objects.filter(action="appraisal.submitted_to_sanction").count(),
                WorkflowEvent.objects.filter(workflow_name="sanction_submission").count(),
            ),
        )
        evidence = " ".join(
            str(value)
            for audit in AuditLog.objects.filter(
                action__in=[
                    "eligibility.assessed", "loan_limit.calculated",
                    "appraisal.submitted_for_review", "appraisal.reviewed",
                    "appraisal.submitted_to_sanction",
                ]
            )
            for value in (audit.old_value_json, audit.new_value_json)
        )
        for free_text in (
            writable["borrower_summary"], writable["risk_assessment"]["risk_mitigation_notes"],
            "Ready for independent review.", "Independent review complete.",
            "Reviewed package ready for committee.",
        ):
            self.assertNotIn(free_text, evidence)

    def _draft_payload(self, **overrides):
        payload = {
            "member_id": str(self.member.member_id),
            "required_loan_amount": "400000.00",
            "requested_tenure_months": 12,
            "declared_purpose": "Crop production loan for grape cultivation",
            "purpose_category": "crop_production",
            "loan_type_requested": "short_term",
            "land_holding_id": str(self.land.land_holding_id),
            "crop_plan_id": str(self.crop.crop_plan_id),
            "bank_account_id": str(self.bank.bank_account_id),
            "cancelled_cheque_id": str(self.cheque.cancelled_cheque_id),
            "borrower_request_notes": "Borrower prefers assisted digital intake.",
            "terms_acceptance_flag": False,
            "nominee_id": str(self.nominee.nominee_id),
        }
        payload.update(overrides)
        return payload

    def _create_and_submit_application(self, **payload_overrides):
        create_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(**payload_overrides),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        application_id = create_response.json()["data"]["loan_application_id"]
        submit_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(submit_response.status_code, 200)
        CropPlan.objects.filter(pk=self.crop.pk).update(loan_application_id=application_id)
        self.crop.refresh_from_db()
        return application_id

    def _reference_generated_application(self, **payload_overrides):
        application_id = self._create_and_submit_application(**payload_overrides)
        self._verify_required_application_documents(application_id)
        generate_response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/completeness-check/pass/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(generate_response.status_code, 200)
        return application_id

    def _eligible_application(self, **payload_overrides):
        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        application_id = self._reference_generated_application(
            terms_acceptance_flag=True,
            **payload_overrides,
        )
        self._create_nominee(application_id)
        response = self.client.post(
            f"/api/v1/loan-applications/{application_id}/eligibility-assessment/run/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["overall_result"], "eligible")
        return application_id

    def _active_loan_policy(self, **overrides):
        values = {
            "policy_name": "Board-approved member loan policy",
            "policy_version": "loan-policy-v1.0",
            "effective_from": timezone.localdate(),
            "short_term_duration_months": 12,
            "approval_threshold_amount": "500000.00",
            "default_scale_of_finance_per_acre_amount": "20000.00",
            "interest_rate_type": "floating",
            "rekyc_frequency_months": 24,
            "record_retention_years": 8,
            "grace_period_months": 3,
            "non_intentional_extension_months": 3,
            "board_approval_reference": "BOARD/2026/006C",
            "status": LoanPolicyConfig.STATUS_ACTIVE,
        }
        values.update(overrides)
        return LoanPolicyConfig.objects.create(**values)

    def _verify_required_application_documents(self, application_id):
        verified_ids = []
        for document_type in (
            "loan_application_form",
            "borrower_pan",
            "borrower_aadhaar_ovd",
            "nominee_pan",
            "nominee_aadhaar_ovd",
            "share_certificate_copy",
            "land_document_7_12",
            "crop_plan",
            "six_month_bank_statement",
        ):
            document_file = self._document_file(file_name=f"{document_type}.pdf")
            upload_response = self.client.post(
                f"/api/v1/loan-applications/{application_id}/application-documents/",
                data={
                    "document_type": document_type,
                    "party_type": "borrower",
                    "party_id": str(self.member.member_id),
                    "document_file_id": str(document_file.document_id),
                },
                content_type="application/json",
                headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
            )
            self.assertEqual(upload_response.status_code, 200)
            application_document_id = upload_response.json()["data"]["application_document_id"]
            verify_response = self.client.post(
                f"/api/v1/application-documents/{application_document_id}/verify/",
                data={"verification_status": "verified", "remarks": "Completeness evidence."},
                content_type="application/json",
                headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
            )
            self.assertEqual(verify_response.status_code, 200)
            verified_ids.append(application_document_id)
        return verified_ids

    def _rejection_note_payload(self, **overrides):
        payload = {
            "rejection_stage": "credit_assessment",
            "rejection_reason_category": "eligibility",
            "detailed_reason": "Borrower does not meet active member criteria.",
            "reapply_allowed_flag": True,
            "communication_mode": "email",
        }
        payload.update(overrides)
        return payload

    def _permission(self, code, name):
        return Permission.objects.create(
            permission_code=code,
            permission_name=name,
            module_name=code.split(".")[0],
            risk_level="high",
        )

    def _user(self, email, password, *permissions, role_code=None):
        role = Role.objects.create(
            role_code=role_code or email.split("@")[0].replace(".", "_"),
            role_name=email,
            is_system_role=True,
            status="active",
        )
        for permission in permissions:
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(full_name=email, email=email, status="active", primary_role=role)
        user.set_password(password)
        user.save()
        return user

    def _token(self, email, password):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _headers(self, email, password):
        return {"Authorization": f"Bearer {self._token(email, password)}"}

    def _portal_token(self, email="borrower.portal@sfpcl.example"):
        portal_user = self._user(email, "PortalPass123!", role_code=email.split("@")[0])
        PortalAccount.objects.create(
            member=self.other_member if email.startswith("suspended") else self.member,
            user=portal_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        response = self.client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": email, "password": "PortalPass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _member(self, suffix, display_name):
        return Member.objects.create(
            member_number=f"MEM-{suffix}",
            member_type="individual_farmer",
            legal_name=display_name,
            display_name=display_name,
            folio_number=f"FOL-{suffix}",
            membership_status="active",
            pan_encrypted=f"{suffix}-member-pan-token",
            pan_hash=f"{suffix}-member-pan-hash",
            aadhaar_encrypted=f"{suffix}-member-aadhaar-token",
            aadhaar_hash=f"{suffix}-member-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )

    def _document_file(self, file_name="borrower-pan.pdf"):
        return DocumentFile.objects.create(
            file_name=file_name,
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=256,
            storage_provider="local",
            storage_key=f"document-files/private/{file_name}",
            checksum_sha256="doc-hash-secret",
            uploaded_by_user=self.creator,
            sensitivity_level="restricted",
        )

    def _create_nominee(self, application_id, **overrides):
        defaults = {
            "member": self.member,
            "loan_application_id": application_id,
            "nominee_name": "Sita Patil",
            "age_at_application": 42,
            "gender": "female",
            "relationship_to_borrower": "Spouse",
            "pan_encrypted": "nominee-pan-token",
            "pan_hash": f"{application_id}-nominee-pan-hash",
            "aadhaar_encrypted": "nominee-aadhaar-token",
            "aadhaar_hash": f"{application_id}-nominee-aadhaar-hash",
            "kyc_status": "verified",
            "minor_flag": False,
        }
        defaults.update(overrides)
        return Nominee.objects.create(**defaults)
