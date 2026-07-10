import json
from uuid import uuid4

from django.test import Client, TestCase

from sfpcl_credit.applications.models import LoanApplication, Witness
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member, Shareholding
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.tests.api_contracts import assert_pagination_shape
from sfpcl_credit.tests.api_contracts import assert_error_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


WITNESS_CREATE_PERMISSION = "members.witness.create"
WITNESS_READ_PERMISSION = "members.witness.read"


class WitnessApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        permission = Permission.objects.create(
            permission_code=WITNESS_CREATE_PERMISSION,
            permission_name="Create witnesses",
            module_name="members",
            risk_level="high",
        )
        read_permission = Permission.objects.create(
            permission_code=WITNESS_READ_PERMISSION,
            permission_name="View witnesses",
            module_name="members",
            risk_level="medium",
        )
        role = Role.objects.create(
            role_code="witness_creator",
            role_name="Witness Creator",
            is_system_role=True,
            status="active",
        )
        RolePermission.objects.create(role=role, permission=permission)
        RolePermission.objects.create(role=role, permission=read_permission)
        self.user = User.objects.create(
            full_name="Compliance Witness Creator",
            email="witness.creator@sfpcl.example",
            status="active",
            primary_role=role,
        )
        self.user.set_password("CreatorPass123!")
        self.user.save()
        self.member = Member.objects.create(
            member_number="MEM-004E",
            member_type="individual_farmer",
            legal_name="Sita Patil",
            display_name="Sita Patil",
            folio_number="FOL-004E",
            membership_status="active",
            pan_encrypted="member-pan-token",
            pan_hash="member-pan-hash",
            aadhaar_encrypted="member-aadhaar-token",
            aadhaar_hash="member-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        self.shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number="FOL-004E",
            number_of_shares=25,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=25,
            status="active",
        )
        self.application = LoanApplication.objects.create(
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.user,
            created_by_user=self.user,
        )

    def test_verified_shareholder_witness_can_be_created_through_application_endpoint(self):
        response = self.client.post(
            self._url(),
            data={
                "member_id": str(self.member.member_id),
                "witness_name": "Sita Patil",
                "pan": "ABCDE1234F",
                "aadhaar": "123412341234",
            },
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["data"]["member_id"], str(self.member.member_id))
        self.assertEqual(payload["data"]["folio_number"], "FOL-004E")
        self.assertEqual(payload["data"]["shareholder_verified_flag"], True)
        self.assertEqual(payload["data"]["verification_status"], "verified")
        self.assertEqual(payload["data"]["pan"]["masked"], "******234F")
        self.assertEqual(payload["data"]["aadhaar"]["masked"], "********1234")

    def test_witness_list_is_scoped_to_the_requested_application(self):
        first = self.client.post(
            self._url(),
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )
        other_application = LoanApplication.objects.create(
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.user,
            created_by_user=self.user,
        )
        self.client.post(
            self._url(other_application),
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )

        response = self.client.get(self._url(), headers=self._headers())

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(body["data"][0]["witness_id"], first.json()["data"]["witness_id"])

    def test_witness_read_retains_verification_time_shareholding_and_folio(self):
        created = self._post()
        self.assertEqual(created.status_code, 200)
        self.assertEqual(
            created.json()["data"]["verification_shareholding_id"],
            str(self.shareholding.shareholding_id),
        )

        self.shareholding.folio_number = "FOL-CHANGED"
        self.shareholding.number_of_shares = 0
        self.shareholding.available_share_count = 0
        self.shareholding.status = "inactive"
        self.shareholding.save()
        Shareholding.objects.create(
            member=self.member,
            folio_number="FOL-NEW",
            number_of_shares=50,
            holding_mode="demat",
            pledged_share_count=0,
            available_share_count=50,
            status="active",
        )

        response = self.client.get(self._url(), headers=self._headers())

        self.assertEqual(response.status_code, 200)
        witness = response.json()["data"][0]
        self.assertEqual(
            witness["verification_shareholding_id"],
            str(self.shareholding.shareholding_id),
        )
        self.assertEqual(witness["folio_number"], "FOL-004E")

    def test_witness_create_rejects_non_shareholder_unverified_kyc_and_name_mismatch(self):
        shareholding = self.member.shareholdings.get()
        shareholding.status = "inactive"
        shareholding.save()
        non_shareholder = self._post()
        self.assertEqual(non_shareholder.status_code, 400)
        assert_error_envelope(self, non_shareholder.json(), "WITNESS_NOT_SHAREHOLDER")

        shareholding.status = "active"
        shareholding.save()
        self.member.kyc_status = "pending"
        self.member.save(update_fields=["kyc_status"])
        unverified_kyc = self._post()
        self.assertEqual(unverified_kyc.status_code, 400)
        assert_error_envelope(self, unverified_kyc.json(), "VALIDATION_ERROR")
        self.assertIn("member_id", unverified_kyc.json()["error"]["field_errors"])

        self.member.kyc_status = "verified"
        self.member.save(update_fields=["kyc_status"])
        wrong_name = self._post(witness_name="Another Person")
        self.assertEqual(wrong_name.status_code, 400)
        assert_error_envelope(self, wrong_name.json(), "VALIDATION_ERROR")
        self.assertIn("witness_name", wrong_name.json()["error"]["field_errors"])
        self.assertEqual(Witness.objects.count(), 0)

    def test_witness_create_rejects_missing_records_invalid_identity_and_forged_verification(self):
        unknown_application = self.client.post(
            f"/api/v1/loan-applications/{uuid4()}/witnesses/",
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(unknown_application.status_code, 404)
        assert_error_envelope(self, unknown_application.json(), "NOT_FOUND")

        unknown_member = self._post(member_id=str(uuid4()))
        self.assertEqual(unknown_member.status_code, 404)
        assert_error_envelope(self, unknown_member.json(), "NOT_FOUND")

        for field, value, code in (
            ("pan", "bad-pan", "INVALID_PAN_FORMAT"),
            ("aadhaar", "1234", "INVALID_AADHAAR_FORMAT"),
            ("pan", "", "MISSING_REQUIRED_FIELD"),
            ("aadhaar", "", "MISSING_REQUIRED_FIELD"),
        ):
            with self.subTest(field=field, code=code):
                response = self._post(**{field: value})
                self.assertEqual(response.status_code, 400)
                assert_error_envelope(self, response.json(), code)

        forged = self._post(shareholder_verified_flag=True, verification_status="verified")
        self.assertEqual(forged.status_code, 400)
        assert_error_envelope(self, forged.json(), "VALIDATION_ERROR")
        self.assertIn("shareholder_verified_flag", forged.json()["error"]["field_errors"])
        self.assertEqual(Witness.objects.count(), 0)

    def test_witness_create_envelopes_malformed_and_non_object_json_without_writes(self):
        headers = self._headers()
        baseline_audits = AuditLog.objects.count()
        baseline_events = WorkflowEvent.objects.count()
        for body in ('{"member_id":', "[]", '"witness"'):
            with self.subTest(body=body):
                response = self.client.post(
                    self._url(),
                    data=body,
                    content_type="application/json",
                    headers=headers,
                )

                self.assertEqual(response.status_code, 400)
                assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
                self.assertEqual(Witness.objects.count(), 0)
                self.assertEqual(AuditLog.objects.count(), baseline_audits)
                self.assertEqual(WorkflowEvent.objects.count(), baseline_events)

    def test_witness_permissions_and_application_object_access_are_enforced(self):
        plain = self._user("witness.plain@sfpcl.example", "PlainPass123!")
        no_permission = self.client.post(
            self._url(),
            data=self._payload(),
            content_type="application/json",
            headers=self._headers_for(plain.email, "PlainPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")

        reader = self._user(
            "witness.reader@sfpcl.example",
            "ReaderPass123!",
            Permission.objects.get(permission_code=WITNESS_READ_PERMISSION),
        )
        read_response = self.client.get(
            self._owned_url(reader), headers=self._headers_for(reader.email, "ReaderPass123!")
        )
        self.assertEqual(read_response.status_code, 200)
        read_only_create = self.client.post(
            self._owned_url(reader),
            data=self._payload(),
            content_type="application/json",
            headers=self._headers_for(reader.email, "ReaderPass123!"),
        )
        self.assertEqual(read_only_create.status_code, 403)
        assert_error_envelope(self, read_only_create.json(), "PERMISSION_DENIED")

        outsider = self._user(
            "witness.outsider@sfpcl.example",
            "OutsiderPass123!",
            Permission.objects.get(permission_code=WITNESS_CREATE_PERMISSION),
        )
        denied = self.client.post(
            self._url(),
            data=self._payload(),
            content_type="application/json",
            headers=self._headers_for(outsider.email, "OutsiderPass123!"),
        )
        self.assertEqual(denied.status_code, 403)
        assert_error_envelope(self, denied.json(), "OBJECT_ACCESS_DENIED")

    def test_witness_identity_is_protected_and_create_audit_is_metadata_only(self):
        response = self._post(pan="KLMNO9876P", aadhaar="987698769876")
        self.assertEqual(response.status_code, 200)
        witness = Witness.objects.get()
        self.assertNotEqual(witness.pan_encrypted, "KLMNO9876P")
        self.assertNotEqual(witness.aadhaar_encrypted, "987698769876")
        self.assertTrue(witness.pan_hash)
        self.assertTrue(witness.aadhaar_hash)
        self.assertTrue(witness.shareholder_verified_flag)
        self.assertEqual(witness.verification_status, "verified")
        self.assertEqual(witness.verified_by_user, self.user)
        self.assertIsNotNone(witness.verified_at)

        serialized_response = json.dumps(response.json()).lower()
        self.assertNotIn("klmno9876p", serialized_response)
        self.assertNotIn("987698769876", serialized_response)
        audit = AuditLog.objects.get(action="applications.witness.created")
        serialized_audit = json.dumps(audit.new_value_json).lower()
        for secret in (
            "klmno9876p",
            "987698769876",
            witness.pan_hash.lower(),
            witness.aadhaar_hash.lower(),
            witness.pan_encrypted.lower(),
            witness.aadhaar_encrypted.lower(),
        ):
            self.assertNotIn(secret, serialized_audit)
        self.assertEqual(audit.new_value_json["loan_application_id"], str(self.application.loan_application_id))
        self.assertEqual(audit.new_value_json["verification_status"], "verified")
        self.assertEqual(WorkflowEvent.objects.count(), 0)

    def _post(self, **overrides):
        return self.client.post(
            self._url(),
            data=self._payload(**overrides),
            content_type="application/json",
            headers=self._headers(),
        )

    def _payload(self, **overrides):
        payload = {
            "member_id": str(self.member.member_id),
            "witness_name": "Sita Patil",
            "pan": "ABCDE1234F",
            "aadhaar": "123412341234",
        }
        payload.update(overrides)
        return payload

    def _headers(self):
        return self._headers_for("witness.creator@sfpcl.example", "CreatorPass123!")

    def _headers_for(self, email, password):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": email,
                "password": password,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

    def _user(self, email, password, *permissions):
        role = Role.objects.create(
            role_code=email.split("@")[0].replace(".", "_"),
            role_name=email,
            is_system_role=True,
            status="active",
        )
        for permission in permissions:
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=email,
            email=email,
            status="active",
            primary_role=role,
        )
        user.set_password(password)
        user.save()
        return user

    def _owned_url(self, owner):
        application = LoanApplication.objects.create(
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=owner,
            created_by_user=owner,
        )
        return self._url(application)

    def _url(self, application=None):
        application = application or self.application
        return f"/api/v1/loan-applications/{application.loan_application_id}/witnesses/"
