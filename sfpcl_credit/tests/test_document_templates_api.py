import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest import skipUnless

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import close_old_connections, connection
from django.test import Client, TestCase, TransactionTestCase, override_settings

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.modules import document_templates
from sfpcl_credit.documents.models import (
    DocumentFile,
    DocumentTemplate,
    DocumentTemplateIdentity,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.tests.api_contracts import assert_success_envelope


DOCUMENT_TEMPLATE_URL = "/api/v1/document-templates/"
DOCUMENT_UPLOAD_URL = "/api/v1/document-files/"


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-template-doc-tests-"))
class DocumentTemplateApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = self._user_with_permission(
            "template_manager", "documents.template.manage"
        )
        self.reader = self._user_with_permission(
            "template_reader", "documents.template.read"
        )
        self.plain = self._user_with_permission("plain_staff", "unrelated.permission")

    def _user_with_permission(self, role_code, permission_code):
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_code.replace("_", " ").title(),
            is_system_role=True,
            status="active",
        )
        permission, _ = Permission.objects.get_or_create(
            permission_code=permission_code,
            defaults={
                "permission_name": permission_code,
                "module_name": "documents",
                "risk_level": "critical",
            },
        )
        RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=role.role_name,
            email=f"{role_code}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password("TemplatePass123!")
        user.save(update_fields=["password_hash"])
        return user

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "TemplatePass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"}

    def _grant_permission(self, user, permission_code):
        permission, _ = Permission.objects.get_or_create(
            permission_code=permission_code,
            defaults={
                "permission_name": permission_code,
                "module_name": "documents",
                "risk_level": "critical",
            },
        )
        RolePermission.objects.get_or_create(
            role=user.primary_role,
            permission=permission,
        )

    def _payload(self, **overrides):
        payload = {
            "template_code": "annexure_e_term_sheet_v1",
            "template_name": "Term Sheet",
            "document_type": "term_sheet",
            "borrower_type": "individual_farmer",
            "template_version": "1.0",
            "template_file_id": None,
            "merge_fields": ["borrower_name", "loan_amount"],
            "approval_status": "approved",
            "effective_from": "2026-01-01",
            "effective_to": "2026-06-30",
        }
        payload.update(overrides)
        return payload

    def _template_source_file(self, *, metadata_overrides=None, **file_overrides):
        values = {
            "file_name": "term-sheet.docx",
            "file_extension": ".docx",
            "mime_type": (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            "file_size_bytes": 100,
            "storage_provider": "local",
            "storage_key": "document-files/test/term-sheet.docx",
            "checksum_sha256": "template-checksum",
            "uploaded_by_user": self.manager,
            "sensitivity_level": "internal",
        }
        values.update(file_overrides)
        document = DocumentFile.objects.create(**values)
        metadata = {
            "document_id": str(document.document_id),
            "file_name": document.file_name,
            "file_extension": document.file_extension,
            "mime_type": document.mime_type,
            "file_size_bytes": document.file_size_bytes,
            "storage_provider": document.storage_provider,
            "storage_key": document.storage_key,
            "checksum_sha256": document.checksum_sha256,
            "sensitivity_level": document.sensitivity_level,
            "document_category": "template_source",
            "related_entity_type": "global",
            "related_entity_id": None,
        }
        metadata.update(metadata_overrides or {})
        AuditLog.objects.create(
            actor_user=document.uploaded_by_user,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=document.document_id,
            new_value_json=metadata,
        )
        return document

    def test_manager_creates_and_supersedes_template_while_reader_lists_history(self):
        created = self.client.post(
            DOCUMENT_TEMPLATE_URL,
            self._payload(),
            content_type="application/json",
            **self._auth(self.manager),
        )

        self.assertEqual(created.status_code, 200, created.content)
        created_body = created.json()
        assert_success_envelope(self, created_body)
        original = created_body["data"]
        self.assertEqual(original["template_version"], "1.0")
        self.assertNotIn("download_url", original)
        self.assertNotIn("available_actions", original)

        successor = self.client.patch(
            f"{DOCUMENT_TEMPLATE_URL}{original['document_template_id']}/",
            self._payload(
                template_code="annexure_e_term_sheet_v2",
                template_version="2.0",
                effective_from="2026-07-01",
                effective_to=None,
            ),
            content_type="application/json",
            **self._auth(self.manager),
        )

        self.assertEqual(successor.status_code, 200, successor.content)
        successor_data = successor.json()["data"]
        self.assertNotEqual(
            successor_data["document_template_id"], original["document_template_id"]
        )
        self.assertEqual(successor_data["template_version"], "2.0")

        listed = self.client.get(DOCUMENT_TEMPLATE_URL, **self._auth(self.reader))

        self.assertEqual(listed.status_code, 200, listed.content)
        listed_body = listed.json()
        assert_success_envelope(self, listed_body)
        self.assertEqual(listed_body["pagination"]["total_count"], 2)
        self.assertEqual(
            {row["template_version"] for row in listed_body["data"]}, {"1.0", "2.0"}
        )

    def test_globally_provenanced_template_upload_is_referenceable_without_download(self):
        self._grant_permission(self.manager, "documents.file.upload")
        self._grant_permission(self.manager, "documents.template.file_reference")

        uploaded = self.client.post(
            DOCUMENT_UPLOAD_URL,
            data={
                "file": SimpleUploadedFile(
                    "term-sheet.docx",
                    b"template-source-bytes",
                    content_type=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                ),
                "document_category": "template_source",
                "sensitivity_level": "internal",
                "related_entity_type": "global",
            },
            **self._auth(self.manager),
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.content)
        document_id = uploaded.json()["data"]["document_id"]

        created = self.client.post(
            DOCUMENT_TEMPLATE_URL,
            self._payload(template_file_id=document_id),
            content_type="application/json",
            **self._auth(self.manager),
        )

        self.assertEqual(created.status_code, 200, created.content)
        data = created.json()["data"]
        self.assertEqual(data["template_file_id"], document_id)
        self.assertEqual(data["template_file_name"], "term-sheet.docx")
        self.assertNotIn("download_url", data)
        self.assertNotIn("storage_key", data)
        self.assertNotIn(
            "documents.file.download",
            Permission.objects.filter(
                role_permissions__role=self.manager.primary_role
            ).values_list("permission_code", flat=True),
        )

    def test_invalid_template_file_provenance_is_indistinguishable_and_zero_write(self):
        self._grant_permission(self.manager, "documents.template.file_reference")
        direct_row = DocumentFile.objects.create(
            file_name="direct.docx",
            storage_provider="local",
            storage_key="direct.docx",
            sensitivity_level="internal",
        )
        corrupt_ledger = self._template_source_file(
            metadata_overrides={"checksum_sha256": "different-checksum"}
        )
        application_owned = self._template_source_file(
            metadata_overrides={
                "document_category": "legal",
                "related_entity_type": "application",
                "related_entity_id": str(uuid.uuid4()),
            }
        )
        loan_owned = self._template_source_file(
            metadata_overrides={
                "related_entity_type": "loan",
                "related_entity_id": str(uuid.uuid4()),
            }
        )
        unsupported_sensitivity = self._template_source_file(
            sensitivity_level="secret"
        )
        duplicate_ledger = self._template_source_file()
        duplicate_audit = AuditLog.objects.get(
            action="documents.file.uploaded",
            entity_id=duplicate_ledger.document_id,
        )
        AuditLog.objects.create(
            actor_user=duplicate_ledger.uploaded_by_user,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=duplicate_ledger.document_id,
            new_value_json=duplicate_audit.new_value_json,
        )
        baseline = (
            DocumentTemplate.objects.count(),
            AuditLog.objects.filter(action__startswith="documents.template.").count(),
            VersionHistory.objects.count(),
        )

        denied_ids = (
            uuid.uuid4(),
            direct_row.document_id,
            corrupt_ledger.document_id,
            application_owned.document_id,
            loan_owned.document_id,
            unsupported_sensitivity.document_id,
            duplicate_ledger.document_id,
        )
        responses = []
        for file_id in denied_ids:
            with self.subTest(file_id=file_id):
                response = self.client.post(
                    DOCUMENT_TEMPLATE_URL,
                    self._payload(template_file_id=str(file_id)),
                    content_type="application/json",
                    **self._auth(self.manager),
                )
                self.assertEqual(response.status_code, 400, response.content)
                responses.append(response.json()["error"])
                self.assertEqual(
                    (
                        DocumentTemplate.objects.count(),
                        AuditLog.objects.filter(
                            action__startswith="documents.template."
                        ).count(),
                        VersionHistory.objects.count(),
                    ),
                    baseline,
                )
        self.assertTrue(
            all(error == responses[0] for error in responses),
            responses,
        )

    def test_permissions_filters_and_bounded_pagination_are_explicit(self):
        for index, (borrower_type, status) in enumerate(
            (("individual_farmer", "draft"), ("fpc", "retired"), (None, "draft")),
            start=1,
        ):
            response = self.client.post(
                DOCUMENT_TEMPLATE_URL,
                self._payload(
                    template_code=f"catalogue_{index}_v1",
                    document_type=f"catalogue_{index}",
                    borrower_type=borrower_type,
                    approval_status=status,
                ),
                content_type="application/json",
                **self._auth(self.manager),
            )
            self.assertEqual(response.status_code, 200, response.content)

        filtered = self.client.get(
            f"{DOCUMENT_TEMPLATE_URL}?borrower_type=fpc&approval_status=retired&page_size=500",
            **self._auth(self.reader),
        )
        self.assertEqual(filtered.status_code, 200, filtered.content)
        self.assertEqual(filtered.json()["pagination"]["page_size"], 100)
        self.assertEqual(len(filtered.json()["data"]), 1)
        self.assertEqual(filtered.json()["data"][0]["borrower_type"], "fpc")

        nullable = self.client.get(
            f"{DOCUMENT_TEMPLATE_URL}?borrower_type=null", **self._auth(self.reader)
        )
        self.assertEqual(nullable.status_code, 200, nullable.content)
        self.assertEqual(len(nullable.json()["data"]), 1)
        self.assertIsNone(nullable.json()["data"][0]["borrower_type"])

        unknown = self.client.get(
            f"{DOCUMENT_TEMPLATE_URL}?ordering=template_code", **self._auth(self.reader)
        )
        self.assertEqual(unknown.status_code, 400, unknown.content)
        self.assertIn("ordering", unknown.json()["error"]["field_errors"])

        self.assertEqual(
            self.client.get(DOCUMENT_TEMPLATE_URL, **self._auth(self.manager)).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(DOCUMENT_TEMPLATE_URL, **self._auth(self.plain)).status_code,
            403,
        )
        self.assertEqual(self.client.get(DOCUMENT_TEMPLATE_URL).status_code, 401)

    def test_borrower_template_variant_resolver_fails_unresolved_mappings_closed(self):
        self.assertEqual(
            document_templates.resolve_borrower_template_variant("individual_farmer"),
            "individual_farmer",
        )
        for member_type in ("fpc", "producer_institution", "unknown"):
            with self.subTest(member_type=member_type):
                with self.assertRaisesMessage(
                    ValidationError,
                    "Template borrower variant mapping requires configuration.",
                ):
                    document_templates.resolve_borrower_template_variant(member_type)

    def test_validation_conflicts_and_exact_replay_preserve_one_evidence_set(self):
        first = self.client.post(
            DOCUMENT_TEMPLATE_URL,
            self._payload(),
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-template-create",
            **self._auth(self.manager),
        )
        replay = self.client.post(
            DOCUMENT_TEMPLATE_URL,
            self._payload(),
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-template-replay",
            **self._auth(self.manager),
        )
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(
            first.json()["data"]["document_template_id"],
            replay.json()["data"]["document_template_id"],
        )
        self.assertEqual(DocumentTemplate.objects.count(), 1)
        self.assertEqual(DocumentTemplateIdentity.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.template.created").count(), 1
        )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="document_template"
            ).count(),
            1,
        )

        invalid_payloads = (
            self._payload(template_code="duplicate-code", template_version="1.0"),
            self._payload(
                template_code="overlap-v2",
                template_version="2.0",
                effective_from="2026-06-30",
                effective_to="2026-12-31",
            ),
            self._payload(
                template_code="invalid-date",
                document_type="invalid_date",
                template_version="1.0",
                effective_to="2025-12-31",
            ),
            self._payload(
                template_code="invalid-status",
                document_type="invalid_status",
                template_version="1.0",
                approval_status="active",
            ),
            self._payload(
                template_code="invalid-fields",
                document_type="invalid_fields",
                template_version="1.0",
                merge_fields=["borrower_name", " borrower_name "],
            ),
        )
        for payload in invalid_payloads:
            with self.subTest(template_code=payload["template_code"]):
                before = (
                    DocumentTemplate.objects.count(),
                    AuditLog.objects.filter(
                        action__startswith="documents.template."
                    ).count(),
                    VersionHistory.objects.filter(
                        versioned_entity_type="document_template"
                    ).count(),
                )
                response = self.client.post(
                    DOCUMENT_TEMPLATE_URL,
                    payload,
                    content_type="application/json",
                    **self._auth(self.manager),
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(
                    (
                        DocumentTemplate.objects.count(),
                        AuditLog.objects.filter(
                            action__startswith="documents.template."
                        ).count(),
                        VersionHistory.objects.filter(
                            versioned_entity_type="document_template"
                        ).count(),
                    ),
                    before,
                )

    def test_successor_replay_retains_predecessor_and_attributable_history(self):
        created = self.client.post(
            DOCUMENT_TEMPLATE_URL,
            self._payload(),
            content_type="application/json",
            **self._auth(self.manager),
        )
        original_data = created.json()["data"]
        successor_payload = self._payload(
            template_code="annexure_e_term_sheet_v2",
            template_version="2.0",
            effective_from="2026-07-01",
            effective_to=None,
        )
        url = f"{DOCUMENT_TEMPLATE_URL}{original_data['document_template_id']}/"
        first = self.client.patch(
            url,
            successor_payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-template-successor",
            **self._auth(self.manager),
        )
        replay = self.client.patch(
            url,
            successor_payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-template-successor-replay",
            **self._auth(self.manager),
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])
        original = DocumentTemplate.objects.get(pk=original_data["document_template_id"])
        self.assertEqual(original.template_version, "1.0")
        self.assertEqual(original.effective_to.isoformat(), "2026-06-30")
        successor = DocumentTemplate.objects.get(supersedes=original)
        self.assertEqual(successor.template_version, "2.0")
        self.assertEqual(DocumentTemplate.objects.count(), 2)

        audit = AuditLog.objects.get(action="documents.template.successor_created")
        self.assertEqual(audit.actor_user, self.manager)
        self.assertEqual(audit.old_value_json["template_version"], "1.0")
        self.assertEqual(audit.new_value_json["template_version"], "2.0")
        self.assertEqual(audit.new_value_json["request_id"], "req-template-successor")
        history = VersionHistory.objects.get(
            versioned_entity_type="document_template",
            versioned_entity_id=successor.pk,
        )
        self.assertEqual(history.author_user, self.manager)
        self.assertEqual(history.old_value_json["template_version"], "1.0")
        self.assertEqual(history.new_value_json["template_version"], "2.0")

        reader_patch = self.client.patch(
            url,
            successor_payload,
            content_type="application/json",
            **self._auth(self.reader),
        )
        self.assertEqual(reader_patch.status_code, 403, reader_patch.content)

    def test_manage_download_and_reference_authorities_remain_separate(self):
        download_permission = Permission.objects.get_or_create(
            permission_code="documents.file.download",
            defaults={
                "permission_name": "Download files",
                "module_name": "documents",
                "risk_level": "critical",
            },
        )[0]
        RolePermission.objects.create(
            role=self.manager.primary_role, permission=download_permission
        )
        template_file = DocumentFile.objects.create(
            file_name="loan-agreement.docx",
            file_extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=200,
            storage_provider="local",
            storage_key="document-files/test/loan-agreement.docx",
            uploaded_by_user=self.manager,
            sensitivity_level="restricted",
        )

        response = self.client.post(
            DOCUMENT_TEMPLATE_URL,
            self._payload(template_file_id=str(template_file.pk)),
            content_type="application/json",
            **self._auth(self.manager),
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(DocumentTemplate.objects.count(), 0)

        reference_only = self._user_with_permission(
            "template_reference_only", "documents.template.file_reference"
        )
        reference_response = self.client.post(
            DOCUMENT_TEMPLATE_URL,
            self._payload(template_file_id=str(template_file.pk)),
            content_type="application/json",
            **self._auth(reference_only),
        )
        self.assertEqual(reference_response.status_code, 403, reference_response.content)
        self.assertEqual(DocumentTemplate.objects.count(), 0)


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative document-template successor race requires PostgreSQL.",
)
class DocumentTemplateConcurrencyTests(TransactionTestCase):
    reset_sequences = True
    setUp = DocumentTemplateApiTests.setUp
    _user_with_permission = DocumentTemplateApiTests._user_with_permission
    _auth = DocumentTemplateApiTests._auth
    _payload = DocumentTemplateApiTests._payload

    def test_five_overlapping_first_versions_persist_one_winner_and_evidence_set(self):
        token_header = self._auth(self.manager)["HTTP_AUTHORIZATION"]

        def submit(index):
            close_old_connections()
            try:
                client = Client()
                response = client.post(
                    DOCUMENT_TEMPLATE_URL,
                    self._payload(
                        template_code=f"annexure_e_first_race_v{index}",
                        template_version=f"1.{index}",
                    ),
                    content_type="application/json",
                    HTTP_AUTHORIZATION=token_header,
                    HTTP_X_REQUEST_ID=f"req-template-first-race-{index}",
                )
                return response.status_code, response.json()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(submit, range(5)))

        statuses = [status for status, _ in results]
        self.assertEqual(statuses.count(200), 1, results)
        self.assertEqual(statuses.count(400), 4, results)
        self.assertEqual(DocumentTemplate.objects.count(), 1)
        self.assertEqual(DocumentTemplateIdentity.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.template.created").count(),
            1,
        )
        winner = DocumentTemplate.objects.get()
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="document_template",
                versioned_entity_id=winner.pk,
            ).count(),
            1,
        )

    def test_five_exact_successor_requests_persist_one_winner_and_evidence_set(self):
        created = self.client.post(
            DOCUMENT_TEMPLATE_URL,
            self._payload(),
            content_type="application/json",
            **self._auth(self.manager),
        )
        self.assertEqual(created.status_code, 200, created.content)
        original_id = created.json()["data"]["document_template_id"]
        token_header = self._auth(self.manager)["HTTP_AUTHORIZATION"]
        payload = self._payload(
            template_code="annexure_e_term_sheet_v2",
            template_version="2.0",
            effective_from="2026-07-01",
            effective_to=None,
        )

        def submit(index):
            close_old_connections()
            try:
                client = Client()
                response = client.patch(
                    f"{DOCUMENT_TEMPLATE_URL}{original_id}/",
                    payload,
                    content_type="application/json",
                    HTTP_AUTHORIZATION=token_header,
                    HTTP_X_REQUEST_ID=f"req-template-race-{index}",
                )
                return response.status_code, response.json()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(submit, range(5)))

        self.assertEqual([status for status, _ in results], [200] * 5)
        ids = {body["data"]["document_template_id"] for _, body in results}
        self.assertEqual(len(ids), 1)
        self.assertEqual(DocumentTemplate.objects.filter(supersedes_id=original_id).count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.template.successor_created").count(),
            1,
        )
        successor = DocumentTemplate.objects.get(supersedes_id=original_id)
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="document_template",
                versioned_entity_id=successor.pk,
            ).count(),
            1,
        )
