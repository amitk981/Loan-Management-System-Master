import ast
from pathlib import Path
from django.apps import apps
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.test import SimpleTestCase, TransactionTestCase
class SecurityInstrumentBoundaryTests(SimpleTestCase):
    def test_security_app_owns_retained_tables_and_policy(self):
        package = apps.get_model("security_instruments", "SecurityPackage")
        poa = apps.get_model("security_instruments", "PowerOfAttorney")
        self.assertEqual(package._meta.db_table, "security_packages")
        self.assertEqual(poa._meta.db_table, "power_of_attorneys")
        with self.assertRaises(LookupError):
            apps.get_model("legal_documents", "SecurityPackage")
        from sfpcl_credit.security_instruments.modules import security_package
        self.assertEqual(
            security_package.read_package.__module__,
            "sfpcl_credit.security_instruments.modules.security_package",
        )

    def test_legal_documents_has_no_reverse_security_policy_dependency(self):
        root = Path(__file__).parents[1] / "legal_documents"
        offenders = []
        for path in root.rglob("*.py"):
            imports = []
            for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
            if any(name.startswith("sfpcl_credit.security_instruments") for name in imports):
                offenders.append(str(path.relative_to(root)))
        self.assertEqual(offenders, [])
class SecurityInstrumentOwnershipMigrationTests(TransactionTestCase):
    def test_state_only_transfer_preserves_retained_table_identities(self):
        executor = MigrationExecutor(connection)
        executor.migrate([
            ("legal_documents", "0010_stage4_maker_checker_constraints"),
            ("security_instruments", None),
        ])
        before = set(connection.introspection.table_names())
        executor = MigrationExecutor(connection)
        executor.migrate([("security_instruments", "0001_transfer_security_ownership")])
        after = set(connection.introspection.table_names())
        self.assertEqual(after, before)
        state = executor.loader.project_state([
            ("security_instruments", "0001_transfer_security_ownership")
        ]).apps
        package = state.get_model("security_instruments", "SecurityPackage")
        poa = state.get_model("security_instruments", "PowerOfAttorney")
        self.assertEqual(package._meta.db_table, "security_packages")
        self.assertEqual(poa._meta.db_table, "power_of_attorneys")
        self.assertIn("activation_evidence_json", {field.name for field in poa._meta.fields})

    def tearDown(self):
        MigrationExecutor(connection).migrate(
            MigrationExecutor(connection).loader.graph.leaf_nodes()
        )
        super().tearDown()
