import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4
from xml.etree import ElementTree

from django.db import IntegrityError, close_old_connections, connection, transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import (
    Client, RequestFactory, TestCase, TransactionTestCase, override_settings,
)
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision
from sfpcl_credit.communications.models import Communication, Notification
from sfpcl_credit.credit.models import (
    AppraisalReviewDecision, LoanAppraisalNote, RiskAssessment,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.services import store_document_upload
from sfpcl_credit.domain_errors import DomainPermissionDenied
from sfpcl_credit.sap_workflow.models import SapCustomerCode, SapCustomerProfileRequest
from sfpcl_credit.sap_workflow.modules.annexure_storage import EncryptedAnnexureStorage
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    SapRequestConflict,
    complete_request,
    create_request,
    send_request,
)
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.shared.encryption import FieldEncryption
from sfpcl_credit.tests.api_contracts import assert_error_envelope
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class SapCustomerProfileRequestApiTests(TestCase):
    password = "SapRequestPass123!"

    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.settings = override_settings(DOCUMENT_STORAGE_ROOT=self.storage.name)
        self.settings.enable()
        self.client = Client()
        self.credit_manager = self._user(
            "credit_manager", "SAP Request Credit Manager",
            "finance.sap_request.create", "finance.sap_request.send",
        )
        self.assignee = self._user(
            "senior_manager_finance", "SAP Senior Manager Finance",
            "finance.sap_request.complete", "finance.sap_code.read",
        )
        self.application = self._terminal_application()

    def tearDown(self):
        self.settings.disable()
        self.storage.cleanup()

    def test_credit_manager_creates_draft_request_after_terminal_sanction(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/sap-customer-profile-request/",
            {"assigned_to_user_id": str(self.assignee.pk)},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-sap-profile-001",
            HTTP_USER_AGENT="SAP request contract test",
            REMOTE_ADDR="203.0.113.90",
            **self._auth(self.credit_manager),
        )

        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        assert_success_envelope(self, payload)
        data = payload["data"]
        self.assertEqual(data["request_status"], "draft")
        self.assertEqual(
            data["assigned_to_user"],
            {"user_id": str(self.assignee.pk), "full_name": self.assignee.full_name},
        )
        self.assertTrue(data["sap_customer_profile_request_id"])
        self.assertTrue(data["excel_file_id"])
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").count(),
            1,
        )

    def test_public_send_complete_and_masked_member_read_happy_path(self):
        created = self._post_request("req-sap-profile-009b-create").json()["data"]
        request_id = created["sap_customer_profile_request_id"]

        sent = self.client.post(
            f"/api/v1/sap-customer-profile-requests/{request_id}/send/",
            {"remarks": "  Exact Annexure I sent to Finance.  "},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-sap-profile-009b-send",
            **self._auth(self.credit_manager),
        )

        self.assertEqual(sent.status_code, 200, sent.content)
        assert_success_envelope(self, sent.json())
        sent_data = sent.json()["data"]
        self.assertEqual(sent_data["sap_customer_profile_request_id"], request_id)
        self.assertEqual(sent_data["request_status"], "sent")
        self.assertEqual(
            sent_data["assigned_to_user"],
            {"user_id": str(self.assignee.pk), "full_name": self.assignee.full_name},
        )
        self.assertTrue(sent_data["sent_at"])
        self.assertTrue(sent_data["communication_id"])
        self.assertTrue(sent_data["task_id"])
        self.assertEqual(Communication.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)

        completed = self.client.post(
            f"/api/v1/sap-customer-profile-requests/{request_id}/complete/",
            {
                "sap_customer_code": "  cust000123  ",
                "sap_vendor_code": "  vend0009  ",
                "created_at_sap": timezone.now().isoformat(),
                "confirmation_document_id": None,
                "confirmation_notes": "  Confirmed in SAP.  ",
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-sap-profile-009b-complete",
            **self._auth(self.assignee),
        )

        self.assertEqual(completed.status_code, 200, completed.content)
        assert_success_envelope(self, completed.json())
        completed_data = completed.json()["data"]
        self.assertEqual(completed_data["sap_customer_profile_request_id"], request_id)
        self.assertEqual(completed_data["member_id"], str(self.application.member_id))
        self.assertEqual(completed_data["loan_application_id"], str(self.application.pk))
        self.assertEqual(completed_data["request_status"], "completed")
        self.assertFalse(completed_data["reuse"])
        self.assertEqual(completed_data["sap_customer_code_masked"], "******0123")
        self.assertEqual(completed_data["sap_vendor_code_masked"], "****0009")
        code = SapCustomerCode.objects.get(pk=completed_data["sap_customer_code_id"])
        self.assertEqual(code.sap_customer_code, "CUST000123")
        self.assertEqual(code.sap_vendor_code, "VEND0009")

        read = self.client.get(
            f"/api/v1/members/{self.application.member_id}/sap-customer-code/",
            **self._auth(self.assignee),
        )
        self.assertEqual(read.status_code, 200, read.content)
        assert_success_envelope(self, read.json())
        self.assertEqual(
            read.json()["data"],
            {
                "sap_customer_code_id": str(code.pk),
                "member_id": str(self.application.member_id),
                "sap_customer_code_masked": "******0123",
                "sap_vendor_code_masked": "****0009",
                "status": "active",
            },
        )
        self.assertNotIn(request_id, str(read.content))
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.sent").count(), 1
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action__in=("sap.customer_code_created", "sap.customer_code_reused")
            ).count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeSent").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeCompleted").count(), 1
        )

        secret_surface = str(list(
            AuditLog.objects.filter(
                action__in=(
                    "finance.sap_customer_code.sent",
                    "sap.customer_code_created",
                    "sap.customer_code_reused",
                )
            ).values_list("new_value_json", flat=True)
        )) + str(list(Communication.objects.values_list("body_snapshot", flat=True)))
        for secret in (
            "ABCDE1234F", "123412341234", "Village Road", "HDFC0001234",
        ):
            self.assertNotIn(secret, secret_surface)

    def test_send_replay_change_owner_and_terminal_state_are_zero_write(self):
        request_id = self._post_request("send-matrix-create").json()["data"][
            "sap_customer_profile_request_id"
        ]
        first = self._send(request_id, remarks="  send once  ")
        replay = self._send(request_id, remarks="send once")
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])

        changed = self._send(request_id, remarks="changed")
        self.assertEqual(changed.status_code, 409, changed.content)
        assert_error_envelope(self, changed.json(), "CONFLICT")
        other_owner = self._user(
            "credit_manager", "Other SAP Credit Manager",
            "finance.sap_request.create", "finance.sap_request.send",
        )
        denied = self._send(request_id, actor=other_owner, remarks="send once")
        self.assertEqual(denied.status_code, 403, denied.content)
        assert_error_envelope(self, denied.json(), "OBJECT_ACCESS_DENIED")
        wrong_role = self._user(
            "sap_sender_outsider", "Wrong SAP Sender", "finance.sap_request.send"
        )
        forbidden = self._send(request_id, actor=wrong_role, remarks="send once")
        self.assertEqual(forbidden.status_code, 403, forbidden.content)
        assert_error_envelope(self, forbidden.json(), "FORBIDDEN")
        missing = self._send(uuid4(), remarks="send once")
        self.assertEqual(missing.status_code, 403, missing.content)
        self.assertEqual(Communication.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.sent").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeSent").count(), 1
        )

        completed = self._complete(request_id, sap_customer_code="SEND-TERMINAL-001")
        self.assertEqual(completed.status_code, 200, completed.content)
        terminal_send = self._send(request_id, remarks="send once")
        self.assertEqual(terminal_send.status_code, 409, terminal_send.content)
        self.assertEqual(Communication.objects.count(), 1)

    def test_completion_replay_changed_facts_and_global_duplicate_are_zero_write(self):
        request_id = self._create_and_send("completion-replay")
        instant = timezone.now().replace(microsecond=0)
        first = self._complete(
            request_id,
            sap_customer_code=" replay-code-001 ",
            sap_vendor_code="vendor-001",
            created_at_sap=instant.isoformat(),
            confirmation_notes="retained facts",
        )
        replay = self._complete(
            request_id,
            sap_customer_code="REPLAY-CODE-001",
            sap_vendor_code="VENDOR-001",
            created_at_sap=instant.isoformat(),
            confirmation_notes="retained facts",
        )
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])

        changed = self._complete(request_id, sap_customer_code="REPLAY-CODE-002")
        self.assertEqual(changed.status_code, 409, changed.content)
        assert_error_envelope(self, changed.json(), "CONFLICT")
        self.assertEqual(SapCustomerCode.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(
                action__in=("sap.customer_code_created", "sap.customer_code_reused")
            ).count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeCompleted").count(), 1
        )

        other_application = self._terminal_application(suffix="DUP-OWNER")
        SapCustomerCode.objects.create(
            member=other_application.member,
            sap_customer_code="OTHER-MEMBER-CODE",
            created_for_loan_application=other_application,
            created_by_user=self.assignee,
        )
        duplicate_request = self._create_and_send("other-member-duplicate", self.application)
        duplicate = self._complete(
            duplicate_request, sap_customer_code=" other-member-code "
        )
        self.assertEqual(duplicate.status_code, 409, duplicate.content)
        duplicate_row = SapCustomerProfileRequest.objects.get(pk=duplicate_request)
        self.assertEqual(duplicate_row.request_status, "sent")
        self.assertIsNone(duplicate_row.completed_at)

    def test_existing_same_member_code_reuses_without_overwriting_history(self):
        retained = SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="RETAINED-MEMBER-CODE",
            sap_vendor_code="RETAINED-VENDOR",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
            created_at_sap=timezone.now() - timedelta(days=2),
            confirmation_notes="Original retained evidence",
        )
        request_id = self._create_and_send("reuse-existing")
        response = self._complete(
            request_id, sap_customer_code=" retained-member-code "
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()["data"]["reuse"])
        self.assertEqual(response.json()["data"]["sap_customer_code_id"], str(retained.pk))
        self.assertEqual(SapCustomerCode.objects.count(), 1)
        retained.refresh_from_db()
        self.assertEqual(retained.sap_vendor_code, "RETAINED-VENDOR")
        self.assertEqual(retained.confirmation_notes, "Original retained evidence")

        replay = self._complete(request_id, sap_customer_code="RETAINED-MEMBER-CODE")
        self.assertEqual(replay.status_code, 200, replay.content)
        changed = self._complete(
            request_id,
            sap_customer_code="RETAINED-MEMBER-CODE",
            sap_vendor_code="DIFFERENT",
        )
        self.assertEqual(changed.status_code, 409, changed.content)

    def test_database_blocks_case_and_padding_variants_of_global_code(self):
        SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="CANONICAL-CODE",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
        )
        other_application = self._terminal_application(suffix="CODE-NORMALIZATION")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SapCustomerCode.objects.create(
                    member=other_application.member,
                    sap_customer_code="  canonical-code  ",
                    created_for_loan_application=other_application,
                    created_by_user=self.assignee,
                )
        self.assertEqual(SapCustomerCode.objects.count(), 1)

    def test_inactive_member_code_history_is_not_reactivated_or_overwritten(self):
        historical = SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="INACTIVE-HISTORICAL-CODE",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
            status=SapCustomerCode.STATUS_INACTIVE,
        )
        request_id = self._create_and_send("inactive-history")
        response = self._complete(request_id, sap_customer_code="NEW-ACTIVE-CODE")
        self.assertEqual(response.status_code, 409, response.content)
        assert_error_envelope(self, response.json(), "CONFLICT")
        historical.refresh_from_db()
        self.assertEqual(historical.status, SapCustomerCode.STATUS_INACTIVE)
        self.assertEqual(SapCustomerCode.objects.count(), 1)
        self.assertEqual(
            SapCustomerProfileRequest.objects.get(pk=request_id).request_status, "sent"
        )

    def test_pending_same_member_request_loses_but_later_request_can_reuse(self):
        second_application = self._terminal_application(suffix="SAME-MEMBER-PENDING")
        second_application.member = self.application.member
        second_application.save(update_fields=["member"])
        first_id = self._create_and_send("same-member-first", self.application)
        second_id = self._create_and_send("same-member-second", second_application)

        winner = self._complete(first_id, sap_customer_code="ONE-MEMBER-ONE-CODE")
        loser = self._complete(second_id, sap_customer_code="ONE-MEMBER-ONE-CODE")
        self.assertEqual(winner.status_code, 200, winner.content)
        self.assertEqual(loser.status_code, 409, loser.content)
        self.assertEqual(SapCustomerCode.objects.count(), 1)
        self.assertEqual(
            SapCustomerProfileRequest.objects.filter(request_status="completed").count(), 1
        )
        self.assertEqual(
            SapCustomerProfileRequest.objects.filter(request_status="sent").count(), 1
        )

        later_application = self._terminal_application(suffix="SAME-MEMBER-LATER")
        later_application.member = self.application.member
        later_application.save(update_fields=["member"])
        later_id = self._create_and_send("same-member-later", later_application)
        later = self._complete(later_id, sap_customer_code="ONE-MEMBER-ONE-CODE")
        self.assertEqual(later.status_code, 200, later.content)
        self.assertTrue(later.json()["data"]["reuse"])
        self.assertEqual(SapCustomerCode.objects.count(), 1)

    def test_completion_rejects_invalid_payload_state_assignee_and_stale_cycle(self):
        draft_id = self._post_request("invalid-draft").json()["data"][
            "sap_customer_profile_request_id"
        ]
        draft = self._complete(draft_id, sap_customer_code="DRAFT-CODE")
        self.assertEqual(draft.status_code, 409, draft.content)

        self._send(draft_id)
        invalid_payloads = (
            {"sap_customer_code": "   "},
            {"sap_customer_code": "X" * 121},
            {
                "sap_customer_code": "FUTURE-CODE",
                "created_at_sap": (timezone.now() + timedelta(days=1)).isoformat(),
            },
            {"sap_customer_code": "VALID-CODE", "forged": "value"},
        )
        for payload in invalid_payloads:
            response = self._complete_raw(draft_id, payload)
            self.assertEqual(response.status_code, 400, response.content)
            assert_error_envelope(self, response.json(), "VALIDATION_ERROR")

        other_assignee = self._user(
            "senior_manager_finance", "Other Senior Finance",
            "finance.sap_request.complete", "finance.sap_code.read",
        )
        denied = self._complete(
            draft_id, actor=other_assignee, sap_customer_code="DENIED-CODE"
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        wrong_role = self._user(
            "sap_completer_outsider", "Wrong SAP Completer",
            "finance.sap_request.complete",
        )
        forbidden = self._complete(
            draft_id, actor=wrong_role, sap_customer_code="DENIED-CODE"
        )
        self.assertEqual(forbidden.status_code, 403, forbidden.content)
        assert_error_envelope(self, forbidden.json(), "FORBIDDEN")
        missing = self._complete(uuid4(), sap_customer_code="MISSING-CODE")
        self.assertEqual(missing.status_code, 403, missing.content)

        decision = SanctionDecision.objects.get(loan_application=self.application)
        review_decision = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=decision.approval_case.loan_appraisal_note,
            decision="reviewed",
            review_comments="Current approval cycle changed.",
            reviewer_user=self.credit_manager,
            from_state="submitted_to_sanction",
            to_state="reviewed",
        )
        replacement_case = ApprovalCase.objects.create(
            loan_application=self.application,
            loan_appraisal_note=decision.approval_case.loan_appraisal_note,
            appraisal_review_decision=review_decision,
            cycle_number=2,
            submitted_by_user=self.credit_manager,
            current_status=ApprovalCase.STATUS_APPROVED,
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=self.application.pk,
            closed_at=timezone.now(),
        )
        decision.approval_case = replacement_case
        decision.save(update_fields=["approval_case"])
        stale = self._complete(draft_id, sap_customer_code="STALE-CODE")
        self.assertEqual(stale.status_code, 409, stale.content)
        stale_denied = self._complete(
            draft_id, actor=other_assignee, sap_customer_code="STALE-CODE"
        )
        self.assertEqual(stale_denied.status_code, 403, stale_denied.content)
        assert_error_envelope(self, stale_denied.json(), "OBJECT_ACCESS_DENIED")
        self.application.application_status = LoanApplication.STATUS_SUBMITTED_TO_SANCTION
        self.application.save(update_fields=["application_status"])
        nonterminal_denied = self._complete(
            draft_id, actor=other_assignee, sap_customer_code="STALE-CODE"
        )
        self.assertEqual(nonterminal_denied.status_code, 403, nonterminal_denied.content)
        assert_error_envelope(self, nonterminal_denied.json(), "OBJECT_ACCESS_DENIED")
        self.assertEqual(SapCustomerCode.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action__in=("sap.customer_code_created", "sap.customer_code_reused")
            ).count(), 0
        )

    def test_restricted_confirmation_evidence_must_match_actor_and_scope(self):
        request_id = self._create_and_send("evidence")
        evidence = self._upload_confirmation(
            related_entity_type="loan_application",
            related_entity_id=self.application.pk,
        )
        completed = self._complete(
            request_id,
            sap_customer_code="EVIDENCE-CODE",
            confirmation_document_id=str(evidence.pk),
        )
        self.assertEqual(completed.status_code, 200, completed.content)
        self.assertEqual(
            completed.json()["data"]["confirmation_document"],
            {
                "document_id": str(evidence.pk),
                "file_name": "sap-confirmation.pdf",
                "mime_type": "application/pdf",
                "sensitivity_level": "restricted",
            },
        )

        other_application = self._terminal_application(suffix="BAD-EVIDENCE")
        other_id = self._create_and_send("bad-evidence", other_application)
        wrong_scope = self._upload_confirmation(
            related_entity_type="loan_application",
            related_entity_id=self.application.pk,
        )
        invalid_evidence = (
            wrong_scope,
            self._upload_confirmation(
                related_entity_type="loan_application",
                related_entity_id=other_application.pk,
                sensitivity_level=DocumentFile.SENSITIVITY_PUBLIC,
            ),
            self._upload_confirmation(
                related_entity_type="loan_application",
                related_entity_id=other_application.pk,
                document_category="template_source",
            ),
            self._upload_confirmation(
                related_entity_type="loan_application",
                related_entity_id=other_application.pk,
                actor=self.credit_manager,
            ),
        )
        for document in invalid_evidence:
            denied = self._complete(
                other_id,
                sap_customer_code="BAD-EVIDENCE-CODE",
                confirmation_document_id=str(document.pk),
            )
            self.assertEqual(denied.status_code, 400, denied.content)
            assert_error_envelope(self, denied.json(), "VALIDATION_ERROR")
            self.assertEqual(
                denied.json()["error"]["field_errors"]["confirmation_document_id"],
                "Document file was not found or is inaccessible.",
            )
        self.assertEqual(SapCustomerCode.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(
                action__in=("sap.customer_code_created", "sap.customer_code_reused")
            ).count(), 1
        )

    def test_member_read_is_masked_assignee_scoped_and_nondisclosing(self):
        request_id = self._create_and_send("read-scope")
        self._complete(request_id, sap_customer_code="MASKED-READ-001")
        other_assignee = self._user(
            "senior_manager_finance", "Unassigned Finance Reader",
            "finance.sap_request.complete", "finance.sap_code.read",
        )
        denied = self.client.get(
            f"/api/v1/members/{self.application.member_id}/sap-customer-code/",
            **self._auth(other_assignee),
        )
        missing = self.client.get(
            f"/api/v1/members/{uuid4()}/sap-customer-code/",
            **self._auth(self.assignee),
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(missing.status_code, 403, missing.content)
        self.assertEqual(denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
        self.assertEqual(missing.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
        for response in (denied, missing):
            self.assertNotIn("MASKED-READ-001", str(response.content))

    def test_service_freezes_canonical_sensitive_facts_in_restricted_annexure(self):
        request = RequestFactory().post(
            "/sap-request/",
            HTTP_X_REQUEST_ID="req-sap-service-001",
            HTTP_USER_AGENT="SAP service contract test",
            REMOTE_ADDR="203.0.113.91",
        )
        response = create_request(
            actor=self.credit_manager,
            application_id=self.application.pk,
            payload={"assigned_to_user_id": str(self.assignee.pk)},
            request=request,
        )

        row = SapCustomerProfileRequest.objects.get(pk=response["sap_customer_profile_request_id"])
        self.assertEqual(row.farmer_full_name, "Ramesh Patil")
        self.assertEqual(row.borrower_type, "individual_farmer")
        self.assertEqual(row.folio_number, "FOL-SAP-001")
        self.assertEqual(row.address_text, "Village Road, Nashik, Nashik, Maharashtra, 422001")
        self.assertEqual(str(row.sanctioned_amount), "400000.00")
        self.assertEqual(
            FieldEncryption.decrypt("finance.sap_request.pan", row.pan_number_encrypted),
            "ABCDE1234F",
        )
        self.assertEqual(
            FieldEncryption.decrypt("finance.sap_request.aadhaar", row.aadhaar_number_encrypted),
            "123412341234",
        )
        self.assertNotIn("ABCDE1234F", row.pan_number_encrypted)
        self.assertNotIn("123412341234", row.aadhaar_number_encrypted)

        document = DocumentFile.objects.get(pk=row.excel_file_id)
        self.assertEqual(document.sensitivity_level, "restricted")
        self.assertEqual(document.file_extension, ".xlsx")
        self.assertEqual(
            document.mime_type,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        physical_bytes = (Path(self.storage.name) / document.storage_key).read_bytes()
        self.assertNotIn(b"ABCDE1234F", physical_bytes)
        self.assertNotIn(b"123412341234", physical_bytes)
        self.assertFalse(zipfile.is_zipfile(BytesIO(physical_bytes)))
        workbook = EncryptedAnnexureStorage().read_verified(document)
        values = self._worksheet_values(workbook)
        self.assertEqual(values[0][:6], [
            "Loan Application Number", "Borrower Full Name", "Borrower Type",
            "Aadhaar Number", "PAN Number", "Registered Address",
        ])
        self.assertEqual(values[1][:6], [
            "LO00000025", "Ramesh Patil", "individual_farmer", "123412341234",
            "ABCDE1234F", "Village Road, Nashik, Nashik, Maharashtra, 422001",
        ])

        self.application.member.legal_name = "Changed after request"
        self.application.member.save(update_fields=["legal_name"])
        row.refresh_from_db()
        self.assertEqual(row.farmer_full_name, "Ramesh Patil")
        evidence = AuditLog.objects.get(action="finance.sap_customer_code.requested")
        serialized_evidence = str(evidence.new_value_json)
        for secret in ("ABCDE1234F", "123412341234", "Village Road"):
            self.assertNotIn(secret, serialized_evidence)
            self.assertNotIn(secret, str(response))

    def test_sequential_retry_returns_same_request_without_duplicate_artifacts(self):
        first = self._post_request("req-sap-replay-1")
        second = self._post_request("req-sap-replay-2")

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(first.json()["data"], second.json()["data"])
        self.assertEqual(SapCustomerProfileRequest.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").count(), 1
        )

    def test_request_replay_remains_zero_write_when_code_appears_later(self):
        first = self._post_request("req-sap-before-code")
        self.assertEqual(first.status_code, 200, first.content)
        SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="SAP-CUST-ACTIVATED-AFTER-REQUEST",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
        )

        replay = self._post_request("req-sap-after-code")

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(SapCustomerProfileRequest.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(), 1
        )

    def test_service_reloads_persisted_actor_before_authorizing(self):
        stale_actor = User.objects.get(pk=self.credit_manager.pk)
        User.objects.filter(pk=stale_actor.pk).update(status="inactive")

        with self.assertRaises(DomainPermissionDenied):
            create_request(
                actor=stale_actor,
                application_id=self.application.pk,
                payload={"assigned_to_user_id": str(self.assignee.pk)},
                request=RequestFactory().post("/sap-request/"),
            )

        self._assert_no_sap_artifacts()

    def test_current_verified_bank_fact_freezes_only_last_four_and_ifsc(self):
        bank_fact = SimpleNamespace(
            valid=True,
            bank_account_masked="********6789",
            ifsc="HDFC0001234",
        )
        with patch(
            "sfpcl_credit.sap_workflow.modules.sap_customer_request.resolve_blank_cheque_bank_fact",
            return_value=bank_fact,
        ):
            response = self._post_request("req-sap-verified-bank")

        self.assertEqual(response.status_code, 200, response.content)
        row = SapCustomerProfileRequest.objects.get(loan_application=self.application)
        self.assertEqual(row.bank_account_last4, "6789")
        self.assertEqual(row.ifsc, "HDFC0001234")
        self.assertFalse(hasattr(row, "bank_account_number"))
        values = self._worksheet_values(
            EncryptedAnnexureStorage().read_verified(row.excel_file)
        )
        self.assertEqual(values[1][11:], ["6789", "HDFC0001234"])

    def test_fpc_request_does_not_fabricate_aadhaar(self):
        application = self._terminal_application(
            suffix="FPC", member_type="fpc", pan="FGHIJ5678K", aadhaar=""
        )
        response = self._post_request("req-sap-fpc", application=application)

        self.assertEqual(response.status_code, 200, response.content)
        row = SapCustomerProfileRequest.objects.get(loan_application=application)
        self.assertEqual(row.aadhaar_number_encrypted, "")
        self.assertEqual(self._worksheet_values(
            EncryptedAnnexureStorage().read_verified(row.excel_file)
        )[1][3], "")

    def test_invalid_requests_leave_no_request_file_or_evidence(self):
        invalid_assignee = self._user("field_officer", "Not Finance Assignee")
        response = self._post_request(
            "req-sap-invalid-assignee", assigned_to=invalid_assignee
        )
        self.assertEqual(response.status_code, 400, response.content)
        assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
        self._assert_no_sap_artifacts()

        self.application.application_status = LoanApplication.STATUS_SUBMITTED_TO_SANCTION
        self.application.save(update_fields=["application_status"])
        response = self._post_request("req-sap-non-terminal")
        self.assertEqual(response.status_code, 409, response.content)
        assert_error_envelope(self, response.json(), "INVALID_STATE_TRANSITION")
        self._assert_no_sap_artifacts()

    def test_active_customer_code_can_start_reuse_request_and_missing_fact_rolls_back(self):
        SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="SAP-CUST-RETAINED-001",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
            status="active",
        )
        response = self._post_request("req-sap-existing-code")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["request_status"], "draft")
        self.assertEqual(SapCustomerProfileRequest.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), 1)

        SapCustomerProfileRequest.objects.all().delete()
        DocumentFile.objects.all().delete()
        SapCustomerCode.objects.all().delete()
        AuditLog.objects.filter(action="finance.sap_customer_code.requested").delete()
        WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").delete()
        self.application.member.registered_pincode = ""
        self.application.member.save(update_fields=["registered_pincode"])
        response = self._post_request("req-sap-missing-fact")
        self.assertEqual(response.status_code, 400, response.content)
        self._assert_no_sap_artifacts()

    def test_wrong_role_and_missing_application_follow_nondisclosure_contract(self):
        outsider = self._user(
            "sap_request_outsider", "SAP Request Outsider", "finance.sap_request.create"
        )
        response = self._post_request("req-sap-wrong-role", actor=outsider)
        self.assertEqual(response.status_code, 403, response.content)
        assert_error_envelope(self, response.json(), "FORBIDDEN")
        self._assert_no_sap_artifacts()

        response = self._post_request(
            "req-sap-missing-parent", application_id=uuid4()
        )
        self.assertEqual(response.status_code, 403, response.content)
        assert_error_envelope(self, response.json(), "OBJECT_ACCESS_DENIED")
        self._assert_no_sap_artifacts()

    def test_cross_object_denial_and_inactive_identities_leave_no_artifacts(self):
        scoped = self._user(
            "sap_scoped_actor", "SAP Scoped Actor", "finance.sap_request.create"
        )
        scoped.approval_authority_type = "credit_manager"
        scoped.save(update_fields=["approval_authority_type"])
        response = self._post_request("req-sap-object-denied", actor=scoped)
        self.assertEqual(response.status_code, 403, response.content)
        assert_error_envelope(self, response.json(), "OBJECT_ACCESS_DENIED")
        self._assert_no_sap_artifacts()

        self.assignee.status = "inactive"
        self.assignee.save(update_fields=["status"])
        response = self._post_request("req-sap-inactive-assignee")
        self.assertEqual(response.status_code, 400, response.content)
        self._assert_no_sap_artifacts()

        self.assignee.status = "active"
        self.assignee.save(update_fields=["status"])
        headers = self._auth(self.credit_manager)
        self.credit_manager.status = "inactive"
        self.credit_manager.save(update_fields=["status"])
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/sap-customer-profile-request/",
            {"assigned_to_user_id": str(self.assignee.pk)},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 401, response.content)
        self._assert_no_sap_artifacts()

    def test_client_cannot_substitute_canonical_fields(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/sap-customer-profile-request/",
            {
                "assigned_to_user_id": str(self.assignee.pk),
                "farmer_full_name": "Forged Borrower",
                "pan_number": "ZZZZZ9999Z",
            },
            content_type="application/json",
            **self._auth(self.credit_manager),
        )
        self.assertEqual(response.status_code, 400, response.content)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertEqual(payload["error"]["field_errors"], {
            "farmer_full_name": "Unknown field.", "pan_number": "Unknown field."
        })
        self._assert_no_sap_artifacts()

    def _terminal_application(
        self, suffix="001", member_type="individual_farmer",
        pan="ABCDE1234F", aadhaar="123412341234",
    ):
        member = Member.objects.create(
            member_number=f"MEM-SAP-{suffix}",
            member_type=member_type,
            legal_name=f"Ramesh Patil {suffix}" if suffix != "001" else "Ramesh Patil",
            display_name=f"Ramesh Patil {suffix}" if suffix != "001" else "Ramesh Patil",
            folio_number=f"FOL-SAP-{suffix}",
            membership_status="active",
            pan_encrypted=FieldEncryption.encrypt("members.pan", pan),
            pan_hash=f"sap-pan-hash-{suffix}",
            aadhaar_encrypted=(
                FieldEncryption.encrypt("members.aadhaar", aadhaar) if aadhaar else ""
            ),
            aadhaar_hash=f"sap-aadhaar-hash-{suffix}" if aadhaar else "",
            registered_address_line1="Village Road",
            registered_village_city="Nashik",
            registered_district="Nashik",
            registered_state="Maharashtra",
            registered_pincode="422001",
            mobile_number=f"9000000{len(str(suffix)):03d}",
            email=f"ramesh-{suffix}@example.com",
            kyc_status="verified",
            default_status="no_default",
        )
        application = LoanApplication.objects.create(
            application_reference_number=("LO00000025" if suffix == "001" else f"LO-{suffix}"),
            member=member,
            borrower_type=member_type,
            received_by_user=self.credit_manager,
            created_by_user=self.credit_manager,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Seasonal crop finance",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
        )
        risk = RiskAssessment.objects.create(
            loan_application=application,
            market_risk_rating="low",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            assessed_by_user=self.credit_manager,
        )
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=self.credit_manager,
            reviewed_by_user=self.credit_manager,
            reviewed_at=timezone.now(),
            last_review_decision="reviewed",
            tat_due_at=timezone.now(),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="10000000-0000-0000-0000-000000000001",
            loan_limit_assessment_id_snapshot="20000000-0000-0000-0000-000000000002",
            eligibility_snapshot_json={"overall_result": "eligible"},
            loan_limit_snapshot_json={"final_eligible_loan_amount": "400000.00"},
            prerequisite_provenance="verified",
            borrower_summary="No prior borrowing.",
            eligibility_summary="Eligible.",
            loan_limit_summary="Within limit.",
            recommended_amount="400000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Standard member security package.",
            repayment_capacity_notes="Adequate.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        case = ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            submitted_by_user=self.credit_manager,
            submission_remarks="Approved SAP request source facts.",
            current_status=ApprovalCase.STATUS_APPROVED,
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=application.pk,
            reason_for_approval="Approved by sanction committee.",
            closed_at=timezone.now(),
        )
        SanctionDecision.objects.create(
            loan_application=application,
            approval_case=case,
            decision="sanctioned",
            sanctioned_amount="400000.00",
            sanctioned_tenure_months=12,
            interest_rate_type="floating",
            security_required_summary="Standard member security package.",
            decision_reason="Approved.",
        )
        return application

    def _post_request(
        self, request_id, *, application=None, application_id=None,
        assigned_to=None, actor=None,
    ):
        application_id = application_id or (application or self.application).pk
        return self.client.post(
            f"/api/v1/loan-applications/{application_id}/sap-customer-profile-request/",
            {"assigned_to_user_id": str((assigned_to or self.assignee).pk)},
            content_type="application/json",
            HTTP_X_REQUEST_ID=request_id,
            **self._auth(actor or self.credit_manager),
        )

    def _create_and_send(self, label, application=None):
        created = self._post_request(
            f"{label}-create", application=application or self.application
        )
        self.assertEqual(created.status_code, 200, created.content)
        request_id = created.json()["data"]["sap_customer_profile_request_id"]
        sent = self._send(request_id, remarks=f"{label} send")
        self.assertEqual(sent.status_code, 200, sent.content)
        return request_id

    def _send(self, request_id, *, actor=None, remarks=""):
        return self.client.post(
            f"/api/v1/sap-customer-profile-requests/{request_id}/send/",
            {"remarks": remarks},
            content_type="application/json",
            HTTP_X_REQUEST_ID=f"send-{request_id}",
            **self._auth(actor or self.credit_manager),
        )

    def _complete(self, request_id, *, sap_customer_code, actor=None, **optional):
        return self._complete_raw(
            request_id,
            {"sap_customer_code": sap_customer_code, **optional},
            actor=actor,
        )

    def _complete_raw(self, request_id, payload, *, actor=None):
        return self.client.post(
            f"/api/v1/sap-customer-profile-requests/{request_id}/complete/",
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID=f"complete-{request_id}",
            **self._auth(actor or self.assignee),
        )

    def _upload_confirmation(
        self, *, related_entity_type, related_entity_id, actor=None,
        sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        document_category="sap_confirmation",
    ):
        actor = actor or self.assignee
        return store_document_upload(
            user=actor,
            request=RequestFactory().post("/documents/"),
            uploaded_file=SimpleUploadedFile(
                "sap-confirmation.pdf", b"safe SAP confirmation evidence",
                content_type="application/pdf",
            ),
            document_category=document_category,
            sensitivity_level=sensitivity_level,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )

    def _assert_no_sap_artifacts(self):
        self.assertEqual(SapCustomerProfileRequest.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(), 0
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").count(), 0
        )

    @staticmethod
    def _worksheet_values(workbook):
        with zipfile.ZipFile(BytesIO(workbook)) as archive:
            root = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        return [
            [cell.findtext("x:is/x:t", default="", namespaces=namespace) for cell in row]
            for row in root.findall("x:sheetData/x:row", namespace)
        ]

    def _user(self, role_code, full_name, *permission_codes):
        role, _ = Role.objects.get_or_create(
            role_code=role_code,
            defaults={"role_name": full_name, "status": "active"},
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "finance",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)
        user = User.objects.create(
            full_name=full_name,
            email=f"{role_code}-{User.objects.count()}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save()
        return user

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.json())
        return {
            "HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"
        }


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class SapCustomerProfileRequestRaceTests(TransactionTestCase):
    reset_sequences = True
    password = SapCustomerProfileRequestApiTests.password

    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.settings = override_settings(DOCUMENT_STORAGE_ROOT=self.storage.name)
        self.settings.enable()
        self.credit_manager = SapCustomerProfileRequestApiTests._user(
            self, "credit_manager", "SAP Race Credit Manager",
            "finance.sap_request.create", "finance.sap_request.send",
        )
        self.assignee = SapCustomerProfileRequestApiTests._user(
            self, "senior_manager_finance", "SAP Race Senior Manager Finance",
            "finance.sap_request.complete", "finance.sap_code.read",
        )

    def tearDown(self):
        self.settings.disable()
        self.storage.cleanup()

    def test_five_caller_race_has_one_request_file_and_evidence_winner_twice(self):
        for round_number in range(2):
            application = SapCustomerProfileRequestApiTests._terminal_application(
                self, suffix=f"RACE-{round_number}"
            )
            barrier = Barrier(5)

            def create(index):
                close_old_connections()
                try:
                    actor = User.objects.get(pk=self.credit_manager.pk)
                    request = RequestFactory().post(
                        "/sap-request/", HTTP_X_REQUEST_ID=f"race-{round_number}-{index}"
                    )
                    barrier.wait(timeout=10)
                    return create_request(
                        actor=actor,
                        application_id=application.pk,
                        payload={"assigned_to_user_id": str(self.assignee.pk)},
                        request=request,
                    )
                finally:
                    close_old_connections()

            with ThreadPoolExecutor(max_workers=5) as pool:
                results = list(pool.map(create, range(5)))
            self.assertEqual(
                len({item["sap_customer_profile_request_id"] for item in results}), 1
            )
            self.assertEqual(SapCustomerProfileRequest.objects.count(), round_number + 1)
            self.assertEqual(DocumentFile.objects.count(), round_number + 1)
            self.assertEqual(
                AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(),
                round_number + 1,
            )
            self.assertEqual(
                WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").count(),
                round_number + 1,
            )

    def test_five_conflicting_code_confirmations_have_one_exact_winner_twice(self):
        for round_number in range(2):
            application = SapCustomerProfileRequestApiTests._terminal_application(
                self, suffix=f"CODE-RACE-{round_number}"
            )
            request_id = self._create_and_send(application, f"code-race-{round_number}")
            barrier = Barrier(5)

            def complete(index):
                close_old_connections()
                try:
                    actor = User.objects.get(pk=self.assignee.pk)
                    request = RequestFactory().post(
                        "/sap-complete/",
                        HTTP_X_REQUEST_ID=f"code-race-{round_number}-{index}",
                    )
                    barrier.wait(timeout=10)
                    try:
                        result = complete_request(
                            actor=actor,
                            request_id=request_id,
                            payload={
                                "sap_customer_code": (
                                    f"CONCURRENT-CODE-{round_number}-{index}"
                                )
                            },
                            request=request,
                        )
                        return ("winner", result["sap_customer_code_id"])
                    except SapRequestConflict:
                        return ("conflict", None)
                finally:
                    close_old_connections()

            with ThreadPoolExecutor(max_workers=5) as pool:
                results = list(pool.map(complete, range(5)))
            self.assertEqual([status for status, _ in results].count("winner"), 1)
            self.assertEqual([status for status, _ in results].count("conflict"), 4)
            winner_ids = {code_id for status, code_id in results if status == "winner"}
            self.assertEqual(len(winner_ids), 1)
            self.assertEqual(SapCustomerCode.objects.count(), round_number + 1)
            self.assertEqual(
                SapCustomerProfileRequest.objects.filter(
                    request_status=SapCustomerProfileRequest.STATUS_COMPLETED
                ).count(),
                round_number + 1,
            )
            self.assertEqual(
                AuditLog.objects.filter(
                    action__in=("sap.customer_code_created", "sap.customer_code_reused")
                ).count(),
                round_number + 1,
            )
            self.assertEqual(
                WorkflowEvent.objects.filter(
                    workflow_name="SAPCustomerCodeCompleted"
                ).count(),
                round_number + 1,
            )

    def test_two_pending_same_member_requests_have_one_terminal_winner_twice(self):
        for round_number in range(2):
            first_application = SapCustomerProfileRequestApiTests._terminal_application(
                self, suffix=f"MEMBER-RACE-{round_number}-A"
            )
            second_application = SapCustomerProfileRequestApiTests._terminal_application(
                self, suffix=f"MEMBER-RACE-{round_number}-B"
            )
            second_application.member = first_application.member
            second_application.save(update_fields=["member"])
            first_id = self._create_and_send(
                first_application, f"member-race-{round_number}-a"
            )
            second_id = self._create_and_send(
                second_application, f"member-race-{round_number}-b"
            )
            barrier = Barrier(2)

            def complete(request_id):
                close_old_connections()
                try:
                    actor = User.objects.get(pk=self.assignee.pk)
                    request = RequestFactory().post(
                        "/sap-complete/",
                        HTTP_X_REQUEST_ID=f"member-race-{round_number}-{request_id}",
                    )
                    barrier.wait(timeout=10)
                    try:
                        result = complete_request(
                            actor=actor,
                            request_id=request_id,
                            payload={
                                "sap_customer_code": f"ONE-MEMBER-{round_number}"
                            },
                            request=request,
                        )
                        return ("winner", result["sap_customer_profile_request_id"])
                    except SapRequestConflict:
                        return ("conflict", None)
                finally:
                    close_old_connections()

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(complete, (first_id, second_id)))
            self.assertEqual([status for status, _ in results].count("winner"), 1)
            self.assertEqual([status for status, _ in results].count("conflict"), 1)
            winner_ids = {request_id for status, request_id in results if status == "winner"}
            self.assertEqual(len(winner_ids), 1)
            self.assertEqual(SapCustomerCode.objects.count(), round_number + 1)
            self.assertEqual(
                SapCustomerProfileRequest.objects.filter(
                    request_status=SapCustomerProfileRequest.STATUS_COMPLETED
                ).count(),
                round_number + 1,
            )
            self.assertEqual(
                SapCustomerProfileRequest.objects.filter(
                    request_status=SapCustomerProfileRequest.STATUS_SENT
                ).count(),
                round_number + 1,
            )
            self.assertEqual(
                AuditLog.objects.filter(
                    action__in=("sap.customer_code_created", "sap.customer_code_reused")
                ).count(),
                round_number + 1,
            )

    def _create_and_send(self, application, label):
        create_http_request = RequestFactory().post(
            "/sap-request/", HTTP_X_REQUEST_ID=f"{label}-create"
        )
        created = create_request(
            actor=self.credit_manager,
            application_id=application.pk,
            payload={"assigned_to_user_id": str(self.assignee.pk)},
            request=create_http_request,
        )
        send_http_request = RequestFactory().post(
            "/sap-send/", HTTP_X_REQUEST_ID=f"{label}-send"
        )
        send_request(
            actor=self.credit_manager,
            request_id=created["sap_customer_profile_request_id"],
            payload={"remarks": label},
            request=send_http_request,
        )
        return created["sap_customer_profile_request_id"]
