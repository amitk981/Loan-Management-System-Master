from decimal import Decimal
from uuid import uuid4

from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member, Shareholding
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


SHAREHOLDING_READ_PERMISSION = "members.shareholding.read"
SHAREHOLDING_CREATE_PERMISSION = "members.shareholding.create"


class MemberShareholdingApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.read_permission = Permission.objects.create(
            permission_code=SHAREHOLDING_READ_PERMISSION,
            permission_name="View shareholding",
            module_name="members",
            risk_level="medium",
        )
        self.create_permission = Permission.objects.create(
            permission_code=SHAREHOLDING_CREATE_PERMISSION,
            permission_name="Create shareholding",
            module_name="members",
            risk_level="high",
        )
        self.reader = self._user(
            "share.reader@sfpcl.example",
            "ReaderPass123!",
            self.read_permission,
        )
        self.creator = self._user(
            "share.creator@sfpcl.example",
            "CreatorPass123!",
            self.create_permission,
        )
        self.reader_creator = self._user(
            "share.full@sfpcl.example",
            "FullPass123!",
            self.read_permission,
            self.create_permission,
        )
        self.plain = self._user("share.plain@sfpcl.example", "PlainPass123!")
        self.member = Member.objects.create(
            member_number="MEM-004F",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            folio_number="FOL-004F",
            membership_status="active",
            pan_encrypted="member-pan-token",
            pan_hash="member-pan-hash",
            aadhaar_encrypted="member-aadhaar-token",
            aadhaar_hash="member-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )

    def test_member_shareholdings_can_be_created_and_listed_with_available_share_count(self):
        create_response = self.client.post(
            self._url(),
            data=self._valid_payload(),
            content_type="application/json",
            headers={
                **self._headers("share.full@sfpcl.example", "FullPass123!"),
                "X-Request-ID": "req-create-shareholding",
            },
        )

        self.assertEqual(create_response.status_code, 200)
        create_payload = create_response.json()
        assert_success_envelope(self, create_payload)
        self.assertEqual(create_payload["meta"]["request_id"], "req-create-shareholding")
        shareholding = create_payload["data"]
        self.assertEqual(shareholding["folio_number"], "FOL-004F")
        self.assertEqual(shareholding["number_of_shares"], 100)
        self.assertEqual(shareholding["holding_mode"], "physical")
        self.assertEqual(shareholding["valuation_per_share"], "2000.00")
        self.assertEqual(shareholding["valuation_effective_date"], "2026-04-01")
        self.assertEqual(shareholding["pledged_share_count"], 15)
        self.assertEqual(shareholding["available_share_count"], 85)
        self.assertEqual(shareholding["future_shares_pledge_flag"], True)
        self.assertEqual(shareholding["status"], "active")

        persisted = Shareholding.objects.get(shareholding_id=shareholding["shareholding_id"])
        self.assertEqual(persisted.available_share_count, 85)
        self.assertEqual(persisted.valuation_per_share, Decimal("2000.00"))
        self.member.refresh_from_db()
        self.assertEqual(self.member.number_of_shares, 100)
        self.assertEqual(self.member.holding_mode, "physical")
        self.assertEqual(self.member.available_share_count, 85)

        list_response = self.client.get(
            self._url(),
            headers=self._headers("share.reader@sfpcl.example", "ReaderPass123!"),
        )

        self.assertEqual(list_response.status_code, 200)
        list_payload = list_response.json()
        assert_pagination_shape(self, list_payload)
        self.assertEqual(list_payload["pagination"]["total_count"], 1)
        self.assertEqual(list_payload["data"][0]["shareholding_id"], shareholding["shareholding_id"])
        self.assertEqual(list_payload["data"][0]["available_share_count"], 85)

    def test_member_shareholdings_require_authentication_and_separate_read_create_permissions(self):
        unauthenticated = self.client.get(self._url())
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        no_read = self.client.get(
            self._url(),
            headers=self._headers("share.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(no_read.status_code, 403)
        assert_error_envelope(self, no_read.json(), "PERMISSION_DENIED")

        no_create = self.client.post(
            self._url(),
            data=self._valid_payload(),
            content_type="application/json",
            headers=self._headers("share.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_create.status_code, 403)
        assert_error_envelope(self, no_create.json(), "PERMISSION_DENIED")

        plain = self.client.post(
            self._url(),
            data=self._valid_payload(),
            content_type="application/json",
            headers=self._headers("share.plain@sfpcl.example", "PlainPass123!"),
        )
        self.assertEqual(plain.status_code, 403)
        assert_error_envelope(self, plain.json(), "PERMISSION_DENIED")

    def test_member_shareholdings_return_not_found_for_unknown_or_deleted_member(self):
        for member_id in (uuid4(), self._deleted_member().member_id):
            with self.subTest(member_id=member_id):
                response = self.client.get(
                    self._url(member_id),
                    headers=self._headers("share.reader@sfpcl.example", "ReaderPass123!"),
                )
                self.assertEqual(response.status_code, 404)
                assert_error_envelope(self, response.json(), "NOT_FOUND")

    def test_member_shareholding_create_rejects_invalid_share_counts(self):
        cases = [
            ("number_of_shares", -1, "number_of_shares"),
            ("pledged_share_count", -1, "pledged_share_count"),
            ("pledged_share_count", 101, "pledged_share_count"),
        ]
        for field, value, error_field in cases:
            with self.subTest(field=field, value=value):
                payload = self._valid_payload()
                payload[field] = value
                response = self.client.post(
                    self._url(),
                    data=payload,
                    content_type="application/json",
                    headers=self._headers("share.creator@sfpcl.example", "CreatorPass123!"),
                )

                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, "VALIDATION_ERROR")
                self.assertIn(error_field, body["error"]["field_errors"])

    def test_member_shareholding_create_audits_metadata_without_workflow_event(self):
        response = self.client.post(
            self._url(),
            data=self._valid_payload(number_of_shares=50, pledged_share_count=0),
            content_type="application/json",
            headers=self._headers("share.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        shareholding_id = response.json()["data"]["shareholding_id"]
        audit = AuditLog.objects.filter(action="members.shareholding.created").get()
        self.assertEqual(str(audit.entity_id), shareholding_id)
        self.assertEqual(audit.entity_type, "shareholding")
        self.assertEqual(audit.new_value_json["member_id"], str(self.member.member_id))
        self.assertEqual(audit.new_value_json["folio_number"], "FOL-004F")
        self.assertEqual(audit.new_value_json["number_of_shares"], 50)
        self.assertEqual(audit.new_value_json["available_share_count"], 50)
        self.assertEqual(WorkflowEvent.objects.count(), 0)

    def _valid_payload(self, **overrides):
        payload = {
            "folio_number": "FOL-004F",
            "number_of_shares": 100,
            "holding_mode": "physical",
            "valuation_per_share": "2000.00",
            "valuation_effective_date": "2026-04-01",
            "pledged_share_count": 15,
            "future_shares_pledge_flag": True,
        }
        payload.update(overrides)
        return payload

    def _user(self, email, password, *permissions):
        role = Role.objects.create(
            role_code=email.split("@")[0].replace(".", "_"),
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

    def _url(self, member_id=None):
        return f"/api/v1/members/{member_id or self.member.member_id}/shareholdings/"

    def _deleted_member(self):
        return Member.objects.create(
            member_type="individual_farmer",
            legal_name="Deleted Member",
            display_name="Deleted Member",
            folio_number=f"FOL-{uuid4()}",
            membership_status="inactive",
            pan_encrypted="deleted-pan-token",
            pan_hash=f"deleted-pan-{uuid4()}",
            kyc_status="missing",
            default_status="no_default",
            is_deleted=True,
        )
