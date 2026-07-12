import json
from datetime import timedelta
from uuid import uuid4

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.applications.models import ApplicationDeficiency, LoanApplication
from sfpcl_credit.configurations.models import LoanPolicyConfig
from sfpcl_credit.credit.models import LoanLimitAssessment
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
    MemberServiceEvidence,
    Nominee,
    ProduceSupplyRecord,
    Shareholding,
    ActiveMemberStatus,
)
from sfpcl_credit.members.modules.active_member_status import ActiveMemberStatusModule
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
        self.assertNotIn("member_id", supply)
        self.assertEqual(supply["records"], [])
        self.assertEqual(supply["source_status"], "persisted_no_qualifying_verified_records")

    def test_staff_tokens_cannot_call_portal_own_data_apis(self):
        token = self._staff_token()
        for path in (
            "/api/v1/portal/dashboard/",
            "/api/v1/portal/profile/",
            "/api/v1/portal/produce-supply/",
            "/api/v1/portal/application-limit-projection/?requested_amount=250000.00",
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

    def test_portal_limit_projection_is_explicitly_unavailable_without_current_verified_authority(self):
        token = self._portal_token()

        response = self.client.get(
            "/api/v1/portal/application-limit-projection/?requested_amount=250000.00",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(
            body["data"],
            {
                "status": "unavailable",
                "unavailable_reason": "verified_active_member_authority_not_available",
                "shareholding_based_limit_amount": None,
                "land_based_limit_amount": None,
                "final_eligible_loan_amount": None,
                "requested_amount": "250000.00",
                "amount_within_limit_flag": None,
                "exception_required_flag": None,
                "calculated_as_of_date": None,
                "calculation_rule_version": None,
            },
        )
        serialized = json.dumps(body)
        self.assertNotIn(str(self.member.member_id), serialized)
        self.assertNotIn("available_actions", serialized)

    def test_portal_limit_projection_uses_current_verified_facts_and_redacts_internal_authority(self):
        today = timezone.localdate()
        calculation_date = today - timedelta(days=1)
        IndividualMemberProfile.objects.create(
            member=self.member,
            first_name="Ganesh",
            last_name="Thorat",
            land_area_under_cultivation_acres="4.50",
        )
        MemberServiceEvidence.objects.create(
            member=self.member,
            service_type="employment",
            recipient_entity_type="subsidiary",
            recipient_entity_id=uuid4(),
            service_from=calculation_date - timedelta(days=1096),
            service_to=calculation_date,
            evidence_reference="PRIVATE-EVIDENCE-REF",
            verified_by_user=self.staff_user,
            verified_at=timezone.now(),
        )
        result = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id,
            as_of_date=calculation_date,
        )
        authority = ActiveMemberStatus.objects.create(
            member=self.member,
            result_id=result.result_id,
            status="active",
            member_type=self.member.member_type,
            services_availed_flag=result.services_availed,
            continuous_supply_years=result.continuous_supply_years,
            evidence_summary="PRIVATE DECISION REASON",
            evidence_snapshot=result.to_snapshot(),
            verified_by_user=self.staff_user,
            verified_at=timezone.now(),
            effective_from=calculation_date,
        )
        self.member.active_member_status_id = authority.active_member_status_id
        self.member.save(update_fields=["active_member_status_id"])
        Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=5,
            holding_mode="physical",
            valuation_per_share="100000.00",
            valuation_effective_date=calculation_date,
            pledged_share_count=0,
            available_share_count=5,
            status="active",
        )
        LandHolding.objects.create(
            member=self.member,
            document_type="7_12_extract",
            survey_number="123/4",
            area_acres="4.50",
            document_id=uuid4(),
            verification_status="verified",
            verified_by_user=self.staff_user,
            verified_at=timezone.now(),
        )
        LoanPolicyConfig.objects.create(
            policy_name="Board policy",
            policy_version="portal-limit-v1",
            effective_from=calculation_date,
            short_term_duration_months=12,
            approval_threshold_amount="500000.00",
            default_scale_of_finance_per_acre_amount="20000.00",
            share_limit_percentage="30.0000",
            per_share_cap_amount=None,
            interest_rate_type="fixed",
            rekyc_frequency_months=24,
            record_retention_years=8,
            grace_period_months=1,
            non_intentional_extension_months=3,
            board_approval_reference="BOARD-2026-01",
            status=LoanPolicyConfig.STATUS_ACTIVE,
        )
        token = self._portal_token()

        unchanged = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id,
            as_of_date=calculation_date,
        )
        self.assertEqual(unchanged.result_id, result.result_id)
        self.assertEqual(unchanged.to_snapshot(), authority.evidence_snapshot)

        response = self.client.get(
            "/api/v1/portal/application-limit-projection/?requested_amount=95000.00",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["status"], "available")
        self.assertEqual(data["shareholding_based_limit_amount"], "150000.00")
        self.assertEqual(data["land_based_limit_amount"], "90000.00")
        self.assertEqual(data["final_eligible_loan_amount"], "90000.00")
        self.assertEqual(data["amount_within_limit_flag"], False)
        self.assertEqual(data["exception_required_flag"], True)
        self.assertEqual(data["calculated_as_of_date"], calculation_date.isoformat())
        self.assertEqual(data["calculation_rule_version"], "portal-limit-v1")
        serialized = json.dumps(data)
        for secret in (
            str(self.member.member_id),
            str(authority.active_member_status_id),
            result.result_id,
            "PRIVATE-EVIDENCE-REF",
            "PRIVATE DECISION REASON",
            str(self.staff_user.user_id),
            "available_actions",
        ):
            self.assertNotIn(secret, serialized)

    def test_portal_limit_projection_keeps_stored_date_policy_authority_after_reload(self):
        calculation_date = timezone.localdate() - timedelta(days=1)
        IndividualMemberProfile.objects.create(
            member=self.member, first_name="Ganesh", last_name="Thorat",
            land_area_under_cultivation_acres="4.50",
        )
        MemberServiceEvidence.objects.create(
            member=self.member, service_type="employment", recipient_entity_type="subsidiary",
            recipient_entity_id=uuid4(), service_from=calculation_date - timedelta(days=1096),
            service_to=calculation_date, evidence_reference="RELOAD-EVIDENCE",
            verified_by_user=self.staff_user, verified_at=timezone.now(),
        )
        result = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id, as_of_date=calculation_date,
        )
        authority = ActiveMemberStatus.objects.create(
            member=self.member, result_id=result.result_id, status="active",
            member_type=self.member.member_type, services_availed_flag=result.services_availed,
            continuous_supply_years=result.continuous_supply_years,
            evidence_summary="Reload decision",
            evidence_snapshot=result.to_snapshot(), verified_by_user=self.staff_user,
            verified_at=timezone.now(), effective_from=calculation_date,
        )
        self.member.active_member_status_id = authority.active_member_status_id
        self.member.save(update_fields=["active_member_status_id"])
        Shareholding.objects.create(
            member=self.member, folio_number=self.member.folio_number, number_of_shares=5,
            holding_mode="physical", valuation_per_share="100000.00",
            valuation_effective_date=calculation_date, pledged_share_count=0,
            available_share_count=5, status="active",
        )
        LandHolding.objects.create(
            member=self.member, document_type="7_12_extract", area_acres="4.50",
            document_id=uuid4(), verification_status="verified",
            verified_by_user=self.staff_user, verified_at=timezone.now(),
        )
        for version, effective_from, scale in (
            ("stored-v1", calculation_date, "20000.00"),
            ("later-v2", calculation_date + timedelta(days=1), "30000.00"),
        ):
            LoanPolicyConfig.objects.create(
                policy_name=version, policy_version=version, effective_from=effective_from,
                short_term_duration_months=12, approval_threshold_amount="500000.00",
                default_scale_of_finance_per_acre_amount=scale,
                share_limit_percentage="30.0000", per_share_cap_amount=None,
                interest_rate_type="fixed",
                rekyc_frequency_months=24, record_retention_years=8, grace_period_months=1,
                non_intentional_extension_months=3, board_approval_reference=version,
                status=LoanPolicyConfig.STATUS_ACTIVE,
            )
        token = self._portal_token()
        reloaded_result = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id, as_of_date=calculation_date,
        )
        self.assertEqual(reloaded_result.result_id, result.result_id)
        self.assertEqual(reloaded_result.to_snapshot(), authority.evidence_snapshot)
        from sfpcl_credit.configurations.modules.configuration_resolver import resolve_effective_loan_policy
        self.assertEqual(resolve_effective_loan_policy(calculation_date=calculation_date).policy_version, "stored-v1")
        before = self._portal_limit_evidence()

        first = self.client.get(
            "/api/v1/portal/application-limit-projection/?requested_amount=95000.00",
            headers={"Authorization": f"Bearer {token}"},
        )
        second = self.client.get(
            "/api/v1/portal/application-limit-projection/?requested_amount=95000.00",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.json()["data"], first.json()["data"])
        self.assertEqual(first.json()["data"]["calculation_rule_version"], "stored-v1")
        self.assertEqual(first.json()["data"]["land_based_limit_amount"], "90000.00")
        self.assertEqual(self._portal_limit_evidence(), before)

        def assert_unavailable_without_write(case):
            denied_before = self._portal_limit_evidence()
            denied = self.client.get(
                "/api/v1/portal/application-limit-projection/?requested_amount=95000.00",
                headers={"Authorization": f"Bearer {token}"},
            )
            self.assertEqual(denied.status_code, 200, case)
            self.assertEqual(denied.json()["data"]["status"], "unavailable", case)
            self.assertNotIn(str(self.member.member_id), json.dumps(denied.json()), case)
            self.assertEqual(self._portal_limit_evidence(), denied_before, case)

        with self.subTest(case="future authority"):
            authority.effective_from = timezone.localdate() + timedelta(days=1)
            authority.save(update_fields=["effective_from"])
            assert_unavailable_without_write("future authority")
            authority.effective_from = calculation_date
            authority.save(update_fields=["effective_from"])
        with self.subTest(case="closed authority"):
            authority.effective_to = calculation_date
            authority.save(update_fields=["effective_to"])
            assert_unavailable_without_write("closed authority")
            authority.effective_to = None
            authority.save(update_fields=["effective_to"])
        with self.subTest(case="manual authority"):
            authority.status = "manual"
            authority.save(update_fields=["status"])
            assert_unavailable_without_write("manual authority")
            authority.status = "active"
            authority.save(update_fields=["status"])
        with self.subTest(case="mismatched authority"):
            original_result_id = authority.result_id
            authority.result_id = uuid4()
            authority.save(update_fields=["result_id"])
            assert_unavailable_without_write("mismatched authority")
            authority.result_id = original_result_id
            authority.save(update_fields=["result_id"])
        with self.subTest(case="changed service provenance"):
            evidence = MemberServiceEvidence.objects.get(member=self.member)
            evidence.evidence_reference = "CHANGED-EVIDENCE"
            evidence.save(update_fields=["evidence_reference"])
            assert_unavailable_without_write("changed service provenance")
            evidence.evidence_reference = "RELOAD-EVIDENCE"
            evidence.save(update_fields=["evidence_reference"])
        with self.subTest(case="duplicate shareholding"):
            duplicate = Shareholding.objects.create(
                member=self.member, folio_number="DUPLICATE", number_of_shares=1,
                holding_mode="physical", valuation_per_share="1.00",
                valuation_effective_date=calculation_date, pledged_share_count=0,
                available_share_count=1, status="active",
            )
            assert_unavailable_without_write("duplicate shareholding")
            duplicate.delete()
        with self.subTest(case="contradictory profile land"):
            profile = IndividualMemberProfile.objects.get(member=self.member)
            profile.land_area_under_cultivation_acres = "4.00"
            profile.save(update_fields=["land_area_under_cultivation_acres"])
            assert_unavailable_without_write("contradictory profile land")
            profile.land_area_under_cultivation_acres = "4.50"
            profile.save(update_fields=["land_area_under_cultivation_acres"])
        with self.subTest(case="no effective policy"):
            stored_policy = LoanPolicyConfig.objects.get(policy_version="stored-v1")
            stored_policy.status = LoanPolicyConfig.STATUS_RETIRED
            stored_policy.save(update_fields=["status"])
            assert_unavailable_without_write("no effective policy")
            stored_policy.status = LoanPolicyConfig.STATUS_ACTIVE
            stored_policy.save(update_fields=["status"])

    def test_portal_limit_denials_are_redacted_and_zero_write(self):
        token = self._portal_token()
        invalid_amounts = ("0", "-1", "not-money", "NaN", "Infinity")
        for requested in invalid_amounts:
            with self.subTest(requested=requested):
                before = self._portal_limit_evidence()
                response = self.client.get(
                    f"/api/v1/portal/application-limit-projection/?requested_amount={requested}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 400)
                assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
                self.assertEqual(set(response.json()["error"]["field_errors"]), {"requested_amount"})
                self.assertNotIn(str(self.member.member_id), json.dumps(response.json()))
                self.assertEqual(self._portal_limit_evidence(), before)

    def _arrange_complete_portal_limit_projection(self):
        token = self._portal_token()
        calculation_date = timezone.localdate() - timedelta(days=1)
        profile = IndividualMemberProfile.objects.create(
            member=self.member, first_name="Ganesh", last_name="Thorat",
            land_area_under_cultivation_acres="4.50",
        )
        service = MemberServiceEvidence.objects.create(
            member=self.member, service_type="employment", recipient_entity_type="subsidiary",
            recipient_entity_id=uuid4(), service_from=calculation_date - timedelta(days=1096),
            service_to=calculation_date, evidence_reference="MATRIX-SERVICE-EVIDENCE",
            verified_by_user=self.staff_user, verified_at=timezone.now(),
        )
        supply = ProduceSupplyRecord.objects.create(
            member=self.member, financial_year="2025-26", supplied_to_entity_type="other",
            supplied_to_entity_id=uuid4(), supply_route="direct", crop_type="grapes",
            quantity="1.000", value_amount="100.00", evidence_reference="MATRIX-SUPPLY-EVIDENCE",
            verified_flag=True, captured_by_user=self.staff_user,
            verified_by_user=self.staff_user, verified_at=timezone.now(),
        )
        result = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id, as_of_date=calculation_date,
        )
        authority = ActiveMemberStatus.objects.create(
            member=self.member, result_id=result.result_id, status="active",
            member_type=self.member.member_type, services_availed_flag=result.services_availed,
            continuous_supply_years=result.continuous_supply_years,
            evidence_summary="MATRIX PRIVATE AUTHORITY", evidence_snapshot=result.to_snapshot(),
            verified_by_user=self.staff_user, verified_at=timezone.now(),
            effective_from=calculation_date,
        )
        self.member.active_member_status_id = authority.active_member_status_id
        self.member.save(update_fields=["active_member_status_id"])
        shareholding = Shareholding.objects.create(
            member=self.member, folio_number=self.member.folio_number, number_of_shares=5,
            holding_mode="physical", valuation_per_share="100000.00",
            valuation_effective_date=calculation_date, pledged_share_count=0,
            available_share_count=5, status="active",
        )
        landholding = LandHolding.objects.create(
            member=self.member, document_type="7_12_extract", area_acres="4.50",
            document_id=uuid4(), verification_status="verified",
            verified_by_user=self.staff_user, verified_at=timezone.now(),
        )
        policy = LoanPolicyConfig.objects.create(
            policy_name="Matrix policy", policy_version="matrix-v1",
            effective_from=calculation_date, short_term_duration_months=12,
            approval_threshold_amount="500000.00",
            default_scale_of_finance_per_acre_amount="20000.00",
            share_limit_percentage="30.0000", per_share_cap_amount=None,
            interest_rate_type="fixed", rekyc_frequency_months=24,
            record_retention_years=8, grace_period_months=1,
            non_intentional_extension_months=3,
            board_approval_reference="MATRIX-BOARD-PRIVATE", status=LoanPolicyConfig.STATUS_ACTIVE,
        )
        return token, authority, supply, service, profile, landholding, shareholding, policy

    def _assert_portal_limit_unavailable_without_write(self, token):
        before = self._portal_limit_evidence()
        response = self.client.get(
            "/api/v1/portal/application-limit-projection/?requested_amount=95000.00",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        assert_success_envelope(self, response.json())
        self.assertEqual(response.json()["data"], {
            "status": "unavailable",
            "unavailable_reason": "verified_active_member_authority_not_available",
            "shareholding_based_limit_amount": None,
            "land_based_limit_amount": None,
            "final_eligible_loan_amount": None,
            "requested_amount": "95000.00",
            "amount_within_limit_flag": None,
            "exception_required_flag": None,
            "calculated_as_of_date": None,
            "calculation_rule_version": None,
        })
        serialized = json.dumps(response.json())
        for private_value in self._portal_limit_private_values():
            self.assertNotIn(private_value, serialized)
        self.assertEqual(self._portal_limit_evidence(), before)

    def _portal_limit_private_values(self):
        values = [str(self.member.member_id), str(self.staff_user.user_id), "available_actions"]
        values.extend(str(value) for value in ActiveMemberStatus.objects.values_list(
            "active_member_status_id", "result_id"
        ).first() or ())
        values.extend(ProduceSupplyRecord.objects.values_list("evidence_reference", flat=True))
        values.extend(MemberServiceEvidence.objects.values_list("evidence_reference", flat=True))
        values.extend(str(value) for value in LoanPolicyConfig.objects.values_list(
            "loan_policy_config_id", flat=True
        ))
        values.extend(LoanPolicyConfig.objects.values_list("board_approval_reference", flat=True))
        return [value for value in values if value]

    def test_portal_limit_denies_stale_authority_snapshot_without_write(self):
        token, authority, *_ = self._arrange_complete_portal_limit_projection()
        authority.evidence_snapshot = {**authority.evidence_snapshot, "continuous_supply_years": 99}
        authority.save(update_fields=["evidence_snapshot"])
        self._assert_portal_limit_unavailable_without_write(token)

    def test_portal_limit_denies_changed_supply_provenance_without_write(self):
        token, _, supply, *_ = self._arrange_complete_portal_limit_projection()
        supply.evidence_reference = "CHANGED-SUPPLY-PRIVATE"
        supply.save(update_fields=["evidence_reference"])
        self._assert_portal_limit_unavailable_without_write(token)

    def test_portal_limit_denies_missing_profile_without_write(self):
        token, _, _, _, profile, *_ = self._arrange_complete_portal_limit_projection()
        profile.delete()
        self._assert_portal_limit_unavailable_without_write(token)

    def test_portal_limit_denies_missing_landholding_without_write(self):
        token, _, _, _, _, landholding, *_ = self._arrange_complete_portal_limit_projection()
        landholding.delete()
        self._assert_portal_limit_unavailable_without_write(token)

    def test_portal_limit_denies_contradictory_profile_land_facts_without_write(self):
        token, _, _, _, profile, *_ = self._arrange_complete_portal_limit_projection()
        profile.land_area_under_cultivation_acres = "4.00"
        profile.save(update_fields=["land_area_under_cultivation_acres"])
        self._assert_portal_limit_unavailable_without_write(token)

    def _portal_limit_evidence(self):
        return {
            "member": list(Member.objects.filter(pk=self.member.pk).values()),
            "authority": list(ActiveMemberStatus.objects.filter(member=self.member).values()),
            "supply": list(ProduceSupplyRecord.objects.filter(member=self.member).values()),
            "service_evidence": list(
                MemberServiceEvidence.objects.filter(member=self.member).values()
            ),
            "shareholdings": list(Shareholding.objects.filter(member=self.member).values()),
            "landholdings": list(LandHolding.objects.filter(member=self.member).values()),
            "individual_profile": list(
                IndividualMemberProfile.objects.filter(member=self.member).values()
            ),
            "assessments": list(LoanLimitAssessment.objects.filter(member=self.member).values()),
            "applications": list(LoanApplication.objects.filter(member=self.member).values()),
            "audits": list(AuditLog.objects.all().values()),
            "workflows": list(WorkflowEvent.objects.all().values()),
            "policies": list(LoanPolicyConfig.objects.all().values()),
        }

    def test_portal_limit_zero_write_ledger_covers_every_required_state_category(self):
        self.assertEqual(
            set(self._portal_limit_evidence()),
            {
                "member",
                "authority",
                "supply",
                "service_evidence",
                "shareholdings",
                "landholdings",
                "individual_profile",
                "assessments",
                "applications",
                "policies",
                "audits",
                "workflows",
            },
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
