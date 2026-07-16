from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class LegalChecklistMigrationAnchorTests(TransactionTestCase):
    boundary = [
        ("applications", "0016_bankverificationdecision_and_more"),
        ("legal_documents", "0012_portal_documentation_submission"),
    ]
    anchored = [
        ("legal_documents", "0013_application_evidence_state_anchor"),
    ]

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_anchor_owns_cross_app_checklist_state_without_duplicate_columns(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.boundary)
        columns_before = self._checklist_action_columns()

        executor = MigrationExecutor(connection)
        executor.migrate(self.anchored)
        state = executor.loader.project_state(self.anchored)
        action = state.apps.get_model("legal_documents", "ChecklistAction")

        self.assertIsNotNone(action._meta.get_field("audit_log"))
        self.assertIsNotNone(action._meta.get_field("version_history"))
        self.assertEqual(self._checklist_action_columns(), columns_before)
        parent_keys = {
            node.key
            for node in executor.loader.graph.node_map[
                ("legal_documents", "0013_application_evidence_state_anchor")
            ].parents
        }
        self.assertIn(
            ("applications", "0016_bankverificationdecision_and_more"), parent_keys
        )

    def test_anchor_reverses_to_supported_boundary_without_schema_change(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.anchored)
        columns_before = self._checklist_action_columns()

        executor = MigrationExecutor(connection)
        executor.migrate(self.boundary)

        self.assertEqual(self._checklist_action_columns(), columns_before)

    @staticmethod
    def _checklist_action_columns():
        with connection.cursor() as cursor:
            return {
                column.name
                for column in connection.introspection.get_table_description(
                    cursor, "checklist_actions"
                )
            }
