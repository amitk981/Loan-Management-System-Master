import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from unittest import skipUnless

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members import services
from sfpcl_credit.members.models import Member, MemberIdentityChangeRequest
from sfpcl_credit.members.modules import MemberRegistry
from sfpcl_credit.members.modules.member_authority import evaluate_member_authority
from sfpcl_credit.members.protected_identity import identity_hash
from sfpcl_credit.identity.modules.object_permissions import ObjectAccessResult
from sfpcl_credit.tests.api_contracts import assert_success_envelope


class MemberGovernanceApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.creator = self._user("creator@sfpcl.example", "members.member.create")

    def _user(self, email, *codes, role_code=None):
        role = Role.objects.create(
            role_code=role_code or email.split("@")[0], role_name=email, is_system_role=True, status="active"
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

    def test_public_registry_enforces_read_permission_and_member_ownership(self):
        owner = self._user("owner@sfpcl.example", "members.member.read")
        member = Member.objects.create(
            member_type="individual_farmer", legal_name="Owned Member", display_name="Owned Member",
            folio_number="OWN-1", membership_status="active", pan_encrypted="enc:owned",
            pan_hash="owned-pan", kyc_status="pending", default_status="no_default",
            created_by_user=owner,
        )

        self.assertEqual(MemberRegistry.get(member.member_id, owner).member_id, member.member_id)
        denied_result = ObjectAccessResult(False, "owner_mismatch", "OBJECT_ACCESS_DENIED", "members.member.read")
        with patch("sfpcl_credit.members.modules.member_registry.evaluate_member_authority", return_value=denied_result), self.assertRaises(PermissionDenied) as denied:
            MemberRegistry.get(member.member_id, owner)
        self.assertEqual(str(denied.exception), "You cannot access this member.")
        with self.assertRaises(PermissionDenied):
            MemberRegistry.get(member.member_id, self.creator)

    def test_registry_authority_uses_owner_global_permission_and_object_policy_without_mocks(self):
        owner = self._user("policy-owner@sfpcl.example", "members.member.read")
        outsider = self._user("policy-outsider@sfpcl.example", "members.member.read")
        manager = self._user("policy-manager@sfpcl.example", "members.member.read")
        missing_permission = self._user("policy-missing@sfpcl.example")
        member = Member.objects.create(
            member_type="individual_farmer", legal_name="Policy Member", display_name="Policy Member",
            folio_number="POLICY-1", membership_status="active", kyc_status="pending",
            default_status="no_default", created_by_user=owner,
        )

        self.assertEqual(MemberRegistry.get(member.member_id, owner), member)
        self.assertEqual(MemberRegistry.get(member.member_id, manager), member)
        unowned = Member.objects.create(
            member_type="individual_farmer", legal_name="Global Policy Member",
            display_name="Global Policy Member", folio_number="POLICY-2",
            membership_status="active", kyc_status="pending", default_status="no_default",
        )
        self.assertEqual(MemberRegistry.get(unowned.member_id, manager), unowned)
        self.assertEqual(MemberRegistry.get(member.member_id, outsider), member)
        with self.assertRaisesRegex(PermissionDenied, "Missing required permission"):
            MemberRegistry.get(member.member_id, missing_permission)

    def test_role_provenance_does_not_change_explicit_global_verification_scope(self):
        permission = "members.active_status.verify"
        system_checker = self._user("system-checker@sfpcl.example", permission)
        custom_checker = self._user("custom-checker@sfpcl.example", permission)
        custom_checker.primary_role.is_system_role = False
        custom_checker.primary_role.save(update_fields=["is_system_role"])
        member = Member.objects.create(
            member_type="individual_farmer", legal_name="Authority Target",
            display_name="Authority Target", folio_number="AUTHORITY-1",
            membership_status="active", kyc_status="verified", default_status="no_default",
            created_by_user=self.creator,
        )

        results = [
            evaluate_member_authority(actor_user=user, member=member, permission=permission)
            for user in (system_checker, custom_checker)
        ]

        self.assertEqual([(result.allowed, result.reason) for result in results], [
            (True, "allowed_global"), (True, "allowed_global"),
        ])

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

    def test_identity_change_request_rejects_duplicate_identity_without_evidence(self):
        requester = self._user("duplicate-requester@sfpcl.example", "members.member.update")
        member = Member.objects.create(
            member_type="individual_farmer", legal_name="Change Target", display_name="Change Target", folio_number="CHANGE-1",
            membership_status="active", pan_encrypted="enc:old", pan_hash="old-change-pan", kyc_status="verified", default_status="no_default",
            created_by_user=requester,
        )
        Member.objects.create(
            member_type="fpc", legal_name="Existing Identity", display_name="Existing Identity", folio_number="CHANGE-2",
            membership_status="active", pan_encrypted="enc:existing", pan_hash=identity_hash("PQRST6789U"), kyc_status="pending", default_status="no_default",
        )
        counts = (MemberIdentityChangeRequest.objects.count(), member.change_history.count(), AuditLog.objects.count())
        with self.assertRaises(ValidationError) as rejected:
            MemberRegistry.request_identity_change(member.member_id, {"version": 1, "pan": "PQRST6789U", "reason": "Correction"}, requester)
        self.assertIn("pan", rejected.exception.message_dict)
        self.assertEqual((MemberIdentityChangeRequest.objects.count(), member.change_history.count(), AuditLog.objects.count()), counts)

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
            created_by_user=updater,
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
            default_status="no_default", created_by_user=updater,
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
        requester = self._user("requester@sfpcl.example", "members.member.update", "members.member.read", "members.member.identity_change.approve")
        approver = self._user("approver@sfpcl.example", "members.member.identity_change.approve", "members.member.read")
        member = Member.objects.create(
            member_type="individual_farmer", legal_name="Governed Farmer", display_name="Governed Farmer",
            folio_number="GOV-1", membership_status="active", pan_encrypted="enc:v1:10:test:1234",
            pan_hash="old-pan", aadhaar_encrypted="enc:v1:12:test:1234", aadhaar_hash="old-aadhaar",
            kyc_status="verified", rekyc_due_date="2027-01-01", default_status="no_default",
            created_by_user=requester,
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

        detail = self.client.get(f"/api/v1/members/{member.member_id}/", **self._headers(requester))
        approval_action = next(item for item in detail.json()["data"]["available_actions"] if item["action_code"] == "members.member.identity_change.approve")
        self.assertFalse(approval_action["enabled"])
        self.assertEqual(approval_action["disabled_reason"], "Requester cannot approve their own change.")

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

    def test_registry_identity_approval_projection_matches_object_denied_write(self):
        requester = self._user("scope-requester@sfpcl.example", "members.member.update")
        checker = self._user(
            "scope-checker@sfpcl.example",
            "members.member.identity_change.approve",
            "members.member.read",
        )
        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Scoped Member",
            display_name="Scoped Member",
            folio_number="SCOPE-1",
            membership_status="active",
            pan_encrypted="enc:old",
            pan_hash="scope-old-pan",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.creator,
        )
        change = MemberIdentityChangeRequest.objects.create(
            member=member,
            requester_user=requester,
            proposed_pan_encrypted="enc:new",
            proposed_pan_hash=identity_hash("PQRST6789U"),
            reason="Correct source identity",
            member_version=member.version,
        )
        denied = ObjectAccessResult(
            False,
            "owner_mismatch",
            "OBJECT_ACCESS_DENIED",
            MemberRegistry.APPROVE_PERMISSION,
        )
        evidence_before = (
            member.change_history.count(),
            AuditLog.objects.count(),
            MemberIdentityChangeRequest.objects.count(),
        )

        with patch(
            "sfpcl_credit.members.modules.member_registry.evaluate_member_authority",
            return_value=denied,
        ):
            action = MemberRegistry.identity_approval_action(member, change, checker)
            self.assertEqual(
                action,
                {
                    "action_code": MemberRegistry.APPROVE_PERMISSION,
                    "label": "Approve identity change",
                    "enabled": False,
                    "disabled_reason": "You cannot access this member.",
                    "required_permission": MemberRegistry.APPROVE_PERMISSION,
                    "required_role": None,
                },
            )
            with self.assertRaises(PermissionDenied) as rejected:
                MemberRegistry.approve_identity_change(
                    change.identity_change_request_id, checker
                )

        self.assertEqual(str(rejected.exception), action["disabled_reason"])
        self.assertEqual(
            (
                member.change_history.count(),
                AuditLog.objects.count(),
                MemberIdentityChangeRequest.objects.count(),
            ),
            evidence_before,
        )

    def test_every_public_registry_operation_enforces_its_own_exact_authority(self):
        plain = self._user("registry-plain@sfpcl.example")
        requester = self._user("registry-requester@sfpcl.example", "members.member.update")
        member = Member.objects.create(
            member_type="individual_farmer", legal_name="Registry Boundary",
            display_name="Registry Boundary", folio_number="REG-BOUNDARY",
            membership_status="active", pan_encrypted="enc:old", pan_hash="registry-old",
            kyc_status="verified", default_status="no_default", created_by_user=self.creator,
        )
        change = MemberIdentityChangeRequest.objects.create(
            member=member, requester_user=requester, proposed_pan_encrypted="enc:new",
            proposed_pan_hash=identity_hash("PQRST6789U"), reason="Boundary proof",
            member_version=member.version,
        )
        before = (Member.objects.count(), MemberIdentityChangeRequest.objects.count(), AuditLog.objects.count())

        with self.assertRaises(PermissionDenied):
            MemberRegistry.create({}, plain)
        with self.assertRaises(PermissionDenied):
            MemberRegistry.get(member.pk, plain)
        with self.assertRaises(PermissionDenied):
            MemberRegistry.update(member.pk, {"version": member.version}, plain)
        with self.assertRaises(PermissionDenied):
            MemberRegistry.request_identity_change(member.pk, {}, plain)
        projected = MemberRegistry.identity_approval_action(member, change, plain)
        self.assertFalse(projected["enabled"])
        self.assertEqual(projected["required_permission"], MemberRegistry.APPROVE_PERMISSION)
        with self.assertRaises(PermissionDenied) as rejected:
            MemberRegistry.approve_identity_change(change.pk, plain)
        self.assertEqual(str(rejected.exception), projected["disabled_reason"])
        self.assertEqual(
            (Member.objects.count(), MemberIdentityChangeRequest.objects.count(), AuditLog.objects.count()),
            before,
        )


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative member registry races require PostgreSQL integration settings.",
)
class MemberRegistryConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def _user(self, email, *codes):
        role = Role.objects.create(
            role_code=email.split("@")[0], role_name=email, is_system_role=True, status="active"
        )
        for code in codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={"permission_name": code, "module_name": "members", "risk_level": "high"},
            )
            RolePermission.objects.create(role=role, permission=permission)
        return User.objects.create(full_name=email, email=email, status="active", primary_role=role)

    def test_competing_duplicate_member_creates_return_one_field_validation_loser(self):
        actor = self._user("race-create@sfpcl.example", "members.member.create")
        barrier = Barrier(2)

        def create(suffix):
            close_old_connections()
            try:
                thread_actor = User.objects.get(pk=actor.pk)
                barrier.wait(timeout=10)
                try:
                    member = MemberRegistry.create(
                        {
                            "member_type": "individual_farmer",
                            "legal_name": f"Race Member {suffix}",
                            "display_name": f"Race Member {suffix}",
                            "folio_number": f"RACE-{suffix}",
                            "pan": "ABCDE1234F",
                            "aadhaar": "111122223333" if suffix == "A" else "444455556666",
                            "registered_address": {},
                            "individual_profile": {"first_name": "Race", "last_name": f"Member {suffix}"},
                        },
                        thread_actor,
                    )
                    return ("success", str(member.member_id))
                except ValidationError as exc:
                    return ("validation", services.validation_field_errors(exc))
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = [future.result(timeout=15) for future in (
                executor.submit(create, "A"), executor.submit(create, "B")
            )]

        self.assertEqual(
            sorted(result[0] for result in results), ["success", "validation"], results
        )
        loser = next(result[1] for result in results if result[0] == "validation")
        self.assertEqual(set(loser), {"pan"})
        self.assertEqual(Member.objects.count(), 1)
        self.assertEqual(Member.objects.get().change_history.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="members.member.created").count(), 1)

    def test_competing_identity_approvals_return_one_field_validation_loser(self):
        requester = self._user("race-requester@sfpcl.example", "members.member.update")
        checker = self._user(
            "race-checker@sfpcl.example", "members.member.identity_change.approve"
        )
        members = [
            Member.objects.create(
                member_type="individual_farmer", legal_name=f"Approval Race {suffix}",
                display_name=f"Approval Race {suffix}", folio_number=f"APR-{suffix}",
                membership_status="active", pan_encrypted=f"enc:{suffix}",
                pan_hash=f"old-{suffix}", kyc_status="verified", default_status="no_default",
            )
            for suffix in ("A", "B")
        ]
        requests = [
            MemberIdentityChangeRequest.objects.create(
                member=member, requester_user=requester,
                proposed_pan_encrypted="enc:shared", proposed_pan_hash=identity_hash("PQRST6789U"),
                reason="Shared corrected identity", member_version=member.version,
            )
            for member in members
        ]
        barrier = Barrier(2)

        def approve(request_id):
            close_old_connections()
            try:
                thread_checker = User.objects.get(pk=checker.pk)
                barrier.wait(timeout=10)
                try:
                    member = MemberRegistry.approve_identity_change(request_id, thread_checker)
                    return ("success", str(member.member_id))
                except ValidationError as exc:
                    return ("validation", services.validation_field_errors(exc))
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = [future.result(timeout=15) for future in (
                executor.submit(approve, requests[0].pk), executor.submit(approve, requests[1].pk)
            )]

        self.assertEqual(sorted(result[0] for result in results), ["success", "validation"])
        loser = next(result[1] for result in results if result[0] == "validation")
        self.assertEqual(set(loser), {"pan"})
        self.assertEqual(MemberIdentityChangeRequest.objects.filter(status="approved").count(), 1)
        self.assertEqual(MemberIdentityChangeRequest.objects.filter(status="pending").count(), 1)
        self.assertEqual(Member.objects.filter(pan_hash=identity_hash("PQRST6789U")).count(), 1)
        self.assertEqual(Member.objects.filter(kyc_status="pending").count(), 1)
        self.assertEqual(Member.objects.filter(change_history__change_type="identity_change_approved").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="members.member.identity_change_approved").count(), 1)
