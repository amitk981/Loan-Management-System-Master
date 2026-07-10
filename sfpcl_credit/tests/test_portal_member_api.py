import json
from uuid import uuid4

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.applications.models import ApplicationDeficiency, LoanApplication
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.models import Permission, PortalAccount, Role, RolePermission, User
from sfpcl_credit.members.models import (
    BankAccount,
    CancelledCheque,
    CropPlan,
    IndividualMemberProfile,
    KycProfile,
    LandHolding,
    Member,
    Nominee,
    Shareholding,
)
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class PortalMemberApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.portal_role = Role.objects.create(
            role_code="borrower_portal_user",
            role_name="Borrower Portal User",
            is_system_role=True,
            status="active",
        )
        self.staff_role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
            is_system_role=True,
            status="active",
        )
        self.staff_user = self._user("staff@sfpcl.example", self.staff_role)
        self.member = self._member("M-005FB", "FOL-005FB", "Ganesh Thorat")
        self.other_member = self._member("M-OTHER", "FOL-OTHER", "Other Member")
        self.portal_user = self._user(
            "ganesh.portal@sfpcl.example",
            self.portal_role,
            full_name="Ganesh Thorat",
        )
        PortalAccount.objects.create(
            member=self.member,
            user=self.portal_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        self.nominee = Nominee.objects.create(
            member=self.member,
            nominee_name="Selected Portal Nominee",
            age_at_application=42,
            gender="female",
            relationship_to_borrower="spouse",
            pan_encrypted="portal-nominee-pan-token",
            pan_hash="portal-nominee-pan-hash",
            aadhaar_encrypted="portal-nominee-aadhaar-token",
            aadhaar_hash="portal-nominee-aadhaar-hash",
            kyc_status="verified",
            minor_flag=False,
        )

    def _user(self, email, role, full_name=None, password="CorrectHorse123!"):
        user = User.objects.create(
            full_name=full_name or email,
            email=email,
            status="active",
            primary_role=role,
        )
        user.set_password(password)
        user.save()
        return user

    def _member(self, member_number, folio, name):
        return Member.objects.create(
            member_number=member_number,
            member_type="individual_farmer",
            legal_name=name,
            display_name=name,
            folio_number=folio,
            membership_start_date="2021-04-01",
            membership_status="active",
            pan_encrypted="ABCDE1234F",
            pan_hash=f"pan-{member_number}",
            aadhaar_encrypted="123456789012",
            aadhaar_hash=f"aadhaar-{member_number}",
            registered_address_line1="Village Road",
            registered_village_city="Nashik",
            registered_state="Maharashtra",
            mobile_number="+919800000042",
            email=f"{member_number.lower()}@sfpcl.example",
            kyc_status="verified",
            rekyc_due_date="2027-06-22",
            default_status="no_default",
            number_of_shares=5,
            holding_mode="physical",
            available_share_count=5,
            active_member_status="active",
            active_member_verified_at=timezone.now(),
        )

    def _portal_token(self):
        response = self.client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": self.portal_user.email, "password": "CorrectHorse123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _staff_token(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": self.staff_user.email, "password": "CorrectHorse123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def test_portal_dashboard_profile_and_supply_use_authenticated_member_scope(self):
        IndividualMemberProfile.objects.create(
            member=self.member,
            first_name="Ganesh",
            last_name="Thorat",
            primary_crop="grapes",
            land_area_under_cultivation_acres="4.50",
            services_availed_flag=True,
        )
        Nominee.objects.create(
            member=self.member,
            nominee_name="Suman Thorat",
            age_at_application=42,
            gender="female",
            relationship_to_borrower="spouse",
            pan_encrypted="ABCDE5678K",
            pan_hash="nominee-pan",
            aadhaar_encrypted="999988881234",
            aadhaar_hash="nominee-aadhaar",
            kyc_status="verified",
            minor_flag=False,
        )
        Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=5,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=5,
        )
        LandHolding.objects.create(
            member=self.member,
            document_type="7_12_extract",
            survey_number="123/4",
            village="Niphad",
            area_acres="4.50",
            document_id=uuid4(),
            verification_status="verified",
        )
        CropPlan.objects.create(
            member=self.member,
            crop_type="grapes",
            season="Kharif 2026",
            planned_area_acres="2.50",
            loan_purpose_alignment="crop_production",
            verification_status="verified",
        )
        cheque = CancelledCheque.objects.create(
            member=self.member,
            document_id=uuid4(),
            account_number_encrypted="enc:v1:12:test-digest:9012",
            account_number_hash="cheque-hash",
            account_number_last4="9012",
            ifsc="SBIN0001234",
            branch_name="Nashik Main",
            verification_status="verified",
        )
        BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.member.member_id,
            account_holder_name="Ganesh Thorat",
            account_number_encrypted="enc:v1:12:test-digest:9012",
            account_number_hash="bank-hash",
            account_number_last4="9012",
            ifsc="SBIN0001234",
            bank_name="State Bank of India",
            branch_name="Nashik Main",
            verification_status="verified",
            cancelled_cheque=cheque,
        )
        KycProfile.objects.create(
            party_type="member",
            party_id=self.member.member_id,
            kyc_status="verified",
            ckyc_consent_flag=True,
            risk_rating="low",
            rekyc_due_date="2027-06-22",
        )
        returned = LoanApplication.objects.create(
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.staff_user,
            required_loan_amount="250000.00",
            declared_purpose="Crop production",
            purpose_category="crop_production",
            application_status=LoanApplication.STATUS_INCOMPLETE_RETURNED,
            completeness_status=LoanApplication.COMPLETENESS_INCOMPLETE,
        )
        LoanApplication.objects.create(
            member=self.other_member,
            borrower_type=self.other_member.member_type,
            received_by_user=self.staff_user,
            application_status=LoanApplication.STATUS_DRAFT,
        )
        ApplicationDeficiency.objects.create(
            loan_application=returned,
            item_code="six_month_bank_statement",
            deficiency_type=ApplicationDeficiency.TYPE_MISSING_DOCUMENT,
            source_reason_code="missing_metadata",
            description="Six-month bank statement is missing.",
            resolution_status=ApplicationDeficiency.STATUS_OPEN,
            raised_by_user=self.staff_user,
            communication_mode="portal",
            message="Please upload the missing statement.",
        )

        token = self._portal_token()
        dashboard_response = self.client.get(
            f"/api/v1/portal/dashboard/?member_id={self.other_member.member_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        profile_response = self.client.get(
            f"/api/v1/portal/profile/?member_id={self.other_member.member_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        supply_response = self.client.get(
            f"/api/v1/portal/produce-supply/?member_id={self.other_member.member_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(dashboard_response.status_code, 200)
        assert_success_envelope(self, dashboard_response.json())
        dashboard = dashboard_response.json()["data"]
        self.assertEqual(dashboard["member"]["member_id"], str(self.member.member_id))
        self.assertEqual(dashboard["application_counts"]["total"], 1)
        self.assertEqual(dashboard["pending_actions"]["open_deficiencies"], 1)
        self.assertEqual(dashboard["loan_counts"]["active"], 0)
        self.assertNotIn(str(self.other_member.member_id), json.dumps(dashboard))

        self.assertEqual(profile_response.status_code, 200)
        profile = profile_response.json()["data"]
        self.assertEqual(profile["member"]["pan"], {"masked": "******234F", "can_view_full": False})
        profile_nominee = next(
            item for item in profile["nominees"] if item["nominee_name"] == "Suman Thorat"
        )
        self.assertEqual(profile_nominee["pan"]["masked"], "******678K")
        self.assertEqual(profile["bank_accounts"][0]["account_number"]["masked"], "********9012")
        self.assertEqual(profile["kyc_profile"]["kyc_status"], "verified")
        self.assertNotIn("123456789012", json.dumps(profile))

        self.assertEqual(supply_response.status_code, 200)
        supply = supply_response.json()["data"]
        self.assertEqual(supply["member_id"], str(self.member.member_id))
        self.assertEqual(supply["records"], [])
        self.assertEqual(supply["source_status"], "model_not_implemented")

    def test_staff_tokens_cannot_call_portal_own_data_apis(self):
        token = self._staff_token()
        for path in (
            "/api/v1/portal/dashboard/",
            "/api/v1/portal/profile/",
            "/api/v1/portal/produce-supply/",
        ):
            response = self.client.get(path, headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(response.status_code, 403)
            assert_error_envelope(self, response.json(), "PERMISSION_DENIED")

    def test_portal_borrower_can_create_update_submit_list_and_read_own_application_status(self):
        other_application = LoanApplication.objects.create(
            member=self.other_member,
            borrower_type=self.other_member.member_type,
            received_by_user=self.staff_user,
            required_loan_amount="100000.00",
            declared_purpose="Other member crop loan",
            purpose_category="crop_production",
            application_status=LoanApplication.STATUS_DRAFT,
        )
        token = self._portal_token()

        create_response = self.client.post(
            "/api/v1/portal/applications/",
            data={
                "member_id": str(self.member.member_id),
                "required_loan_amount": "250000.00",
                "declared_purpose": "Crop production for grapes",
                "purpose_category": "crop_production",
                "loan_type_requested": "short_term",
                "terms_acceptance_flag": True,
                "nominee_id": str(self.nominee.nominee_id),
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}", "X-Request-ID": "req-portal-create"},
        )

        self.assertEqual(create_response.status_code, 200)
        body = create_response.json()
        assert_success_envelope(self, body)
        draft = body["data"]
        self.assertEqual(draft["application_status"], "draft")
        self.assertEqual(draft["member"]["member_id"], str(self.member.member_id))
        self.assertEqual(draft["required_loan_amount"], "250000.00")
        self.assertEqual(draft["pending_with"], "Borrower")
        self.assertEqual(draft["open_deficiency_count"], 0)
        self.assertIsNone(draft["application_reference_number"])
        self.assertEqual(draft["nominee"]["nominee_id"], str(self.nominee.nominee_id))
        self.assertEqual(draft["nominee"]["nominee_name"], "Selected Portal Nominee")
        self.assertNotIn("pan", draft["nominee"])
        self.assertNotIn("aadhaar", draft["nominee"])
        self.assertNotIn("available_actions", draft)
        self.assertNotIn(str(self.other_member.member_id), str(body))

        update_response = self.client.patch(
            f"/api/v1/portal/applications/{draft['loan_application_id']}/",
            data={
                "required_loan_amount": "300000.00",
                "declared_purpose": "Updated grape crop production",
                "nominee_id": str(self.nominee.nominee_id),
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}", "X-Request-ID": "req-portal-update"},
        )
        self.assertEqual(update_response.status_code, 200)
        updated = update_response.json()["data"]
        self.assertEqual(updated["required_loan_amount"], "300000.00")
        self.assertEqual(updated["application_status"], "draft")
        self.assertEqual(updated["nominee"]["nominee_id"], str(self.nominee.nominee_id))

        submit_response = self.client.post(
            f"/api/v1/portal/applications/{draft['loan_application_id']}/submit/",
            data={"submission_notes": "Borrower confirmed application."},
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}", "X-Request-ID": "req-portal-submit"},
        )
        self.assertEqual(submit_response.status_code, 200)
        submitted = submit_response.json()["data"]
        self.assertEqual(submitted["application_status"], "submitted")
        self.assertEqual(submitted["current_stage"], "initial_loan_request")
        self.assertEqual(submitted["completeness_status"], "not_started")
        self.assertEqual(submitted["pending_with"], "SFPCL")
        self.assertIsNone(submitted["application_reference_number"])
        self.assertIsNotNone(submitted["submitted_at"])

        list_response = self.client.get(
            f"/api/v1/portal/applications/?member_id={self.other_member.member_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(list_response.status_code, 200)
        listed = list_response.json()["data"]["items"]
        self.assertEqual([item["loan_application_id"] for item in listed], [draft["loan_application_id"]])
        self.assertEqual(listed[0]["display_reference"], draft["loan_application_id"][:8].upper())

        status_response = self.client.get(
            f"/api/v1/portal/applications/{draft['loan_application_id']}/",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(status_response.status_code, 200)
        status = status_response.json()["data"]
        self.assertEqual(status["loan_application_id"], draft["loan_application_id"])
        self.assertEqual(status["timeline"][0]["event"], "Draft created")
        self.assertEqual(status["timeline"][1]["event"], "Application submitted")

        cross_read = self.client.get(
            f"/api/v1/portal/applications/{other_application.loan_application_id}/",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(cross_read.status_code, 403)
        assert_error_envelope(self, cross_read.json(), "OBJECT_ACCESS_DENIED")

        cross_create = self.client.post(
            "/api/v1/portal/applications/",
            data={
                "member_id": str(self.other_member.member_id),
                "required_loan_amount": "150000.00",
                "declared_purpose": "Other member attempt",
                "purpose_category": "crop_production",
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(cross_create.status_code, 403)
        assert_error_envelope(self, cross_create.json(), "OBJECT_ACCESS_DENIED")
        self.assertEqual(LoanApplication.objects.filter(member=self.other_member).count(), 1)

        self.assertEqual(
            AuditLog.objects.filter(action="portal.application.draft_created").count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="portal.application.saved").count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="portal.application.submitted").count(),
            1,
        )
        self.assertFalse(
            AuditLog.objects.filter(
                action__in=[
                    "applications.loan_application.created",
                    "applications.loan_application.updated",
                    "applications.loan_application.submitted",
                ]
            ).exists()
        )
        portal_audit_payloads = list(
            AuditLog.objects.filter(action__startswith="portal.application.").values_list(
                "new_value_json", flat=True
            )
        )
        flattened_audit = json.dumps(portal_audit_payloads)
        self.assertNotIn("ABCDE1234F", flattened_audit)
        self.assertNotIn("123456789012", flattened_audit)
        self.assertNotIn("CorrectHorse123!", flattened_audit)
        self.assertEqual(
            WorkflowEvent.objects.filter(entity_type="loan_application", to_state="submitted").count(),
            1,
        )

    def test_invalid_portal_nominee_create_and_patch_preserve_application_and_evidence(self):
        cross_member = Nominee.objects.create(
            member=self.other_member,
            nominee_name="Cross Member Nominee",
            age_at_application=42,
            minor_flag=False,
        )
        minor = Nominee.objects.create(
            member=self.member,
            nominee_name="Minor Nominee",
            age_at_application=16,
            minor_flag=True,
        )
        missing_age = Nominee.objects.create(
            member=self.member,
            nominee_name="Missing Age Nominee",
            age_at_application=None,
            date_of_birth=None,
            minor_flag=False,
        )
        invalid_ids = (
            cross_member.nominee_id,
            minor.nominee_id,
            missing_age.nominee_id,
            uuid4(),
        )
        token = self._portal_token()
        base_payload = {
            "required_loan_amount": "250000.00",
            "declared_purpose": "Crop production for grapes",
            "purpose_category": "crop_production",
        }

        for nominee_id in invalid_ids:
            with self.subTest(path="create", nominee_id=nominee_id):
                response = self.client.post(
                    "/api/v1/portal/applications/",
                    data={**base_payload, "nominee_id": str(nominee_id)},
                    content_type="application/json",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("nominee_id", response.json()["error"]["field_errors"])
                self.assertEqual(LoanApplication.objects.filter(member=self.member).count(), 0)
                self.assertFalse(
                    AuditLog.objects.filter(action="portal.application.draft_created").exists()
                )
                self.assertFalse(
                    WorkflowEvent.objects.filter(entity_type="loan_application").exists()
                )

        created = self.client.post(
            "/api/v1/portal/applications/",
            data={**base_payload, "nominee_id": str(self.nominee.nominee_id)},
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(created.status_code, 200)
        application_id = created.json()["data"]["loan_application_id"]
        before = self.client.get(
            f"/api/v1/portal/applications/{application_id}/",
            headers={"Authorization": f"Bearer {token}"},
        ).json()["data"]
        baseline = {
            "saved": AuditLog.objects.filter(
                action="portal.application.saved", entity_id=application_id
            ).count(),
            "workflows": WorkflowEvent.objects.filter(entity_id=application_id).count(),
        }

        for nominee_id in invalid_ids:
            with self.subTest(path="patch", nominee_id=nominee_id):
                response = self.client.patch(
                    f"/api/v1/portal/applications/{application_id}/",
                    data={"nominee_id": str(nominee_id)},
                    content_type="application/json",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("nominee_id", response.json()["error"]["field_errors"])
                after = self.client.get(
                    f"/api/v1/portal/applications/{application_id}/",
                    headers={"Authorization": f"Bearer {token}"},
                ).json()["data"]
                self.assertEqual(after, before)
                self.assertEqual(
                    AuditLog.objects.filter(
                        action="portal.application.saved", entity_id=application_id
                    ).count(),
                    baseline["saved"],
                )
                self.assertEqual(
                    WorkflowEvent.objects.filter(entity_id=application_id).count(),
                    baseline["workflows"],
                )

    def test_portal_created_application_never_projects_borrower_as_staff_owner(self):
        read_permission = Permission.objects.create(
            permission_code="applications.loan_application.read",
            permission_name="Read loan applications",
            module_name="applications",
        )
        RolePermission.objects.create(
            role=self.staff_role,
            permission=read_permission,
            granted_by_user=self.staff_user,
        )
        portal_token = self._portal_token()
        created = self.client.post(
            "/api/v1/portal/applications/",
            data={
                "required_loan_amount": "250000.00",
                "declared_purpose": "Crop production for grapes",
                "purpose_category": "crop_production",
                "nominee_id": str(self.nominee.nominee_id),
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {portal_token}"},
        )
        self.assertEqual(created.status_code, 200)
        application_id = created.json()["data"]["loan_application_id"]
        application = LoanApplication.objects.get(pk=application_id)
        self.assertEqual(application.received_by_user_id, self.portal_user.user_id)
        application.current_stage = LoanApplication.STAGE_CREDIT_ASSESSMENT
        application.save(update_fields=["current_stage"])

        staff_token = self._staff_token()
        detail = self.client.get(
            f"/api/v1/loan-applications/{application_id}/",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        listed = self.client.get(
            "/api/v1/loan-applications/",
            headers={"Authorization": f"Bearer {staff_token}"},
        )

        self.assertEqual(detail.status_code, 200)
        self.assertIsNone(detail.json()["data"]["assigned_owner"])
        self.assertEqual(listed.status_code, 200)
        item = next(
            item
            for item in listed.json()["data"]
            if item["loan_application_id"] == application_id
        )
        self.assertIsNone(item["assigned_owner"])

    def test_portal_status_marks_returned_incomplete_as_borrower_rectification_work(self):
        returned = LoanApplication.objects.create(
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.staff_user,
            required_loan_amount="250000.00",
            declared_purpose="Crop production",
            purpose_category="crop_production",
            application_status=LoanApplication.STATUS_INCOMPLETE_RETURNED,
            completeness_status=LoanApplication.COMPLETENESS_INCOMPLETE,
            current_stage=LoanApplication.STAGE_INITIAL,
        )
        ApplicationDeficiency.objects.create(
            loan_application=returned,
            item_code="six_month_bank_statement",
            deficiency_type=ApplicationDeficiency.TYPE_MISSING_DOCUMENT,
            source_reason_code="missing_metadata",
            description="Six-month bank statement is missing.",
            resolution_status=ApplicationDeficiency.STATUS_OPEN,
            raised_by_user=self.staff_user,
            communication_mode="portal",
            message="Please upload the missing statement.",
        )

        token = self._portal_token()
        response = self.client.get(
            f"/api/v1/portal/applications/{returned.loan_application_id}/",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        status = response.json()["data"]
        self.assertEqual(status["application_status"], "incomplete_returned")
        self.assertEqual(status["completeness_status"], "incomplete")
        self.assertEqual(status["current_stage"], "initial_loan_request")
        self.assertEqual(status["pending_with"], "Borrower")
        self.assertEqual(status["open_deficiency_count"], 1)
        self.assertEqual(status["borrower_action"], "Review deficiencies")
        self.assertEqual(status["deficiencies"][0]["item_code"], "six_month_bank_statement")

    def test_staff_token_cannot_call_portal_application_apis(self):
        token = self._staff_token()
        for method, path in (
            ("get", "/api/v1/portal/applications/"),
            ("post", "/api/v1/portal/applications/"),
            ("get", f"/api/v1/portal/applications/{uuid4()}/"),
            ("patch", f"/api/v1/portal/applications/{uuid4()}/"),
            ("post", f"/api/v1/portal/applications/{uuid4()}/submit/"),
        ):
            response = getattr(self.client, method)(
                path,
                data={},
                content_type="application/json",
                headers={"Authorization": f"Bearer {token}"},
            )
            self.assertEqual(response.status_code, 403)
            assert_error_envelope(self, response.json(), "PERMISSION_DENIED")

    def test_suspended_portal_account_cannot_use_existing_session_for_portal_routes(self):
        token = self._portal_token()
        account = PortalAccount.objects.get(user=self.portal_user)
        account.status = PortalAccount.STATUS_SUSPENDED
        account.save(update_fields=["status"])

        for path in (
            "/api/v1/portal/dashboard/",
            "/api/v1/portal/profile/",
            "/api/v1/portal/produce-supply/",
            "/api/v1/portal/applications/",
        ):
            response = self.client.get(path, headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(response.status_code, 401)
            assert_error_envelope(self, response.json(), "INVALID_TOKEN")

        create_response = self.client.post(
            "/api/v1/portal/applications/",
            data={
                "required_loan_amount": "250000.00",
                "declared_purpose": "Suspended account attempt",
                "purpose_category": "crop_production",
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(create_response.status_code, 401)
        assert_error_envelope(self, create_response.json(), "INVALID_TOKEN")
        self.assertEqual(LoanApplication.objects.filter(member=self.member).count(), 0)
        self.assertFalse(AuditLog.objects.filter(action__startswith="portal.application.").exists())
        self.assertFalse(WorkflowEvent.objects.exists())
