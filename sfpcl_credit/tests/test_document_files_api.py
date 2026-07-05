import hashlib
import tempfile
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from sfpcl_credit.documents.models import DocumentFile
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
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _auth_headers(self, **kwargs):
        return {"Authorization": f"Bearer {self._access_token(**kwargs)}"}

    def _sample_file(self, name="borrower-pan.pdf", content=b"sample-pan-bytes"):
        return SimpleUploadedFile(name, content, content_type="application/pdf")

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
