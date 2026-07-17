import ast
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.test import SimpleTestCase, TransactionTestCase
from django.utils import timezone


class SapRuntimeModelOwnershipTests(SimpleTestCase):
    def test_sap_workflow_owns_models_without_changing_physical_identity(self):
        from sfpcl_credit.finance.models import (
            SapCustomerCode as LegacySapCustomerCode,
            SapCustomerProfileRequest as LegacySapCustomerProfileRequest,
        )
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.sap_workflow.models import (
            SapCustomerCode,
            SapCustomerProfileRequest,
        )

        self.assertIs(LegacySapCustomerCode, SapCustomerCode)
        self.assertIs(LegacySapCustomerProfileRequest, SapCustomerProfileRequest)
        self.assertEqual(SapCustomerCode._meta.app_label, "sap_workflow")
        self.assertEqual(SapCustomerProfileRequest._meta.app_label, "sap_workflow")
        self.assertEqual(SapCustomerCode._meta.db_table, "sap_customer_codes")
        self.assertEqual(
            SapCustomerProfileRequest._meta.db_table,
            "sap_customer_profile_requests",
        )
        self.assertEqual(
            {constraint.name for constraint in SapCustomerCode._meta.constraints},
            {
                "uniq_active_sap_code_member",
                "sap_customer_code_status_valid",
                "sap_customer_code_not_blank",
                "uniq_sap_customer_code_ci",
            },
        )
        self.assertEqual(
            {constraint.name for constraint in SapCustomerProfileRequest._meta.constraints},
            {
                "uniq_active_sap_request_app",
                "sap_request_status_valid",
                "sap_request_amount_positive",
                "sap_request_lifecycle_evidence",
            },
        )
        self.assertIs(
            LoanAccount._meta.get_field("sap_customer_code").remote_field.model,
            SapCustomerCode,
        )

    def test_legacy_model_module_is_a_policy_free_compatibility_import(self):
        finance_models = Path(__file__).parents[1] / "finance" / "models.py"
        module = ast.parse(finance_models.read_text())

        self.assertFalse(
            [node for node in module.body if isinstance(
                node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            )]
        )
        imported_modules = {
            node.module for node in module.body if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(imported_modules, {"sfpcl_credit.sap_workflow.models"})

    def test_fresh_migration_graph_resolves_one_state_only_owner_transfer(self):
        loader = MigrationLoader(None)
        target = ("sap_workflow", "0001_sap_model_owner_state")
        migration = loader.disk_migrations[target]

        self.assertEqual(migration.dependencies, [("loans", "0001_initial")])
        self.assertEqual(loader.graph.forwards_plan(target).count(target), 1)
        self.assertEqual(len(migration.operations), 1)
        self.assertFalse(migration.operations[0].reduces_to_sql)
        apps = loader.project_state([target]).apps
        self.assertEqual(
            apps.get_model("sap_workflow", "SapCustomerCode")._meta.db_table,
            "sap_customer_codes",
        )
        self.assertEqual(
            apps.get_model("sap_workflow", "SapCustomerProfileRequest")._meta.db_table,
            "sap_customer_profile_requests",
        )


class SapModelOwnershipMigrationTests(TransactionTestCase):
    migrate_from = [("sap_workflow", None)]
    migrate_to = [("sap_workflow", "0001_sap_model_owner_state")]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        old_targets = [
            node for node in self.executor.loader.graph.leaf_nodes()
            if node[0] not in {"sap_workflow", "disbursements"}
        ]
        self.old_apps = self.executor.loader.project_state(old_targets).apps
        self.identifiers = self._create_finance_owned_rows(self.old_apps)
        self.before_manifest = self._manifest(self.old_apps, "finance")

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_forward_and_reverse_transfer_preserve_exact_business_state(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        moved_apps = self.executor.loader.project_state(
            self.executor.loader.graph.leaf_nodes()
        ).apps

        with self.assertRaises(LookupError):
            moved_apps.get_model("finance", "SapCustomerCode")
        with self.assertRaises(LookupError):
            moved_apps.get_model("finance", "SapCustomerProfileRequest")
        self.assertEqual(self._manifest(moved_apps, "sap_workflow"), self.before_manifest)
        self.assertEqual(
            moved_apps.get_model("loans", "LoanAccount")
            ._meta.get_field("sap_customer_code").remote_field.model._meta.app_label,
            "sap_workflow",
        )

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        reversed_targets = [
            node for node in self.executor.loader.graph.leaf_nodes()
            if node[0] not in {"sap_workflow", "disbursements"}
        ]
        reversed_apps = self.executor.loader.project_state(reversed_targets).apps
        with self.assertRaises(LookupError):
            reversed_apps.get_model("sap_workflow", "SapCustomerCode")
        self.assertEqual(self._manifest(reversed_apps, "finance"), self.before_manifest)
        self.assertEqual(
            reversed_apps.get_model("loans", "LoanAccount")
            ._meta.get_field("sap_customer_code").remote_field.model._meta.app_label,
            "finance",
        )

    def _manifest(self, apps, owner):
        Request = apps.get_model(owner, "SapCustomerProfileRequest")
        Code = apps.get_model(owner, "SapCustomerCode")
        AuditLog = apps.get_model("identity", "AuditLog")
        WorkflowEvent = apps.get_model("workflows", "WorkflowEvent")
        request = Request.objects.get(pk=self.identifiers["request_id"])
        code = Code.objects.get(pk=self.identifiers["code_id"])
        audit = AuditLog.objects.get(pk=self.identifiers["audit_id"])
        workflow = WorkflowEvent.objects.get(pk=self.identifiers["workflow_id"])
        tables = set(connection.introspection.table_names())
        with connection.cursor() as cursor:
            physical_constraints = {
                table: connection.introspection.get_constraints(cursor, table)
                for table in ("sap_customer_profile_requests", "sap_customer_codes")
            }
        return {
            "request_count": Request.objects.count(),
            "code_count": Code.objects.count(),
            "request_table": Request._meta.db_table,
            "code_table": Code._meta.db_table,
            "physical_tables": tuple(sorted(
                tables & {"sap_customer_profile_requests", "sap_customer_codes"}
            )),
            "physical_constraints_and_indexes": physical_constraints,
            "request": {
                "id": request.pk,
                "application_id": request.loan_application_id,
                "member_id": request.member_id,
                "requester_id": request.requested_by_user_id,
                "assignee_id": request.assigned_to_user_id,
                "file_id": request.excel_file_id,
                "communication_id": request.sent_communication_id,
                "task_id": request.sent_task_id,
                "code_id": request.sap_customer_code_id,
                "aadhaar_ciphertext": request.aadhaar_number_encrypted,
                "pan_ciphertext": request.pan_number_encrypted,
                "workbook_checksum": request.excel_file.checksum_sha256,
                "delivery_checksum": request.delivery_checksum_sha256,
                "completion_digest": request.completion_input_digest,
                "delivery_reference": request.delivery_reference,
                "status": request.request_status,
                "sent_at": request.sent_at,
                "completed_at": request.completed_at,
            },
            "code": {
                "id": code.pk,
                "member_id": code.member_id,
                "application_id": code.created_for_loan_application_id,
                "creator_id": code.created_by_user_id,
                "customer_code": code.sap_customer_code,
                "vendor_code": code.sap_vendor_code,
                "status": code.status,
            },
            "audit": (audit.entity_id, audit.action, audit.actor_user_id),
            "workflow": (
                workflow.entity_id, workflow.workflow_name,
                workflow.to_state, workflow.triggered_by_user_id,
            ),
        }

    def _create_finance_owned_rows(self, apps):
        Role = apps.get_model("identity", "Role")
        User = apps.get_model("identity", "User")
        Member = apps.get_model("members", "Member")
        LoanApplication = apps.get_model("applications", "LoanApplication")
        DocumentFile = apps.get_model("documents", "DocumentFile")
        Communication = apps.get_model("communications", "Communication")
        Notification = apps.get_model("communications", "Notification")
        Request = apps.get_model("finance", "SapCustomerProfileRequest")
        Code = apps.get_model("finance", "SapCustomerCode")
        AuditLog = apps.get_model("identity", "AuditLog")
        WorkflowEvent = apps.get_model("workflows", "WorkflowEvent")

        role = Role.objects.create(
            role_code="sap_migration_owner",
            role_name="SAP Migration Owner",
        )
        requester = User.objects.create(
            full_name="Migration Requester",
            email="sap-migration-requester@sfpcl.example",
            primary_role=role,
            password_hash="not-a-real-password",
        )
        assignee = User.objects.create(
            full_name="Migration Assignee",
            email="sap-migration-assignee@sfpcl.example",
            primary_role=role,
            password_hash="not-a-real-password",
        )
        member = Member.objects.create(
            member_number="MEM-SAP-MIGRATION",
            member_type="individual_farmer",
            legal_name="Synthetic Migration Member",
            display_name="Synthetic Migration Member",
            folio_number="FOL-SAP-MIGRATION",
            membership_status="active",
            pan_encrypted="ciphertext-pan-before-transfer",
            pan_hash="synthetic-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        application = LoanApplication.objects.create(
            member=member,
            borrower_type="individual_farmer",
            received_by_user=requester,
        )
        workbook = DocumentFile.objects.create(
            file_name="synthetic-annexure.xlsx",
            file_extension="xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            file_size_bytes=321,
            storage_provider="migration-proof",
            storage_key="synthetic/encrypted/token",
            checksum_sha256="w" * 64,
            uploaded_by_user=requester,
            sensitivity_level="restricted",
        )
        request_id = uuid4()
        communication = Communication.objects.create(
            related_entity_type="sap_customer_profile_request",
            related_entity_id=request_id,
            recipient_party_type="user",
            recipient_party_id=assignee.pk,
            channel="email",
            subject_snapshot="Synthetic SAP transfer proof",
            body_snapshot="No personal data",
            sent_by_user=requester,
            sent_at=timezone.now(),
            delivery_status="pending",
        )
        task = Notification.objects.create(
            communication=communication,
            notification_type="sap_customer_profile_request",
            category="task",
            severity="info",
            title="Synthetic SAP migration task",
            related_entity_type="sap_customer_profile_request",
            related_entity_id=request_id,
            sender_user=requester,
            recipient_user=assignee,
        )
        code = Code.objects.create(
            member=member,
            sap_customer_code="SYNTHETIC-SAP-001",
            sap_vendor_code="SYNTHETIC-VENDOR-001",
            created_for_loan_application=application,
            created_by_user=assignee,
            created_at_sap=timezone.now(),
            confirmation_notes="Synthetic migration evidence",
            status="active",
        )
        sent_at = timezone.now()
        request = Request.objects.create(
            sap_customer_profile_request_id=request_id,
            loan_application=application,
            member=member,
            request_status="completed",
            requested_by_user=requester,
            assigned_to_user=assignee,
            farmer_full_name="Synthetic Migration Member",
            borrower_type="individual_farmer",
            folio_number="FOL-SAP-MIGRATION",
            aadhaar_number_encrypted="ciphertext-aadhaar-before-transfer",
            pan_number_encrypted="ciphertext-pan-before-transfer",
            address_text="Synthetic address",
            email_id="synthetic-member@sfpcl.example",
            mobile_number="0000000000",
            loan_application_number="APP-SAP-MIGRATION",
            sanctioned_amount=Decimal("12345.67"),
            sanction_date=date(2026, 7, 16),
            bank_account_last4="0000",
            ifsc="SYNTH000001",
            excel_file=workbook,
            sent_remarks="Synthetic migration proof",
            sent_communication=communication,
            sent_task=task,
            delivery_reference="manual:sap-transfer-proof",
            delivery_checksum_sha256="d" * 64,
            delivery_file_id_snapshot=workbook.pk,
            delivery_assignee_id_snapshot=assignee.pk,
            delivery_capability_version=7,
            delivery_capability_expires_at=timezone.now(),
            delivery_capability_consumed_at=timezone.now(),
            sap_customer_code=code,
            completion_reused_existing_code=False,
            completion_input_digest="c" * 64,
            sent_at=sent_at,
            completed_at=timezone.now(),
        )
        audit = AuditLog.objects.create(
            actor_user=assignee,
            action="sap.customer_code_created",
            entity_type="sap_customer_profile_request",
            entity_id=request.pk,
        )
        workflow = WorkflowEvent.objects.create(
            workflow_name="SAPCustomerCodeCompleted",
            entity_type="sap_customer_profile_request",
            entity_id=request.pk,
            from_state="sent",
            to_state="completed",
            triggered_by_user=assignee,
        )
        return {
            "request_id": request.pk,
            "code_id": code.pk,
            "audit_id": audit.pk,
            "workflow_id": workflow.pk,
        }
