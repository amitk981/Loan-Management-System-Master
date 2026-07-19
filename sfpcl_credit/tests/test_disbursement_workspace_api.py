from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    resolve_current_disbursement_evidence,
)
from sfpcl_credit.identity.models import AuditLog, RolePermission
from sfpcl_credit.tests.api_contracts import assert_pagination_shape


class DisbursementWorkspaceApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_disbursement_authorisation_api import (
            DisbursementAuthorisationApiTests,
        )

        fixture = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        fixture.setUp()
        self.fixture = fixture
        self.row = Disbursement.objects.select_related(
            "loan_account", "loan_application", "member",
            "borrower_bank_account", "source_bank_account", "initiated_by_user",
        ).get()
        self.client = Client()

    def test_cfc_queue_is_masked_paginated_and_projects_server_owned_actions(self):
        response = self.client.get(
            "/api/v1/disbursement-workspaces/?page=1&page_size=20",
            **self.fixture.fixture._auth(self.fixture.cfc),
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_pagination_shape(self, response.json())
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        item = response.json()["data"][0]
        self.assertEqual(item["workspace_id"], str(self.row.pk))
        self.assertEqual(item["disbursement_id"], str(self.row.pk))
        self.assertEqual(item["member"]["display_name"], self.row.member.display_name)
        self.assertEqual(item["disbursement_amount"], f"{self.row.disbursement_amount:.2f}")
        self.assertEqual(item["beneficiary_bank"]["account_number_masked"], f"******{self.row.borrower_bank_account.account_number_last4}")
        self.assertNotIn("bank_account_id", item["beneficiary_bank"])
        self.assertNotIn("bank_account_id", item["source_bank"])
        self.assertEqual(
            [action["action_code"] for action in item["available_actions"]],
            ["authorise_disbursement", "reject_disbursement"],
        )
        serialized = str(item)
        self.assertNotIn(self.row.borrower_bank_account.account_number_encrypted, serialized)
        self.assertNotIn(self.row.source_bank_account.account_number_encrypted, serialized)
        self.assertNotIn(self.row.idempotency_key_digest, serialized)

    def test_permission_or_role_alone_cannot_read_the_queue(self):
        wrong_role = self.fixture.fixture.fixture._user(
            "field_officer", "Permission Only Workspace Reader"
        )
        self.fixture.fixture.fixture._grant(
            wrong_role, "finance.disbursement.authorise"
        )
        denied = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(wrong_role),
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")

    def test_primary_cfc_role_without_governed_authority_discloses_no_row_or_action(self):
        self.fixture.cfc.approval_authority_type = ""
        self.fixture.cfc.save(update_fields=["approval_authority_type"])

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.cfc),
        )

        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(response.json()["error"]["code"], "FORBIDDEN")

    def test_query_validation_is_strict(self):
        for query in ("page=0", "page_size=101", "status=pending"):
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/v1/disbursement-workspaces/?{query}",
                    **self.fixture.fixture._auth(self.fixture.cfc),
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")

    def test_admitted_senior_finance_reader_does_not_hit_internal_permission(self):
        self.client.raise_request_exception = False

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.fixture.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)

    def test_incoherent_approved_disbursement_is_not_projected(self):
        approved = self.fixture._post(
            "approved", "Independent transfer authorisation retained."
        )
        self.assertEqual(approved.status_code, 200, approved.content)
        self.fixture.fixture.fixture._grant(
            self.fixture.fixture.actor, "finance.loan_account.read"
        )
        Disbursement.objects.filter(pk=self.row.pk).update(
            final_verification_comments=(
                "Changed after the immutable initiation ledger."
            )
        )
        self.row.refresh_from_db()
        self.assertIsNone(
            resolve_current_disbursement_evidence(
                disbursement_id=self.row.pk,
                allowed_authorisation_statuses=("approved",),
            )
        )

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.fixture.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_stale_initiation_affects_neither_total_nor_page(self):
        Disbursement.objects.filter(pk=self.row.pk).update(
            final_verification_comments=(
                "Changed after immutable initiation evidence."
            )
        )

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.cfc),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])


class SapStaffWorkspaceApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_sap_customer_profile_request_api import (
            SapCustomerProfileRequestApiTests,
        )

        self.fixture = SapCustomerProfileRequestApiTests(
            "test_credit_manager_creates_draft_request_after_terminal_sanction"
        )
        self.fixture.setUp()
        self.client = Client()

    def tearDown(self):
        self.fixture.tearDown()

    def test_credit_manager_gets_safe_s36_create_then_send_actions(self):
        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(self.fixture.credit_manager),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        row = response.json()["data"][0]
        self.assertEqual(row["loan_application_id"], str(self.fixture.application.pk))
        self.assertEqual(
            row["application_reference_number"],
            self.fixture.application.application_reference_number,
        )
        self.assertEqual(
            row["available_actions"][0]["action_code"], "create_sap_request"
        )
        action = row["available_actions"][0]
        self.assertEqual(
            action["action_url"],
            f"/api/v1/loan-applications/{self.fixture.application.pk}/sap-customer-profile-request/",
        )
        self.assertEqual(action["fields"][0]["type"], "select")
        self.assertEqual(
            action["fields"][0]["options"],
            [
                {
                    "value": str(self.fixture.assignee.pk),
                    "label": self.fixture.assignee.full_name,
                }
            ],
        )
        serialized = str(row)
        self.assertNotIn("aadhaar", serialized.lower())
        self.assertNotIn("pan_number", serialized.lower())
        self.assertNotIn("excel_file", serialized.lower())

        created = self.fixture._post_request("workspace-s36-create")
        self.assertEqual(created.status_code, 200, created.content)
        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(self.fixture.credit_manager),
        )
        action = response.json()["data"][0]["available_actions"][0]
        self.assertEqual(action["action_code"], "send_sap_request")
        self.assertEqual(action["required_permission"], "finance.sap_request.send")
        self.assertEqual(action["fields"][0]["name"], "remarks")

    def test_every_credit_manager_accepted_by_create_owner_reaches_s36_candidate(self):
        other_credit_manager = self.fixture._user(
            "credit_manager",
            "Current Credit Manager Outside Intake Ownership",
            "finance.sap_request.create",
            "finance.sap_request.send",
        )

        workspace = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(other_credit_manager),
        )
        mutation = self.client.post(
            (
                f"/api/v1/loan-applications/{self.fixture.application.pk}/"
                "sap-customer-profile-request/"
            ),
            {"assigned_to_user_id": str(self.fixture.assignee.pk)},
            content_type="application/json",
            **self.fixture._auth(other_credit_manager),
        )

        self.assertEqual(mutation.status_code, 200, mutation.content)
        self.assertEqual(workspace.status_code, 200, workspace.content)
        self.assertEqual(workspace.json()["pagination"]["total_count"], 1)

    def test_populated_s36_collection_has_a_query_ceiling(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v1/disbursement-workspaces/?page=1&page_size=20",
                **self.fixture._auth(self.fixture.credit_manager),
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertLessEqual(len(queries), 30)

    def test_exact_assignee_gets_optional_s37_completion_action(self):
        request_id = self.fixture._create_and_send("workspace-s37")

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(self.fixture.assignee),
        )

        self.assertEqual(response.status_code, 200, response.content)
        row = response.json()["data"][0]
        action = row["available_actions"][0]
        self.assertEqual(action["action_code"], "complete_sap_request")
        self.assertEqual(
            action["required_permission"], "finance.sap_request.complete"
        )
        required = {field["name"]: field["required"] for field in action["fields"]}
        self.assertEqual(
            required,
            {
                "sap_customer_code": True,
                "sap_vendor_code": False,
                "created_at_sap": False,
                "confirmation_document_id": False,
                "confirmation_notes": False,
            },
        )
        self.assertEqual(row["sap"]["request_id"], request_id)

        RolePermission.objects.filter(
            role=self.fixture.assignee.primary_role,
            permission__permission_code="finance.sap_request.complete",
        ).delete()
        denied = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(self.fixture.assignee),
        )
        self.assertEqual(denied.status_code, 403, denied.content)

    def test_send_digest_drift_affects_neither_total_nor_page(self):
        request_id = self.fixture._create_and_send("s37-selector-drift")
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
            action="finance.sap_customer_code.sent",
        )
        audit.new_value_json = {
            **audit.new_value_json,
            "annexure_checksum_sha256": "0" * 64,
        }
        audit.save(update_fields=["new_value_json"])

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(self.fixture.assignee),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])
