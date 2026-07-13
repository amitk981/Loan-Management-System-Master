import hashlib
import tempfile
import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.utils.dateparse import parse_datetime

from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    User,
)
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope


DOCUMENT_UPLOAD_URL = "/api/v1/document-files/"
DOCUMENT_UPLOAD_PERMISSION = "documents.file.upload"
DOCUMENT_DOWNLOAD_PERMISSION = "documents.file.download"
DOCUMENT_RESPONSE_FIELDS = {
    "document_id",
    "file_name",
    "mime_type",
    "file_size_bytes",
    "sensitivity_level",
    "uploaded_at",
}


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-doc-tests-"))
class DocumentFilesApiTests(TestCase):
    """003C: generic document-file metadata and local storage adapter."""

    def setUp(self):
        self.client = Client()
        self.upload_role = Role.objects.create(
            role_code="document_uploader",
            role_name="Document Uploader",
            is_system_role=True,
            status="active",
        )
        upload_permission = Permission.objects.create(
            permission_code=DOCUMENT_UPLOAD_PERMISSION,
            permission_name="Upload files",
            module_name="documents",
            risk_level="high",
        )
        RolePermission.objects.create(role=self.upload_role, permission=upload_permission)
        self.uploader = User.objects.create(
            full_name="Uma Uploader",
            email="uploader@sfpcl.example",
            status="active",
            primary_role=self.upload_role,
        )
        self.uploader.set_password("UploaderPass123!")
        self.uploader.save()

        self.download_role = Role.objects.create(
            role_code="document_downloader",
            role_name="Document Downloader",
            is_system_role=True,
            status="active",
        )
        download_permission = Permission.objects.create(
            permission_code=DOCUMENT_DOWNLOAD_PERMISSION,
            permission_name="Download files",
            module_name="documents",
            risk_level="critical",
        )
        RolePermission.objects.create(
            role=self.download_role, permission=download_permission
        )
        self.downloader = User.objects.create(
            full_name="Dina Downloader",
            email="downloader@sfpcl.example",
            status="active",
            primary_role=self.download_role,
        )
        self.downloader.set_password("DownloaderPass123!")
        self.downloader.save()

        self.plain_role = Role.objects.create(
            role_code="plain_staff",
            role_name="Plain Staff",
            is_system_role=True,
            status="active",
        )
        self.plain_user = User.objects.create(
            full_name="Paul Plain",
            email="plain@sfpcl.example",
            status="active",
            primary_role=self.plain_role,
        )
        self.plain_user.set_password("PlainPass123!")
        self.plain_user.save()

    def _access_token(self, email="uploader@sfpcl.example", password="UploaderPass123!"):
        tokens = self._tokens(email=email, password=password)
        return tokens["access_token"]

    def _tokens(self, email="uploader@sfpcl.example", password="UploaderPass123!"):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]

    def _auth_headers(self, **kwargs):
        return {"Authorization": f"Bearer {self._access_token(**kwargs)}"}

    def _sample_file(self, name="borrower-pan.pdf", content=b"sample-pan-bytes"):
        return SimpleUploadedFile(name, content, content_type="application/pdf")

    def _document(self, **overrides):
        defaults = {
            "file_name": "board-approval.pdf",
            "file_extension": ".pdf",
            "mime_type": "application/pdf",
            "file_size_bytes": 128,
            "storage_provider": "local",
            "storage_key": "document-files/test/board-approval.pdf",
            "checksum_sha256": "abc123",
            "uploaded_by_user": self.uploader,
            "sensitivity_level": "restricted",
        }
        defaults.update(overrides)
        return DocumentFile.objects.create(**defaults)

    def _download_url(self, document):
        return f"/api/v1/document-files/{document.document_id}/download/"

    def test_authenticated_upload_stores_file_metadata_checksum_and_audit(self):
        file_bytes = b"borrower-pan-upload"
        related_entity_id = uuid.uuid4()

        response = self.client.post(
            DOCUMENT_UPLOAD_URL,
            data={
                "file": self._sample_file(content=file_bytes),
                "document_category": "kyc",
                "sensitivity_level": "restricted",
                "related_entity_type": "member",
                "related_entity_id": str(related_entity_id),
            },
            headers={**self._auth_headers(), "X-Request-ID": "req-doc-upload"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-doc-upload")
        self.assertEqual(set(payload["data"].keys()), DOCUMENT_RESPONSE_FIELDS)

        data = payload["data"]
        self.assertEqual(data["file_name"], "borrower-pan.pdf")
        self.assertEqual(data["mime_type"], "application/pdf")
        self.assertEqual(data["file_size_bytes"], len(file_bytes))
        self.assertEqual(data["sensitivity_level"], "restricted")

        document = DocumentFile.objects.get(document_id=data["document_id"])
        self.assertEqual(document.file_name, "borrower-pan.pdf")
        self.assertEqual(document.file_extension, ".pdf")
        self.assertEqual(document.mime_type, "application/pdf")
        self.assertEqual(document.file_size_bytes, len(file_bytes))
        self.assertEqual(document.storage_provider, "local")
        self.assertTrue(document.storage_key)
        self.assertEqual(document.uploaded_by_user, self.uploader)
        self.assertEqual(document.sensitivity_level, "restricted")
        self.assertEqual(document.checksum_sha256, hashlib.sha256(file_bytes).hexdigest())

        stored_path = Path(settings.DOCUMENT_STORAGE_ROOT) / document.storage_key
        self.assertTrue(stored_path.exists())
        self.assertEqual(stored_path.read_bytes(), file_bytes)

        audit = AuditLog.objects.get(action="documents.file.uploaded")
        self.assertEqual(audit.actor_user, self.uploader)
        self.assertEqual(audit.entity_type, "document_file")
        self.assertEqual(audit.entity_id, document.document_id)
        self.assertEqual(audit.new_value_json["document_id"], str(document.document_id))
        self.assertEqual(audit.new_value_json["file_name"], "borrower-pan.pdf")
        self.assertEqual(audit.new_value_json["storage_provider"], "local")
        self.assertNotIn("file", audit.new_value_json)
        self.assertNotIn("file_bytes", audit.new_value_json)

    def test_exception_reference_boundary_enforces_provenance_scope_and_access_without_writes(self):
        self.upload_role.role_code = "credit_manager"
        self.upload_role.save(update_fields=["role_code"])
        download_permission = Permission.objects.get(
            permission_code=DOCUMENT_DOWNLOAD_PERMISSION
        )
        RolePermission.objects.create(
            role=self.upload_role, permission=download_permission
        )
        application_id = uuid.uuid4()

        def upload(name="support.pdf", category="legal"):
            response = self.client.post(
                DOCUMENT_UPLOAD_URL,
                data={
                    "file": self._sample_file(name=name),
                    "document_category": category,
                    "sensitivity_level": "restricted",
                    "related_entity_type": "application",
                    "related_entity_id": str(application_id),
                },
                headers=self._auth_headers(),
            )
            self.assertEqual(response.status_code, 200, response.content)
            return response.json()["data"]["document_id"]

        def resolve(
            document_id,
            *,
            permissions=None,
            related_id=application_id,
            related_access=True,
            role_codes=frozenset({"credit_manager"}),
        ):
            document_id = uuid.UUID(str(document_id))
            return document_services.resolve_referenceable_documents(
                actor_permissions=(
                    {DOCUMENT_DOWNLOAD_PERMISSION}
                    if permissions is None
                    else permissions
                ),
                document_ids_by_field={"supporting_document_ids.0": document_id},
                context=document_services.DocumentReferenceContext(
                    related_entity_type="application",
                    related_entity_id=related_id,
                    related_entity_access_allowed=related_access,
                    workflow_scope=document_services.EXCEPTION_WORKFLOW_SCOPE,
                    actor_role_codes=role_codes,
                    actor_is_related_case_approver=False,
                ),
                purpose=document_services.EXCEPTION_REFERENCE_PURPOSE,
            )

        valid_id = upload()
        before = list(AuditLog.objects.order_by("audit_log_id").values())
        resolved = resolve(valid_id)
        self.assertEqual(
            str(resolved["supporting_document_ids.0"].document_id), valid_id
        )
        self.assertEqual(list(AuditLog.objects.order_by("audit_log_id").values()), before)

        finance_id = upload(name="finance.pdf", category="finance")
        denied_cases = (
            lambda: resolve(valid_id, related_id=uuid.uuid4()),
            lambda: resolve(finance_id),
            lambda: resolve(valid_id, permissions=set()),
            lambda: resolve(valid_id, related_access=False),
            lambda: resolve(valid_id, role_codes=frozenset({"plain_staff"})),
        )
        for denied in denied_cases:
            ledger = list(AuditLog.objects.order_by("audit_log_id").values())
            with self.assertRaises(ValidationError) as error:
                denied()
            self.assertIn("not found or is inaccessible", str(error.exception))
            self.assertEqual(
                list(AuditLog.objects.order_by("audit_log_id").values()), ledger
            )

        document = DocumentFile.objects.get(pk=valid_id)
        document.sensitivity_level = "internal"
        document.save(update_fields=["sensitivity_level"])
        ledger = list(AuditLog.objects.order_by("audit_log_id").values())
        with self.assertRaises(ValidationError):
            resolve(valid_id)
        self.assertEqual(list(AuditLog.objects.order_by("audit_log_id").values()), ledger)

    def test_sensitivity_level_is_case_normalized(self):
        response = self.client.post(
            DOCUMENT_UPLOAD_URL,
            data={
                "file": self._sample_file(name="credit-note.txt", content=b"note"),
                "document_category": "finance",
                "sensitivity_level": "Confidential",
            },
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["sensitivity_level"], "confidential")
        self.assertEqual(DocumentFile.objects.get().sensitivity_level, "confidential")

    def test_missing_required_fields_return_validation_errors_without_writes(self):
        response = self.client.post(
            DOCUMENT_UPLOAD_URL,
            data={"related_entity_type": "member"},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("file", payload["error"]["field_errors"])
        self.assertIn("document_category", payload["error"]["field_errors"])
        self.assertIn("sensitivity_level", payload["error"]["field_errors"])
        self.assertEqual(DocumentFile.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="documents.file.uploaded").count(), 0)

    def test_authorized_download_returns_time_limited_descriptor(self):
        document = self._document()
        before = AuditLog.objects.filter(action="documents.file.downloaded").count()

        response = self.client.get(
            self._download_url(document),
            headers={
                **self._auth_headers(
                    email="downloader@sfpcl.example",
                    password="DownloaderPass123!",
                ),
                "X-Request-ID": "req-doc-download",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-doc-download")
        self.assertEqual(set(payload["data"].keys()), {"download_url", "expires_at"})
        self.assertIn(str(document.document_id), payload["data"]["download_url"])
        self.assertNotIn(document.storage_key, payload["data"]["download_url"])
        self.assertNotIn("checksum", payload["data"]["download_url"])
        self.assertIsNotNone(parse_datetime(payload["data"]["expires_at"]))

        self.assertEqual(
            AuditLog.objects.filter(action="documents.file.downloaded").count(),
            before + 1,
        )
        audit = AuditLog.objects.get(action="documents.file.downloaded")
        self.assertEqual(audit.actor_user, self.downloader)
        self.assertEqual(audit.entity_type, "document_file")
        self.assertEqual(audit.entity_id, document.document_id)
        self.assertEqual(audit.new_value_json["file_name"], "board-approval.pdf")
        self.assertEqual(audit.new_value_json["sensitivity_level"], "restricted")
        self.assertEqual(audit.new_value_json["storage_provider"], "local")
        self.assertNotIn("storage_key", audit.new_value_json)
        self.assertNotIn("checksum_sha256", audit.new_value_json)

    def test_download_response_never_exposes_storage_metadata_or_raw_bytes(self):
        document = self._document(storage_key="document-files/secret/private.pdf")

        response = self.client.get(
            self._download_url(document),
            headers=self._auth_headers(
                email="downloader@sfpcl.example",
                password="DownloaderPass123!",
            ),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(set(data.keys()), {"download_url", "expires_at"})
        serialized = str(data)
        self.assertNotIn("storage_key", serialized)
        self.assertNotIn(document.storage_key, serialized)
        self.assertNotIn("checksum_sha256", serialized)
        self.assertNotIn("abc123", serialized)
        self.assertNotIn("raw", serialized)

    def test_actor_without_download_permission_is_forbidden_and_not_audited(self):
        document = self._document()

        response = self.client.get(
            self._download_url(document),
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, response.json(), "PERMISSION_DENIED")
        self.assertEqual(AuditLog.objects.filter(action="documents.file.downloaded").count(), 0)

    def test_unknown_document_download_returns_404_without_audit_or_metadata(self):
        missing_id = uuid.uuid4()

        response = self.client.get(
            f"/api/v1/document-files/{missing_id}/download/",
            headers=self._auth_headers(
                email="downloader@sfpcl.example",
                password="DownloaderPass123!",
            ),
        )

        self.assertEqual(response.status_code, 404)
        payload = response.json()
        assert_error_envelope(self, payload, "NOT_FOUND")
        self.assertNotIn("storage", str(payload).lower())
        self.assertNotIn("file_name", str(payload))
        self.assertEqual(AuditLog.objects.filter(action="documents.file.downloaded").count(), 0)

    def test_unauthenticated_download_returns_auth_required_without_audit(self):
        document = self._document()

        response = self.client.get(self._download_url(document))

        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "AUTH_REQUIRED")
        self.assertEqual(AuditLog.objects.filter(action="documents.file.downloaded").count(), 0)

    def test_malformed_download_bearer_returns_invalid_token_without_audit(self):
        document = self._document()

        response = self.client.get(
            self._download_url(document),
            headers={"Authorization": "Bearer"},
        )

        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "INVALID_TOKEN")
        self.assertEqual(AuditLog.objects.filter(action="documents.file.downloaded").count(), 0)

    def test_revoked_download_token_returns_invalid_token_without_audit(self):
        document = self._document()
        tokens = self._tokens(
            email="downloader@sfpcl.example",
            password="DownloaderPass123!",
        )
        logout_response = self.client.post(
            "/api/v1/auth/logout/",
            data={"refresh_token": tokens["refresh_token"]},
            content_type="application/json",
        )
        self.assertEqual(logout_response.status_code, 200)

        response = self.client.get(
            self._download_url(document),
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "INVALID_TOKEN")
        self.assertEqual(AuditLog.objects.filter(action="documents.file.downloaded").count(), 0)

    def test_invalid_sensitivity_and_related_entity_id_return_validation_errors(self):
        response = self.client.post(
            DOCUMENT_UPLOAD_URL,
            data={
                "file": self._sample_file(),
                "document_category": "kyc",
                "sensitivity_level": "secret",
                "related_entity_id": "not-a-uuid",
            },
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("sensitivity_level", payload["error"]["field_errors"])
        self.assertIn("related_entity_id", payload["error"]["field_errors"])
        self.assertEqual(DocumentFile.objects.count(), 0)

    def test_unauthenticated_upload_returns_401_before_writes(self):
        response = self.client.post(
            DOCUMENT_UPLOAD_URL,
            data={
                "file": self._sample_file(),
                "document_category": "kyc",
                "sensitivity_level": "restricted",
            },
        )

        self.assertEqual(response.status_code, 401)
        assert_error_envelope(self, response.json(), "AUTH_REQUIRED")
        self.assertEqual(DocumentFile.objects.count(), 0)

    def test_actor_without_upload_permission_is_forbidden_before_writes(self):
        response = self.client.post(
            DOCUMENT_UPLOAD_URL,
            data={
                "file": self._sample_file(),
                "document_category": "kyc",
                "sensitivity_level": "restricted",
            },
            headers=self._auth_headers(email="plain@sfpcl.example", password="PlainPass123!"),
        )

        self.assertEqual(response.status_code, 403)
        assert_error_envelope(self, response.json(), "PERMISSION_DENIED")
        self.assertEqual(DocumentFile.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="documents.file.uploaded").count(), 0)
