import ast
import os
from pathlib import Path
import subprocess
import sys
from django.apps import apps
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.test import SimpleTestCase, TransactionTestCase
class SecurityInstrumentBoundaryTests(SimpleTestCase):
    def test_security_evidence_recorder_redacts_sensitive_values_recursively(self):
        from sfpcl_credit.legal_documents.modules import checklist_actions
        from sfpcl_credit.security_instruments.modules.evidence_recorder import (
            redact_security_evidence,
        )
        from sfpcl_credit.shared.masking import redact_sensitive_mapping

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
        self.assertIs(redact_security_evidence, redact_sensitive_mapping)
        self.assertIs(checklist_actions._redact, redact_sensitive_mapping)

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
        forged_calls = (
            (security_instrument_evidence.read_poa, {"security_package_id": "missing"}),
            (security_instrument_evidence.read_sh4, {"security_package_id": "missing"}),
            (security_instrument_evidence.read_pledge, {"security_package_id": "missing"}),
            (security_instrument_evidence.read_blank_cheque, {"security_package_id": "missing"}),
        )
        for function, kwargs in forged_calls:
            with self.subTest(function=function.__name__):
                with self.assertRaises(UncoordinatedEvidence):
                    function(actor=None, evidence_access=object(), **kwargs)

    def test_source_dependency_graph_uses_only_top_level_cross_owner_process(self):
        backend = Path(__file__).parents[1]
        forbidden = (
            "sfpcl_credit.approvals",
            "sfpcl_credit.documents",
            "sfpcl_credit.legal_documents",
        )
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

        reverse_offenders = []
        for owner in (backend / "legal_documents", backend / "approvals"):
            for path in owner.rglob("*.py"):
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
                        if name.startswith("sfpcl_credit.security_instruments"):
                            reverse_offenders.append(
                                f"{path.relative_to(backend)}:{node.lineno}:{name}"
                            )
        self.assertEqual(reverse_offenders, [])

        coordinator = backend / "processes" / "security_instrument_evidence.py"
        self.assertTrue(coordinator.exists())
        coordinator_source = coordinator.read_text()
        self.assertIn("sfpcl_credit.legal_documents", coordinator_source)
        self.assertIn("sfpcl_credit.security_instruments", coordinator_source)
        self.assertFalse(
            (backend / "legal_documents" / "modules" / "power_of_attorney.py").exists()
        )

    def test_owner_modules_import_cleanly_in_both_orders_in_fresh_processes(self):
        environment = {
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "sfpcl_credit.config.settings",
        }
        orders = (
            ("sfpcl_credit.security_instruments.models", "sfpcl_credit.legal_documents.models", "sfpcl_credit.approvals.models"),
            ("sfpcl_credit.approvals.models", "sfpcl_credit.legal_documents.models", "sfpcl_credit.security_instruments.models"),
        )
        for order in orders:
            script = (
                "import django,importlib;django.setup();"
                + ";".join(f"importlib.import_module({name!r})" for name in order)
            )
            completed = subprocess.run(
                [sys.executable, "-c", script], cwd=Path(__file__).parents[2],
                env=environment, capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_security_app_owns_retained_tables_and_policy(self):
        package = apps.get_model("security_instruments", "SecurityPackage")
        poa = apps.get_model("security_instruments", "PowerOfAttorney")
        cdsl = apps.get_model("security_instruments", "CDSLSharePledge")
        blank_cheque = apps.get_model("security_instruments", "BlankDatedCheque")
        self.assertEqual(package._meta.db_table, "security_packages")
        self.assertEqual(poa._meta.db_table, "power_of_attorneys")
        self.assertEqual(cdsl._meta.db_table, "cdsl_share_pledges")
        self.assertEqual(blank_cheque._meta.db_table, "blank_dated_cheques")
        with self.assertRaises(LookupError):
            apps.get_model("legal_documents", "SecurityPackage")
        from sfpcl_credit.security_instruments.modules import security_package
        from sfpcl_credit.security_instruments.modules import blank_dated_cheque
        self.assertEqual(
            security_package.read_package.__module__,
            "sfpcl_credit.security_instruments.modules.security_package",
        )
        self.assertEqual(
            blank_dated_cheque.create_cheque.__module__,
            "sfpcl_credit.security_instruments.modules.blank_dated_cheque",
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
