import uuid

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
)
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.models import WorkflowEvent


WORKFLOW_ITEM_FIELDS = {
    "workflow_event_id",
    "workflow_name",
    "module",
    "entity_type",
    "entity_id",
    "linked_record",
    "from_state",
    "to_state",
    "triggered_by_user",
    "trigger_reason",
    "created_at",
}


class WorkflowEventServiceTests(TestCase):
    """003B: canonical write interface for the source §26.2 workflow_events table."""

    def setUp(self):
        self.role = Role.objects.create(
            role_code="workflow_actor",
            role_name="Workflow Actor",
            is_system_role=True,
            status="active",
        )
        self.actor = User.objects.create(
            full_name="Workflow Actor",
            email="workflow.actor@sfpcl.example",
            status="active",
            primary_role=self.role,
        )

    def test_record_workflow_event_persists_canonical_workflow_facts(self):
        entity_id = uuid.uuid4()

        event = record_workflow_event(
            actor=self.actor,
            workflow_name="application",
            entity_type="loan_application",
            entity_id=entity_id,
            from_state="draft",
            to_state="submitted",
            trigger_reason="Application submitted for credit review",
        )

        persisted = WorkflowEvent.objects.get(workflow_event_id=event.workflow_event_id)
        self.assertEqual(persisted.workflow_name, "application")
        self.assertEqual(persisted.entity_type, "loan_application")
        self.assertEqual(persisted.entity_id, entity_id)
        self.assertEqual(persisted.from_state, "draft")
        self.assertEqual(persisted.to_state, "submitted")
        self.assertEqual(persisted.triggered_by_user, self.actor)
        self.assertEqual(
            persisted.trigger_reason, "Application submitted for credit review"
        )


class WorkflowEventsApiTests(TestCase):
    """003B: protected GET /api/v1/workflow-events/ over canonical WorkflowEvent."""

    URL = "/api/v1/workflow-events/"

    def setUp(self):
        self.client = Client()

        self.auditor_role = Role.objects.create(
            role_code="internal_auditor",
            role_name="Internal Auditor",
            is_system_role=True,
            status="active",
        )
        self.workflow_permission = Permission.objects.create(
            permission_code="audit.workflow_event.read",
            permission_name="View workflow events",
            module_name="audit",
            risk_level="high",
        )
        RolePermission.objects.create(
            role=self.auditor_role, permission=self.workflow_permission
        )
        ApprovalCaseReadScopeGrant.objects.create(
            role=self.auditor_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        )
        self.auditor = User.objects.create(
            full_name="Ivy Auditor",
            email="auditor@sfpcl.example",
            status="active",
            primary_role=self.auditor_role,
        )
        self.auditor.set_password("AuditorPass123!")
        self.auditor.save()

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

        base = timezone.now() - timezone.timedelta(hours=1)
        self.loan_entity_id = uuid.uuid4()
        self.other_entity_id = uuid.uuid4()

        self.row_oldest = WorkflowEvent.objects.create(
            workflow_name="application",
            entity_type="loan_application",
            entity_id=self.loan_entity_id,
            from_state="draft",
            to_state="submitted",
            triggered_by_user=self.auditor,
            trigger_reason="Submitted for review",
            created_at=base,
        )
        self.row_other = WorkflowEvent.objects.create(
            workflow_name="member",
            entity_type="member",
            entity_id=self.other_entity_id,
            from_state=None,
            to_state="active",
            triggered_by_user=self.plain_user,
            trigger_reason="Member activated",
            created_at=base + timezone.timedelta(minutes=10),
        )
        self.row_system = WorkflowEvent.objects.create(
            workflow_name="configuration",
            entity_type="config",
            entity_id=uuid.uuid4(),
            from_state="draft",
            to_state="published",
            triggered_by_user=None,
            trigger_reason="Policy version published",
            created_at=base + timezone.timedelta(minutes=20),
        )

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

    def test_unauthenticated_request_returns_auth_required(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "AUTH_REQUIRED")

    def test_user_without_workflow_event_permission_is_forbidden(self):
        headers = self._auth_headers(
            email="manager@sfpcl.example", password="ManagerPass123!"
        )
        response = self.client.get(self.URL, headers=headers)
        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, response.json(), "PERMISSION_DENIED")

    def test_authorized_list_returns_item_shape_and_pagination_newest_first(self):
        response = self.client.get(
            self.URL,
            headers={**self._auth_headers(), "X-Request-ID": "req-workflow-list"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-workflow-list")

        for item in payload["data"]:
            self.assertEqual(set(item.keys()), WORKFLOW_ITEM_FIELDS)

        self.assertEqual(
            [item["workflow_event_id"] for item in payload["data"][:3]],
            [
                str(self.row_system.workflow_event_id),
                str(self.row_other.workflow_event_id),
                str(self.row_oldest.workflow_event_id),
            ],
        )
        actor_item = next(
            item
            for item in payload["data"]
            if item["workflow_event_id"] == str(self.row_oldest.workflow_event_id)
        )
        self.assertEqual(
            actor_item["triggered_by_user"],
            {"user_id": str(self.auditor.user_id), "full_name": "Ivy Auditor"},
        )
        self.assertEqual(actor_item["workflow_name"], "application")
        self.assertEqual(actor_item["entity_type"], "loan_application")
        self.assertEqual(actor_item["entity_id"], str(self.loan_entity_id))
        self.assertEqual(actor_item["from_state"], "draft")
        self.assertEqual(actor_item["to_state"], "submitted")
        self.assertEqual(actor_item["trigger_reason"], "Submitted for review")

    def test_system_row_without_actor_serializes_triggered_by_user_null(self):
        response = self.client.get(
            self.URL + f"?entity_type=config&entity_id={self.row_system.entity_id}",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(len(payload["data"]), 1)
        item = payload["data"][0]
        self.assertIsNone(item["triggered_by_user"])
        self.assertEqual(item["workflow_name"], "configuration")
        self.assertEqual(item["to_state"], "published")

    def test_entity_type_and_entity_id_filter_returns_only_matching_rows(self):
        response = self.client.get(
            self.URL
            + f"?entity_type=loan_application&entity_id={self.loan_entity_id}",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(
            [item["workflow_event_id"] for item in payload["data"]],
            [str(self.row_oldest.workflow_event_id)],
        )

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
