from django.test import Client, TestCase

from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member, MemberScopeAssignment
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_pagination_shape


MEMBERS_URL = "/api/v1/members/"
MEMBER_READ_PERMISSION = "members.member.read"


class MemberDirectoryApiTests(TestCase):
    """004A: read-only member directory API backed by source §13.1."""

    def setUp(self):
        self.client = Client()
        self.member_permission = Permission.objects.create(
            permission_code=MEMBER_READ_PERMISSION,
            permission_name="View member list / details",
            module_name="members",
            risk_level="medium",
        )
        self.credit_manager = self._user_with_role(
            role_code="credit_manager",
            role_name="Credit Manager",
            email="credit.members@sfpcl.example",
            password="CreditPass123!",
            grant_member_read=True,
        )
        self.plain_user = self._user_with_role(
            role_code="plain_staff",
            role_name="Plain Staff",
            email="plain.members@sfpcl.example",
            password="PlainPass123!",
            grant_member_read=False,
        )
        MemberScopeAssignment.objects.create(
            user=self.credit_manager,
            permission_code=MEMBER_READ_PERMISSION,
            scope_type="global",
        )
        self._create_member(
            member_number="MEM-00125",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            folio_number="FOL-456",
            membership_status="active",
            pan_encrypted="enc:test-pan-token",
            pan_hash="hash-test-pan",
            aadhaar_encrypted="enc:test-aadhaar-token",
            aadhaar_hash="hash-test-aadhaar",
            mobile_number="9876547890",
            email="ramesh@example.com",
            kyc_status="verified",
            rekyc_due_date="2027-06-22",
            default_status="no_default",
            number_of_shares=100,
            holding_mode="physical",
            available_share_count=100,
            active_member_status="active",
            active_member_verified_at="2026-06-22T10:30:00Z",
        )
        self._create_member(
            member_number="MEM-00126",
            member_type="producer_institution",
            legal_name="Sahyadri Producer Company",
            display_name="Sahyadri Producer Company",
            folio_number="FOL-789",
            membership_status="inactive",
            pan_encrypted="enc:test-company-pan-token",
            pan_hash="hash-test-company-pan",
            aadhaar_encrypted="",
            aadhaar_hash="",
            mobile_number="9123451111",
            email="contact@sahyadri.example",
            kyc_status="missing",
            rekyc_due_date=None,
            default_status="past_default",
            number_of_shares=25,
            holding_mode="demat",
            available_share_count=15,
            active_member_status="inactive",
            active_member_verified_at=None,
        )

    def _create_member(self, **fields):
        return Member.objects.create(**fields)

    def _user_with_role(
        self, *, role_code, role_name, email, password, grant_member_read
    ):
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_name,
            is_system_role=True,
            status="active",
        )
        if grant_member_read:
            RolePermission.objects.create(role=role, permission=self.member_permission)
        user = User.objects.create(
            full_name=role_name,
            email=email,
            status="active",
            primary_role=role,
        )
        user.set_password(password)
        user.save()
        return user

    def _access_token(self, email="credit.members@sfpcl.example", password="CreditPass123!"):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self._access_token()}"}

    def _plain_auth_headers(self):
        return {
            "Authorization": f"Bearer {self._access_token('plain.members@sfpcl.example', 'PlainPass123!')}"
        }

    def test_authenticated_user_can_list_members_with_paginated_masked_fields(self):
        response = self.client.get(
            MEMBERS_URL,
            headers={**self._auth_headers(), "X-Request-ID": "req-members-list"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-members-list")
        self.assertEqual(payload["pagination"]["total_count"], 2)
        self.assertEqual(payload["data"][0]["member_number"], "MEM-00125")
        self.assertEqual(payload["data"][0]["display_name"], "Ramesh Patil")
        self.assertEqual(payload["data"][0]["mobile_number"], "******7890")
        self.assertEqual(payload["data"][0]["share_summary"]["number_of_shares"], 100)
        self.assertEqual(payload["data"][0]["active_member_status"]["status"], "active")
        serialized = str(payload["data"][0]).lower()
        self.assertNotIn("pan", serialized)
        self.assertNotIn("aadhaar", serialized)

    def test_member_directory_supports_source_filters_and_search(self):
        response = self.client.get(
            f"{MEMBERS_URL}?search=Sahyadri&member_type=producer_institution&membership_status=inactive&kyc_status=missing&default_status=past_default",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["pagination"]["total_count"], 1)
        self.assertEqual(payload["data"][0]["member_number"], "MEM-00126")
        self.assertEqual(payload["data"][0]["share_summary"]["holding_mode"], "demat")

    def test_member_directory_uses_standard_pagination(self):
        response = self.client.get(
            f"{MEMBERS_URL}?page=2&page_size=1",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(
            payload["pagination"],
            {
                "page": 2,
                "page_size": 1,
                "total_count": 2,
                "total_pages": 2,
                "has_next": False,
                "has_previous": True,
            },
        )
        self.assertEqual(len(payload["data"]), 1)

    def test_member_directory_rejects_unknown_and_invalid_filters(self):
        cases = [
            (f"{MEMBERS_URL}?crop=grapes", "crop"),
            (f"{MEMBERS_URL}?member_type=borrower", "member_type"),
            (f"{MEMBERS_URL}?page_size=zero", "page_size"),
        ]
        for url, field in cases:
            with self.subTest(field=field):
                response = self.client.get(url, headers=self._auth_headers())

                self.assertEqual(response.status_code, 400)
                payload = response.json()
                assert_error_envelope(self, payload, "VALIDATION_ERROR")
                self.assertIn(field, payload["error"]["field_errors"])

    def test_member_directory_requires_authentication_and_member_read_permission(self):
        unauthenticated = self.client.get(MEMBERS_URL)

        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        forbidden = self.client.get(MEMBERS_URL, headers=self._plain_auth_headers())

        self.assertEqual(forbidden.status_code, 403)
        assert_error_envelope(self, forbidden.json(), "PERMISSION_DENIED")
