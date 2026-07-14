import ast
from pathlib import Path
from django.apps import apps
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.test import SimpleTestCase, TransactionTestCase
class SecurityInstrumentBoundaryTests(SimpleTestCase):
    def test_security_evidence_recorder_redacts_sensitive_values_recursively(self):
        from sfpcl_credit.security_instruments.modules.evidence_recorder import (
            redact_security_evidence,
        )

        redacted = redact_security_evidence(
            {
                "pledgor_bo_account": "1234567890123456",
                "nested": {"bank_account_number": "1234567890", "request_id": "req-1"},
                "already_masked": "************3456",
            }
        )
        self.assertEqual(redacted["pledgor_bo_account"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["bank_account_number"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["request_id"], "req-1")
        self.assertEqual(redacted["already_masked"], "************3456")

    def test_top_level_process_rejects_caller_supplied_evidence_authority(self):
        from sfpcl_credit.processes import security_instrument_evidence
        from sfpcl_credit.security_instruments.evidence_contract import (
            UncoordinatedEvidence,
        )

        with self.assertRaises(UncoordinatedEvidence):
            security_instrument_evidence.read_package(
                actor=None,
                application_id="00000000-0000-0000-0000-000000000000",
                evidence_access=object(),
            )

    def test_source_dependency_graph_uses_only_top_level_cross_owner_process(self):
        backend = Path(__file__).parents[1]
        forbidden = ("sfpcl_credit.approvals", "sfpcl_credit.legal_documents")
        offenders = []
        for path in (backend / "security_instruments").rglob("*.py"):
            if "migrations" in path.parts:
                continue
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    if name.startswith(forbidden):
                        offenders.append(f"{path.relative_to(backend)}:{node.lineno}:{name}")
        self.assertEqual(offenders, [])

        coordinator = backend / "processes" / "security_instrument_evidence.py"
        self.assertTrue(coordinator.exists())
        coordinator_source = coordinator.read_text()
        self.assertIn("sfpcl_credit.legal_documents", coordinator_source)
        self.assertIn("sfpcl_credit.security_instruments", coordinator_source)
        self.assertFalse(
            (backend / "legal_documents" / "modules" / "power_of_attorney.py").exists()
        )

    def test_security_app_owns_retained_tables_and_policy(self):
        package = apps.get_model("security_instruments", "SecurityPackage")
        poa = apps.get_model("security_instruments", "PowerOfAttorney")
        cdsl = apps.get_model("security_instruments", "CDSLSharePledge")
        self.assertEqual(package._meta.db_table, "security_packages")
        self.assertEqual(poa._meta.db_table, "power_of_attorneys")
        self.assertEqual(cdsl._meta.db_table, "cdsl_share_pledges")
        with self.assertRaises(LookupError):
            apps.get_model("legal_documents", "SecurityPackage")
        from sfpcl_credit.security_instruments.modules import security_package
        self.assertEqual(
            security_package.read_package.__module__,
            "sfpcl_credit.security_instruments.modules.security_package",
        )

    def test_security_app_is_the_real_power_of_attorney_policy_owner(self):
        from sfpcl_credit.security_instruments.modules import power_of_attorney

        self.assertEqual(
            power_of_attorney.create_poa.__module__,
            "sfpcl_credit.security_instruments.modules.power_of_attorney",
        )
        path = (
            Path(__file__).parents[1]
            / "security_instruments"
            / "modules"
            / "power_of_attorney.py"
        )
        tree = ast.parse(path.read_text(), filename=str(path))
        imported_modules = []
        defined_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined_names.add(node.name)
        self.assertFalse(
            any(
                name.startswith(
                    "sfpcl_credit.legal_documents.modules.power_of_attorney"
                )
                for name in imported_modules
            )
        )
        self.assertNotIn("bind_security_owner", defined_names)
        self.assertNotIn("__getattr__", defined_names)
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
