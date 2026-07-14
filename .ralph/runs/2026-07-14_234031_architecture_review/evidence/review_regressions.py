"""Independent review-only regressions; not added to the production test tree."""

from unittest.mock import patch

from sfpcl_credit.legal_documents.modules import stamp_notary
from sfpcl_credit.tests.test_cdsl_share_pledge_api import CDSLSharePledgeApiTests
from sfpcl_credit.tests.test_power_of_attorney_api import PowerOfAttorneyApiTests


class ArchitectureReviewCDSLRegression(CDSLSharePledgeApiTests):
    def test_pending_preparation_accepts_nullable_evidence_document(self):
        package = self._refresh_package()
        payload = self._payload(None)
        payload["evidence_document_id"] = None
        response = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/cdsl-share-pledge/",
            payload,
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIsNone(response.json()["data"]["evidence_document_id"])


class ArchitectureReviewPoARegression(PowerOfAttorneyApiTests):
    def test_one_rupee_stamp_cannot_activate_poa(self):
        original_record_stamp = stamp_notary.record_stamp

        def replace_adequate_amount(*args, **kwargs):
            payload = dict(kwargs["payload"])
            if payload.get("status") == "adequate":
                payload["stamp_paper_amount"] = "1.00"
            return original_record_stamp(*args, **{**kwargs, "payload": payload})

        original_patch = self.client.patch

        def reject_successful_activation(path, data=None, **kwargs):
            response = original_patch(path, data, **kwargs)
            if isinstance(data, dict) and data.get("status") == "active":
                self.assertNotEqual(
                    response.status_code,
                    200,
                    "PoA activation accepted an adequate ₹1 stamp instead of requiring ₹500.",
                )
            return response

        self.client.patch = reject_successful_activation
        with patch.object(stamp_notary, "record_stamp", side_effect=replace_adequate_amount):
            self.test_company_secretary_activates_only_with_current_maker_checker_and_signatures()
