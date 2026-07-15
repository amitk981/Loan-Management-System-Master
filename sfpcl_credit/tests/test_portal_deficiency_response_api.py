import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from sfpcl_credit.applications.models import ApplicationDeficiency, ApplicationDeficiencyResponse, ApplicationDocument, LoanApplication
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, Permission, PortalAccount, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import ChecklistAction, ChecklistItem, DocumentChecklist
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class PortalDeficiencyResponseApiTests(TestCase):
    def setUp(self):
        self.storage_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage_directory.cleanup)
        storage_override = override_settings(DOCUMENT_STORAGE_ROOT=self.storage_directory.name)
        storage_override.enable()
        self.addCleanup(storage_override.disable)
        self.client = Client()
        portal_role = Role.objects.create(
            role_code="borrower_portal_user", role_name="Borrower Portal User",
            is_system_role=True, status="active",
        )
        staff_role = Role.objects.create(
            role_code="deputy_manager_finance", role_name="Deputy Manager Finance",
            is_system_role=True, status="active",
        )
        self.staff_user = self._user("staff@sfpcl.example", staff_role)
        read_permission = Permission.objects.create(
            permission_code="applications.loan_application.read",
            permission_name="Read loan applications", module_name="applications",
            risk_level=Permission.RISK_MEDIUM,
        )
        RolePermission.objects.create(role=staff_role, permission=read_permission)
        self.member = self._member("M-008L2", "FOL-008L2")
        self.portal_user = self._user("member.portal@sfpcl.example", portal_role)
        self.portal_account = PortalAccount.objects.create(
            member=self.member, user=self.portal_user, status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        self.application = LoanApplication.objects.create(
            member=self.member, borrower_type=self.member.member_type,
            received_by_user=self.staff_user, required_loan_amount="250000.00",
            declared_purpose="Crop production", purpose_category="crop_production",
            application_status=LoanApplication.STATUS_INCOMPLETE_RETURNED,
            completeness_status=LoanApplication.COMPLETENESS_INCOMPLETE,
            current_stage=LoanApplication.STAGE_INITIAL,
        )
        self.deficiency = self._deficiency(self.application)

    def _user(self, email, role):
        user = User.objects.create(full_name=email, email=email, status="active", primary_role=role)
        user.set_password("CorrectHorse123!")
        user.save()
        return user

    def _member(self, number, folio):
        return Member.objects.create(
            member_number=number, member_type="individual_farmer", legal_name="Portal Member",
            display_name="Portal Member", folio_number=folio, membership_start_date="2021-04-01",
            membership_status="active", pan_encrypted="protected-pan", pan_hash=f"pan-{number}",
            aadhaar_encrypted="protected-aadhaar", aadhaar_hash=f"aadhaar-{number}",
            registered_address_line1="Village Road", registered_village_city="Nashik",
            registered_state="Maharashtra", mobile_number="+919800000042", kyc_status="verified",
            default_status="no_default",
        )

    def _deficiency(self, application, *, item_code="six_month_bank_statement"):
        return ApplicationDeficiency.objects.create(
            loan_application=application, item_code=item_code,
            deficiency_type=ApplicationDeficiency.TYPE_MISSING_DOCUMENT,
            source_reason_code="missing_metadata",
            description=("Upload the missing six-month bank statement." if item_code == "six_month_bank_statement" else "Upload crop plan."),
            remarks="Internal staff assessment must stay hidden.",
            resolution_status=ApplicationDeficiency.STATUS_OPEN, raised_by_user=self.staff_user,
            communication_mode="portal", message="Please correct the requested item.",
        )

    def _token(self, *, staff=False):
        url = "/api/v1/auth/login/" if staff else "/api/v1/portal/auth/login/"
        data = ({"email": self.staff_user.email} if staff else {"identifier": self.portal_user.email})
        response = self.client.post(url, data={**data, "password": "CorrectHorse123!"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _url(self, suffix=""):
        return f"/api/v1/portal/applications/{self.application.pk}/deficiencies/{suffix}"

    def _upload(self, token, *, name="bank-statement.pdf", remark="The missing statement is attached."):
        return self.client.post(
            self._url(f"{self.deficiency.pk}/upload/"),
            data={
                "file": SimpleUploadedFile(name, b"%PDF-1.4 corrected statement", "application/pdf"),
                "document_category": "finance", "sensitivity_level": "confidential",
                "response_remark": remark,
            },
            headers={"Authorization": f"Bearer {token}", "X-Request-ID": "upload-1"},
        )

    def test_borrower_reads_open_deficiencies_without_internal_staff_notes(self):
        response = self.client.get(self._url(), headers={"Authorization": f"Bearer {self._token()}", "X-Request-ID": "read-1"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        data = body["data"]
        self.assertEqual(data["loan_application_id"], str(self.application.pk))
        self.assertIsNone(data["application_reference_number"])
        self.assertEqual(data["deficiency_note_action_url"], self._url("note/"))
        self.assertFalse(data["resubmission_allowed"])
        item = data["items"][0]
        self.assertEqual(
            {key: item[key] for key in ("deficiency_id", "item_code", "deficiency_type", "description", "resolution_status")},
            {
                "deficiency_id": str(self.deficiency.pk), "item_code": "six_month_bank_statement",
                "deficiency_type": "missing_document", "description": "Upload the missing six-month bank statement.",
                "resolution_status": "open",
            },
        )
        self.assertEqual(item["upload_contract"], {
            "document_category": "finance", "sensitivity_level": "confidential",
            "allowed_extensions": ["pdf", "jpg", "jpeg", "png"], "max_size_bytes": 5242880,
        })
        self.assertEqual((item["response"], item["draft"]), (None, None))
        self.assertNotIn("Internal staff assessment", str(body))
        self.assertNotIn("raised_by", str(body))

    def test_borrower_saves_response_draft_and_downloads_borrower_safe_deficiency_note(self):
        token = self._token()
        remark = "I will attach the corrected statement tomorrow."
        draft = self.client.post(
            self._url(f"{self.deficiency.pk}/draft/"), data={"response_remark": remark},
            content_type="application/json", headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(draft.status_code, 200, draft.content)
        self.assertEqual(draft.json()["data"]["response_remark"], remark)
        self.assertEqual(ApplicationDeficiencyResponse.objects.count(), 0)
        self.assertTrue(AuditLog.objects.filter(action="portal.deficiency.draft_saved").exists())
        projection = self.client.get(self._url(), headers={"Authorization": f"Bearer {token}"}).json()["data"]
        self.assertEqual(projection["items"][0]["draft"]["response_remark"], remark)
        self.assertFalse(projection["resubmission_allowed"])
        note = self.client.get(projection["deficiency_note_action_url"], headers={"Authorization": f"Bearer {token}"})
        self.assertEqual((note.status_code, note["Content-Type"]), (200, "text/plain; charset=utf-8"))
        self.assertIn(str(self.application.pk).encode(), note.content)
        self.assertIn(b"Upload the missing six-month bank statement.", note.content)
        self.assertNotIn(b"Internal staff assessment", note.content)
        self.assertTrue(AuditLog.objects.filter(action="portal.deficiency.note_downloaded").exists())

    def test_borrower_uploads_response_and_resubmits_to_completeness_review(self):
        token = self._token()
        upload = self._upload(token)
        self.assertEqual(upload.status_code, 200, upload.content)
        upload_data = upload.json()["data"]
        self.assertEqual((upload_data["deficiency_id"], upload_data["response_status"]), (str(self.deficiency.pk), "responded"))
        self.assertEqual(upload_data["document"]["file_name"], "bank-statement.pdf")
        self.assertNotIn("storage_key", str(upload.json()))
        replacement = ApplicationDocument.objects.get(document_file_id=upload_data["document"]["document_id"])
        self.assertEqual((replacement.loan_application, replacement.document_type), (self.application, "six_month_bank_statement"))
        self.assertEqual((replacement.party_type, replacement.party_id), ("borrower", self.member.pk))
        self.assertEqual(replacement.verification_status, ApplicationDocument.VERIFICATION_PENDING)
        resubmit = self.client.post(self._url("resubmit/"), data={}, content_type="application/json", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resubmit.status_code, 200, resubmit.content)
        data = resubmit.json()["data"]
        self.assertEqual((data["application_status"], data["completeness_status"], data["pending_with"]), ("submitted", "not_started", "SFPCL"))
        self.deficiency.refresh_from_db()
        self.assertEqual(self.deficiency.resolution_status, ApplicationDeficiency.STATUS_OPEN)
        self.assertIsNone(self.deficiency.resolved_by_user)
        self.assertIsNone(self.deficiency.resolved_at)
        for action in ("portal.document.uploaded", "portal.deficiency.responded", "portal.application.resubmitted"):
            self.assertTrue(AuditLog.objects.filter(action=action).exists())
        self.assertTrue(WorkflowEvent.objects.filter(entity_type="loan_application", entity_id=self.application.pk, from_state="incomplete_returned", to_state="submitted").exists())
        queue = self.client.get("/api/v1/loan-applications/?application_status=submitted", headers={"Authorization": f"Bearer {self._token(staff=True)}"})
        self.assertEqual(queue.status_code, 200)
        self.assertIn(str(self.application.pk), str(queue.json()["data"]))
        status = self.client.get(f"/api/v1/portal/applications/{self.application.pk}/", headers={"Authorization": f"Bearer {token}"})
        self.assertIn("Application resubmitted", [event["event"] for event in status.json()["data"]["timeline"]])

    def test_cross_member_read_upload_and_resubmit_are_nondisclosing_and_audited(self):
        other_member = self._member("M-OTHER-L2", "FOL-OTHER-L2")
        other_application = LoanApplication.objects.create(
            member=other_member, borrower_type=other_member.member_type, received_by_user=self.staff_user,
            required_loan_amount="180000.00", declared_purpose="Other crop production",
            purpose_category="crop_production", application_status=LoanApplication.STATUS_INCOMPLETE_RETURNED,
            completeness_status=LoanApplication.COMPLETENESS_INCOMPLETE, current_stage=LoanApplication.STAGE_INITIAL,
        )
        other_deficiency = self._deficiency(other_application, item_code="crop_plan")
        root = f"/api/v1/portal/applications/{other_application.pk}/deficiencies/"
        token = self._token()
        responses = (
            self.client.get(root, headers={"Authorization": f"Bearer {token}"}),
            self.client.post(
                f"{root}{other_deficiency.pk}/upload/",
                data={"file": SimpleUploadedFile("crop.pdf", b"%PDF-other", "application/pdf"), "document_category": "legal", "sensitivity_level": "confidential"},
                headers={"Authorization": f"Bearer {token}"},
            ),
            self.client.post(f"{root}resubmit/", data={}, content_type="application/json", headers={"Authorization": f"Bearer {token}"}),
        )
        for response in responses:
            self.assertEqual(response.status_code, 404)
            self.assertNotIn(str(other_member.pk), str(response.content))
        self.assertEqual(AuditLog.objects.filter(action="portal.deficiency.access_denied").count(), 3)
        self.assertFalse(AuditLog.objects.filter(action="documents.file.uploaded").exists())
        self.assertFalse(WorkflowEvent.objects.exists())

    def test_upload_contract_and_resubmission_state_guards_reject_without_side_effects(self):
        token = self._token()
        upload_url = self._url(f"{self.deficiency.pk}/upload/")
        invalid_requests = (
            {"file": SimpleUploadedFile("missing-category.pdf", b"%PDF-one", "application/pdf"), "sensitivity_level": "confidential"},
            {"file": SimpleUploadedFile("script.exe", b"unsafe", "application/octet-stream"), "document_category": "finance", "sensitivity_level": "confidential"},
            {"file": SimpleUploadedFile("oversized.pdf", b"x" * (5 * 1024 * 1024 + 1), "application/pdf"), "document_category": "finance", "sensitivity_level": "confidential"},
            {"file": SimpleUploadedFile("restricted.pdf", b"%PDF-one", "application/pdf"), "document_category": "finance", "sensitivity_level": "restricted"},
        )
        for payload in invalid_requests:
            response = self.client.post(upload_url, data=payload, headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(response.status_code, 400)
            assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
        for payload in ({}, {"force": True}):
            response = self.client.post(self._url("resubmit/"), data=payload, content_type="application/json", headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(response.status_code, 400)
            assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
        self.application.application_status = LoanApplication.STATUS_SUBMITTED
        self.application.submitted_at = timezone.now()
        self.application.save()
        responses = (
            self.client.post(upload_url, data={"file": SimpleUploadedFile("valid.pdf", b"%PDF-valid", "application/pdf"), "document_category": "finance", "sensitivity_level": "confidential"}, headers={"Authorization": f"Bearer {token}"}),
            self.client.post(self._url("resubmit/"), data={}, content_type="application/json", headers={"Authorization": f"Bearer {token}"}),
        )
        for response in responses:
            self.assertEqual(response.status_code, 409)
            assert_error_envelope(self, response.json(), "INVALID_STATE_TRANSITION")
        self.assertFalse(AuditLog.objects.filter(action__in=["documents.file.uploaded", "portal.deficiency.responded"]).exists())
        self.assertFalse(WorkflowEvent.objects.exists())

    def test_reupload_retains_immutable_history_and_projects_only_the_current_response(self):
        token = self._token()
        response_ids = []
        for name, remark in (("statement-v1.pdf", "First response"), ("statement-v2.pdf", "Corrected response")):
            response = self._upload(token, name=name, remark=remark)
            self.assertEqual(response.status_code, 200)
            response_ids.append(response.json()["data"]["response"]["deficiency_response_id"])
        first, second = (ApplicationDeficiencyResponse.objects.get(pk=response_id) for response_id in response_ids)
        self.assertEqual((second.supersedes, first.successor), (first, second))
        self.assertEqual(ApplicationDeficiencyResponse.objects.count(), 2)
        first.response_remark = "rewrite"
        with self.assertRaises(ValidationError):
            first.save()
        with self.assertRaises(ValidationError):
            ApplicationDeficiencyResponse.objects.filter(pk=first.pk).update(response_remark="rewrite")
        projection = self.client.get(self._url(), headers={"Authorization": f"Bearer {token}"}).json()["data"]
        current = projection["items"][0]["response"]
        self.assertEqual((current["deficiency_response_id"], current["response_remark"]), (str(second.pk), "Corrected response"))
        self.assertEqual(current["document"]["file_name"], "statement-v2.pdf")
        self.assertNotIn("statement-v1.pdf", str(projection))

    def test_current_response_content_requires_a_fresh_authenticated_portal_read(self):
        token = self._token()
        self.assertEqual(self._upload(token, name="statement.pdf").status_code, 200)
        projection = self.client.get(self._url(), headers={"Authorization": f"Bearer {token}"}).json()["data"]
        descriptor = self.client.get(projection["items"][0]["response"]["document"]["action_url"], headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(descriptor.status_code, 200)
        download_url = descriptor.json()["data"]["download_url"]
        self.assertIn("token=", download_url)
        self.assertNotIn("expires_at=", download_url)
        denied = self.client.get(download_url)
        self.assertEqual(denied.status_code, 401)
        assert_error_envelope(self, denied.json(), "AUTH_REQUIRED")
        content = self.client.get(download_url, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual((content.status_code, content.content, content["Content-Type"]), (200, b"%PDF-1.4 corrected statement", "application/pdf"))
        tampered = self.client.get(download_url.replace("token=", "token=tampered"), headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(tampered.status_code, 404)
        assert_error_envelope(self, tampered.json(), "NOT_FOUND")
        self.assertTrue(AuditLog.objects.filter(action="portal.deficiency.document_downloaded").exists())

    def test_deficiency_resubmission_cannot_mutate_stage4_checklist_truth(self):
        checklist = DocumentChecklist.objects.create(
            loan_application=self.application, checklist_status=DocumentChecklist.STATUS_IN_PROGRESS,
            remarks="K3 verifier remarks must remain unchanged.",
        )
        item = ChecklistItem.objects.create(
            document_checklist=checklist, item_code="final_checklist",
            item_label="Final documentation checklist", display_order=11, required_flag=True,
            applicable_flag=True, completion_status=ChecklistItem.STATUS_PENDING,
            applicability_source="canonical_approval", remarks="K3 item remarks must remain unchanged.",
        )
        token = self._token()
        self.assertEqual(self._upload(token, name="statement.pdf").status_code, 200)
        resubmit = self.client.post(self._url("resubmit/"), data={}, content_type="application/json", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resubmit.status_code, 200)
        checklist.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual((checklist.checklist_status, checklist.remarks), (DocumentChecklist.STATUS_IN_PROGRESS, "K3 verifier remarks must remain unchanged."))
        self.assertEqual((checklist.company_secretary_signature_id, checklist.credit_manager_signature_id, checklist.sanction_committee_signature_id), (None, None, None))
        self.assertEqual((item.completion_status, item.remarks), (ChecklistItem.STATUS_PENDING, "K3 item remarks must remain unchanged."))
        self.assertFalse(ChecklistAction.objects.exists())
        self.assertFalse(VersionHistory.objects.filter(versioned_entity_type__in=["checklist_item_completion", "document_checklist_approval"]).exists())
        self.assertFalse(AuditLog.objects.filter(action__startswith="document_checklist.").exists())
        self.assertFalse(WorkflowEvent.objects.filter(workflow_name="documentation_checklist").exists())

    def test_staff_and_suspended_portal_sessions_cannot_use_deficiency_routes(self):
        routes = (("get", self._url()), ("post", self._url("resubmit/")))
        for method, route in routes:
            response = getattr(self.client, method)(route, data={}, content_type="application/json", headers={"Authorization": f"Bearer {self._token(staff=True)}"})
            self.assertEqual(response.status_code, 403)
            assert_error_envelope(self, response.json(), "FORBIDDEN")
        portal_token = self._token()
        self.portal_account.status = PortalAccount.STATUS_SUSPENDED
        self.portal_account.save(update_fields=["status"])
        for method, route in routes:
            response = getattr(self.client, method)(route, data={}, content_type="application/json", headers={"Authorization": f"Bearer {portal_token}"})
            self.assertEqual(response.status_code, 401)
            assert_error_envelope(self, response.json(), "INVALID_TOKEN")
