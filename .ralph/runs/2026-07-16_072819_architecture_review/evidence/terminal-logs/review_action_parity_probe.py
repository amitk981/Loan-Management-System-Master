from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.tests.test_final_documentation_approval_api import (
    FinalDocumentationApprovalApiTests,
)


class ReviewActionParityProbe(FinalDocumentationApprovalApiTests):
    def test_advertised_completion_is_not_executable(self):
        self._grant(self.compliance, "documents.checklist.read")
        document = self._current_document("loan_agreement")
        document.verification_status = LoanDocument.VERIFICATION_PENDING
        document.verified_by_user = None
        document.verified_at = None
        document.save(
            update_fields=["verification_status", "verified_by_user", "verified_at"]
        )

        workspace = self._workspace(self.compliance)
        self.assertEqual(workspace.status_code, 200, workspace.content)
        item = next(
            row
            for row in workspace.json()["data"]["items"]
            if row["item_code"] == "loan_agreement"
        )
        action = next(
            row for row in item["available_actions"] if row["action_code"] == "complete_item"
        )
        response = self.client.post(
            action["action_url"],
            {**action["fixed_payload"], "remarks": "Review action parity probe."},
            content_type="application/json",
            HTTP_X_REQUEST_ID="architecture-review-action-parity",
            **self.fixture._auth(self.compliance),
        )

        print(
            {
                "advertised_action": action["action_code"],
                "advertised_enabled": action["enabled"],
                "execution_status": response.status_code,
                "execution_error": response.json().get("error", {}).get("code"),
            }
        )
        self.assertNotEqual(
            response.status_code,
            200,
            "The probe requires an advertised action that its owner rejects in the same state.",
        )
