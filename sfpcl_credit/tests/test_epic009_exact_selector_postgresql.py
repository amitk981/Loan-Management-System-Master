"""Authoritative PostgreSQL proof for Epic 009 exact owner selectors."""

import json
from unittest import skipUnless

from django.db import connection
from django.test import Client, TestCase

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.tests import test_disbursement_workspace_api as workspace_tests
from sfpcl_credit.tests import test_loan_account_reads_api as account_tests


@skipUnless(
    connection.vendor == "postgresql",
    "Exact SHA-256 selector acceptance requires PostgreSQL.",
)
class Epic009ExactSelectorPostgreSQLAcceptanceTests(TestCase):
    def test_loan_account_selector_excludes_non_array_creation_team_evidence(self):
        fixture = account_tests.LoanAccountReadApiTests(
            "test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections"
        )
        fixture.setUp()
        audit = AuditLog.objects.get(
            action="finance.loan_account.created", entity_id=fixture.account.pk
        )
        changed = {
            **audit.new_value_json,
            "actor_team_codes": "not-an-immutable-team-list",
        }
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

    def test_s37_selector_excludes_send_body_key_drift(self):
        fixture = workspace_tests.SapStaffWorkspaceApiTests(
            "test_exact_assignee_gets_optional_s37_completion_action"
        )
        fixture.setUp()
        request_id = fixture.fixture._create_and_send("postgresql-s37-body-drift")
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

    def test_combined_senior_finance_selector_projects_its_exact_count(self):
        fixture = workspace_tests.DisbursementWorkspaceApiTests(
            "test_admitted_senior_finance_reader_does_not_hit_internal_permission"
        )
        fixture.setUp()

        response = Client().get(
            "/api/v1/disbursement-workspaces/",
            **fixture.fixture.fixture._auth(fixture.fixture.fixture.actor),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["pagination"]["total_count"],
            len(response.json()["data"]),
        )
        self.assertEqual(len(response.json()["data"]), 1)

    def test_cfc_selector_executes_sha256_and_excludes_comment_drift(self):
        fixture = workspace_tests.DisbursementWorkspaceApiTests(
            "test_cfc_queue_is_masked_paginated_and_projects_server_owned_actions"
        )
        fixture.setUp()
        Disbursement.objects.filter(pk=fixture.row.pk).update(
            final_verification_comments="Changed after immutable initiation evidence."
        )

        response = Client().get(
            "/api/v1/disbursement-workspaces/",
            **fixture.fixture.fixture._auth(fixture.fixture.cfc),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])
