from django.test import Client, TestCase

from sfpcl_credit.disbursements.models import Disbursement
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

    def test_query_validation_is_strict(self):
        for query in ("page=0", "page_size=101", "status=pending"):
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/v1/disbursement-workspaces/?{query}",
                    **self.fixture.fixture._auth(self.fixture.cfc),
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
