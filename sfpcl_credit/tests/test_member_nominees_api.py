from datetime import date
from uuid import uuid4

from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


NOMINEE_READ_PERMISSION = "members.nominee.read"
NOMINEE_CREATE_PERMISSION = "members.nominee.create"


class MemberNomineeApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.read_permission = Permission.objects.create(
            permission_code=NOMINEE_READ_PERMISSION,
            permission_name="View nominees",
            module_name="members",
            risk_level="medium",
        )
        self.create_permission = Permission.objects.create(
            permission_code=NOMINEE_CREATE_PERMISSION,
            permission_name="Create nominee",
            module_name="members",
            risk_level="high",
        )
        self.reader = self._user(
            "nominee.reader@sfpcl.example",
            "ReaderPass123!",
            self.read_permission,
        )
        self.creator = self._user(
            "nominee.creator@sfpcl.example",
            "CreatorPass123!",
            self.create_permission,
        )
        self.reader_creator = self._user(
            "nominee.full@sfpcl.example",
            "FullPass123!",
            self.read_permission,
            self.create_permission,
        )
        self.plain = self._user("nominee.plain@sfpcl.example", "PlainPass123!")
        self.member = Member.objects.create(
            member_number="MEM-004D",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            folio_number="FOL-004D",
            membership_status="active",
            pan_encrypted="member-pan-token",
            pan_hash="member-pan-hash",
            aadhaar_encrypted="member-aadhaar-token",
            aadhaar_hash="member-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )

    def test_member_nominees_can_be_created_and_listed_with_masked_identifiers(self):
        create_response = self.client.post(
            self._url(),
            data=self._valid_payload(),
            content_type="application/json",
            headers={**self._headers("nominee.full@sfpcl.example", "FullPass123!"), "X-Request-ID": "req-create-nominee"},
        )

        self.assertEqual(create_response.status_code, 200)
        create_payload = create_response.json()
        assert_success_envelope(self, create_payload)
        self.assertEqual(create_payload["meta"]["request_id"], "req-create-nominee")
        nominee = create_payload["data"]
        self.assertEqual(nominee["nominee_name"], "Sita Patil")
        self.assertEqual(nominee["gender"], "female")
        self.assertEqual(nominee["relationship_to_borrower"], "Spouse")
        self.assertEqual(nominee["kyc_status"], "pending")
        self.assertEqual(nominee["minor_flag"], False)
        self.assertEqual(nominee["signature_required_flag"], True)
        self.assertEqual(nominee["pan"]["masked"], "******234F")
        self.assertEqual(nominee["aadhaar"]["masked"], "********1234")
        self.assertGreaterEqual(nominee["age_at_application"], 18)
        serialized = str(create_payload).lower()
        self.assertNotIn("abcde1234f", serialized)
        self.assertNotIn("123412341234", serialized)

        list_response = self.client.get(
            self._url(),
            headers=self._headers("nominee.reader@sfpcl.example", "ReaderPass123!"),
        )

        self.assertEqual(list_response.status_code, 200)
        list_payload = list_response.json()
        assert_pagination_shape(self, list_payload)
        self.assertEqual(list_payload["pagination"]["total_count"], 1)
        self.assertEqual(list_payload["data"][0]["nominee_id"], nominee["nominee_id"])
        self.assertEqual(list_payload["data"][0]["pan"], {"masked": "******234F", "can_view_full": False})
        self.assertEqual(list_payload["data"][0]["aadhaar"], {"masked": "********1234", "can_view_full": False})

    def test_member_nominees_require_authentication_and_separate_read_create_permissions(self):
        unauthenticated = self.client.get(self._url())
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        no_read = self.client.get(
            self._url(),
            headers=self._headers("nominee.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(no_read.status_code, 403)
        assert_error_envelope(self, no_read.json(), "PERMISSION_DENIED")

        no_create = self.client.post(
            self._url(),
            data=self._valid_payload(),
            content_type="application/json",
            headers=self._headers("nominee.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_create.status_code, 403)
        assert_error_envelope(self, no_create.json(), "PERMISSION_DENIED")

        plain = self.client.post(
            self._url(),
            data=self._valid_payload(),
            content_type="application/json",
            headers=self._headers("nominee.plain@sfpcl.example", "PlainPass123!"),
        )
        self.assertEqual(plain.status_code, 403)
        assert_error_envelope(self, plain.json(), "PERMISSION_DENIED")

    def test_member_nominees_return_not_found_for_unknown_or_deleted_member(self):
        for member_id in (uuid4(), self._deleted_member().member_id):
            with self.subTest(member_id=member_id):
                response = self.client.get(
                    self._url(member_id),
                    headers=self._headers("nominee.reader@sfpcl.example", "ReaderPass123!"),
                )
                self.assertEqual(response.status_code, 404)
                assert_error_envelope(self, response.json(), "NOT_FOUND")

    def test_member_nominee_create_rejects_missing_and_invalid_identity_fields(self):
        cases = [
            ("pan", "", "MISSING_REQUIRED_FIELD", "pan"),
            ("aadhaar", "", "MISSING_REQUIRED_FIELD", "aadhaar"),
            ("pan", "bad-pan", "INVALID_PAN_FORMAT", "pan"),
            ("aadhaar", "1234", "INVALID_AADHAAR_FORMAT", "aadhaar"),
        ]
        for field, value, code, error_field in cases:
            with self.subTest(field=field, code=code):
                payload = self._valid_payload()
                payload[field] = value
                response = self.client.post(
                    self._url(),
                    data=payload,
                    content_type="application/json",
                    headers=self._headers("nominee.creator@sfpcl.example", "CreatorPass123!"),
                )

                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, code)
                self.assertIn(error_field, body["error"]["field_errors"])

    def test_member_nominee_create_rejects_minor_and_missing_birth_date(self):
        for date_of_birth, code in (
            (None, "MISSING_REQUIRED_FIELD"),
            (self._years_ago(17).isoformat(), "NOMINEE_MINOR_NOT_ALLOWED"),
        ):
            with self.subTest(code=code):
                payload = self._valid_payload()
                payload["date_of_birth"] = date_of_birth
                response = self.client.post(
                    self._url(),
                    data=payload,
                    content_type="application/json",
                    headers=self._headers("nominee.creator@sfpcl.example", "CreatorPass123!"),
                )

                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, code)
                self.assertIn("date_of_birth", body["error"]["field_errors"])

    def test_member_nominee_create_audits_metadata_without_plaintext_identity_values(self):
        response = self.client.post(
            self._url(),
            data=self._valid_payload(pan="KLMNO9876P", aadhaar="987698769876"),
            content_type="application/json",
            headers=self._headers("nominee.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        nominee_id = response.json()["data"]["nominee_id"]
        audit = AuditLog.objects.filter(action="members.nominee.created").get()
        self.assertEqual(str(audit.entity_id), nominee_id)
        self.assertEqual(audit.entity_type, "nominee")
        self.assertEqual(audit.new_value_json["member_id"], str(self.member.member_id))
        serialized_audit = str(audit.new_value_json).lower()
        self.assertNotIn("klmno9876p", serialized_audit)
        self.assertNotIn("987698769876", serialized_audit)
        self.assertEqual(WorkflowEvent.objects.count(), 0)

    def _valid_payload(self, **overrides):
        payload = {
            "nominee_name": "Sita Patil",
            "date_of_birth": "1985-05-20",
            "gender": "female",
            "relationship_to_borrower": "Spouse",
            "pan": "ABCDE1234F",
            "aadhaar": "123412341234",
            "signature_required_flag": True,
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
        return f"/api/v1/members/{member_id or self.member.member_id}/nominees/"

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

    def _years_ago(self, years):
        today = date.today()
        try:
            return today.replace(year=today.year - years)
        except ValueError:
            return today.replace(month=2, day=28, year=today.year - years)
