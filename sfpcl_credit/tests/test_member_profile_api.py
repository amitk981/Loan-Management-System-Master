import uuid

from django.core.exceptions import ValidationError
from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import (
    IndividualMemberProfile,
    Member,
    ProducerInstitutionProfile,
)
from sfpcl_credit.tests.api_contracts import (
    assert_available_actions_shape,
    assert_error_envelope,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


MEMBER_READ_PERMISSION = "members.member.read"
APPLICATION_CREATE_PERMISSION = "applications.loan_application.create"
REVEAL_PAN_PERMISSION = "members.sensitive.reveal_pan"
REVEAL_AADHAAR_PERMISSION = "members.sensitive.reveal_aadhaar"


class MemberProfileApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        member_read = Permission.objects.create(
            permission_code=MEMBER_READ_PERMISSION,
            permission_name="View member list / details",
            module_name="members",
            risk_level="medium",
        )
        app_create = Permission.objects.create(
            permission_code=APPLICATION_CREATE_PERMISSION,
            permission_name="Create loan application",
            module_name="applications",
            risk_level="high",
        )
        reveal_pan = Permission.objects.create(
            permission_code=REVEAL_PAN_PERMISSION,
            permission_name="Reveal PAN",
            module_name="members",
            risk_level="critical",
        )
        self.reveal_aadhaar = Permission.objects.create(
            permission_code=REVEAL_AADHAAR_PERMISSION,
            permission_name="Reveal Aadhaar",
            module_name="members",
            risk_level="critical",
        )
        self.reader = self._user("reader@sfpcl.example", "ReaderPass123!", member_read, app_create)
        self.pan_revealer = self._user(
            "pan.revealer@sfpcl.example",
            "RevealPass123!",
            member_read,
            reveal_pan,
        )
        self.aadhaar_revealer = self._user(
            "aadhaar.revealer@sfpcl.example",
            "RevealAadhaar123!",
            member_read,
            self.reveal_aadhaar,
        )
        self.plain = self._user("plain@sfpcl.example", "PlainPass123!")
        self.member = Member.objects.create(
            member_number="MEM-00125",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            folio_number="FOL-456",
            membership_start_date="2021-04-01",
            membership_status="active",
            pan_encrypted="ABCDE1234F",
            pan_hash="hash-pan",
            aadhaar_encrypted="123456789012",
            aadhaar_hash="hash-aadhaar",
            registered_address_line1="Village Road",
            registered_address_line2="Near Market",
            registered_village_city="Nashik",
            registered_district="Nashik",
            registered_state="Maharashtra",
            registered_pincode="422001",
            mobile_number="9876547890",
            email="ramesh@example.com",
            kyc_status="verified",
            rekyc_due_date="2027-06-22",
            default_status="no_default",
            number_of_shares=100,
            holding_mode="physical",
            available_share_count=100,
            active_member_status="active",
        )
        IndividualMemberProfile.objects.create(
            member=self.member,
            first_name="Ramesh",
            middle_name=None,
            last_name="Patil",
            gender="male",
            date_of_birth="1980-01-15",
            occupation="Farmer",
            land_area_under_cultivation_acres="5.00",
            primary_crop="grapes",
            services_availed_flag=True,
            employment_or_service_years="12.50",
        )
        self.deleted = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Deleted Member",
            display_name="Deleted Member",
            folio_number="FOL-999",
            membership_status="inactive",
            pan_encrypted="ABCDE9999F",
            pan_hash="hash-deleted-pan",
            kyc_status="missing",
            default_status="no_default",
            is_deleted=True,
        )

    def _user(self, email, password, *permissions):
        role = Role.objects.create(
            role_code=email.split("@")[0],
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

    def _token(self, email="reader@sfpcl.example", password="ReaderPass123!"):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _headers(self):
        return {"Authorization": f"Bearer {self._token()}"}

    def _pan_reveal_headers(self):
        return {
            "Authorization": f"Bearer {self._token('pan.revealer@sfpcl.example', 'RevealPass123!')}"
        }

    def _aadhaar_reveal_headers(self):
        return {
            "Authorization": f"Bearer {self._token('aadhaar.revealer@sfpcl.example', 'RevealAadhaar123!')}"
        }

    def _plain_headers(self):
        return {"Authorization": f"Bearer {self._token('plain@sfpcl.example', 'PlainPass123!')}"}

    def _url(self, member_id):
        return f"/api/v1/members/{member_id}/"

    def _reveal_url(self, member_id=None):
        return f"/api/v1/members/{member_id or self.member.member_id}/reveal-sensitive-field/"

    def test_authenticated_user_can_retrieve_masked_member_profile_detail(self):
        response = self.client.get(
            self._url(self.member.member_id),
            headers={**self._headers(), "X-Request-ID": "req-member-detail"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-member-detail")
        data = payload["data"]
        self.assertEqual(data["member_id"], str(self.member.member_id))
        self.assertEqual(data["member_number"], "MEM-00125")
        self.assertEqual(data["folio_number"], "FOL-456")
        self.assertEqual(data["membership_status"], "active")
        self.assertEqual(data["kyc_status"], "verified")
        self.assertEqual(data["default_status"], "no_default")
        self.assertEqual(data["pan"], {"masked": "******234F", "can_view_full": False})
        self.assertEqual(data["aadhaar"], {"masked": "********9012", "can_view_full": False})
        self.assertEqual(data["registered_address"]["line1"], "Village Road")
        self.assertEqual(
            data["individual_profile"],
            {
                "first_name": "Ramesh",
                "middle_name": None,
                "last_name": "Patil",
                "gender": "male",
                "date_of_birth": "1980-01-15",
                "occupation": "Farmer",
                "land_area_under_cultivation_acres": "5.00",
                "primary_crop": "grapes",
                "services_availed_flag": True,
                "employment_or_service_years": "12.50",
            },
        )
        self.assertIsNone(data["producer_institution_profile"])
        assert_available_actions_shape(self, data["available_actions"])
        self.assertEqual(
            {action["action_code"] for action in data["available_actions"]},
            {"members.member.update", "members.member.reverify_identity"},
        )
        self.assertTrue(all(not action["enabled"] for action in data["available_actions"]))
        serialized = str(data).lower()
        for forbidden in ("pan_encrypted", "aadhaar_encrypted", "pan_hash", "aadhaar_hash", "abcde1234f", "123456789012"):
            self.assertNotIn(forbidden, serialized)

    def test_member_profile_sets_can_view_full_by_field_specific_permissions_without_full_values(self):
        response = self.client.get(self._url(self.member.member_id), headers=self._pan_reveal_headers())

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["pan"], {"masked": "******234F", "can_view_full": True})
        self.assertEqual(data["aadhaar"], {"masked": "********9012", "can_view_full": False})
        serialized = str(data).lower()
        for forbidden in ("abcde1234f", "123456789012", "hash-pan", "hash-aadhaar"):
            self.assertNotIn(forbidden, serialized)

    def test_member_profile_does_not_derive_loan_start_actions_from_member_statuses(self):
        status_cases = [
            ("active", "verified", "no_default"),
            ("inactive", "verified", "no_default"),
            ("active", "missing", "no_default"),
            ("active", "verified", "in_default"),
        ]

        for membership_status, kyc_status, default_status in status_cases:
            with self.subTest(
                membership_status=membership_status,
                kyc_status=kyc_status,
                default_status=default_status,
            ):
                member = self._member(
                    membership_status=membership_status,
                    kyc_status=kyc_status,
                    default_status=default_status,
                    folio_number=f"FOL-{uuid.uuid4()}",
                )
                response = self.client.get(self._url(member.member_id), headers=self._headers())

                self.assertEqual(response.status_code, 200)
                data = response.json()["data"]
                assert_available_actions_shape(self, data["available_actions"])
                self.assertFalse(
                    any(action["action_code"] == "create_loan_application" for action in data["available_actions"])
                )

    def test_member_profile_returns_not_found_for_unknown_or_deleted_member(self):
        for member_id in (uuid.uuid4(), self.deleted.member_id):
            response = self.client.get(self._url(member_id), headers=self._headers())
            self.assertEqual(response.status_code, 404)
            assert_error_envelope(self, response.json(), "NOT_FOUND")

    def test_producer_institution_profile_serializes_non_sensitive_fields_only(self):
        producer = self._member(
            member_type="fpc",
            legal_name="ABC Farmer Producer Company Limited",
            display_name="ABC FPC",
            folio_number="FOL-789",
            pan_hash="hash-producer-pan",
        )
        ProducerInstitutionProfile.objects.create(
            member=producer,
            institution_type="farmer_producer_company",
            registration_number="U00000MH2021PTC000000",
            authorised_signatory_name="Authorised Person",
            board_resolution_required_flag=True,
            services_availed_flag=True,
            produce_supply_years="2.00",
        )

        response = self.client.get(self._url(producer.member_id), headers=self._headers())

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIsNone(data["individual_profile"])
        self.assertEqual(
            data["producer_institution_profile"],
            {
                "institution_type": "farmer_producer_company",
                "registration_number": "U00000MH2021PTC000000",
                "authorised_signatory_name": "Authorised Person",
                "board_resolution_required_flag": True,
                "services_availed_flag": True,
                "produce_supply_years": "2.00",
            },
        )
        serialized = str(data["producer_institution_profile"]).lower()
        self.assertNotIn("signatory_pan", serialized)
        self.assertNotIn("signatory_aadhaar", serialized)

    def test_member_without_type_specific_profile_returns_null_profile_objects(self):
        producer = self._member(
            member_type="producer_institution",
            legal_name="Missing Profile Producer Institution",
            display_name="Missing Profile PI",
            folio_number="FOL-790",
            pan_hash="hash-missing-profile-pan",
        )

        response = self.client.get(self._url(producer.member_id), headers=self._headers())

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIsNone(data["individual_profile"])
        self.assertIsNone(data["producer_institution_profile"])

    def test_profile_models_reject_member_type_mismatches(self):
        fpc = self._member(
            member_type="fpc",
            legal_name="Wrong Individual Owner",
            display_name="Wrong Individual Owner",
            folio_number="FOL-791",
            pan_hash="hash-wrong-individual",
        )
        individual = self._member(
            member_type="individual_farmer",
            legal_name="Wrong Producer Owner",
            display_name="Wrong Producer Owner",
            folio_number="FOL-792",
            pan_hash="hash-wrong-producer",
        )

        with self.assertRaises(ValidationError):
            IndividualMemberProfile.objects.create(
                member=fpc,
                first_name="Wrong",
                last_name="Profile",
            )
        with self.assertRaises(ValidationError):
            ProducerInstitutionProfile.objects.create(
                member=individual,
                institution_type="farmer_producer_company",
                authorised_signatory_name="Wrong Profile",
            )

    def test_member_profile_requires_authentication_and_member_read_permission(self):
        unauthenticated = self.client.get(self._url(self.member.member_id))
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        forbidden = self.client.get(self._url(self.member.member_id), headers=self._plain_headers())
        self.assertEqual(forbidden.status_code, 403)
        assert_error_envelope(self, forbidden.json(), "PERMISSION_DENIED")

    def test_masked_profile_read_does_not_create_audit_or_workflow_events(self):
        response = self.client.get(self._url(self.member.member_id), headers=self._headers())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditLog.objects.count(), 1)
        self.assertEqual(AuditLog.objects.first().action, "auth.login.succeeded")
        self.assertEqual(WorkflowEvent.objects.count(), 0)

    def test_pan_reveal_returns_temporary_value_and_audits_metadata_only(self):
        response = self.client.post(
            self._reveal_url(),
            data={"field_name": "pan", "reason": "KYC verification during loan application"},
            content_type="application/json",
            headers={
                **self._pan_reveal_headers(),
                "X-Request-ID": "req-pan-reveal",
                "User-Agent": "sfpcl-test-agent",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["Pragma"], "no-cache")
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-pan-reveal")
        self.assertEqual(payload["data"]["field_name"], "pan")
        self.assertEqual(payload["data"]["value"], "ABCDE1234F")
        self.assertRegex(payload["data"]["expires_at"], r"Z$")

        audit = AuditLog.objects.filter(action="members.sensitive_field.revealed").get()
        self.assertEqual(audit.actor_user, self.pan_revealer)
        self.assertEqual(audit.entity_type, "member")
        self.assertEqual(audit.entity_id, self.member.member_id)
        self.assertEqual(audit.ip_address, "127.0.0.1")
        self.assertEqual(audit.user_agent, "sfpcl-test-agent")
        self.assertEqual(
            audit.new_value_json,
            {
                "member_id": str(self.member.member_id),
                "field_name": "pan",
                "reason": "KYC verification during loan application",
                "outcome": "success",
                "request_id": "req-pan-reveal",
                "expires_at": payload["data"]["expires_at"],
            },
        )
        serialized_audit = str(audit.new_value_json).lower()
        for forbidden in ("abcde1234f", "123456789012", "hash-pan", "hash-aadhaar"):
            self.assertNotIn(forbidden, serialized_audit)
        self.assertEqual(WorkflowEvent.objects.count(), 0)

    def test_aadhaar_reveal_uses_aadhaar_permission_only(self):
        response = self.client.post(
            self._reveal_url(),
            data={"field_name": "aadhaar", "reason": "Re-KYC verification"},
            content_type="application/json",
            headers=self._aadhaar_reveal_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["data"]["field_name"], "aadhaar")
        self.assertEqual(payload["data"]["value"], "123456789012")
        self.assertRegex(payload["data"]["expires_at"], r"Z$")

        pan_attempt = self.client.post(
            self._reveal_url(),
            data={"field_name": "pan", "reason": "Wrong permission check"},
            content_type="application/json",
            headers=self._aadhaar_reveal_headers(),
        )
        self.assertEqual(pan_attempt.status_code, 403)
        assert_error_envelope(self, pan_attempt.json(), "SENSITIVE_FIELD_ACCESS_DENIED")

    def test_reveal_requires_authentication_base_read_and_field_permission(self):
        unauthenticated = self.client.post(
            self._reveal_url(),
            data={"field_name": "pan", "reason": "KYC verification"},
            content_type="application/json",
        )
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")
        self.assertFalse(AuditLog.objects.filter(action="members.sensitive_field.reveal_denied").exists())

        missing_read = self.client.post(
            self._reveal_url(),
            data={"field_name": "pan", "reason": "KYC verification"},
            content_type="application/json",
            headers=self._plain_headers(),
        )
        self.assertEqual(missing_read.status_code, 403)
        assert_error_envelope(self, missing_read.json(), "PERMISSION_DENIED")

        missing_field_permission = self.client.post(
            self._reveal_url(),
            data={"field_name": "aadhaar", "reason": "KYC verification"},
            content_type="application/json",
            headers=self._pan_reveal_headers(),
        )
        self.assertEqual(missing_field_permission.status_code, 403)
        assert_error_envelope(self, missing_field_permission.json(), "SENSITIVE_FIELD_ACCESS_DENIED")

        denials = AuditLog.objects.filter(action="members.sensitive_field.reveal_denied").order_by("created_at")
        self.assertEqual(denials.count(), 2)
        self.assertEqual(denials[0].new_value_json["outcome"], "denied")
        self.assertEqual(denials[0].new_value_json["denial_reason"], "missing_base_read_permission")
        self.assertEqual(denials[0].new_value_json["field_name"], "pan")
        self.assertEqual(denials[0].new_value_json["reason"], "KYC verification")
        self.assertEqual(denials[1].new_value_json["denial_reason"], "missing_field_permission")
        self.assertEqual(denials[1].new_value_json["field_name"], "aadhaar")
        serialized = str([row.new_value_json for row in denials]).lower()
        for forbidden in ("abcde1234f", "123456789012", "hash-pan", "hash-aadhaar"):
            self.assertNotIn(forbidden, serialized)

    def test_reveal_validates_field_reason_member_and_available_value(self):
        cases = [
            ({"reason": "KYC verification"}, "field_name"),
            ({"field_name": "ifsc", "reason": "KYC verification"}, "field_name"),
            ({"field_name": "pan", "reason": "   "}, "reason"),
        ]
        for body, expected_field in cases:
            with self.subTest(body=body):
                response = self.client.post(
                    self._reveal_url(),
                    data=body,
                    content_type="application/json",
                    headers=self._pan_reveal_headers(),
                )
                self.assertEqual(response.status_code, 400)
                payload = response.json()
                assert_error_envelope(self, payload, "VALIDATION_ERROR")
                self.assertIn(expected_field, payload["error"]["field_errors"])

        for member_id in (uuid.uuid4(), self.deleted.member_id):
            response = self.client.post(
                self._reveal_url(member_id),
                data={"field_name": "pan", "reason": "KYC verification"},
                content_type="application/json",
                headers=self._pan_reveal_headers(),
            )
            self.assertEqual(response.status_code, 404)
            assert_error_envelope(self, response.json(), "NOT_FOUND")

        missing_value_member = self._member(aadhaar_encrypted="", aadhaar_hash="")
        response = self.client.post(
            self._reveal_url(missing_value_member.member_id),
            data={"field_name": "aadhaar", "reason": "KYC verification"},
            content_type="application/json",
            headers=self._aadhaar_reveal_headers(),
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("field_name", payload["error"]["field_errors"])

        self.assertGreaterEqual(
            AuditLog.objects.filter(action="members.sensitive_field.reveal_denied").count(),
            5,
        )

    def _member(self, **overrides):
        values = {
            "member_type": "individual_farmer",
            "legal_name": "Member",
            "display_name": "Member",
            "folio_number": f"FOL-{uuid.uuid4()}",
            "membership_status": "active",
            "pan_encrypted": "ABCDE1234F",
            "pan_hash": f"hash-{uuid.uuid4()}",
            "kyc_status": "verified",
            "default_status": "no_default",
        }
        values.update(overrides)
        return Member.objects.create(**values)
