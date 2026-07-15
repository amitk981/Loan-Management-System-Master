import hashlib
import tempfile
from pathlib import Path
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.utils import timezone
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.identity.models import AuditLog, PortalAccount, Role, User
from sfpcl_credit.legal_documents.models import ChecklistAction, LoanDocument
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.tests import test_document_checklist_api
class PortalDocumentationActionsApiTests(TestCase):
    password = "PortalDocuments123!"
    def setUp(self):
        self.storage_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage_directory.cleanup)
        storage_override = override_settings(DOCUMENT_STORAGE_ROOT=self.storage_directory.name)
        storage_override.enable()
        self.addCleanup(storage_override.disable)
        self.fixture = test_document_checklist_api.DocumentChecklistApiTests(
            methodName="test_approved_sanction_creates_ordered_applicability_once_with_evidence")
        self.fixture.setUp()
        self.application = self.fixture.application
        self.checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.fixture.actor, application_id=self.application.pk,
            source_reason="portal_documentation_test")
        portal_role, _ = Role.objects.get_or_create(
            role_code="borrower_portal_user",
            defaults={
                "role_name": "Borrower Portal User",
                "is_system_role": True,
                "status": "active",
            },
        )
        self.portal_user = User.objects.create(
            full_name=self.application.member.display_name, email="portal.documents@sfpcl.example",
            status="active", primary_role=portal_role)
        self.portal_user.set_password(self.password)
        self.portal_user.save()
        self.portal_account = PortalAccount.objects.create(
            member=self.application.member, user=self.portal_user,
            status=PortalAccount.STATUS_ACTIVE, activated_at=timezone.now())
        self.client = Client()
    def test_own_sanctioned_application_returns_ordered_borrower_safe_actions(self):
        response = self.client.get(
            self._collection_url(),
            headers=self._portal_auth(),
        )
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_success_envelope(self, body)
        data = body["data"]
        self.assertEqual(data["loan_application_id"], str(self.application.pk))
        self.assertEqual(
            [action["action_code"] for action in data["actions"]],
            [
                "witness_pan_aadhaar",
                "cancelled_cheque",
                "blank_dated_cheque",
                "poa",
                "tri_party_agreement",
                "sh4",
                "cdsl_pledge",
                "term_sheet",
                "loan_agreement",
                "bank_verification_letter",
                "final_checklist",
            ],
        )
        tri_party = self._action(data, "tri_party_agreement")
        sh4 = self._action(data, "sh4")
        cdsl = self._action(data, "cdsl_pledge")
        blank_cheque = self._action(data, "blank_dated_cheque")
        self.assertTrue(tri_party["applicable"])
        self.assertTrue(sh4["applicable"])
        self.assertFalse(cdsl["applicable"])
        self.assertFalse(cdsl["upload_allowed"])
        self.assertFalse(blank_cheque["upload_allowed"])
        serialized = str(body).lower()
        for forbidden in (
            "storage_key",
            "cheque_number",
            "bo_account",
            "checklist_item_id",
            "verified_by_user",
            "workflow_event",
            "terminal_evidence",
        ):
            self.assertNotIn(forbidden, serialized)
    def test_upload_and_reupload_retain_provenance_without_completing_internal_item(self):
        item = self.checklist.items.get(item_code="cancelled_cheque")
        before = {
            "completion_status": item.completion_status,
            "checklist_actions": ChecklistAction.objects.count(),
            "workflow_events": apps.get_model("workflows", "WorkflowEvent").objects.count(),
            "version_history": apps.get_model("configurations", "VersionHistory").objects.count(),
        }
        first = self.client.post(
            f"{self._collection_url()}cancelled_cheque/upload/",
            data={
                "file": self._pdf("cancelled-cheque.pdf", b"%PDF-1.4 first portal copy"),
                "notes": "Borrower-provided cancelled cheque.",
            },
            headers=self._portal_auth(),
        )
        self.assertEqual(first.status_code, 200, first.content)
        first_data = first.json()["data"]
        self.assertEqual(first_data["action_code"], "cancelled_cheque")
        self.assertEqual(first_data["document"]["file_name"], "cancelled-cheque.pdf")
        self.assertEqual(first_data["document"]["mime_type"], "application/pdf")
        self.assertNotIn("storage_key", str(first.json()).lower())
        canonical = self.client.get(self._collection_url(), headers=self._portal_auth())
        self.assertEqual(canonical.status_code, 200, canonical.content)
        cancelled = self._action(canonical.json()["data"], "cancelled_cheque")
        self.assertEqual(cancelled["status"], "submitted")
        self.assertFalse(cancelled["upload_allowed"])
        self.assertTrue(cancelled["reupload_allowed"])
        second = self.client.post(
            f"{self._collection_url()}cancelled_cheque/upload/",
            data={
                "file": self._pdf("cancelled-cheque-replacement.pdf", b"%PDF-1.4 second portal copy"),
                "notes": "Clearer replacement.",
            },
            headers=self._portal_auth(),
        )
        self.assertEqual(second.status_code, 200, second.content)
        submission_model = apps.get_model("legal_documents", "PortalDocumentationSubmission")
        submissions = list(submission_model.objects.order_by("created_at"))
        self.assertEqual(len(submissions), 2)
        self.assertEqual(submissions[0].portal_account_id, self.portal_account.pk)
        self.assertEqual(submissions[0].uploader_member_id, self.application.member_id)
        self.assertEqual(submissions[0].loan_application_id, self.application.pk)
        self.assertEqual(submissions[1].supersedes_id, submissions[0].pk)
        self.assertNotEqual(submissions[0].document_id, submissions[1].document_id)
        self.assertEqual(DocumentFile.objects.count(), 2)
        with self.assertRaises(ValidationError):
            submission_model.objects.filter(pk=submissions[0].pk).update(notes="mutated")
        with self.assertRaises(ValidationError):
            submissions[0].delete()
        with self.assertRaises(ValidationError):
            submissions[0].save()
        self.assertEqual(
            AuditLog.objects.filter(action="portal.documentation.uploaded").count(), 2
        )
        self.assertEqual(
            AuditLog.objects.filter(action="documents.file.uploaded").count(), 2
        )
        item.refresh_from_db()
        self.assertEqual(item.completion_status, before["completion_status"])
        self.assertEqual(ChecklistAction.objects.count(), before["checklist_actions"])
        self.assertEqual(
            apps.get_model("workflows", "WorkflowEvent").objects.count(),
            before["workflow_events"],
        )
        self.assertEqual(
            apps.get_model("configurations", "VersionHistory").objects.count(),
            before["version_history"],
        )
    def test_scope_stage_action_and_upload_shape_fail_closed_without_success_evidence(self):
        missing = self.client.get(
            "/api/v1/portal/applications/10000000-0000-0000-0000-000000000099/documentation-actions/",
            headers=self._portal_auth())
        self.assertEqual(missing.status_code, 404)
        other_member = self.fixture._approved_application(
            "portal-other", holding_mode="demat", subsidiary=False
        )[0].member
        other_user = User.objects.create(
            full_name="Other Portal Member", email="other.portal.documents@sfpcl.example",
            status="active", primary_role=self.portal_user.primary_role)
        other_user.set_password(self.password)
        other_user.save()
        PortalAccount.objects.create(
            member=other_member, user=other_user, status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now())
        cross_member = self.client.get(self._collection_url(), headers=self._auth_for(other_user))
        self.assertEqual(cross_member.status_code, 404)
        internal = self.client.get(self._collection_url(), headers={
            key.removeprefix("HTTP_").replace("_", "-"): value
            for key, value in self.fixture._auth(self.fixture.actor).items()})
        self.assertEqual(internal.status_code, 404)
        portal_auth = self._portal_auth()
        self.portal_account.status = PortalAccount.STATUS_SUSPENDED
        self.portal_account.save(update_fields=["status"])
        self.assertEqual(self.client.get(self._collection_url(), headers=portal_auth).status_code, 401)
        self.portal_account.status = PortalAccount.STATUS_ACTIVE
        self.portal_account.save(update_fields=["status"])
        self.application.application_status = self.application.STATUS_DRAFT
        self.application.save(update_fields=["application_status"])
        blocked = self.client.get(self._collection_url(), headers=self._portal_auth())
        self.assertEqual(blocked.status_code, 200)
        self.assertEqual(blocked.json()["data"]["availability"], "blocked")
        self.assertEqual(blocked.json()["data"]["actions"], [])
        blocked_upload = self.client.post(
            f"{self._collection_url()}cancelled_cheque/upload/",
            data={"file": self._pdf("blocked.pdf", b"%PDF blocked")},
            headers=self._portal_auth(),
        )
        self.assertEqual(blocked_upload.status_code, 409)
        self.application.application_status = self.application.STATUS_APPROVED_BY_SANCTION
        self.application.save(update_fields=["application_status"])
        invalid_requests = [
            ("cdsl_pledge", {"file": self._pdf("cdsl.pdf", b"%PDF cdsl")}, 409),
            ("unknown", {"file": self._pdf("unknown.pdf", b"%PDF unknown")}, 409),
            ("cancelled_cheque", {"notes": "missing file"}, 400),
            ("cancelled_cheque", {"file": self._pdf("empty.pdf", b"")}, 400),
            (
                "cancelled_cheque",
                {"file": self._pdf("too-large.pdf", b"%PDF" + b"x" * (5 * 1024 * 1024))},
                400,
            ),
            (
                "cancelled_cheque",
                {
                    "file": SimpleUploadedFile("wrong.png", b"image", content_type="application/pdf")
                },
                400,
            ),
            (
                "cancelled_cheque",
                {
                    "file": self._pdf("crafted.pdf", b"%PDF crafted"),
                    "terminal_evidence_digest": "forged",
                    "checklist_action_id": "10000000-0000-0000-0000-000000000001",
                },
                400,
            ),
            (
                "cancelled_cheque",
                {"file": self._pdf("notes.pdf", b"%PDF notes"), "notes": "x" * 4001},
                400,
            ),
        ]
        for code, payload, expected_status in invalid_requests:
            with self.subTest(code=code, fields=sorted(payload)):
                response = self.client.post(
                    f"{self._collection_url()}{code}/upload/",
                    data=payload,
                    headers=self._portal_auth(),
                )
                self.assertEqual(response.status_code, expected_status, response.content)
        self.assertEqual(DocumentFile.objects.count(), 0)
        self.assertFalse(
            AuditLog.objects.filter(action="portal.documentation.uploaded").exists()
        )
        self.assertFalse(
            AuditLog.objects.filter(action="documents.file.uploaded").exists()
        )
    def test_current_term_sheet_download_uses_borrower_safe_descriptor_and_separate_audit(self):
        output, loan_document = self._generated_document(
            "term_sheet", b"current term sheet bytes", "current-term-sheet.pdf")
        item = self.checklist.items.get(item_code="term_sheet")
        item.loan_document = loan_document
        item.save(update_fields=["loan_document"])
        projection = self.client.get(self._collection_url(), headers=self._portal_auth())
        self.assertEqual(projection.status_code, 200, projection.content)
        metadata = self._action(projection.json()["data"], "term_sheet")["download"]
        self.assertEqual(
            metadata,
            {
                "file_name": "current-term-sheet.pdf",
                "mime_type": "application/pdf",
                "action_url": (
                    f"/api/v1/portal/applications/{self.application.pk}/"
                    "documentation-actions/term_sheet/download/"
                ),
            },
        )
        self.assertNotIn("storage_key", str(projection.json()).lower())
        download = self.client.get(
            metadata["action_url"],
            headers={**self._portal_auth(), "X-Request-ID": "portal-download-1"},
        )
        self.assertEqual(download.status_code, 200, download.content)
        descriptor = download.json()["data"]
        self.assertIn("documentation-actions/term_sheet/download/?content=1", descriptor["download_url"])
        self.assertIn("expires_at", descriptor)
        content = self.client.get(
            descriptor["download_url"],
            headers={**self._portal_auth(), "X-Request-ID": "portal-download-1"})
        self.assertEqual(content.status_code, 200, content.content)
        self.assertEqual(content.content, b"current term sheet bytes")
        audit = AuditLog.objects.get(action="portal.documentation.downloaded")
        self.assertEqual(audit.actor_user, self.portal_user)
        self.assertEqual(audit.new_value_json["portal_account_id"], str(self.portal_account.pk))
        self.assertEqual(audit.new_value_json["member_id"], str(self.application.member_id))
        self.assertEqual(audit.new_value_json["loan_application_id"], str(self.application.pk))
        self.assertEqual(audit.new_value_json["action_code"], "term_sheet")
        self.assertEqual(audit.new_value_json["document_id"], str(output.pk))
        self.assertEqual(audit.new_value_json["request_id"], "portal-download-1")
        self.assertNotIn("storage_key", str(audit.new_value_json).lower())
        denied = self.client.get(
            f"{self._collection_url()}poa/download/",
            headers=self._portal_auth(),
        )
        self.assertEqual(denied.status_code, 404)
        self.assertEqual(
            AuditLog.objects.filter(action="portal.documentation.downloaded").count(), 1
        )
    def test_status_only_completion_is_never_shown_complete(self):
        item = self.checklist.items.get(item_code="cancelled_cheque")
        _output, loan_document = self._generated_document(
            "cancelled_cheque", b"synthetic cheque", "synthetic-cancelled-cheque.pdf")
        completed_at = timezone.now()
        type(item).objects.filter(pk=item.pk).update(
            completion_status="complete",
            loan_document=loan_document,
            verified_by_user=self.fixture.actor,
            verified_at=completed_at,
            remarks="Synthetic status-only completion.",
        )
        response = self.client.get(self._collection_url(), headers=self._portal_auth())
        self.assertEqual(response.status_code, 200, response.content)
        projected = self._action(response.json()["data"], "cancelled_cheque")
        self.assertEqual(projected["status"], "pending_borrower")
        self.assertTrue(projected["upload_allowed"])
        self.assertFalse(projected["reupload_allowed"])
    def test_every_canonical_borrower_upload_code_is_accepted_only_when_applicable(self):
        self.checklist.items.model.objects.filter(
            document_checklist=self.checklist, item_code="bank_verification_letter").update(
            required_flag=True, applicable_flag=True, completion_status="pending",
            applicability_blocker=None)
        allowed = ("cancelled_cheque", "poa", "tri_party_agreement", "sh4", "term_sheet",
                   "loan_agreement", "bank_verification_letter")
        for code in allowed:
            with self.subTest(code=code):
                response = self.client.post(f"{self._collection_url()}{code}/upload/", data={
                    "file": self._pdf(f"{code}.pdf", f"%PDF {code}".encode())},
                    headers=self._portal_auth())
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["data"]["action_code"], code)
        self.assertEqual(DocumentFile.objects.count(), len(allowed))
        self.assertEqual(AuditLog.objects.filter(
            action="portal.documentation.uploaded").count(), len(allowed))
    def test_portal_actor_gets_no_internal_checklist_security_or_reveal_authority(self):
        auth = self._portal_auth()
        denied = (
            self.client.post(f"/api/v1/checklist-items/{self.checklist.items.first().pk}/complete/",
                             data={"loan_document_id": "10000000-0000-0000-0000-000000000001"},
                             content_type="application/json", headers=auth),
            self.client.get(f"/api/v1/loan-applications/{self.application.pk}/security-package/",
                            headers=auth),
            self.client.post(
                "/api/v1/blank-dated-cheques/10000000-0000-0000-0000-000000000001/reveal-cheque-number/",
                data={"reason": "Forbidden portal reveal"}, content_type="application/json",
                headers=auth))
        self.assertTrue(all(response.status_code in {403, 404} for response in denied))
        self.assertFalse(AuditLog.objects.filter(action__contains="revealed").exists())
        self.assertFalse(ChecklistAction.objects.exists())
    def _collection_url(self):
        return (
            f"/api/v1/portal/applications/{self.application.pk}/"
            "documentation-actions/"
        )
    def _portal_auth(self):
        return self._auth_for(self.portal_user)
    def _auth_for(self, user):
        response = self.client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}
    def _generated_document(self, code, content, file_name):
        checksum = hashlib.sha256(content).hexdigest()
        output = DocumentFile.objects.create(
            file_name=file_name, file_extension=".pdf", mime_type="application/pdf",
            file_size_bytes=len(content), storage_provider="local", storage_key=f"generated/{file_name}",
            checksum_sha256=checksum, uploaded_by_user=self.fixture.actor,
            sensitivity_level="confidential")
        path = Path(self.storage_directory.name, output.storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        template = DocumentTemplate.objects.create(
            template_code=f"portal-{code}-v1", template_name=f"Portal {code}",
            document_type=code, borrower_type="individual_farmer", template_version="1.0",
            merge_fields_json=[], approval_status="approved", effective_from=timezone.localdate())
        document = LoanDocument.objects.create(
            loan_application=self.application, document_type=code, document_category="legal",
            party_required="borrower", document_template=template, document=output,
            output_format="pdf", generation_status="generated", execution_status="pending",
            verification_status="verified", renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=output.pk,
            renderer_validated_checksum_sha256=output.checksum_sha256)
        return output, document
    @staticmethod
    def _pdf(name, content):
        return SimpleUploadedFile(name, content, content_type="application/pdf")
    @staticmethod
    def _action(data, code):
        return next(action for action in data["actions"] if action["action_code"] == code)
