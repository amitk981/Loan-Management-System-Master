from importlib import import_module
from uuid import uuid4

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class WitnessEvidenceMigrationTests(TransactionTestCase):
    migrate_from = [("applications", "0011_witness")]
    migrate_to = [("applications", "0012_witness_verification_evidence")]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        legacy_targets = [
            node
            for node in executor.loader.graph.leaf_nodes()
            # Configuration, legal, finance, loan, interest, monitoring, default, recovery, SAP,
            # and communications owners explicitly anchor later application state. Exclude those
            # descendants when projecting the pre-0012 application model or the historical state
            # would outrun the reversed schema.
            if node[0]
            not in {
                "applications",
                "finance",
                "legal_documents",
                "loans",
                "sap_workflow",
                "disbursements",
                "communications",
                "configurations",
                "interest",
                "monitoring",
                "defaults",
                "recovery",
            }
        ] + self.migrate_from
        old_apps = executor.loader.project_state(legacy_targets).apps
        self.ids = self._create_legacy_rows(old_apps)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_backfill_only_links_unambiguous_audited_shareholding_evidence(self):
        apps = self._migrate_forward()
        Witness = apps.get_model("applications", "Witness")

        linked = Witness.objects.get(pk=self.ids["linked_witness_id"])
        self.assertEqual(linked.verification_shareholding_id, self.ids["linked_shareholding_id"])
        self.assertEqual(linked.verification_folio_number, "FOL-LINKED")

        for witness_id in (
            self.ids["ambiguous_witness_id"],
            self.ids["no_match_witness_id"],
            self.ids["no_audit_witness_id"],
        ):
            witness = Witness.objects.get(pk=witness_id)
            self.assertIsNone(witness.verification_shareholding_id)
            self.assertIsNone(witness.verification_folio_number)

    def test_backfill_is_idempotent_and_reverse_preserves_legacy_rows(self):
        apps = self._migrate_forward()
        migration = import_module(
            "sfpcl_credit.applications.migrations.0012_witness_verification_evidence"
        )
        with connection.schema_editor() as schema_editor:
            migration.backfill_witness_evidence(apps, schema_editor)
            migration.backfill_witness_evidence(apps, schema_editor)
        Witness = apps.get_model("applications", "Witness")
        self.assertEqual(
            Witness.objects.get(pk=self.ids["linked_witness_id"]).verification_shareholding_id,
            self.ids["linked_shareholding_id"],
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        reversed_apps = executor.loader.project_state(self.migrate_from).apps
        ReversedWitness = reversed_apps.get_model("applications", "Witness")
        self.assertEqual(ReversedWitness.objects.count(), 4)

    def test_witness_operational_indexes_exist_exactly_once(self):
        self._migrate_forward()
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, "witnesses")
        indexes = {
            name: details
            for name, details in constraints.items()
            if details.get("index")
        }
        expected = {
            "idx_witnesses_application": ["loan_application_id"],
            "idx_witnesses_pan_hash": ["pan_hash"],
            "idx_witnesses_aadhaar_hash": ["aadhaar_hash"],
        }
        for name, columns in expected.items():
            self.assertIn(name, indexes)
            self.assertEqual(indexes[name]["columns"], columns)
            same_columns = [
                index_name
                for index_name, details in indexes.items()
                if details["columns"] == columns
            ]
            self.assertEqual(same_columns, [name])

    def _migrate_forward(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        return executor.loader.project_state(self.migrate_to).apps

    def _create_legacy_rows(self, apps):
        Role = apps.get_model("identity", "Role")
        User = apps.get_model("identity", "User")
        Member = apps.get_model("members", "Member")
        Shareholding = apps.get_model("members", "Shareholding")
        LoanApplication = apps.get_model("applications", "LoanApplication")
        Witness = apps.get_model("applications", "Witness")
        AuditLog = apps.get_model("identity", "AuditLog")

        role = Role.objects.create(role_code="witness_migration", role_name="Witness Migration")
        user = User.objects.create(
            full_name="Migration Actor",
            email="witness-migration@sfpcl.example",
            primary_role=role,
            password_hash="synthetic-not-a-password",
        )
        member = Member.objects.create(
            member_number="MEM-WITNESS-MIGRATION",
            member_type="individual_farmer",
            legal_name="Migration Witness",
            display_name="Migration Witness",
            folio_number="FOL-LINKED",
            membership_status="active",
            pan_encrypted="synthetic-member-pan",
            pan_hash="synthetic-member-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        application = LoanApplication.objects.create(
            member=member,
            borrower_type="individual_farmer",
            received_by_user=user,
        )

        linked_shareholding = self._shareholding(Shareholding, member, "FOL-LINKED")
        self._shareholding(Shareholding, member, "FOL-AMBIGUOUS")
        self._shareholding(Shareholding, member, "FOL-AMBIGUOUS")

        witnesses = {}
        for label in ("linked", "ambiguous", "no_match", "no_audit"):
            witness = Witness.objects.create(
                loan_application=application,
                member=member,
                witness_name=f"Migration Witness {label}",
                pan_encrypted=f"pan-{label}",
                pan_hash=f"pan-hash-{label}",
                aadhaar_encrypted=f"aadhaar-{label}",
                aadhaar_hash=f"aadhaar-hash-{label}",
                shareholder_verified_flag=True,
                verification_status="verified",
                verified_by_user=user,
                verified_at=application.created_at,
            )
            witnesses[f"{label}_witness_id"] = witness.witness_id

        for label, folio in (
            ("linked", "FOL-LINKED"),
            ("ambiguous", "FOL-AMBIGUOUS"),
            ("no_match", "FOL-NO-MATCH"),
        ):
            AuditLog.objects.create(
                actor_user=user,
                action="applications.witness.created",
                entity_type="witness",
                entity_id=witnesses[f"{label}_witness_id"],
                new_value_json={"folio_number": folio},
            )

        return {
            **witnesses,
            "linked_shareholding_id": linked_shareholding.shareholding_id,
        }

    @staticmethod
    def _shareholding(model, member, folio):
        return model.objects.create(
            shareholding_id=uuid4(),
            member=member,
            folio_number=folio,
            number_of_shares=10,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=10,
            status="active",
        )
