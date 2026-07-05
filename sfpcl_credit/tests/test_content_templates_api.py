import uuid

from django.test import Client, TestCase

from sfpcl_credit.communications.models import ContentTemplate
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)


CONTENT_TEMPLATES_URL = "/api/v1/content-templates/"
CONTENT_TEMPLATE_READ_PERMISSION = "communications.content_template.read"
CONTENT_TEMPLATE_MANAGE_PERMISSION = "communications.content_template.manage"

CONTENT_TEMPLATE_RESPONSE_FIELDS = {
    "content_template_id",
    "template_code",
    "template_name",
    "template_type",
    "language_code",
    "audience",
    "subject_template",
    "body_template",
    "variables",
    "approval_status",
    "template_version",
    "effective_from",
    "effective_to",
}


class ContentTemplateApiTests(TestCase):
    """003F: protected content-template metadata API shell."""

    def setUp(self):
        self.client = Client()
        self.reader_role = Role.objects.create(
            role_code="content_template_reader",
            role_name="Content Template Reader",
            is_system_role=True,
            status="active",
        )
        read_permission = Permission.objects.create(
            permission_code=CONTENT_TEMPLATE_READ_PERMISSION,
            permission_name="View content templates",
            module_name="communications",
            risk_level="medium",
        )
        RolePermission.objects.create(role=self.reader_role, permission=read_permission)
        self.reader = User.objects.create(
            full_name="Rina Reader",
            email="rina.reader@sfpcl.example",
            status="active",
            primary_role=self.reader_role,
        )
        self.reader.set_password("ReaderPass123!")
        self.reader.save()

        self.manager_role = Role.objects.create(
            role_code="content_template_manager",
            role_name="Content Template Manager",
            is_system_role=True,
            status="active",
        )
        manage_permission = Permission.objects.create(
            permission_code=CONTENT_TEMPLATE_MANAGE_PERMISSION,
            permission_name="Manage content templates",
            module_name="communications",
            risk_level="medium",
        )
        RolePermission.objects.create(role=self.manager_role, permission=read_permission)
        RolePermission.objects.create(role=self.manager_role, permission=manage_permission)
        self.manager = User.objects.create(
            full_name="Meera Manager",
            email="meera.manager@sfpcl.example",
            status="active",
            primary_role=self.manager_role,
        )
        self.manager.set_password("ManagerPass123!")
        self.manager.save()

        self.plain_role = Role.objects.create(
            role_code="plain_staff",
            role_name="Plain Staff",
            is_system_role=True,
            status="active",
        )
        self.plain_user = User.objects.create(
            full_name="Paul Plain",
            email="paul.content@sfpcl.example",
            status="active",
            primary_role=self.plain_role,
        )
        self.plain_user.set_password("PlainPass123!")
        self.plain_user.save()

    def _access_token(self, email="rina.reader@sfpcl.example", password="ReaderPass123!"):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _auth_headers(self, **kwargs):
        return {"Authorization": f"Bearer {self._access_token(**kwargs)}"}

    def _manager_headers(self):
        return self._auth_headers(
            email="meera.manager@sfpcl.example", password="ManagerPass123!"
        )

    def _plain_headers(self):
        return self._auth_headers(
            email="paul.content@sfpcl.example", password="PlainPass123!"
        )

    def _sample_payload(self, **overrides):
        payload = {
            "template_code": "loan_rejection_email_v1",
            "template_name": "Loan Rejection Email",
            "template_type": "email",
            "language_code": "en",
            "audience": "borrower",
            "subject_template": (
                "Loan Application {{application_reference_number}} - Rejection Note"
            ),
            "body_template": (
                "Dear {{borrower_name}}, your application has been rejected."
            ),
            "variables": [
                "application_reference_number",
                "borrower_name",
                "rejection_reason",
            ],
            "approval_status": "approved",
            "template_version": "1.0",
            "effective_from": "2026-04-01",
        }
        payload.update(overrides)
        return payload

    def _content_template(self, **overrides):
        defaults = {
            "template_code": "loan_rejection_email_v1",
            "template_name": "Loan Rejection Email",
            "template_type": "email",
            "language_code": "en",
            "audience": "borrower",
            "subject_template": (
                "Loan Application {{application_reference_number}} - Rejection Note"
            ),
            "body_template": (
                "Dear {{borrower_name}}, your application has been rejected."
            ),
            "variables_json": [
                "application_reference_number",
                "borrower_name",
                "rejection_reason",
            ],
            "approval_status": "approved",
            "template_version": "1.0",
            "effective_from": "2026-04-01",
        }
        defaults.update(overrides)
        return ContentTemplate.objects.create(**defaults)

    def test_authorized_list_returns_standard_pagination_and_metadata_fields(self):
        row = self._content_template()

        response = self.client.get(
            CONTENT_TEMPLATES_URL,
            headers={**self._auth_headers(), "X-Request-ID": "req-content-list"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-content-list")
        self.assertEqual(len(payload["data"]), 1)
        item = payload["data"][0]
        self.assertEqual(set(item.keys()), CONTENT_TEMPLATE_RESPONSE_FIELDS)
        self.assertEqual(item["content_template_id"], str(row.content_template_id))
        self.assertEqual(item["variables"], row.variables_json)
        self.assertNotIn("rendered_body", item)
        self.assertNotIn("merge_data", item)

    def test_create_persists_variables_and_writes_metadata_only_audit(self):
        response = self.client.post(
            CONTENT_TEMPLATES_URL,
            data=self._sample_payload(),
            content_type="application/json",
            headers={**self._manager_headers(), "X-Request-ID": "req-content-create"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-content-create")
        self.assertEqual(set(payload["data"].keys()), CONTENT_TEMPLATE_RESPONSE_FIELDS)
        self.assertEqual(payload["data"]["variables"], self._sample_payload()["variables"])

        row = ContentTemplate.objects.get(
            content_template_id=payload["data"]["content_template_id"]
        )
        self.assertEqual(row.template_code, "loan_rejection_email_v1")
        self.assertEqual(row.variables_json, self._sample_payload()["variables"])

        audit = AuditLog.objects.get(action="communications.content_template.created")
        self.assertEqual(audit.actor_user, self.manager)
        self.assertEqual(audit.entity_type, "content_template")
        self.assertEqual(audit.entity_id, row.content_template_id)
        self.assertEqual(audit.new_value_json["template_code"], row.template_code)
        self.assertEqual(audit.new_value_json["variables"], row.variables_json)
        self.assertNotIn("rendered_body", audit.new_value_json)
        self.assertNotIn("merge_data", audit.new_value_json)

    def test_patch_updates_template_and_writes_audit(self):
        row = self._content_template(approval_status="draft")

        response = self.client.patch(
            f"{CONTENT_TEMPLATES_URL}{row.content_template_id}/",
            data={
                "template_name": "Updated Rejection Email",
                "approval_status": "approved",
                "effective_to": "2027-03-31",
            },
            content_type="application/json",
            headers=self._manager_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["data"]["template_name"], "Updated Rejection Email")
        self.assertEqual(payload["data"]["approval_status"], "approved")
        self.assertEqual(payload["data"]["effective_to"], "2027-03-31")

        audit = AuditLog.objects.get(action="communications.content_template.updated")
        self.assertEqual(audit.old_value_json["template_name"], "Loan Rejection Email")
        self.assertEqual(
            audit.new_value_json["template_name"], "Updated Rejection Email"
        )

    def test_create_validation_errors_do_not_write_rows_or_audit(self):
        invalid = self._sample_payload(
            template_code="",
            variables=[{"name": "borrower_name"}],
            approval_status="published",
            effective_from="not-a-date",
            effective_to="2026-03-31",
        )
        invalid.pop("body_template")

        response = self.client.post(
            CONTENT_TEMPLATES_URL,
            data=invalid,
            content_type="application/json",
            headers=self._manager_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        for field in (
            "template_code",
            "body_template",
            "variables",
            "approval_status",
            "effective_from",
        ):
            self.assertIn(field, payload["error"]["field_errors"])
        self.assertEqual(ContentTemplate.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action__startswith="communications.content_template."
            ).count(),
            0,
        )

    def test_duplicate_template_code_returns_validation_error_without_audit(self):
        self._content_template()

        response = self.client.post(
            CONTENT_TEMPLATES_URL,
            data=self._sample_payload(),
            content_type="application/json",
            headers=self._manager_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("template_code", payload["error"]["field_errors"])
        self.assertEqual(ContentTemplate.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(
                action__startswith="communications.content_template."
            ).count(),
            0,
        )

    def test_unknown_content_template_id_returns_standard_not_found(self):
        response = self.client.patch(
            f"{CONTENT_TEMPLATES_URL}{uuid.uuid4()}/",
            data={"template_name": "Missing"},
            content_type="application/json",
            headers=self._manager_headers(),
        )

        self.assertEqual(response.status_code, 404)
        assert_error_envelope(self, response.json(), "NOT_FOUND")

    def test_unauthenticated_and_no_permission_requests_do_not_write(self):
        response = self.client.get(CONTENT_TEMPLATES_URL)
        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "AUTH_REQUIRED")

        forbidden = self.client.post(
            CONTENT_TEMPLATES_URL,
            data=self._sample_payload(),
            content_type="application/json",
            headers=self._plain_headers(),
        )
        self.assertEqual(forbidden.status_code, 403)
        assert_error_envelope(self, forbidden.json(), "PERMISSION_DENIED")
        self.assertEqual(ContentTemplate.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action__startswith="communications.content_template."
            ).count(),
            0,
        )

    def test_reader_cannot_write_and_manager_can_list(self):
        forbidden = self.client.post(
            CONTENT_TEMPLATES_URL,
            data=self._sample_payload(),
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(forbidden.status_code, 403)
        assert_error_envelope(self, forbidden.json(), "PERMISSION_DENIED")

        response = self.client.get(
            CONTENT_TEMPLATES_URL,
            headers=self._manager_headers(),
        )
        self.assertEqual(response.status_code, 200)
        assert_pagination_shape(self, response.json())
