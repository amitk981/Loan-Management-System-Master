import importlib
import inspect
import subprocess
import sys
from datetime import date
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase
from django.test import TransactionTestCase

from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.legal_documents.modules import document_generation
from sfpcl_credit.workflows.models import WorkflowEvent


class LegalDocumentDependencyDirectionTests(TestCase):
    def test_legal_app_owns_public_module_and_retained_model(self):
        foundation_models = importlib.import_module("sfpcl_credit.documents.models")
        legal_models = importlib.import_module("sfpcl_credit.legal_documents.models")

        self.assertFalse(hasattr(foundation_models, "LoanDocument"))
        self.assertEqual(
            legal_models.LoanDocument._meta.app_label,
            "legal_documents",
        )
        self.assertEqual(
            legal_models.LoanDocument._meta.db_table,
            "loan_documents",
        )
        self.assertEqual(
            document_generation.generate.__module__,
            "sfpcl_credit.legal_documents.modules.document_generation",
        )

    def test_foundation_imports_without_business_owners_and_legal_module_has_no_transport(self):
        import_probe = """
import builtins
from django.conf import settings

real_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name.startswith(("sfpcl_credit.applications", "sfpcl_credit.approvals", "sfpcl_credit.legal_documents")):
        raise AssertionError(f"foundation import crossed business boundary: {name}")
    return real_import(name, *args, **kwargs)

builtins.__import__ = guarded_import
settings.configure(
    SECRET_KEY="dependency-probe",
    INSTALLED_APPS=[
        "sfpcl_credit.identity",
        "sfpcl_credit.configurations",
        "sfpcl_credit.documents",
    ],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
import django
django.setup()
import sfpcl_credit.documents.models
import sfpcl_credit.documents.selectors
import sfpcl_credit.documents.services
import sfpcl_credit.documents.storage
from sfpcl_credit.documents.modules import document_templates
"""
        venv_python = Path(sys.prefix) / "bin" / "python"
        completed = subprocess.run(
            [str(venv_python), "-c", import_probe],
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

        self.assertNotIn("request", inspect.signature(document_generation.generate).parameters)
        imported_modules = {
            value.__name__
            for value in vars(document_generation).values()
            if isinstance(value, ModuleType)
        }
        self.assertFalse(
            any(
                name.startswith("django.http") or name.endswith(".views")
                for name in imported_modules
            ),
            imported_modules,
        )


class LegalDocumentOwnershipMigrationTests(TransactionTestCase):
    reset_sequences = True

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_renderer_provenance_migration_preserves_retained_row_as_legacy(self):
        executor = MigrationExecutor(connection)
        executor.migrate([("legal_documents", "0002_document_checklists")])
        old_apps = executor.loader.project_state(
            [("legal_documents", "0002_document_checklists")]
        ).apps
        Role = old_apps.get_model("identity", "Role")
        User = old_apps.get_model("identity", "User")
        Member = old_apps.get_model("members", "Member")
        LoanApplication = old_apps.get_model("applications", "LoanApplication")
        DocumentFile = old_apps.get_model("documents", "DocumentFile")
        DocumentTemplate = old_apps.get_model("documents", "DocumentTemplate")
        OldLoanDocument = old_apps.get_model("legal_documents", "LoanDocument")
        role = Role.objects.create(
            role_code="migration_renderer", role_name="Migration renderer", status="active"
        )
        user = User.objects.create(
            full_name="Migration Renderer",
            email="migration-renderer@sfpcl.example",
            password_hash="not-a-real-password",
            primary_role=role,
        )
        member = Member.objects.create(
            member_number="MEM-MIGRATION-RENDERER",
            member_type="individual_farmer",
            legal_name="Migration Renderer Borrower",
            display_name="Migration Renderer Borrower",
            folio_number="FOL-MIGRATION-RENDERER",
            membership_status="active",
            pan_encrypted="synthetic",
            pan_hash="synthetic-renderer-pan",
            kyc_status="verified",
            default_status="no_default",
        )
        application = LoanApplication.objects.create(
            application_reference_number="LO-MIGRATION-RENDERER",
            borrower_type="individual_farmer",
            member=member,
            received_by_user=user,
        )
        source = DocumentFile.objects.create(
            file_name="renderer-template.docx",
            storage_provider="local",
            storage_key="renderer-template.docx",
            sensitivity_level="internal",
        )
        output = DocumentFile.objects.create(
            file_name="legacy-renderer-output.pdf",
            storage_provider="local",
            storage_key="legacy-renderer-output.pdf",
            checksum_sha256="c" * 64,
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code="migration_renderer_template_v1",
            template_name="Migration renderer template",
            document_type="term_sheet",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=source,
            merge_fields_json=[],
            approval_status="approved",
            effective_from=date(2026, 7, 1),
        )
        retained = OldLoanDocument.objects.create(
            loan_application=application,
            document_type="term_sheet",
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=output,
            output_format="pdf",
            generation_status="generated",
            execution_status="executed",
            verification_status="verified",
            stamp_status="adequate",
            notarisation_status="completed",
        )

        executor = MigrationExecutor(connection)
        executor.migrate([("legal_documents", "0003_loan_document_renderer_provenance")])
        new_apps = executor.loader.project_state(
            [("legal_documents", "0003_loan_document_renderer_provenance")]
        ).apps
        migrated = new_apps.get_model("legal_documents", "LoanDocument").objects.get(
            pk=retained.pk
        )

        self.assertEqual(migrated.loan_application_id, application.pk)
        self.assertEqual(migrated.document_template_id, template.pk)
        self.assertEqual(migrated.document_id, output.pk)
        self.assertEqual(migrated.execution_status, "executed")
        self.assertEqual(migrated.verification_status, "verified")
        self.assertIsNone(migrated.renderer_contract_version)
        self.assertIsNone(migrated.renderer_validated_document_id)
        self.assertIsNone(migrated.renderer_validated_checksum_sha256)

    def test_retained_row_survives_state_only_owner_transfer(self):
        executor = MigrationExecutor(connection)
        executor.migrate([("legal_documents", None)])
        old_apps = executor.loader.project_state(
            [("documents", "0004_loandocument")]
        ).apps

        Role = old_apps.get_model("identity", "Role")
        User = old_apps.get_model("identity", "User")
        Member = old_apps.get_model("members", "Member")
        LoanApplication = old_apps.get_model("applications", "LoanApplication")
        DocumentFile = old_apps.get_model("documents", "DocumentFile")
        DocumentTemplate = old_apps.get_model("documents", "DocumentTemplate")
        OldLoanDocument = old_apps.get_model("documents", "LoanDocument")

        role = Role.objects.create(
            role_code="migration_legal_owner", role_name="Migration legal owner", status="active"
        )
        user = User.objects.create(
            full_name="Migration Legal Owner",
            email="migration-legal-owner@sfpcl.example",
            password_hash="not-a-real-password", primary_role=role,
        )
        member = Member.objects.create(
            member_number="MEM-MIGRATION-LEGAL",
            member_type="individual_farmer",
            legal_name="Migration Borrower", display_name="Migration Borrower",
            folio_number="FOL-MIGRATION-LEGAL",
            membership_status="active",
            pan_encrypted="synthetic", pan_hash="synthetic-migration-pan",
            kyc_status="verified", default_status="no_default",
        )
        application = LoanApplication.objects.create(
            application_reference_number="LO-MIGRATION-LEGAL",
            borrower_type="individual_farmer",
            member=member, received_by_user=user,
        )
        source_file = DocumentFile.objects.create(
            file_name="migration-template.docx",
            storage_provider="local", storage_key="migration-template.docx",
            sensitivity_level="internal"
        )
        generated_file = DocumentFile.objects.create(
            file_name="migration-output.pdf",
            storage_provider="local", storage_key="migration-output.pdf",
            sensitivity_level="confidential"
        )
        template = DocumentTemplate.objects.create(
            template_code="migration_template_v1",
            template_name="Migration template", document_type="term_sheet",
            borrower_type="individual_farmer",
            template_version="1.0", template_file=source_file, merge_fields_json=[],
            approval_status="approved",
            effective_from=date(2026, 7, 1),
        )
        retained = OldLoanDocument.objects.create(
            loan_application=application, document_type="term_sheet",
            document_category="legal", party_required="borrower",
            document_template=template, document=generated_file, output_format="pdf",
            generation_status="generated",
            execution_status="pending", verification_status="pending",
        )

        executor = MigrationExecutor(connection)
        executor.migrate(
            [("legal_documents", "0001_transfer_loan_document_owner")]
        )
        new_apps = executor.loader.project_state(
            [("legal_documents", "0001_transfer_loan_document_owner")]
        ).apps
        NewLoanDocument = new_apps.get_model("legal_documents", "LoanDocument")
        migrated = NewLoanDocument.objects.get(pk=retained.pk)

        self.assertEqual(migrated.loan_application_id, application.pk)
        self.assertEqual(migrated.document_template_id, template.pk)
        self.assertEqual(migrated.document_id, generated_file.pk)
        self.assertIsNone(migrated.loan_account_id)


class LegalDocumentGenerationAuthorityTests(TestCase):
    def test_direct_generation_without_permission_reads_nothing_and_writes_nothing(self):
        actor = self._actor_with_permissions()

        with (
            patch.object(document_generation.application_facts, "resolve_for_generation") as application_read,
            patch.object(document_generation.approval_facts, "resolve_for_generation") as approval_read,
            patch.object(document_generation.document_templates, "resolve_borrower_template_variant") as variant_read,
            patch.object(document_generation.document_services, "resolve_template_source_reference") as file_read,
            patch.object(document_generation.LocalDocumentStorage, "store") as storage_write,
            self.assertRaises(document_generation.LegalDocumentAccessDenied) as denied,
        ):
            document_generation.generate(
                actor=actor,
                application_id="10000000-0000-0000-0000-000000000001",
                payload={},
                metadata=document_generation.RequestMetadata(
                    "req-direct-denied", "127.0.0.1", "test"
                ),
            )

        self.assertEqual(denied.exception.error_code, "FORBIDDEN")
        application_read.assert_not_called()
        approval_read.assert_not_called()
        variant_read.assert_not_called()
        file_read.assert_not_called()
        storage_write.assert_not_called()
        self._assert_zero_success_writes()

    def test_direct_generation_without_template_reference_permission_reads_nothing(self):
        actor = self._actor_with_permissions("documents.loan_document.generate")

        with (
            patch.object(document_generation.application_facts, "resolve_for_generation") as application_read,
            patch.object(document_generation.approval_facts, "resolve_for_generation") as approval_read,
            patch.object(document_generation.document_templates, "resolve_borrower_template_variant") as variant_read,
            patch.object(document_generation.document_services, "resolve_template_source_reference") as file_read,
            patch.object(document_generation.LocalDocumentStorage, "store") as storage_write,
            self.assertRaises(document_generation.LegalDocumentAccessDenied) as denied,
        ):
            document_generation.generate(
                actor=actor,
                application_id="10000000-0000-0000-0000-000000000001",
                payload={
                    "document_type": "term_sheet",
                    "template_id": "20000000-0000-0000-0000-000000000002",
                    "output_format": "pdf",
                },
                metadata=document_generation.RequestMetadata(None, "127.0.0.1", "test"),
            )

        self.assertEqual(denied.exception.error_code, "FORBIDDEN")
        application_read.assert_not_called()
        approval_read.assert_not_called()
        variant_read.assert_not_called()
        file_read.assert_not_called()
        storage_write.assert_not_called()
        self._assert_zero_success_writes()

    def test_direct_generation_with_inactive_actor_reads_nothing(self):
        actor = self._actor_with_permissions(
            "documents.loan_document.generate",
            "documents.template.file_reference",
        )
        actor.status = "suspended"
        actor.save(update_fields=["status"])

        with (
            patch.object(document_generation.application_facts, "resolve_for_generation") as application_read,
            patch.object(document_generation.approval_facts, "resolve_for_generation") as approval_read,
            patch.object(document_generation.document_templates, "resolve_borrower_template_variant") as variant_read,
            patch.object(document_generation.document_services, "resolve_template_source_reference") as file_read,
            patch.object(document_generation.LocalDocumentStorage, "store") as storage_write,
            self.assertRaises(document_generation.LegalDocumentAccessDenied) as denied,
        ):
            document_generation.generate(
                actor=actor,
                application_id="10000000-0000-0000-0000-000000000001",
                payload={
                    "document_type": "term_sheet",
                    "template_id": "20000000-0000-0000-0000-000000000002",
                    "output_format": "pdf",
                },
                metadata=document_generation.RequestMetadata(None, "127.0.0.1", "test"),
            )

        self.assertEqual(denied.exception.error_code, "FORBIDDEN")
        application_read.assert_not_called()
        approval_read.assert_not_called()
        variant_read.assert_not_called()
        file_read.assert_not_called()
        storage_write.assert_not_called()
        self._assert_zero_success_writes()

    def _assert_zero_success_writes(self):
        self.assertEqual(LoanDocument.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="documents.loan_document.generated").count(),
            0,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="loan_document_generation").count(),
            0,
        )

    def _actor_with_permissions(self, *permission_codes):
        role = Role.objects.create(
            role_code=f"legal_boundary_role_{Role.objects.count()}",
            role_name="Legal boundary test role",
            is_system_role=True,
            status="active",
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "documents",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.create(role=role, permission=permission)
        return User.objects.create(
            full_name="Legal Boundary Actor",
            email=f"legal-boundary-{User.objects.count()}@sfpcl.example",
            status="active",
            primary_role=role,
        )
