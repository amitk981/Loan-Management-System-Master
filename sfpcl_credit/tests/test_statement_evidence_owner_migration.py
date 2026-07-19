from uuid import UUID, uuid4

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class StatementEvidenceOwnerMigrationTests(TransactionTestCase):
    migrate_from = [("loans", "0006_repayment_allocation_admission")]
    migrate_to = [("loans", "0007_statement_evidence_owner_scope_closure")]

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_coherent_and_orphan_legacy_links_migrate_without_inventing_lines(self):
        from sfpcl_credit.tests.test_bank_statement_matching_api import (
            BankStatementMatchingApiTests,
        )

        fixture = BankStatementMatchingApiTests(
            "test_exact_statement_evidence_matches_one_receipt_without_financial_mutation"
        )
        fixture.setUp()
        first = fixture.fixture._capture(
            {
                **fixture.fixture._payload(),
                "amount_received": "62000.00",
                "received_date": "2026-12-14",
                "bank_reference_number": "UTR-MIGRATION-COHERENT",
            },
            "statement-migration-coherent",
        )
        coherent_repayment_id = first.json()["data"]["repayment_id"]
        imported = fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-14,2026-12-14,62000.00,Receipt for {fixture.account.loan_account_number},"
            f"UTR-MIGRATION-COHERENT,{fixture.account.loan_account_number}\n",
            key="statement-migration-import",
        ).json()["data"]
        coherent_line_id = imported["lines"][0]["bank_statement_line_id"]
        second = fixture.fixture._capture(
            {
                **fixture.fixture._payload(),
                "amount_received": "63000.00",
                "received_date": "2026-12-15",
                "bank_reference_number": "UTR-MIGRATION-ORPHAN",
            },
            "statement-migration-orphan",
        )
        orphan_repayment_id = second.json()["data"]["repayment_id"]
        orphan_line_id = uuid4()

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        OldRepayment = old_apps.get_model("loans", "Repayment")
        OldRepayment.objects.filter(pk=orphan_repayment_id).update(
            bank_statement_line_id=orphan_line_id
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        migrated_apps = executor.loader.project_state(self.migrate_to).apps
        Repayment = migrated_apps.get_model("loans", "Repayment")
        Line = migrated_apps.get_model("loans", "BankStatementLine")
        ExceptionEvidence = migrated_apps.get_model(
            "loans", "StatementLinkMigrationException"
        )
        self.assertEqual(
            str(Line.objects.get(pk=coherent_line_id).matched_repayment_id),
            coherent_repayment_id,
        )
        self.assertFalse(
            ExceptionEvidence.objects.filter(
                repayment_id=coherent_repayment_id
            ).exists()
        )
        orphan = ExceptionEvidence.objects.get(repayment_id=orphan_repayment_id)
        self.assertEqual(orphan.legacy_statement_line_id, orphan_line_id)
        self.assertEqual(orphan.reason_code, "legacy_statement_line_orphan")
        self.assertFalse(Line.objects.filter(pk=orphan_line_id).exists())
        self.assertNotIn(
            "bank_statement_line_id",
            {field.name for field in Repayment._meta.local_fields},
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        reversed_apps = executor.loader.project_state(self.migrate_from).apps
        ReversedRepayment = reversed_apps.get_model("loans", "Repayment")
        self.assertEqual(
            ReversedRepayment.objects.get(
                pk=coherent_repayment_id
            ).bank_statement_line_id,
            UUID(coherent_line_id),
        )
        self.assertEqual(
            ReversedRepayment.objects.get(
                pk=orphan_repayment_id
            ).bank_statement_line_id,
            orphan_line_id,
        )
