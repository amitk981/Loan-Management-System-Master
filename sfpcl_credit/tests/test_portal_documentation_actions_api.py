import tempfile
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import close_old_connections, connection, connections
from django.test import Client, RequestFactory, TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog, Permission, PortalAccount, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import ChecklistAction, LoanDocument, SignatureRecord
from sfpcl_credit.legal_documents.modules import document_checklist, document_generation
from sfpcl_credit.legal_documents.modules.checklist_actions import RequestMetadata
from sfpcl_credit.processes import document_checklist_actions, portal_documentation_actions
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.tests import test_document_checklist_api, test_loan_document_generation_api
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
        audits = list(
            AuditLog.objects.filter(action="portal.document.uploaded").order_by(
                "created_at", "audit_log_id"
            )
        )
        self.assertEqual(len(audits), 2)
        self.assertFalse(
            AuditLog.objects.filter(action="documents.file.uploaded").exists()
        )
        self.assertEqual(audits[0].actor_type, "portal_account")
        self.assertEqual(
            audits[0].new_value_json,
            {
                "portal_account_id": str(self.portal_account.pk),
                "member_id": str(self.application.member_id),
                "loan_application_id": str(self.application.pk),
                "action_code": "cancelled_cheque",
                "document_id": str(submissions[0].document_id),
                "document_version": 1,
                "document_category": "legal",
                "sensitivity_level": "confidential",
                "reason": "borrower_portal_submission",
                "request_id": None,
                "network": {"ip_address": "127.0.0.1", "user_agent": ""},
                "outcome": "accepted",
            },
        )
        self.assertNotIn("storage", str(audits[0].new_value_json).lower())
        self.assertNotIn("checksum", str(audits[0].new_value_json).lower())
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
            AuditLog.objects.filter(action="documents.file.uploaded").exists()
        )
        self.assertFalse(
            AuditLog.objects.filter(action="documents.file.uploaded").exists()
        )
    def test_current_term_sheet_download_uses_latest_renderer_without_checklist_pointer(self):
        output, loan_document = self._generated_document(
            "term_sheet", b"current term sheet bytes", "current-term-sheet.pdf")
        projection = self.client.get(self._collection_url(), headers=self._portal_auth())
        self.assertEqual(projection.status_code, 200, projection.content)
        metadata = self._action(projection.json()["data"], "term_sheet")["download"]
        self.assertEqual(
            metadata,
            {
                "file_name": output.file_name,
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
        self.assertIn("token=", descriptor["download_url"])
        self.assertNotIn("expires_at=", descriptor["download_url"])
        self.assertIn("expires_at", descriptor)
        tampered = self.client.get(
            descriptor["download_url"].replace("token=", "token=tampered"),
            headers=self._portal_auth(),
        )
        self.assertEqual(tampered.status_code, 404, tampered.content)
        content = self.client.get(
            descriptor["download_url"],
            headers={**self._portal_auth(), "X-Request-ID": "portal-download-1"})
        self.assertEqual(content.status_code, 200, content.content)
        self.assertTrue(content.content.startswith(b"%PDF"))
        self.assertEqual(content["Cache-Control"], "no-store")
        self.assertEqual(content["Pragma"], "no-cache")
        audit = AuditLog.objects.get(action="portal.document.downloaded")
        self.assertEqual(audit.actor_user, self.portal_user)
        self.assertEqual(audit.new_value_json["portal_account_id"], str(self.portal_account.pk))
        self.assertEqual(audit.new_value_json["member_id"], str(self.application.member_id))
        self.assertEqual(audit.new_value_json["loan_application_id"], str(self.application.pk))
        self.assertEqual(audit.new_value_json["action_code"], "term_sheet")
        self.assertEqual(audit.new_value_json["document_id"], str(output.pk))
        self.assertEqual(audit.new_value_json["document_version"], "1.0")
        self.assertEqual(audit.new_value_json["document_category"], "legal")
        self.assertEqual(audit.new_value_json["sensitivity_level"], "confidential")
        self.assertEqual(
            audit.new_value_json["reason"], "borrower_portal_published_document"
        )
        self.assertEqual(audit.new_value_json["network"]["ip_address"], "127.0.0.1")
        self.assertTrue(audit.new_value_json["capability_verified"])
        self.assertEqual(audit.new_value_json["request_id"], "portal-download-1")
        self.assertNotIn("storage_key", str(audit.new_value_json).lower())
        self.assertNotIn("checksum", str(audit.new_value_json).lower())
        self.assertFalse(
            AuditLog.objects.filter(action="documents.file.downloaded").exists()
        )
        denied = self.client.get(
            f"{self._collection_url()}poa/download/",
            headers=self._portal_auth(),
        )
        self.assertEqual(denied.status_code, 404)
        self.assertEqual(
            AuditLog.objects.filter(action="portal.document.downloaded").count(), 1
        )
    def test_signed_download_capability_expires_and_cannot_cross_current_document_or_action(self):
        _output, term_sheet = self._generated_document(
            "term_sheet", b"term sheet v1", "term-sheet-v1.pdf"
        )
        action_url = self._action(
            self.client.get(
                self._collection_url(), headers=self._portal_auth()
            ).json()["data"],
            "term_sheet",
        )["download"]["action_url"]
        descriptor = self.client.get(
            action_url, headers=self._portal_auth()
        ).json()["data"]

        with patch("django.core.signing.time.time", return_value=9_999_999_999):
            expired = self.client.get(
                descriptor["download_url"], headers=self._portal_auth()
            )
        self.assertEqual(expired.status_code, 404, expired.content)

        fresh = self.client.get(action_url, headers=self._portal_auth()).json()["data"]
        _replacement_output, replacement = self._generated_document(
            "term_sheet", b"term sheet v2", "term-sheet-v2.pdf", template_version="2.0"
        )
        replaced = self.client.get(
            fresh["download_url"], headers=self._portal_auth()
        )
        self.assertEqual(replaced.status_code, 404, replaced.content)

        LoanDocument.objects.filter(pk=replacement.pk).update(
            execution_status="executed"
        )
        _agreement_output, agreement = self._generated_document(
            "loan_agreement", b"loan agreement", "loan-agreement.pdf"
        )
        cross_action = self.client.get(
            fresh["download_url"].replace(
                "/term_sheet/download/", "/loan_agreement/download/"
            ),
            headers=self._portal_auth(),
        )
        self.assertEqual(cross_action.status_code, 404, cross_action.content)
        self.assertFalse(AuditLog.objects.filter(action="portal.document.downloaded").exists())
    def test_stale_status_only_completion_cannot_be_reopened_by_portal_upload(self):
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
        self.assertFalse(projected["upload_allowed"])
        self.assertFalse(projected["reupload_allowed"])
        document_count = DocumentFile.objects.count()
        generic_upload_audit_count = AuditLog.objects.filter(
            action="documents.file.uploaded"
        ).count()
        portal_upload_audit_count = AuditLog.objects.filter(
            action="portal.document.uploaded"
        ).count()
        crafted = self.client.post(
            f"{self._collection_url()}cancelled_cheque/upload/",
            data={"file": self._pdf("crafted.pdf", b"%PDF crafted")},
            headers=self._portal_auth(),
        )
        self.assertEqual(crafted.status_code, 409, crafted.content)
        self.assertEqual(DocumentFile.objects.count(), document_count)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.file.uploaded").count(),
            generic_upload_audit_count,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="portal.document.uploaded").count(),
            portal_upload_audit_count,
        )
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
            action="portal.document.uploaded").count(), len(allowed))
        self.assertFalse(
            AuditLog.objects.filter(action="documents.file.uploaded").exists()
        )
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
    def _generated_document(self, code, content, file_name, *, template_version="1.0"):
        del content, file_name
        for permission_code in (
            "documents.loan_document.generate",
            "documents.template.file_reference",
        ):
            permission, _ = Permission.objects.get_or_create(
                permission_code=permission_code,
                defaults={
                    "permission_name": permission_code,
                    "module_name": "documents",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(
                role=self.fixture.actor.primary_role, permission=permission
            )
        storage = LocalDocumentStorage()
        source_bytes = test_loan_document_generation_api.LoanDocumentGenerationApiTests._genuine_docx_fixture([])
        stored = storage.store(ContentFile(source_bytes, name=f"{code}-template.docx"))
        source = DocumentFile.objects.create(
            file_name=f"{code}-template.docx",
            file_extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=self.fixture.actor,
            sensitivity_level="internal",
        )
        AuditLog.objects.create(
            actor_user=self.fixture.actor,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=source.pk,
            new_value_json={
                "document_id": str(source.pk),
                "file_name": source.file_name,
                "file_extension": source.file_extension,
                "mime_type": source.mime_type,
                "file_size_bytes": source.file_size_bytes,
                "storage_provider": source.storage_provider,
                "storage_key": source.storage_key,
                "checksum_sha256": source.checksum_sha256,
                "sensitivity_level": source.sensitivity_level,
                "document_category": "template_source",
                "related_entity_type": "global",
                "related_entity_id": None,
            },
        )
        template = DocumentTemplate.objects.create(
            template_code=f"portal-{code}-v{template_version}", template_name=f"Portal {code}",
            document_type=code, borrower_type="individual_farmer", template_version=template_version,
            template_file=source, merge_fields_json=[], approval_status="approved",
            effective_from=timezone.localdate())
        generated = document_generation.generate(
            actor=self.fixture.actor,
            application_id=self.application.pk,
            payload={
                "document_type": code,
                "template_id": str(template.pk),
                "output_format": "pdf",
            },
            metadata=document_generation.RequestMetadata(
                request_id=f"portal-{code}-{template_version}",
                ip_address="127.0.0.1",
                user_agent="portal-test",
            ),
            storage=storage,
        )
        document = LoanDocument.objects.select_related("document").get(
            pk=generated["loan_document_id"]
        )
        return document.document, document
    @staticmethod
    def _pdf(name, content):
        return SimpleUploadedFile(name, content, content_type="application/pdf")
    @staticmethod
    def _action(data, code):
        return next(action for action in data["actions"] if action["action_code"] == code)


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative portal completion/upload race requires PostgreSQL row locks.",
)
class PortalDocumentationActionConcurrencyTests(TransactionTestCase):
    reset_sequences = True
    setUp = PortalDocumentationActionsApiTests.setUp
    _generated_document = PortalDocumentationActionsApiTests._generated_document
    _pdf = staticmethod(PortalDocumentationActionsApiTests._pdf)
    _action = staticmethod(PortalDocumentationActionsApiTests._action)

    def test_completion_and_upload_serialize_to_one_coherent_projection(self):
        permission, _ = Permission.objects.get_or_create(
            permission_code="documents.checklist.update",
            defaults={
                "permission_name": "Update document checklist",
                "module_name": "documents",
                "risk_level": Permission.RISK_HIGH,
            },
        )
        RolePermission.objects.get_or_create(
            role=self.fixture.actor.primary_role, permission=permission
        )
        _output, term_sheet = self._generated_document(
            "term_sheet", b"unused", "unused.pdf"
        )
        for party_type, party_id in (
            ("borrower", self.application.member_id),
            ("nominee", self.application.nominee_id),
            ("user", self.fixture.cfo.pk),
        ):
            SignatureRecord.objects.create(
                loan_document=term_sheet,
                signer_party_type=party_type,
                signer_party_id=party_id,
                signer_name_snapshot=party_type,
                signature_method="wet_ink",
                signature_status="signed",
                signature_mismatch_flag=False,
                signed_at=timezone.now(),
                captured_by_user=self.fixture.actor,
            )
        item = self.checklist.items.get(item_code="term_sheet")
        barrier = Barrier(2)
        baseline = {
            "documents": DocumentFile.objects.count(),
            "submissions": apps.get_model(
                "legal_documents", "PortalDocumentationSubmission"
            ).objects.count(),
            "portal_audits": AuditLog.objects.filter(
                action="portal.document.uploaded"
            ).count(),
        }

        def complete():
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.fixture.actor.pk)
                barrier.wait(timeout=10)
                document_checklist_actions.complete_item(
                    actor=actor,
                    checklist_item_id=item.pk,
                    payload={
                        "loan_document_id": str(term_sheet.pk),
                        "remarks": "Concurrent verified Term Sheet.",
                    },
                    metadata=RequestMetadata(
                        request_id="portal-race-complete",
                        ip_address="127.0.0.1",
                        user_agent="portal-race",
                    ),
                )
                return "completed"
            finally:
                connections["default"].close()

        def upload():
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.portal_user.pk)
                request = RequestFactory().post(
                    "/portal-race-upload/",
                    data={"file": self._pdf("signed-term-sheet.pdf", b"%PDF race")},
                    HTTP_X_REQUEST_ID="portal-race-upload",
                )
                barrier.wait(timeout=10)
                try:
                    portal_documentation_actions.upload(
                        actor=actor,
                        application_id=self.application.pk,
                        action_code="term_sheet",
                        request=request,
                    )
                    return "uploaded"
                except portal_documentation_actions.PortalDocumentationUnavailable:
                    return "denied"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(complete), pool.submit(upload)]
            results = {future.result(timeout=30) for future in futures}

        self.assertIn("completed", results)
        item.refresh_from_db()
        self.assertEqual(item.completion_status, "complete")
        projection = portal_documentation_actions.get_projection(
            actor=User.objects.get(pk=self.portal_user.pk),
            application_id=self.application.pk,
        )
        projected = self._action(projection, "term_sheet")
        self.assertEqual(projected["status"], "complete")
        self.assertFalse(projected["upload_allowed"])
        self.assertFalse(projected["reupload_allowed"])
        submission_count = apps.get_model(
            "legal_documents", "PortalDocumentationSubmission"
        ).objects.count()
        if "denied" in results:
            self.assertEqual(DocumentFile.objects.count(), baseline["documents"])
            self.assertEqual(submission_count, baseline["submissions"])
            self.assertEqual(
                AuditLog.objects.filter(action="portal.document.uploaded").count(),
                baseline["portal_audits"],
            )
        else:
            self.assertEqual(submission_count, baseline["submissions"] + 1)
            self.assertEqual(
                AuditLog.objects.filter(action="portal.document.uploaded").count(),
                baseline["portal_audits"] + 1,
            )

    def test_generation_and_old_capability_read_serialize_at_application_lock(self):
        _output, original = self._generated_document(
            "term_sheet", b"unused", "unused.pdf"
        )
        storage = LocalDocumentStorage()
        source_bytes = (
            test_loan_document_generation_api.LoanDocumentGenerationApiTests
            ._genuine_docx_fixture([])
        )
        stored = storage.store(ContentFile(source_bytes, name="term-sheet-v2-template.docx"))
        source = DocumentFile.objects.create(
            file_name="term-sheet-v2-template.docx",
            file_extension=".docx",
            mime_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=self.fixture.actor,
            sensitivity_level="internal",
        )
        AuditLog.objects.create(
            actor_user=self.fixture.actor,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=source.pk,
            new_value_json={
                "document_id": str(source.pk),
                "file_name": source.file_name,
                "file_extension": source.file_extension,
                "mime_type": source.mime_type,
                "file_size_bytes": source.file_size_bytes,
                "storage_provider": source.storage_provider,
                "storage_key": source.storage_key,
                "checksum_sha256": source.checksum_sha256,
                "sensitivity_level": source.sensitivity_level,
                "document_category": "template_source",
                "related_entity_type": "global",
                "related_entity_id": None,
            },
        )
        template = DocumentTemplate.objects.create(
            template_code="portal-term-sheet-race-v2",
            template_name="Portal Term Sheet race v2",
            document_type="term_sheet",
            borrower_type="individual_farmer",
            template_version="2.0",
            template_file=source,
            merge_fields_json=[],
            approval_status="approved",
            effective_from=timezone.localdate(),
        )
        scope = {
            "portal_account_id": str(self.portal_account.pk),
            "member_id": str(self.application.member_id),
            "loan_application_id": str(self.application.pk),
            "action_code": "term_sheet",
            "loan_document_id": str(original.pk),
        }
        capability = document_services.issue_download_capability(
            document=original.document, scope=scope
        )
        barrier = Barrier(2)
        baseline_audits = AuditLog.objects.filter(
            action="portal.document.downloaded"
        ).count()

        def generate_successor():
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.fixture.actor.pk)
                barrier.wait(timeout=10)
                result = document_generation.generate(
                    actor=actor,
                    application_id=self.application.pk,
                    payload={
                        "document_type": "term_sheet",
                        "template_id": str(template.pk),
                        "output_format": "pdf",
                    },
                    metadata=document_generation.RequestMetadata(
                        request_id="portal-generation-race",
                        ip_address="127.0.0.1",
                        user_agent="portal-race",
                    ),
                    storage=LocalDocumentStorage(),
                )
                return result["loan_document_id"]
            finally:
                connections["default"].close()

        def read_original():
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.portal_user.pk)
                request = RequestFactory().get(
                    "/portal-race-download/",
                    data={"content": "1", "token": capability["token"]},
                    HTTP_X_REQUEST_ID="portal-read-race",
                )
                barrier.wait(timeout=10)
                try:
                    portal_documentation_actions.download(
                        actor=actor,
                        application_id=self.application.pk,
                        action_code="term_sheet",
                        request=request,
                        storage=LocalDocumentStorage(),
                    )
                    return "served_original"
                except portal_documentation_actions.PortalDocumentationNotFound:
                    return "denied_original"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            generation_future = pool.submit(generate_successor)
            read_future = pool.submit(read_original)
            successor_id = generation_future.result(timeout=30)
            read_result = read_future.result(timeout=30)

        projection = portal_documentation_actions.get_projection(
            actor=User.objects.get(pk=self.portal_user.pk),
            application_id=self.application.pk,
        )
        self.assertEqual(
            self._action(projection, "term_sheet")["download"]["file_name"],
            LoanDocument.objects.get(pk=successor_id).document.file_name,
        )
        expected_audits = baseline_audits + (read_result == "served_original")
        self.assertEqual(
            AuditLog.objects.filter(action="portal.document.downloaded").count(),
            expected_audits,
        )
        stale_request = RequestFactory().get(
            "/portal-stale-download/",
            data={"content": "1", "token": capability["token"]},
        )
        with self.assertRaises(portal_documentation_actions.PortalDocumentationNotFound):
            portal_documentation_actions.download(
                actor=User.objects.get(pk=self.portal_user.pk),
                application_id=self.application.pk,
                action_code="term_sheet",
                request=stale_request,
                storage=LocalDocumentStorage(),
            )
        self.assertEqual(
            AuditLog.objects.filter(action="portal.document.downloaded").count(),
            expected_audits,
        )
