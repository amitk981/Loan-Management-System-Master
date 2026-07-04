import uuid

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    User,
)
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
)


AUDIT_ITEM_FIELDS = {
    "audit_log_id",
    "actor",
    "actor_type",
    "action",
    "entity_type",
    "entity_id",
    "old_value",
    "new_value",
    "ip_address",
    "created_at",
}


class AuditLogsApiTests(TestCase):
    """003A: read-only GET /api/v1/audit-logs/ over the existing identity.AuditLog."""

    URL = "/api/v1/audit-logs/"

    def setUp(self):
        self.client = Client()

        # Role holding the canonical audit-read permission (002C catalogue).
        self.auditor_role = Role.objects.create(
            role_code="internal_auditor",
            role_name="Internal Auditor",
            is_system_role=True,
            status="active",
        )
        self.audit_permission = Permission.objects.create(
            permission_code="audit.audit_log.read",
            permission_name="View audit logs",
            module_name="audit",
            risk_level="high",
        )
        RolePermission.objects.create(
            role=self.auditor_role, permission=self.audit_permission
        )
        self.auditor = User.objects.create(
            full_name="Ivy Auditor",
            email="auditor@sfpcl.example",
            status="active",
            primary_role=self.auditor_role,
        )
        self.auditor.set_password("AuditorPass123!")
        self.auditor.save()

        # Role WITHOUT the audit-read permission.
        self.plain_role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
            is_system_role=True,
            status="active",
        )
        self.plain_user = User.objects.create(
            full_name="Carl Manager",
            email="manager@sfpcl.example",
            status="active",
            primary_role=self.plain_role,
        )
        self.plain_user.set_password("ManagerPass123!")
        self.plain_user.save()

        # Deterministic timestamps so newest-first ordering is assertable.
        base = timezone.now() - timezone.timedelta(hours=1)
        self.loan_entity_id = uuid.uuid4()
        self.other_entity_id = uuid.uuid4()

        # Oldest: a user-actor row on a loan_application entity.
        self.row_actor = AuditLog.objects.create(
            actor_user=self.auditor,
            actor_type="user",
            action="loan_application.submitted",
            entity_type="loan_application",
            entity_id=self.loan_entity_id,
            old_value_json={"application_status": "draft"},
            new_value_json={"application_status": "submitted"},
            ip_address="10.0.0.1",
            created_at=base,
        )
        # Middle: a different entity_type/entity_id, different actor.
        self.row_other_entity = AuditLog.objects.create(
            actor_user=self.plain_user,
            actor_type="user",
            action="member.updated",
            entity_type="member",
            entity_id=self.other_entity_id,
            ip_address="10.0.0.2",
            created_at=base + timezone.timedelta(minutes=10),
        )
        # Newest: a system row with no actor (actor_user is None).
        self.row_system = AuditLog.objects.create(
            actor_user=None,
            actor_type="system",
            action="config.updated",
            entity_type="config",
            entity_id=uuid.uuid4(),
            old_value_json={"flag": False},
            new_value_json={"flag": True},
            ip_address="",
            created_at=base + timezone.timedelta(minutes=20),
        )

    # ---- helpers -------------------------------------------------------

    def _access_token(self, email="auditor@sfpcl.example", password="AuditorPass123!"):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _auth_headers(self, **kwargs):
        return {"Authorization": f"Bearer {self._access_token(**kwargs)}"}

    def _items_by_id(self, payload):
        return {item["audit_log_id"]: item for item in payload["data"]}

    # ---- auth / permission --------------------------------------------

    def test_unauthenticated_request_returns_auth_required(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 401)
        payload = response.json()
        assert_error_envelope(self, payload, "AUTH_REQUIRED")

    def test_malformed_bearer_returns_invalid_token(self):
        response = self.client.get(
            self.URL, headers={"Authorization": "Bearer"}
        )
        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "INVALID_TOKEN")

    def test_user_without_audit_permission_is_forbidden(self):
        headers = self._auth_headers(
            email="manager@sfpcl.example", password="ManagerPass123!"
        )
        response = self.client.get(self.URL, headers=headers)
        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, response.json(), "PERMISSION_DENIED")

    # ---- success / shape ----------------------------------------------

    def test_authorized_list_returns_item_shape_and_pagination_newest_first(self):
        response = self.client.get(
            self.URL,
            headers={**self._auth_headers(), "X-Request-ID": "req-audit-list"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-audit-list")

        # Every item carries exactly the §42.1 field set.
        for item in payload["data"]:
            self.assertEqual(set(item.keys()), AUDIT_ITEM_FIELDS)

        items = self._items_by_id(payload)
        actor_item = items[str(self.row_actor.audit_log_id)]
        self.assertEqual(
            actor_item["actor"],
            {"user_id": str(self.auditor.user_id), "full_name": "Ivy Auditor"},
        )
        self.assertEqual(actor_item["actor_type"], "user")
        self.assertEqual(actor_item["action"], "loan_application.submitted")
        self.assertEqual(actor_item["entity_type"], "loan_application")
        self.assertEqual(actor_item["entity_id"], str(self.loan_entity_id))
        self.assertEqual(actor_item["old_value"], {"application_status": "draft"})
        self.assertEqual(actor_item["new_value"], {"application_status": "submitted"})
        self.assertEqual(actor_item["ip_address"], "10.0.0.1")

        # Newest-first: the three seeded rows appear in descending created_at order.
        seeded = [self.row_system, self.row_other_entity, self.row_actor]
        order = [str(row.audit_log_id) for row in seeded]
        positions = {
            item["audit_log_id"]: index
            for index, item in enumerate(payload["data"])
        }
        found = [audit_id for audit_id in order if audit_id in positions]
        self.assertEqual(found, order)
        self.assertEqual(
            [positions[audit_id] for audit_id in found],
            sorted(positions[audit_id] for audit_id in found),
        )

    def test_system_row_without_actor_serializes_actor_null(self):
        response = self.client.get(
            self.URL + f"?entity_type=config&entity_id={self.row_system.entity_id}",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(len(payload["data"]), 1)
        item = payload["data"][0]
        self.assertIsNone(item["actor"])
        self.assertEqual(item["actor_type"], "system")
        self.assertEqual(item["action"], "config.updated")
        self.assertEqual(item["entity_type"], "config")
        self.assertEqual(item["entity_id"], str(self.row_system.entity_id))
        self.assertIn("created_at", item)

    # ---- filters ------------------------------------------------------

    def test_entity_type_and_entity_id_filter_returns_only_matching_rows(self):
        response = self.client.get(
            self.URL
            + f"?entity_type=loan_application&entity_id={self.loan_entity_id}",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        ids = {item["audit_log_id"] for item in payload["data"]}
        self.assertEqual(ids, {str(self.row_actor.audit_log_id)})

    def test_actor_user_id_filter_returns_only_that_actors_rows(self):
        response = self.client.get(
            self.URL + f"?actor_user_id={self.plain_user.user_id}",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        ids = {item["audit_log_id"] for item in payload["data"]}
        self.assertEqual(ids, {str(self.row_other_entity.audit_log_id)})

    def test_empty_result_set_returns_success_empty_data_and_pagination(self):
        response = self.client.get(
            self.URL + f"?entity_id={uuid.uuid4()}",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["data"], [])
        self.assertEqual(payload["pagination"]["total_count"], 0)

    # ---- validation ---------------------------------------------------

    def test_invalid_uuid_filter_returns_validation_error_with_field_errors(self):
        response = self.client.get(
            self.URL + "?entity_id=not-a-uuid",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("entity_id", payload["error"]["field_errors"])

    def test_unknown_query_parameter_returns_validation_error(self):
        response = self.client.get(
            self.URL + "?not_a_filter=1",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("not_a_filter", payload["error"]["field_errors"])

    def test_known_pagination_parameters_remain_allowed(self):
        response = self.client.get(
            self.URL + "?page=1&page_size=2",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["pagination"]["page"], 1)
        self.assertEqual(payload["pagination"]["page_size"], 2)

    # ---- append-only / no read auditing -------------------------------

    def test_reading_audit_logs_creates_no_new_audit_row(self):
        # Mint the token first (login writes audit rows); count AFTER that so we
        # measure only what the GET itself does.
        headers = self._auth_headers()
        before = AuditLog.objects.count()
        response = self.client.get(self.URL, headers=headers)
        self.assertEqual(response.status_code, 200)
        after = AuditLog.objects.count()
        self.assertEqual(after, before)
