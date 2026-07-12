from django.test import Client, TestCase

from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog, Permission, PortalAccount, Role, RolePermission, User
from sfpcl_credit.members.modules.active_member_status import ActiveMemberStatusModule
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
                "version": self.member.version,
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

    def test_public_active_member_projection_requires_service_and_qualifying_continuity(self):
        for financial_year, verified in [
            ("2022-23", True), ("2023-24", True), ("2024-25", True), ("2025-26", True),
            ("2021-22", False),
        ]:
            ProduceSupplyRecord.objects.create(
                member=self.member, financial_year=financial_year,
                supplied_to_entity_type="sfpcl", supply_route="direct",
                evidence_reference=f"ERP-{financial_year}", captured_by_user=self.actor, verified_flag=verified,
            )

        result = ActiveMemberStatusModule().calculate(member_id=self.member.member_id)

        self.assertEqual(result.member_active_check, "pass")
        self.assertEqual(result.continuous_supply_years, 4)
        self.assertEqual(len(result.supply_rows), 5)
        self.assertEqual(sum(row.qualifying for row in result.supply_rows), 4)

        ProduceSupplyRecord.objects.filter(financial_year="2024-25").update(verified_flag=False)
        self.assertEqual(
            ActiveMemberStatusModule().calculate(member_id=self.member.member_id).member_active_check,
            "manual_evidence_required",
        )

        self.member.individual_profile.services_availed_flag = False
        self.member.individual_profile.save(update_fields=["services_availed_flag"])
        self.member.active_member_status = "active"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])
        ProduceSupplyRecord.objects.filter(financial_year="2024-25").update(verified_flag=True)
        self.assertEqual(
            ActiveMemberStatusModule().calculate(member_id=self.member.member_id).member_active_check,
            "manual_evidence_required",
        )

    def test_capture_rejects_non_object_unknown_stale_and_non_qualifying_facts(self):
        url = f"/api/v1/members/{self.member.member_id}/produce-supply-records/"
        headers = self._headers()
        cases = [
            (["not", "an", "object"], "non_field_errors"),
            ({"financial_year": "2025-26", "supplied_to_entity_type": "sfpcl", "supply_route": "direct", "evidence_reference": "ERP-1", "version": self.member.version, "extra": True}, "extra"),
            ({"financial_year": "25-26", "supplied_to_entity_type": "sfpcl", "supply_route": "direct", "evidence_reference": "ERP-1", "version": self.member.version}, "financial_year"),
            ({"financial_year": "2025-26", "supplied_to_entity_type": "unknown", "supply_route": "direct", "evidence_reference": "ERP-1", "version": self.member.version}, "supplied_to_entity_type"),
            ({"financial_year": "2025-26", "supplied_to_entity_type": "sfpcl", "supply_route": "producer_institution", "evidence_reference": "ERP-1", "version": self.member.version}, "producer_institution_member_id"),
            ({"financial_year": "2025-26", "supplied_to_entity_type": "sfpcl", "supply_route": "direct", "evidence_reference": "ERP-1", "quantity": "-1", "version": self.member.version}, "quantity"),
            ({"financial_year": "2025-26", "supplied_to_entity_type": "sfpcl", "supply_route": "direct", "evidence_reference": "", "version": self.member.version}, "evidence_reference"),
        ]
        for payload, field in cases:
            response = self.client.post(url, data=payload, content_type="application/json", headers=headers)
            self.assertEqual(response.status_code, 400, response.content)
            self.assertIn(field, response.json()["error"]["field_errors"])
        self.assertEqual(ProduceSupplyRecord.objects.count(), 0)

        stale = self.client.post(url, data={"financial_year": "2025-26", "supplied_to_entity_type": "sfpcl", "supply_route": "direct", "evidence_reference": "ERP-1", "version": self.member.version + 1}, content_type="application/json", headers=headers)
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.json()["error"]["code"], "STALE_WRITE")

        competing_payload = {"financial_year": "2025-26", "supplied_to_entity_type": "sfpcl", "supply_route": "direct", "evidence_reference": "ERP-1", "version": self.member.version}
        winner = self.client.post(url, data=competing_payload, content_type="application/json", headers=headers)
        loser = self.client.post(url, data=competing_payload, content_type="application/json", headers=headers)
        self.assertEqual(winner.status_code, 200)
        self.assertEqual(loser.status_code, 409)
        self.assertEqual(ProduceSupplyRecord.objects.count(), 1)
        self.assertEqual(MemberChangeHistory.objects.filter(change_type="produce_supply_captured").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="members.produce_supply.created").count(), 1)

    def test_staff_verifies_the_dated_active_member_result_through_public_route(self):
        verify_permission = Permission.objects.create(
            permission_code="members.active_status.verify",
            permission_name="Verify active member status",
            module_name="members",
            risk_level="high",
        )
        checker = self._user("status.checker@sfpcl.example", verify_permission)
        for financial_year in ("2022-23", "2023-24", "2024-25", "2025-26"):
            ProduceSupplyRecord.objects.create(
                member=self.member,
                financial_year=financial_year,
                supplied_to_entity_type="sfpcl",
                supply_route="direct",
                evidence_reference=f"ERP-STATUS-{financial_year}",
                captured_by_user=self.actor,
                verified_flag=True,
            )
        result = ActiveMemberStatusModule().calculate(member_id=self.member.member_id)

        response = self.client.post(
            f"/api/v1/members/{self.member.member_id}/active-status/verify/",
            data={
                "result_id": result.result_id,
                "as_of_date": result.calculated_as_of_date,
                "decision": "active",
                "reason": "Dated source evidence reviewed.",
                "version": self.member.version,
            },
            content_type="application/json",
            headers=self._headers(checker.email),
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["result"], result.to_snapshot())
        self.assertEqual(data["decision"], "active")
        self.assertEqual(data["reason"], "Dated source evidence reviewed.")

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
            evidence_reference="ERP-PORTAL-1", captured_by_user=self.actor, verified_flag=True,
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
        self.assertTrue(data["records"][0]["qualifying"])
        self.assertIsNone(data["records"][0]["non_qualifying_reason"])
        self.assertEqual(data["summary"]["total_quantity"], "10.000")
        self.assertEqual(data["summary"]["continuous_supply_years"], "1")
        self.assertIsNotNone(data["summary"]["calculated_as_of_date"])
        self.assertIsNotNone(data["summary"]["result_id"])
        self.assertEqual(data["source_status"], "persisted_qualifying_verified_records")
