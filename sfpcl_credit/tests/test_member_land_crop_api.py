from uuid import uuid4

from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import CropPlan, LandHolding, Member
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


MEMBER_READ_PERMISSION = "members.member.read"
MEMBER_UPDATE_PERMISSION = "members.member.update"


class MemberLandCropApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.read_permission = Permission.objects.create(
            permission_code=MEMBER_READ_PERMISSION,
            permission_name="View members",
            module_name="members",
            risk_level="medium",
        )
        self.update_permission = Permission.objects.create(
            permission_code=MEMBER_UPDATE_PERMISSION,
            permission_name="Update members",
            module_name="members",
            risk_level="high",
        )
        self.reader = self._user(
            "land.reader@sfpcl.example",
            "ReaderPass123!",
            self.read_permission,
        )
        self.creator = self._user(
            "land.creator@sfpcl.example",
            "CreatorPass123!",
            self.update_permission,
        )
        self.reader_creator = self._user(
            "land.full@sfpcl.example",
            "FullPass123!",
            self.read_permission,
            self.update_permission,
        )
        self.plain = self._user("land.plain@sfpcl.example", "PlainPass123!")
        self.member = Member.objects.create(
            member_number="MEM-004G",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            folio_number="FOL-004G",
            membership_status="active",
            pan_encrypted="member-pan-token",
            pan_hash="member-pan-hash",
            aadhaar_encrypted="member-aadhaar-token",
            aadhaar_hash="member-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )

    def test_land_holding_can_be_created_and_listed(self):
        response = self.client.post(
            self._land_url(),
            data=self._land_payload(),
            content_type="application/json",
            headers={
                **self._headers("land.full@sfpcl.example", "FullPass123!"),
                "X-Request-ID": "req-create-land-holding",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["meta"]["request_id"], "req-create-land-holding")
        land = body["data"]
        self.assertEqual(land["document_type"], "7_12_extract")
        self.assertEqual(land["survey_number"], "123/4")
        self.assertEqual(land["village"], "Village Name")
        self.assertEqual(land["taluka"], "Niphad")
        self.assertEqual(land["district"], "Nashik")
        self.assertEqual(land["state"], "Maharashtra")
        self.assertEqual(land["area_acres"], "5.00")
        self.assertEqual(land["document_id"], self.land_document_id)
        self.assertEqual(land["verification_status"], "pending")
        self.assertIsNone(land["verified_by_user_id"])
        self.assertIsNone(land["verified_at"])

        persisted = LandHolding.objects.get(land_holding_id=land["land_holding_id"])
        self.assertEqual(str(persisted.member_id), str(self.member.member_id))

        list_response = self.client.get(
            self._land_url(),
            headers=self._headers("land.reader@sfpcl.example", "ReaderPass123!"),
        )

        self.assertEqual(list_response.status_code, 200)
        list_body = list_response.json()
        assert_pagination_shape(self, list_body)
        self.assertEqual(list_body["pagination"]["total_count"], 1)
        self.assertEqual(list_body["data"][0]["land_holding_id"], land["land_holding_id"])

    def test_crop_plan_can_be_created_and_listed(self):
        response = self.client.post(
            self._crop_url(),
            data=self._crop_payload(),
            content_type="application/json",
            headers=self._headers("land.full@sfpcl.example", "FullPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        crop = body["data"]
        self.assertEqual(crop["loan_application_id"], self.loan_application_id)
        self.assertEqual(crop["crop_type"], "grapes")
        self.assertEqual(crop["season"], "FY2026 Kharif")
        self.assertEqual(crop["planned_area_acres"], "5.00")
        self.assertEqual(crop["estimated_cost_amount"], "100000.00")
        self.assertEqual(crop["loan_purpose_alignment"], "agriculture_aligned")
        self.assertEqual(crop["document_id"], self.crop_document_id)
        self.assertEqual(crop["verification_status"], "pending")

        persisted = CropPlan.objects.get(crop_plan_id=crop["crop_plan_id"])
        self.assertEqual(str(persisted.member_id), str(self.member.member_id))

        list_response = self.client.get(
            self._crop_url(),
            headers=self._headers("land.reader@sfpcl.example", "ReaderPass123!"),
        )

        self.assertEqual(list_response.status_code, 200)
        list_body = list_response.json()
        assert_pagination_shape(self, list_body)
        self.assertEqual(list_body["pagination"]["total_count"], 1)
        self.assertEqual(list_body["data"][0]["crop_plan_id"], crop["crop_plan_id"])

    def test_land_and_crop_endpoints_require_authentication_and_separate_read_update_permissions(self):
        for url in (self._land_url(), self._crop_url()):
            with self.subTest(url=url):
                unauthenticated = self.client.get(url)
                self.assertEqual(unauthenticated.status_code, 401)
                assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

                no_read = self.client.get(
                    url,
                    headers=self._headers("land.creator@sfpcl.example", "CreatorPass123!"),
                )
                self.assertEqual(no_read.status_code, 403)
                assert_error_envelope(self, no_read.json(), "PERMISSION_DENIED")

                no_create = self.client.post(
                    url,
                    data=self._land_payload() if "land-holdings" in url else self._crop_payload(),
                    content_type="application/json",
                    headers=self._headers("land.reader@sfpcl.example", "ReaderPass123!"),
                )
                self.assertEqual(no_create.status_code, 403)
                assert_error_envelope(self, no_create.json(), "PERMISSION_DENIED")

                plain = self.client.post(
                    url,
                    data=self._land_payload() if "land-holdings" in url else self._crop_payload(),
                    content_type="application/json",
                    headers=self._headers("land.plain@sfpcl.example", "PlainPass123!"),
                )
                self.assertEqual(plain.status_code, 403)
                assert_error_envelope(self, plain.json(), "PERMISSION_DENIED")

    def test_land_and_crop_endpoints_return_not_found_for_unknown_or_deleted_member(self):
        for url_factory in (self._land_url, self._crop_url):
            for member_id in (uuid4(), self._deleted_member().member_id):
                with self.subTest(url=url_factory, member_id=member_id):
                    response = self.client.get(
                        url_factory(member_id),
                        headers=self._headers("land.reader@sfpcl.example", "ReaderPass123!"),
                    )
                    self.assertEqual(response.status_code, 404)
                    assert_error_envelope(self, response.json(), "NOT_FOUND")

    def test_land_holding_create_rejects_invalid_acreage_and_document_id(self):
        cases = [
            ({"area_acres": "0"}, "area_acres"),
            ({"area_acres": "-0.01"}, "area_acres"),
            ({"document_id": ""}, "document_id"),
            ({"document_id": "not-a-uuid"}, "document_id"),
        ]
        for override, field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    self._land_url(),
                    data=self._land_payload(**override),
                    content_type="application/json",
                    headers=self._headers("land.creator@sfpcl.example", "CreatorPass123!"),
                )

                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, "VALIDATION_ERROR")
                self.assertIn(field, body["error"]["field_errors"])

    def test_crop_plan_create_rejects_invalid_acreage_and_malformed_uuids(self):
        cases = [
            ({"planned_area_acres": "0"}, "planned_area_acres"),
            ({"planned_area_acres": "-0.01"}, "planned_area_acres"),
            ({"loan_application_id": "not-a-uuid"}, "loan_application_id"),
            ({"document_id": "not-a-uuid"}, "document_id"),
        ]
        for override, field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    self._crop_url(),
                    data=self._crop_payload(**override),
                    content_type="application/json",
                    headers=self._headers("land.creator@sfpcl.example", "CreatorPass123!"),
                )

                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, "VALIDATION_ERROR")
                self.assertIn(field, body["error"]["field_errors"])

    def test_land_and_crop_creates_audit_metadata_without_workflow_event(self):
        land_response = self.client.post(
            self._land_url(),
            data=self._land_payload(area_acres="3.25"),
            content_type="application/json",
            headers=self._headers("land.creator@sfpcl.example", "CreatorPass123!"),
        )
        crop_response = self.client.post(
            self._crop_url(),
            data=self._crop_payload(planned_area_acres="2.50"),
            content_type="application/json",
            headers=self._headers("land.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(land_response.status_code, 200)
        self.assertEqual(crop_response.status_code, 200)
        land_id = land_response.json()["data"]["land_holding_id"]
        crop_id = crop_response.json()["data"]["crop_plan_id"]

        land_audit = AuditLog.objects.filter(action="members.land_holding.created").get()
        self.assertEqual(str(land_audit.entity_id), land_id)
        self.assertEqual(land_audit.entity_type, "land_holding")
        self.assertEqual(land_audit.new_value_json["member_id"], str(self.member.member_id))
        self.assertEqual(land_audit.new_value_json["area_acres"], "3.25")
        self.assertEqual(land_audit.new_value_json["document_id"], self.land_document_id)

        crop_audit = AuditLog.objects.filter(action="members.crop_plan.created").get()
        self.assertEqual(str(crop_audit.entity_id), crop_id)
        self.assertEqual(crop_audit.entity_type, "crop_plan")
        self.assertEqual(crop_audit.new_value_json["member_id"], str(self.member.member_id))
        self.assertEqual(crop_audit.new_value_json["planned_area_acres"], "2.50")
        self.assertEqual(crop_audit.new_value_json["loan_purpose_alignment"], "agriculture_aligned")
        self.assertEqual(WorkflowEvent.objects.count(), 0)

    def _land_payload(self, **overrides):
        self.land_document_id = getattr(self, "land_document_id", str(uuid4()))
        payload = {
            "document_type": "7_12_extract",
            "survey_number": "123/4",
            "village": "Village Name",
            "taluka": "Niphad",
            "district": "Nashik",
            "state": "Maharashtra",
            "area_acres": "5.00",
            "document_id": self.land_document_id,
        }
        payload.update(overrides)
        return payload

    def _crop_payload(self, **overrides):
        self.loan_application_id = getattr(self, "loan_application_id", str(uuid4()))
        self.crop_document_id = getattr(self, "crop_document_id", str(uuid4()))
        payload = {
            "loan_application_id": self.loan_application_id,
            "crop_type": "grapes",
            "season": "FY2026 Kharif",
            "planned_area_acres": "5.00",
            "estimated_cost_amount": "100000.00",
            "loan_purpose_alignment": "agriculture_aligned",
            "document_id": self.crop_document_id,
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

    def _land_url(self, member_id=None):
        return f"/api/v1/members/{member_id or self.member.member_id}/land-holdings/"

    def _crop_url(self, member_id=None):
        return f"/api/v1/members/{member_id or self.member.member_id}/crop-plans/"

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
