import json

from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member, MemberIdentityChangeRequest
from sfpcl_credit.tests.api_contracts import assert_success_envelope


class MemberGovernanceApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.creator = self._user("creator@sfpcl.example", "members.member.create")

    def _user(self, email, *codes):
        role = Role.objects.create(
            role_code=email.split("@")[0], role_name=email, is_system_role=True, status="active"
        )
        for code in codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "members",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=email, email=email, status="active", primary_role=role
        )
        user.set_password("MemberPass123!")
        user.save(update_fields=["password_hash"])
        return user

    def _headers(self, user=None):
        user = user or self.creator
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": user.email, "password": "MemberPass123!"},
            content_type="application/json",
        )
        if login.status_code != 200:
            user.set_password("MemberPass123!")
            user.save(update_fields=["password_hash"])
            login = self.client.post(
                "/api/v1/auth/login/",
                data={"email": user.email, "password": "MemberPass123!"},
                content_type="application/json",
            )
        return {"HTTP_AUTHORIZATION": f"Bearer {login.json()['data']['access_token']}"}

    def test_create_individual_member_persists_profile_history_and_audit(self):
        response = self.client.post(
            "/api/v1/members/",
            data={
                "member_type": "individual_farmer",
                "legal_name": "Synthetic Farmer",
                "display_name": "Synthetic Farmer",
                "folio_number": "SYN-FOL-001",
                "membership_start_date": "2024-04-01",
                "pan": "ABCDE1234F",
                "aadhaar": "123412341234",
                "registered_address": {
                    "line1": "Synthetic Road",
                    "village_city": "Nashik",
                    "district": "Nashik",
                    "state": "Maharashtra",
                    "pincode": "422001",
                },
                "mobile_number": "+919000000001",
                "email": "synthetic.farmer@example.test",
                "individual_profile": {
                    "first_name": "Synthetic",
                    "last_name": "Farmer",
                    "gender": "other",
                    "date_of_birth": "1980-01-15",
                    "occupation": "Farmer",
                    "land_area_under_cultivation_acres": "5.00",
                    "primary_crop": "grapes",
                    "services_availed_flag": True,
                    "employment_or_service_years": None,
                },
            },
            content_type="application/json",
            **self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        assert_success_envelope(self, response.json())
        member = Member.objects.get(member_id=response.json()["data"]["member_id"])
        self.assertNotEqual(member.pan_encrypted, "ABCDE1234F")
        self.assertNotEqual(member.aadhaar_encrypted, "123412341234")
        self.assertEqual(member.individual_profile.first_name, "Synthetic")
        history = member.change_history.get()
        self.assertEqual(history.actor_user, self.creator)
        serialized = json.dumps(history.new_value_json)
        self.assertNotIn("ABCDE1234F", serialized)
        self.assertNotIn("123412341234", serialized)
        self.assertTrue(AuditLog.objects.filter(action="members.member.created").exists())

    def test_create_fpc_protects_signatory_identity(self):
        payload = {
            "member_type": "fpc", "legal_name": "Synthetic Producer Limited",
            "display_name": "Synthetic Producer", "folio_number": "SYN-FOL-002",
            "pan": "FGHIJ5678K", "registered_address": {"line1": "Synthetic Office"},
            "mobile_number": "+919000000002", "email": "producer@example.test",
            "producer_institution_profile": {
                "institution_type": "farmer_producer_company",
                "registration_number": "SYNTHETIC-REG-001",
                "authorised_signatory_name": "Synthetic Signatory",
                "authorised_signatory_pan": "KLMNO1234P",
                "authorised_signatory_aadhaar": "999988887777",
                "board_resolution_required_flag": True,
                "services_availed_flag": True, "produce_supply_years": "2.00",
            },
        }
        response = self.client.post(
            "/api/v1/members/", data=payload, content_type="application/json", **self._headers()
        )
        self.assertEqual(response.status_code, 200)
        profile = Member.objects.get(member_id=response.json()["data"]["member_id"]).producer_institution_profile
        self.assertNotEqual(profile.authorised_signatory_pan_encrypted, "KLMNO1234P")
        self.assertNotEqual(profile.authorised_signatory_aadhaar_encrypted, "999988887777")

    def test_mutations_require_authentication_and_exact_permission(self):
        payload = {"member_type": "individual_farmer"}
        anonymous = self.client.post("/api/v1/members/", data=payload, content_type="application/json")
        self.assertEqual(anonymous.status_code, 401)
        plain = self._user("plain@sfpcl.example")
        forbidden = self.client.post(
            "/api/v1/members/", data=payload, content_type="application/json", **self._headers(plain)
        )
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(Member.objects.count(), 0)

    def test_duplicate_pan_and_aadhaar_are_field_errors_with_zero_writes(self):
        payload = {
            "member_type": "individual_farmer", "legal_name": "First", "display_name": "First",
            "folio_number": "DUP-1", "pan": "ABCDE1234F", "aadhaar": "123412341234",
            "registered_address": {}, "individual_profile": {"first_name": "First", "last_name": "Member"},
        }
        first = self.client.post("/api/v1/members/", data=payload, content_type="application/json", **self._headers())
        self.assertEqual(first.status_code, 200)
        headers = self._headers()
        counts = (Member.objects.count(), AuditLog.objects.count())
        payload.update({"folio_number": "DUP-2", "legal_name": "Second"})
        duplicate = self.client.post("/api/v1/members/", data=payload, content_type="application/json", **headers)
        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(set(duplicate.json()["error"]["field_errors"]), {"pan", "aadhaar"})
        self.assertEqual((Member.objects.count(), AuditLog.objects.count()), counts)

    def test_update_with_membership_date_persists_json_safe_history(self):
        updater = self._user("date-updater@sfpcl.example", "members.member.update")
        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Dated Member",
            display_name="Dated Member",
            folio_number="DATE-1",
            membership_start_date="2024-04-01",
            membership_status="active",
            kyc_status="pending",
            default_status="no_default",
            created_by_user=self.creator,
        )

        response = self.client.patch(
            f"/api/v1/members/{member.member_id}/",
            data={
                "display_name": "Dated Member Updated",
                "membership_start_date": "2024-04-01",
                "version": 1,
            },
            content_type="application/json",
            **self._headers(updater),
        )

        self.assertEqual(response.status_code, 200)
        history = member.change_history.get()
        self.assertEqual(history.old_value_json["membership_start_date"], "2024-04-01")
        self.assertEqual(history.new_value_json["membership_start_date"], "2024-04-01")
        json.dumps(history.old_value_json)
        json.dumps(history.new_value_json)

    def test_verified_identity_requires_reverification_and_stale_writes_are_atomic(self):
        updater = self._user("updater@sfpcl.example", "members.member.update", "members.member.read")
        member = Member.objects.create(
            member_type="individual_farmer", legal_name="Synthetic Existing",
            display_name="Synthetic Existing", folio_number="SYN-FOL-003",
            membership_status="active", pan_encrypted="enc:v1:10:synthetic:1234",
            pan_hash="synthetic-pan-hash", aadhaar_encrypted="enc:v1:12:synthetic:1234",
            aadhaar_hash="synthetic-aadhaar-hash", kyc_status="verified",
            default_status="no_default", created_by_user=self.creator,
        )
        headers = self._headers(updater)
        before_audits = AuditLog.objects.count()
        locked = self.client.patch(
            f"/api/v1/members/{member.member_id}/",
            data={"pan": "PQRST6789U", "version": 1}, content_type="application/json", **headers,
        )
        self.assertEqual(locked.status_code, 409)
        self.assertEqual(member.change_history.count(), 0)
        self.assertEqual(AuditLog.objects.count(), before_audits + 1)
        member.refresh_from_db()
        self.assertEqual(member.pan_hash, "synthetic-pan-hash")

        changed = self.client.post(
            f"/api/v1/members/{member.member_id}/reverification/",
            data={"pan": "PQRST6789U", "reason": "Synthetic correction evidence", "version": 1},
            content_type="application/json", **headers,
        )
        self.assertEqual(changed.status_code, 200)
        member.refresh_from_db()
        self.assertEqual(member.kyc_status, "verified")
        self.assertEqual(member.version, 1)
        self.assertEqual(MemberIdentityChangeRequest.objects.get().status, "pending")
        self.assertNotIn("PQRST6789U", json.dumps(changed.json()))

        counts = (member.change_history.count(), AuditLog.objects.count())
        stale = self.client.patch(
            f"/api/v1/members/{member.member_id}/",
            data={"email": "stale@example.test", "version": 0},
            content_type="application/json", **headers,
        )
        self.assertEqual(stale.status_code, 409)
        self.assertEqual((member.change_history.count(), AuditLog.objects.count()), counts)

        detail = self.client.get(f"/api/v1/members/{member.member_id}/", **headers)
        actions = {item["action_code"]: item for item in detail.json()["data"]["available_actions"]}
        self.assertEqual(set(actions), {"members.member.update", "members.member.reverify_identity", "members.member.identity_change.approve"})
        self.assertTrue(actions["members.member.update"]["enabled"])
        self.assertFalse(actions["members.member.reverify_identity"]["enabled"])
        for action in actions.values():
            self.assertEqual(len(action), 6)

    def test_identity_change_requires_a_different_permissioned_approver(self):
        requester = self._user("requester@sfpcl.example", "members.member.update", "members.member.read")
        approver = self._user("approver@sfpcl.example", "members.member.identity_change.approve", "members.member.read")
        member = Member.objects.create(
            member_type="individual_farmer", legal_name="Governed Farmer", display_name="Governed Farmer",
            folio_number="GOV-1", membership_status="active", pan_encrypted="enc:v1:10:test:1234",
            pan_hash="old-pan", aadhaar_encrypted="enc:v1:12:test:1234", aadhaar_hash="old-aadhaar",
            kyc_status="verified", rekyc_due_date="2027-01-01", default_status="no_default",
            created_by_user=self.creator,
        )
        requested = self.client.post(
            f"/api/v1/members/{member.member_id}/identity-change-requests/",
            data={"version": 1, "pan": "PQRST6789U", "reason": "Correction backed by source record"},
            content_type="application/json", **self._headers(requester),
        )
        self.assertEqual(requested.status_code, 200)
        change_request = MemberIdentityChangeRequest.objects.get()
        self.assertEqual(change_request.status, "pending")
        self.assertNotIn("PQRST6789U", json.dumps(requested.json()))
        member.refresh_from_db()
        self.assertEqual(member.pan_hash, "old-pan")

        self_approval = self.client.post(
            f"/api/v1/member-identity-change-requests/{change_request.identity_change_request_id}/approve/",
            data={}, content_type="application/json", **self._headers(requester),
        )
        self.assertEqual(self_approval.status_code, 403)

        approved = self.client.post(
            f"/api/v1/member-identity-change-requests/{change_request.identity_change_request_id}/approve/",
            data={}, content_type="application/json", **self._headers(approver),
        )
        self.assertEqual(approved.status_code, 200)
        member.refresh_from_db(); change_request.refresh_from_db()
        self.assertEqual(change_request.status, "approved")
        self.assertEqual(member.kyc_status, "pending")
        self.assertIsNone(member.rekyc_due_date)
        self.assertEqual(member.version, 2)
        self.assertNotEqual(member.pan_hash, "old-pan")
