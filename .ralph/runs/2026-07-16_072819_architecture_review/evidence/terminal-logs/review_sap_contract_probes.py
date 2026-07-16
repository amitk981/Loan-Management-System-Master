from datetime import timedelta

from django.utils import timezone

from sfpcl_credit.finance.models import SapCustomerCode, SapCustomerProfileRequest
from sfpcl_credit.tests.test_sap_customer_profile_request_api import (
    SapCustomerProfileRequestApiTests,
)


class ReviewSapContractProbes(SapCustomerProfileRequestApiTests):
    def test_sent_request_does_not_deliver_the_retained_workbook(self):
        request_id = self._create_and_send("architecture-review-delivery")
        row = SapCustomerProfileRequest.objects.select_related(
            "sent_communication", "sent_task"
        ).get(pk=request_id)
        download = self.client.get(
            f"/api/v1/document-files/{row.excel_file_id}/download/",
            **self._auth(self.assignee),
        )

        result = {
            "request_status": row.request_status,
            "communication_delivery_status": row.sent_communication.delivery_status,
            "communication_has_attachment_field": hasattr(
                row.sent_communication, "attachment"
            ),
            "task_action_url": row.sent_task.action_url,
            "assignee_workbook_download_status": download.status_code,
        }
        print(result)
        self.assertEqual(row.request_status, "sent")
        self.assertEqual(download.status_code, 403)
        self.assertFalse(result["communication_has_attachment_field"])
        self.assertTrue(row.sent_task.action_url.endswith("/complete/"))

    def test_reuse_changed_optional_payload_is_accepted_as_replay(self):
        retained = SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="REVIEW-RETAINED-CODE",
            sap_vendor_code="REVIEW-RETAINED-VENDOR",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
            created_at_sap=timezone.now() - timedelta(days=2),
            confirmation_notes="Original retained evidence",
        )
        request_id = self._create_and_send("architecture-review-replay")
        first = self._complete(
            request_id,
            sap_customer_code=retained.sap_customer_code,
        )
        changed = self._complete(
            request_id,
            sap_customer_code=retained.sap_customer_code,
            sap_vendor_code=retained.sap_vendor_code,
            created_at_sap=retained.created_at_sap.isoformat(),
            confirmation_notes=retained.confirmation_notes,
        )

        print(
            {
                "first_status": first.status_code,
                "changed_payload_status": changed.status_code,
                "same_response": first.json()["data"] == changed.json()["data"],
            }
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(first.json()["data"], changed.json()["data"])
