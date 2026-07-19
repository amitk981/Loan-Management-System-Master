"""Public regressions for Epic 009 owner-selector equivalence."""

import json

from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.tests import test_disbursement_workspace_api as workspace_tests
from sfpcl_credit.tests import test_loan_account_reads_api as account_tests


class Epic009OwnerSelectorEquivalenceTests(TestCase):
    def test_creation_synced_json_copies_with_stale_digest_are_excluded(self):
        fixture = account_tests.LoanAccountReadApiTests(
            "test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections"
        )
        fixture.setUp()
        audit = AuditLog.objects.get(
            action="finance.loan_account.created", entity_id=fixture.account.pk
        )
        changed = {**audit.new_value_json, "request_id": "synced-body-drift"}
        audit.new_value_json = changed
        audit.old_value_json = {
            **audit.old_value_json,
            "selector_manifest": changed,
        }
        audit.selector_manifest_json = json.dumps(
            changed, sort_keys=True, separators=(",", ":")
        )
        audit.save(
            update_fields=[
                "new_value_json",
                "old_value_json",
                "selector_manifest_json",
            ]
        )

        response = Client().get("/api/v1/loan-accounts/", **fixture.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_s37_synced_json_copies_with_stale_digest_are_excluded(self):
        fixture = workspace_tests.SapStaffWorkspaceApiTests(
            "test_exact_assignee_gets_optional_s37_completion_action"
        )
        fixture.setUp()
        request_id = fixture.fixture._create_and_send("synced-s37-digest-drift")
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
            action="finance.sap_customer_code.sent",
        )
        changed = {**audit.new_value_json, "reason": "synced body drift"}
        audit.new_value_json = changed
        audit.old_value_json = {
            **audit.old_value_json,
            "selector_manifest": changed,
        }
        audit.selector_manifest_json = json.dumps(
            changed, sort_keys=True, separators=(",", ":")
        )
        audit.save(
            update_fields=[
                "new_value_json",
                "old_value_json",
                "selector_manifest_json",
            ]
        )

        response = Client().get(
            "/api/v1/disbursement-workspaces/",
            **fixture.fixture._auth(fixture.fixture.assignee),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_cfc_synced_json_copies_with_stale_digest_are_excluded(self):
        fixture = workspace_tests.DisbursementWorkspaceApiTests(
            "test_cfc_queue_is_masked_paginated_and_projects_server_owned_actions"
        )
        fixture.setUp()
        audit = fixture.row.initiation_audit
        changed = {**audit.new_value_json, "outcome": "synced-body-drift"}
        audit.new_value_json = changed
        audit.old_value_json = {
            **audit.old_value_json,
            "selector_manifest": changed,
        }
        audit.selector_manifest_json = json.dumps(
            changed, sort_keys=True, separators=(",", ":")
        )
        audit.save(
            update_fields=[
                "new_value_json",
                "old_value_json",
                "selector_manifest_json",
            ]
        )

        response = Client().get(
            "/api/v1/disbursement-workspaces/",
            **fixture.fixture.fixture._auth(fixture.fixture.cfc),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_creation_team_shape_drift_affects_neither_total_nor_page(self):
        fixture = account_tests.LoanAccountReadApiTests(
            "test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections"
        )
        fixture.setUp()
        audit = AuditLog.objects.get(
            action="finance.loan_account.created",
            entity_id=fixture.account.pk,
        )
        audit.new_value_json = {
            **audit.new_value_json,
            "actor_team_codes": "not-an-immutable-team-list",
        }
        audit.save(update_fields=["new_value_json"])

        response = Client().get("/api/v1/loan-accounts/", **fixture.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_completion_body_drift_affects_neither_total_nor_page(self):
        fixture = account_tests.ActiveLoanAccountReadApiTests(
            "test_completion_digest_drift_affects_neither_total_nor_page"
        )
        fixture.setUp()
        request = SapCustomerProfileRequest.objects.get(
            loan_application_id=fixture.account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request.pk,
            action__in=("sap.customer_code_created", "sap.customer_code_reused"),
        )
        audit.new_value_json = {**audit.new_value_json, "review_drift": True}
        audit.save(update_fields=["new_value_json"])

        response = Client().get("/api/v1/loan-accounts/", **fixture.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_send_body_drift_affects_neither_total_nor_page(self):
        fixture = workspace_tests.SapStaffWorkspaceApiTests(
            "test_exact_assignee_gets_optional_s37_completion_action"
        )
        fixture.setUp()
        request_id = fixture.fixture._create_and_send("owner-s37-body-drift")
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
            action="finance.sap_customer_code.sent",
        )
        audit.new_value_json = {**audit.new_value_json, "review_drift": True}
        audit.save(update_fields=["new_value_json"])

        response = Client().get(
            "/api/v1/disbursement-workspaces/",
            **fixture.fixture._auth(fixture.fixture.assignee),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_initiation_body_drift_affects_neither_total_nor_page(self):
        fixture = workspace_tests.DisbursementWorkspaceApiTests(
            "test_cfc_queue_is_masked_paginated_and_projects_server_owned_actions"
        )
        fixture.setUp()
        audit = fixture.row.initiation_audit
        audit.new_value_json = {
            **audit.new_value_json,
            "maker_team_codes": ["drifted-after-initiation"],
        }
        audit.save(update_fields=["new_value_json"])

        response = Client().get(
            "/api/v1/disbursement-workspaces/",
            **fixture.fixture.fixture._auth(fixture.fixture.cfc),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_each_creation_audit_component_uses_the_same_selector_manifest(self):
        fixture = account_tests.LoanAccountReadApiTests(
            "test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections"
        )
        fixture.setUp()
        audit = AuditLog.objects.get(
            action="finance.loan_account.created", entity_id=fixture.account.pk
        )
        original = audit.new_value_json
        mutations = {
            "request": {**original, "request_id": "drifted-request"},
            "actor": {**original, "actor_role_codes": ["drifted-role"]},
            "identity": {**original, "loan_terms_id": str(fixture.account.pk)},
            "shape": {**original, "unexpected": True},
        }

        for component, changed in mutations.items():
            with self.subTest(component=component):
                audit.new_value_json = changed
                audit.save(update_fields=["new_value_json"])
                response = Client().get("/api/v1/loan-accounts/", **fixture.auth)
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["pagination"]["total_count"], 0)
                self.assertEqual(response.json()["data"], [])
                audit.new_value_json = original
                audit.save(update_fields=["new_value_json"])

    def test_s37_related_delivery_components_are_excluded_before_count(self):
        fixture = workspace_tests.SapStaffWorkspaceApiTests(
            "test_exact_assignee_gets_optional_s37_completion_action"
        )
        fixture.setUp()
        request_id = fixture.fixture._create_and_send("owner-s37-related-matrix")
        request = SapCustomerProfileRequest.objects.select_related(
            "sent_communication", "sent_task", "excel_file"
        ).get(pk=request_id)
        cases = (
            (request.sent_communication, "body_snapshot", "drifted body"),
            (request.sent_task, "action_label", "Drifted action"),
            (request.excel_file, "mime_type", "text/plain"),
        )

        for row, field, changed in cases:
            with self.subTest(model=type(row).__name__, field=field):
                original = getattr(row, field)
                setattr(row, field, changed)
                row.save(update_fields=[field])
                response = Client().get(
                    "/api/v1/disbursement-workspaces/",
                    **fixture.fixture._auth(fixture.fixture.assignee),
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["pagination"]["total_count"], 0)
                self.assertEqual(response.json()["data"], [])
                setattr(row, field, original)
                row.save(update_fields=[field])

    def test_cfc_task_and_workflow_components_are_excluded_before_count(self):
        fixture = workspace_tests.DisbursementWorkspaceApiTests(
            "test_cfc_queue_is_masked_paginated_and_projects_server_owned_actions"
        )
        fixture.setUp()
        cases = (
            (fixture.row.cfc_task, "message", "drifted task message"),
            (
                fixture.row.initiation_workflow_event,
                "trigger_reason",
                "drifted workflow trace",
            ),
        )

        for row, field, changed in cases:
            with self.subTest(model=type(row).__name__, field=field):
                original = getattr(row, field)
                setattr(row, field, changed)
                row.save(update_fields=[field])
                response = Client().get(
                    "/api/v1/disbursement-workspaces/",
                    **fixture.fixture.fixture._auth(fixture.fixture.cfc),
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["pagination"]["total_count"], 0)
                self.assertEqual(response.json()["data"], [])
                setattr(row, field, original)
                row.save(update_fields=[field])
