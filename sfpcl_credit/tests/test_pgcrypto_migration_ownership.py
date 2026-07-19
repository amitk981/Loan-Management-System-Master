"""Non-destructive reversal contract for the exact-selector prerequisite."""

from importlib import import_module

from django.test import SimpleTestCase


migration = import_module(
    "sfpcl_credit.disbursements.migrations.0010_enable_pgcrypto_for_exact_selector"
)


class _Connection:
    def __init__(self, vendor):
        self.vendor = vendor


class _SchemaEditor:
    def __init__(self, vendor):
        self.connection = _Connection(vendor)
        self.executed = []

    def execute(self, sql):
        self.executed.append(" ".join(sql.split()))


class PgcryptoMigrationOwnershipTests(SimpleTestCase):
    def test_postgresql_forward_is_idempotent_for_preexisting_extension(self):
        editor = _SchemaEditor("postgresql")

        migration.enable_pgcrypto(None, editor)

        self.assertEqual(len(editor.executed), 1)
        statement = editor.executed[0]
        self.assertIn("pg_extension", statement)
        self.assertIn("CREATE EXTENSION IF NOT EXISTS pgcrypto", statement)
        self.assertIn("sfpcl_disbursements_pgcrypto_ownership", statement)
        self.assertIn("NOT extension_preexisting", statement)

    def test_reverse_drops_only_when_the_durable_marker_proves_app_ownership(self):
        editor = _SchemaEditor("postgresql")

        migration.disable_pgcrypto(None, editor)

        self.assertEqual(len(editor.executed), 1)
        statement = editor.executed[0]
        self.assertIn("TO_REGCLASS", statement)
        self.assertIn("IF app_created THEN DROP EXTENSION IF EXISTS pgcrypto", statement)
        self.assertIn("DROP TABLE sfpcl_disbursements_pgcrypto_ownership", statement)

    def test_sqlite_forward_and_reverse_are_noops(self):
        editor = _SchemaEditor("sqlite")

        migration.enable_pgcrypto(None, editor)
        migration.disable_pgcrypto(None, editor)

        self.assertEqual(editor.executed, [])
