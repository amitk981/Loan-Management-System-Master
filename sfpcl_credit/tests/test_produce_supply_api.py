from django.test import Client, TestCase

from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog, Permission, PortalAccount, Role, RolePermission, User
from sfpcl_credit.credit.modules.eligibility_assessment import _active_member_check
from sfpcl_credit.members.models import IndividualMemberProfile, Member, MemberChangeHistory, ProduceSupplyRecord


class ProduceSupplyApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.capture_permission = Permission.objects.create(
            permission_code="members.active_status.calculate",
            permission_name="Calculate active member status",
            module_name="members",
            risk_level="medium",
        )
        self.actor = self._user("capture@sfpcl.example", self.capture_permission)
        self.member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Synthetic Farmer",
            display_name="Synthetic Farmer",
            folio_number="FOL-SUPPLY",
            membership_status="active",
            pan_encrypted="ABCDE1234F",
            pan_hash="supply-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        IndividualMemberProfile.objects.create(
            member=self.member,
            first_name="Synthetic",
            last_name="Farmer",
            services_availed_flag=True,
        )

    def _user(self, email, *permissions):
        role = Role.objects.create(
            role_code=email.split("@")[0], role_name=email, status="active"
        )
        for permission in permissions:
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=email, email=email, status="active", primary_role=role
        )
        user.set_password("SupplyPass123!")
        user.save()
        return user

    def _headers(self, email="capture@sfpcl.example"):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": "SupplyPass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

    def test_staff_can_capture_source_backed_supply_record(self):
        response = self.client.post(
            f"/api/v1/members/{self.member.member_id}/produce-supply-records/",
            data={
                "financial_year": "2025-26",
                "supplied_to_entity_type": "sfpcl",
                "supply_route": "direct",
                "crop_type": "grapes",
                "quantity": "1250.500",
                "value_amount": "240000.00",
                "evidence_reference": "ERP-SYNTHETIC-001",
            },
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["member_id"], str(self.member.member_id))
        self.assertEqual(data["financial_year"], "2025-26")
        self.assertEqual(data["quantity"], "1250.500")
        self.assertFalse(data["verified_flag"])
        self.assertEqual(data["version"], 1)
        self.assertEqual(
            data["available_actions"][0],
            {
                "action_code": "members.active_status.verify",
                "label": "Verify supply record",
                "enabled": False,
                "disabled_reason": "The record maker cannot verify this supply record.",
                "required_permission": "members.active_status.verify",
                "required_role": None,
            },
        )
        plain = self._user("plain.supply@sfpcl.example")
        denied = self.client.post(
            f"/api/v1/members/{self.member.member_id}/produce-supply-records/",
            data={"financial_year": "2024-25", "supplied_to_entity_type": "sfpcl", "supply_route": "direct"},
            content_type="application/json", headers=self._headers(plain.email),
        )
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(ProduceSupplyRecord.objects.count(), 1)

    def test_separate_checker_verifies_with_optimistic_version_and_maker_is_denied(self):
        verify_permission = Permission.objects.create(
            permission_code="members.active_status.verify",
            permission_name="Verify active member status",
            module_name="members",
            risk_level="high",
        )
        checker = self._user("checker@sfpcl.example", verify_permission)
        record = ProduceSupplyRecord.objects.create(
            member=self.member,
            financial_year="2025-26",
            supplied_to_entity_type="sfpcl",
            supply_route="direct",
            crop_type="grapes",
            captured_by_user=self.actor,
        )

        denied = self.client.post(
            f"/api/v1/produce-supply-records/{record.produce_supply_record_id}/verify/",
            data={"version": 1}, content_type="application/json", headers=self._headers(),
        )
        self.assertEqual(denied.status_code, 403)
        record.refresh_from_db()
        self.assertFalse(record.verified_flag)

        verified = self.client.post(
            f"/api/v1/produce-supply-records/{record.produce_supply_record_id}/verify/",
            data={"version": 1}, content_type="application/json",
            headers=self._headers(checker.email),
        )
        self.assertEqual(verified.status_code, 200)
        self.assertTrue(verified.json()["data"]["verified_flag"])
        self.assertEqual(verified.json()["data"]["version"], 2)
        evidence_counts = (
            AuditLog.objects.filter(action="members.produce_supply.verified").count(),
            MemberChangeHistory.objects.filter(change_type="produce_supply_verified").count(),
        )

        stale = self.client.post(
            f"/api/v1/produce-supply-records/{record.produce_supply_record_id}/verify/",
            data={"version": 1}, content_type="application/json",
            headers=self._headers(checker.email),
        )
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.json()["error"]["code"], "STALE_WRITE")
        self.assertEqual(
            evidence_counts,
            (
                AuditLog.objects.filter(action="members.produce_supply.verified").count(),
                MemberChangeHistory.objects.filter(change_type="produce_supply_verified").count(),
            ),
        )

    def test_active_member_check_uses_four_continuous_verified_supply_years(self):
        for financial_year, verified in [
            ("2022-23", True), ("2023-24", True), ("2024-25", True), ("2025-26", True),
            ("2021-22", False),
        ]:
            ProduceSupplyRecord.objects.create(
                member=self.member, financial_year=financial_year,
                supplied_to_entity_type="sfpcl", supply_route="direct",
                captured_by_user=self.actor, verified_flag=verified,
            )

        result = _active_member_check(self.member)

        self.assertEqual(result["member_active_check"], "pass")
        self.assertIn("four continuous verified financial years", result["assessment_notes"])

        ProduceSupplyRecord.objects.filter(financial_year="2024-25").update(verified_flag=False)
        self.assertEqual(
            _active_member_check(self.member)["member_active_check"],
            "manual_evidence_required",
        )

    def test_portal_supply_is_read_only_and_scoped_from_portal_account(self):
        portal_role = Role.objects.create(
            role_code="borrower_portal_user", role_name="Borrower Portal User", status="active"
        )
        portal_user = User.objects.create(
            full_name="Portal Farmer", email="portal.supply@sfpcl.example",
            status="active", primary_role=portal_role,
        )
        portal_user.set_password("PortalSupply123!")
        portal_user.save()
        PortalAccount.objects.create(
            member=self.member, user=portal_user, status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        ProduceSupplyRecord.objects.create(
            member=self.member, financial_year="2025-26", supplied_to_entity_type="sfpcl",
            supply_route="direct", quantity="10.000", value_amount="500.00",
            captured_by_user=self.actor, verified_flag=True,
        )
        other = Member.objects.create(
            member_type="individual_farmer", legal_name="Other Synthetic Farmer",
            display_name="Other Synthetic Farmer", folio_number="FOL-OTHER-SUPPLY",
            membership_status="active", pan_encrypted="ABCDE9999F",
            pan_hash="other-supply-pan", kyc_status="verified", default_status="no_default",
        )
        ProduceSupplyRecord.objects.create(
            member=other, financial_year="2024-25", supplied_to_entity_type="sfpcl",
            supply_route="direct", captured_by_user=self.actor, verified_flag=True,
        )
        login = self.client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": portal_user.email, "password": "PortalSupply123!"},
            content_type="application/json",
        )
        token = login.json()["data"]["access_token"]

        response = self.client.get(
            f"/api/v1/portal/produce-supply/?member_id={other.member_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual([row["financial_year"] for row in data["records"]], ["2025-26"])
        self.assertNotIn("member_id", data)
        self.assertNotIn("available_actions", data["records"][0])
        self.assertEqual(data["summary"]["total_quantity"], "10.000")
        self.assertEqual(data["source_status"], "persisted_verified_records")
