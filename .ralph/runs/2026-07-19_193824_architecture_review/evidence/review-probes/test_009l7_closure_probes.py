"""Review-only public probe for the final Epic 009 read-boundary closure."""

from django.test import Client, TestCase

from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_post_transfer_evidence,
)
from sfpcl_credit.tests import test_loan_account_reads_api as account_tests


class Epic009L7ClosureReviewProbes(TestCase):
    def test_transfer_file_drift_is_excluded_from_public_list_and_detail(self):
        fixture = account_tests.ActiveLoanAccountReadApiTests(
            "test_exact_transfer_projects_active_funded_amounts_and_activation_time"
        )
        fixture.setUp()
        evidence = fixture.fixture.evidence
        evidence.checksum_sha256 = "0" * 64
        evidence.save(update_fields=["checksum_sha256"])

        self.assertIsNone(
            resolve_post_transfer_evidence(
                application_id=fixture.account.loan_application_id
            )
        )

        listing = Client().get("/api/v1/loan-accounts/", **fixture.auth)
        detail = Client().get(
            f"/api/v1/loan-accounts/{fixture.account.pk}/", **fixture.auth
        )

        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(
            (
                listing.json()["pagination"]["total_count"],
                listing.json()["data"],
                detail.status_code,
            ),
            (0, [], 404),
            detail.content,
        )
