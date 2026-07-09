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
        self.reader = self._user("reader@sfpcl.example", "ReaderPass123!", member_read, app_create)
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

    def _plain_headers(self):
        return {"Authorization": f"Bearer {self._token('plain@sfpcl.example', 'PlainPass123!')}"}

    def _url(self, member_id):
        return f"/api/v1/members/{member_id}/"

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
        self.assertEqual(data["available_actions"][0]["action_code"], "create_loan_application")
        self.assertTrue(data["available_actions"][0]["enabled"])
        serialized = str(data).lower()
        for forbidden in ("pan_encrypted", "aadhaar_encrypted", "pan_hash", "aadhaar_hash", "abcde1234f", "123456789012"):
            self.assertNotIn(forbidden, serialized)

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
