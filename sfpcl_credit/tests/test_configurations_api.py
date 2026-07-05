import uuid

from django.test import Client, TestCase

from sfpcl_credit.configurations.models import LoanPolicyConfig, VersionHistory
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)


LOAN_POLICY_URL = "/api/v1/config/loan-policy/"
LOAN_POLICY_READ_PERMISSION = "config.loan_policy.read"
LOAN_POLICY_MANAGE_PERMISSION = "config.loan_policy.manage"
VERSION_HISTORY_URL = "/api/v1/version-histories/"
VERSION_HISTORY_READ_PERMISSION = "audit.version_history.read"

LOAN_POLICY_RESPONSE_FIELDS = {
    "loan_policy_config_id",
    "policy_name",
    "policy_version",
    "effective_from",
    "effective_to",
    "short_term_duration_months",
    "min_secured_loan_months",
    "max_secured_loan_years",
    "approval_threshold_amount",
    "default_scale_of_finance_per_acre_amount",
    "share_limit_percentage",
    "per_share_cap_amount",
    "interest_rate_type",
    "interest_benchmark",
    "penal_interest_rate",
    "rekyc_frequency_months",
    "record_retention_years",
    "grace_period_months",
    "non_intentional_extension_months",
    "board_approval_reference",
    "status",
}

VERSION_HISTORY_RESPONSE_FIELDS = {
    "version_history_id",
    "versioned_entity_type",
    "versioned_entity_id",
    "version_number",
    "change_summary",
    "author",
    "reviewer",
    "approver",
    "board_approval_reference",
    "effective_from",
    "effective_to",
    "created_at",
}


class LoanPolicyConfigApiTests(TestCase):
    """003E: protected loan-policy configuration API shell."""

    def setUp(self):
        self.client = Client()
        self.config_reader_role = Role.objects.create(
            role_code="config_reader",
            role_name="Configuration Reader",
            is_system_role=True,
            status="active",
        )
        read_permission = Permission.objects.create(
            permission_code=LOAN_POLICY_READ_PERMISSION,
            permission_name="View loan policy config",
            module_name="config",
            risk_level="medium",
        )
        RolePermission.objects.create(
            role=self.config_reader_role, permission=read_permission
        )
        version_history_read_permission = Permission.objects.create(
            permission_code=VERSION_HISTORY_READ_PERMISSION,
            permission_name="View version history",
            module_name="audit",
            risk_level="medium",
        )
        RolePermission.objects.create(
            role=self.config_reader_role, permission=version_history_read_permission
        )
        self.config_reader = User.objects.create(
            full_name="Rita Reader",
            email="rita.reader@sfpcl.example",
            status="active",
            primary_role=self.config_reader_role,
        )
        self.config_reader.set_password("ReaderPass123!")
        self.config_reader.save()

        self.config_manager_role = Role.objects.create(
            role_code="config_manager",
            role_name="Configuration Manager",
            is_system_role=True,
            status="active",
        )
        manage_permission = Permission.objects.create(
            permission_code=LOAN_POLICY_MANAGE_PERMISSION,
            permission_name="Manage loan policy config",
            module_name="config",
            risk_level="critical",
        )
        RolePermission.objects.create(
            role=self.config_manager_role, permission=manage_permission
        )
        RolePermission.objects.create(
            role=self.config_manager_role, permission=read_permission
        )
        RolePermission.objects.create(
            role=self.config_manager_role, permission=version_history_read_permission
        )
        self.config_manager = User.objects.create(
            full_name="Mira Manager",
            email="mira.manager@sfpcl.example",
            status="active",
            primary_role=self.config_manager_role,
        )
        self.config_manager.set_password("ManagerPass123!")
        self.config_manager.save()

        self.plain_role = Role.objects.create(
            role_code="plain_staff",
            role_name="Plain Staff",
            is_system_role=True,
            status="active",
        )
        self.plain_user = User.objects.create(
            full_name="Paul Plain",
            email="paul.plain@sfpcl.example",
            status="active",
            primary_role=self.plain_role,
        )
        self.plain_user.set_password("PlainPass123!")
        self.plain_user.save()

    def _access_token(self, email="rita.reader@sfpcl.example", password="ReaderPass123!"):
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
            email="mira.manager@sfpcl.example", password="ManagerPass123!"
        )

    def _plain_headers(self):
        return self._auth_headers(
            email="paul.plain@sfpcl.example", password="PlainPass123!"
        )

    def _sample_payload(self, **overrides):
        payload = {
            "policy_name": "SFPCL Loan Policy",
            "policy_version": "1.0",
            "effective_from": "2026-04-01",
            "short_term_duration_months": 12,
            "min_secured_loan_months": 3,
            "max_secured_loan_years": 7,
            "approval_threshold_amount": "500000.00",
            "default_scale_of_finance_per_acre_amount": "20000.00",
            "share_limit_percentage": "10.0000",
            "per_share_cap_amount": "200.00",
            "interest_rate_type": "floating",
            "interest_benchmark": None,
            "penal_interest_rate": None,
            "rekyc_frequency_months": 24,
            "record_retention_years": 8,
            "grace_period_months": 3,
            "non_intentional_extension_months": 12,
            "board_approval_reference": "BOARD-REF-001",
        }
        payload.update(overrides)
        return payload

    def _loan_policy_config(self, **overrides):
        defaults = {
            "policy_name": "SFPCL Loan Policy",
            "policy_version": "1.0",
            "effective_from": "2026-04-01",
            "short_term_duration_months": 12,
            "min_secured_loan_months": 3,
            "max_secured_loan_years": 7,
            "approval_threshold_amount": "500000.00",
            "default_scale_of_finance_per_acre_amount": "20000.00",
            "share_limit_percentage": "10.0000",
            "per_share_cap_amount": "200.00",
            "interest_rate_type": "floating",
            "interest_benchmark": None,
            "penal_interest_rate": None,
            "rekyc_frequency_months": 24,
            "record_retention_years": 8,
            "grace_period_months": 3,
            "non_intentional_extension_months": 12,
            "board_approval_reference": "BOARD-REF-001",
            "status": "draft",
        }
        defaults.update(overrides)
        return LoanPolicyConfig.objects.create(**defaults)

    def test_authorized_list_returns_standard_pagination_and_policy_fields(self):
        response = self.client.get(
            LOAN_POLICY_URL,
            headers={**self._auth_headers(), "X-Request-ID": "req-loan-policy-list"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-loan-policy-list")
        self.assertEqual(payload["data"], [])

    def test_create_draft_policy_persists_source_fields_and_writes_audit(self):
        response = self.client.post(
            LOAN_POLICY_URL,
            data=self._sample_payload(),
            content_type="application/json",
            headers={**self._manager_headers(), "X-Request-ID": "req-policy-create"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-policy-create")
        self.assertEqual(set(payload["data"].keys()), LOAN_POLICY_RESPONSE_FIELDS)
        self.assertEqual(payload["data"]["status"], "draft")
        self.assertEqual(payload["data"]["approval_threshold_amount"], "500000.00")
        self.assertEqual(payload["data"]["share_limit_percentage"], "10.0000")

        config = LoanPolicyConfig.objects.get(
            loan_policy_config_id=payload["data"]["loan_policy_config_id"]
        )
        self.assertEqual(config.policy_name, "SFPCL Loan Policy")
        self.assertEqual(config.board_approval_reference, "BOARD-REF-001")

        audit = AuditLog.objects.get(action="config.loan_policy.created")
        self.assertEqual(audit.actor_user, self.config_manager)
        self.assertEqual(audit.entity_type, "loan_policy_config")
        self.assertEqual(audit.entity_id, config.loan_policy_config_id)
        self.assertEqual(
            audit.new_value_json["loan_policy_config_id"],
            str(config.loan_policy_config_id),
        )
        self.assertEqual(audit.new_value_json["policy_version"], "1.0")

    def test_patch_draft_policy_updates_fields_and_writes_audit(self):
        config = self._loan_policy_config()

        response = self.client.patch(
            f"{LOAN_POLICY_URL}{config.loan_policy_config_id}/",
            data={"policy_name": "Updated Policy", "effective_to": "2027-03-31"},
            content_type="application/json",
            headers=self._manager_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["data"]["policy_name"], "Updated Policy")
        self.assertEqual(payload["data"]["effective_to"], "2027-03-31")
        audit = AuditLog.objects.get(action="config.loan_policy.updated")
        self.assertEqual(audit.old_value_json["policy_name"], "SFPCL Loan Policy")
        self.assertEqual(audit.new_value_json["policy_name"], "Updated Policy")

    def test_patch_rejects_invalid_dates_decimals_status_and_non_draft_state(self):
        draft = self._loan_policy_config()
        response = self.client.patch(
            f"{LOAN_POLICY_URL}{draft.loan_policy_config_id}/",
            data={
                "effective_to": "2026-03-31",
                "approval_threshold_amount": "-1.00",
                "status": "published",
            },
            content_type="application/json",
            headers=self._manager_headers(),
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("effective_to", payload["error"]["field_errors"])
        self.assertIn("approval_threshold_amount", payload["error"]["field_errors"])
        self.assertIn("status", payload["error"]["field_errors"])

        active = self._loan_policy_config(policy_version="2.0", status="active")
        response = self.client.patch(
            f"{LOAN_POLICY_URL}{active.loan_policy_config_id}/",
            data={"policy_name": "Cannot Change"},
            content_type="application/json",
            headers=self._manager_headers(),
        )
        self.assertEqual(response.status_code, 409)
        assert_error_envelope(self, response.json(), "INVALID_STATE_TRANSITION")
        self.assertEqual(
            AuditLog.objects.filter(action="config.loan_policy.updated").count(), 0
        )

    def test_activate_requires_evidence_permission_and_writes_version_history_and_audit(self):
        previous_active = self._loan_policy_config(
            policy_version="0.9",
            effective_from="2025-04-01",
            status="active",
            board_approval_reference="BOARD-OLD",
        )
        draft = self._loan_policy_config(policy_version="1.0")

        forbidden = self.client.post(
            f"{LOAN_POLICY_URL}{draft.loan_policy_config_id}/activate/",
            headers=self._plain_headers(),
        )
        self.assertEqual(forbidden.status_code, 403)
        assert_error_envelope(self, forbidden.json(), "PERMISSION_DENIED")

        response = self.client.post(
            f"{LOAN_POLICY_URL}{draft.loan_policy_config_id}/activate/",
            headers=self._manager_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["data"]["status"], "active")

        draft.refresh_from_db()
        previous_active.refresh_from_db()
        self.assertEqual(draft.status, "active")
        self.assertEqual(previous_active.status, "retired")
        self.assertEqual(previous_active.effective_to.isoformat(), "2026-03-31")

        version = VersionHistory.objects.get(
            versioned_entity_type="loan_policy_config",
            versioned_entity_id=draft.loan_policy_config_id,
        )
        self.assertEqual(version.version_number, "1.0")
        self.assertEqual(version.author_user, self.config_manager)
        self.assertEqual(version.approver_user, self.config_manager)
        self.assertEqual(version.board_approval_reference, "BOARD-REF-001")

        audit = AuditLog.objects.get(action="config.loan_policy.activated")
        self.assertEqual(audit.actor_user, self.config_manager)
        self.assertEqual(audit.entity_id, draft.loan_policy_config_id)

    def test_activate_without_board_approval_reference_returns_validation_error(self):
        draft = self._loan_policy_config(board_approval_reference=None)

        response = self.client.post(
            f"{LOAN_POLICY_URL}{draft.loan_policy_config_id}/activate/",
            headers=self._manager_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("board_approval_reference", payload["error"]["field_errors"])
        self.assertEqual(VersionHistory.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="config.loan_policy.activated").count(), 0
        )

    def test_version_history_list_filters_and_requires_permission(self):
        config = self._loan_policy_config(status="active")
        other_entity_id = uuid.uuid4()
        row = VersionHistory.objects.create(
            versioned_entity_type="loan_policy_config",
            versioned_entity_id=config.loan_policy_config_id,
            version_number="1.0",
            change_summary="Activated loan policy version 1.0.",
            author_user=self.config_manager,
            approver_user=self.config_manager,
            board_approval_reference="BOARD-REF-001",
            effective_from="2026-04-01",
        )
        VersionHistory.objects.create(
            versioned_entity_type="content_template",
            versioned_entity_id=other_entity_id,
            version_number="1.0",
            change_summary="Other history.",
            effective_from="2026-04-01",
        )

        forbidden = self.client.get(
            VERSION_HISTORY_URL,
            headers=self._plain_headers(),
        )
        self.assertEqual(forbidden.status_code, 403)
        assert_error_envelope(self, forbidden.json(), "PERMISSION_DENIED")

        response = self.client.get(
            VERSION_HISTORY_URL
            + "?versioned_entity_type=loan_policy_config"
            + f"&versioned_entity_id={config.loan_policy_config_id}",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(len(payload["data"]), 1)
        item = payload["data"][0]
        self.assertEqual(set(item.keys()), VERSION_HISTORY_RESPONSE_FIELDS)
        self.assertEqual(item["version_history_id"], str(row.version_history_id))
        self.assertEqual(item["versioned_entity_type"], "loan_policy_config")
        self.assertEqual(
            item["versioned_entity_id"], str(config.loan_policy_config_id)
        )
        self.assertEqual(
            item["approver"],
            {"user_id": str(self.config_manager.user_id), "full_name": "Mira Manager"},
        )

    def test_version_history_invalid_uuid_returns_validation_error(self):
        response = self.client.get(
            VERSION_HISTORY_URL
            + "?versioned_entity_type=loan_policy_config&versioned_entity_id=bad-uuid",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("versioned_entity_id", payload["error"]["field_errors"])

    def test_unauthenticated_and_no_permission_requests_do_not_write_audit(self):
        response = self.client.get(LOAN_POLICY_URL)
        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "AUTH_REQUIRED")

        forbidden = self.client.post(
            LOAN_POLICY_URL,
            data=self._sample_payload(),
            content_type="application/json",
            headers=self._plain_headers(),
        )
        self.assertEqual(forbidden.status_code, 403)
        assert_error_envelope(self, forbidden.json(), "PERMISSION_DENIED")
        self.assertEqual(LoanPolicyConfig.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action__startswith="config.loan_policy.").count(), 0
        )
