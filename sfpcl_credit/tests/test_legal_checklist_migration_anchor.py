from pathlib import Path

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.test import SimpleTestCase, TransactionTestCase

from sfpcl_credit.shared.migration_state_guard import (
    LEGAL_CHECKLIST_STATE_ALLOWLIST,
    legal_checklist_state_ownership_violations,
)


class LegalChecklistMigrationAnchorTests(SimpleTestCase):
    boundary = [
        ("applications", "0016_bankverificationdecision_and_more"),
        ("legal_documents", "0012_portal_documentation_submission"),
    ]
    anchored = [
        ("legal_documents", "0013_application_evidence_state_anchor"),
    ]

    def test_anchor_owns_cross_app_checklist_state_without_duplicate_columns(self):
        loader = MigrationLoader(None)
        before = loader.project_state(self.boundary)
        state = loader.project_state(self.anchored)
        before_action = before.apps.get_model("legal_documents", "ChecklistAction")
        action = state.apps.get_model("legal_documents", "ChecklistAction")

        self.assertIsNotNone(action._meta.get_field("audit_log"))
        self.assertIsNotNone(action._meta.get_field("version_history"))
        self.assertEqual(
            {field.name for field in action._meta.local_fields},
            {field.name for field in before_action._meta.local_fields},
        )
        parent_keys = {
            node.key
            for node in loader.graph.node_map[
                ("legal_documents", "0013_application_evidence_state_anchor")
            ].parents
        }
        self.assertIn(
            ("applications", "0016_bankverificationdecision_and_more"), parent_keys
        )

    def test_anchor_reverses_to_supported_boundary_without_schema_change(self):
        loader = MigrationLoader(None)
        migration = loader.disk_migrations[self.anchored[0]]

        self.assertEqual(migration.operations, [])
        self.assertEqual(
            migration.dependencies,
            [
                ("applications", "0016_bankverificationdecision_and_more"),
                ("legal_documents", "0012_portal_documentation_submission"),
            ],
        )


class LegalChecklistConstraintOwnerMigrationTests(TransactionTestCase):
    reset_sequences = True

    before_009g2 = [
        ("communications", "0003_notification"),
        ("disbursements", "0004_transfer_success"),
        ("legal_documents", "0014_staff_documentation_durable_actions"),
    ]
    current_dependencies = [
        ("communications", "0004_advice_outbox_and_receipt_owner"),
        (
            "disbursements",
            "0007_remove_disbursement_disb_success_evidence_complete_and_more",
        ),
        ("legal_documents", "0014_staff_documentation_durable_actions"),
    ]
    anchored = [
        ("legal_documents", "0015_checklist_constraint_state_owner_anchor"),
    ]
    live_constraints = {
        "checklist_finance_requires_sanction",
        "checklist_ready_evidence_complete",
    }
    retired_constraints = {
        "checklist_account_requires_epic_009",
        "checklist_finance_requires_epic_009",
    }

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_anchor_preserves_exact_state_schema_and_rows_through_reverse_reapply(self):
        before_apps = self._migrate(self.before_009g2)
        retained = self._create_retained_facts(before_apps)

        anchored_apps = self._migrate(self.anchored)
        anchored_manifest = self._manifest(anchored_apps, retained)
        self._assert_live_constraint_manifest(anchored_apps, anchored_manifest)

        reversed_apps = self._migrate(self.current_dependencies)
        reversed_manifest = self._manifest(reversed_apps, retained)
        self._assert_live_constraint_manifest(reversed_apps, reversed_manifest)
        self.assertEqual(reversed_manifest, anchored_manifest)

        reapplied_apps = self._migrate(self.anchored)
        reapplied_manifest = self._manifest(reapplied_apps, retained)
        self._assert_live_constraint_manifest(reapplied_apps, reapplied_manifest)
        self.assertEqual(reapplied_manifest, anchored_manifest)

    def test_anchor_is_legal_owned_zero_sql_and_anchors_all_reviewed_leaves(self):
        loader = MigrationLoader(None)
        target = self.anchored[0]
        migration = loader.disk_migrations[target]

        self.assertEqual(migration.operations, [])
        self.assertEqual(
            set(migration.dependencies),
            {
                ("communications", "0004_advice_outbox_and_receipt_owner"),
                (
                    "disbursements",
                    "0007_remove_disbursement_disb_success_evidence_complete_and_more",
                ),
                (
                    "disbursements",
                    "0005_disbursementadviceintent_loanregisterupdate_and_more",
                ),
                ("legal_documents", "0014_staff_documentation_durable_actions"),
            },
        )
        self.assertEqual(loader.graph.forwards_plan(target).count(target), 1)

    def _migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def _create_retained_facts(self, apps):
        Role = apps.get_model("identity", "Role")
        User = apps.get_model("identity", "User")
        Member = apps.get_model("members", "Member")
        LoanApplication = apps.get_model("applications", "LoanApplication")
        DocumentChecklist = apps.get_model("legal_documents", "DocumentChecklist")
        WorkflowEvent = apps.get_model("workflows", "WorkflowEvent")
        ChecklistAction = apps.get_model("legal_documents", "ChecklistAction")

        role = Role.objects.create(
            role_code="migration_guard_reviewer",
            role_name="Migration guard reviewer",
            description="Synthetic migration fixture role",
        )
        actor = User.objects.create(
            full_name="Migration Guard Reviewer",
            email="migration-guard@example.invalid",
            mobile_number="0000000000",
            approval_authority_type="none",
            password_hash="not-a-real-password",
            primary_role=role,
        )
        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Migration Fixture Member",
            display_name="Migration Fixture Member",
            folio_number="MIG-009G4",
            membership_status="active",
            pan_encrypted="synthetic-pan-token",
            pan_hash="synthetic-pan-hash",
            aadhaar_encrypted="synthetic-aadhaar-token",
            aadhaar_hash="synthetic-aadhaar-hash",
            registered_address_line1="Synthetic address",
            registered_address_line2="",
            registered_village_city="Synthetic village",
            registered_district="Synthetic district",
            registered_state="Synthetic state",
            registered_pincode="000000",
            mobile_number="0000000000",
            email="member-migration@example.invalid",
            kyc_status="verified",
            default_status="current",
            holding_mode="physical",
            active_member_status="active",
        )
        application = LoanApplication.objects.create(
            application_reference_number="MIG-009G4-APP",
            borrower_type="individual_farmer",
            declared_purpose="Synthetic migration fixture",
            purpose_category="crop_finance",
            loan_type_requested="short_term",
            borrower_request_notes="",
            member=member,
            received_by_user=actor,
        )
        checklist = DocumentChecklist.objects.create(
            loan_application=application,
            remarks="Retain this exact checklist fact",
        )
        workflow = WorkflowEvent.objects.create(
            workflow_name="document_checklist",
            entity_type="document_checklist",
            entity_id=checklist.pk,
            to_state="item_completed",
            trigger_reason="Synthetic retained migration fact",
            triggered_by_user=actor,
        )
        action = ChecklistAction.objects.create(
            document_checklist=checklist,
            action_type="company_secretary_approval",
            meaning="Synthetic retained checklist approval",
            comments="Retain this exact action fact",
            actor_user=actor,
            actor_user_name_snapshot=actor.full_name,
            canonical_role_code=role.role_code,
            request_id="migration-009g4-retained",
            workflow_event=workflow,
        )
        return {
            "checklist_id": checklist.pk,
            "action_id": action.pk,
        }

    def _manifest(self, apps, retained):
        DocumentChecklist = apps.get_model("legal_documents", "DocumentChecklist")
        ChecklistAction = apps.get_model("legal_documents", "ChecklistAction")
        checklist = DocumentChecklist.objects.values(
            "document_checklist_id",
            "loan_application_id",
            "checklist_status",
            "remarks",
        ).get(pk=retained["checklist_id"])
        action = ChecklistAction.objects.values(
            "checklist_action_id",
            "document_checklist_id",
            "action_type",
            "meaning",
            "comments",
            "actor_user_name_snapshot",
            "canonical_role_code",
            "request_id",
            "workflow_event_id",
        ).get(pk=retained["action_id"])
        with connection.cursor() as cursor:
            physical = connection.introspection.get_constraints(
                cursor, "document_checklists"
            )
        physical_schema = {
            name: {
                key: tuple(value) if isinstance(value, list) else value
                for key, value in details.items()
                if key
                in {
                    "columns",
                    "primary_key",
                    "unique",
                    "foreign_key",
                    "check",
                    "index",
                }
            }
            for name, details in physical.items()
        }
        return {
            "checklist": {key: str(value) for key, value in checklist.items()},
            "action": {key: str(value) for key, value in action.items()},
            "live_physical_constraint_counts": {
                name: int(name in physical) for name in self.live_constraints
            },
            "retired_physical_constraint_counts": {
                name: int(name in physical) for name in self.retired_constraints
            },
            "physical_schema": physical_schema,
        }

    def _assert_live_constraint_manifest(self, apps, manifest):
        DocumentChecklist = apps.get_model("legal_documents", "DocumentChecklist")
        state_names = [
            constraint.name for constraint in DocumentChecklist._meta.constraints
        ]
        for name in self.live_constraints:
            self.assertEqual(state_names.count(name), 1, state_names)
            self.assertEqual(manifest["live_physical_constraint_counts"][name], 1)
        for name in self.retired_constraints:
            self.assertEqual(state_names.count(name), 0, state_names)
            self.assertEqual(manifest["retired_physical_constraint_counts"][name], 0)


class LegalChecklistMigrationOwnershipGuardTests(SimpleTestCase):
    def test_guard_rejects_synthetic_cross_app_checklist_state_mutation(self):
        synthetic = {
            Path("future_app/migrations/0001_bad.py"): """
from django.db.migrations.operations.base import Operation

class BadChecklistMutation(Operation):
    def state_forwards(self, app_label, state):
        state.models[("legal_documents", "documentchecklist")].options.clear()
"""
        }

        self.assertEqual(
            legal_checklist_state_ownership_violations(sources=synthetic),
            ["future_app/migrations/0001_bad.py:BadChecklistMutation"],
        )

    def test_guard_allows_only_reviewed_009g2_history_in_repository(self):
        package_root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            LEGAL_CHECKLIST_STATE_ALLOWLIST,
            {
                "disbursements/migrations/"
                "0005_disbursementadviceintent_loanregisterupdate_and_more.py:"
                "AddLegalChecklistConstraint",
                "disbursements/migrations/"
                "0005_disbursementadviceintent_loanregisterupdate_and_more.py:"
                "RemoveLegalChecklistConstraint",
            },
        )
        self.assertEqual(
            legal_checklist_state_ownership_violations(package_root=package_root),
            [],
        )
