from datetime import date

from django.db import connection
from django.db import IntegrityError, transaction
from django.db.migrations.loader import MigrationLoader
from django.db.models import Q
from django.test import TestCase

from sfpcl_credit.documents.models import DocumentTemplate


class DocumentTemplateMigrationStateTests(TestCase):
    expected_constraint_values = {
        "doc_template_approval_status": (
            "draft",
            "approved",
            "retired",
        ),
        "doc_template_borrower_type": (
            "individual_farmer",
            "fpc",
            "fpo",
        ),
    }

    def test_migration_facing_constraint_values_are_ordered_and_exact(self):
        model_constraints = DocumentTemplate._meta.constraints
        migration_constraints = self._terminal_migration_constraints()

        for constraint_name, expected_values in self.expected_constraint_values.items():
            with self.subTest(constraint=constraint_name, state="model"):
                self.assertEqual(
                    self._in_values(model_constraints, constraint_name),
                    expected_values,
                )
            with self.subTest(constraint=constraint_name, state="migration"):
                self.assertEqual(
                    self._in_values(migration_constraints, constraint_name),
                    expected_values,
                )

    def test_database_constraints_preserve_exact_allowed_values(self):
        for index, approval_status in enumerate(
            self.expected_constraint_values["doc_template_approval_status"]
        ):
            DocumentTemplate.objects.create(
                **self._template_values(
                    index=f"approval-{index}",
                    approval_status=approval_status,
                    borrower_type="individual_farmer",
                )
            )
        for index, borrower_type in enumerate(
            (None,)
            + self.expected_constraint_values["doc_template_borrower_type"]
        ):
            DocumentTemplate.objects.create(
                **self._template_values(
                    index=f"borrower-{index}",
                    approval_status="draft",
                    borrower_type=borrower_type,
                )
            )

        invalid_values = (
            self._template_values(
                index="invalid-approval",
                approval_status="pending",
                borrower_type="individual_farmer",
            ),
            self._template_values(
                index="invalid-borrower",
                approval_status="draft",
                borrower_type="producer_institution",
            ),
        )
        for values in invalid_values:
            with self.subTest(template_code=values["template_code"]):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    DocumentTemplate.objects.create(**values)

    def _template_values(self, *, index, approval_status, borrower_type):
        return {
            "template_code": f"constraint-{index}",
            "template_name": f"Constraint {index}",
            "document_type": f"constraint-{index}",
            "borrower_type": borrower_type,
            "template_version": "1.0",
            "approval_status": approval_status,
            "effective_from": date(2026, 1, 1),
        }

    def _terminal_migration_constraints(self):
        loader = MigrationLoader(connection)
        leaf_nodes = loader.graph.leaf_nodes("documents")
        self.assertEqual(len(leaf_nodes), 1, leaf_nodes)
        project_state = loader.project_state(leaf_nodes)
        return project_state.models[
            ("documents", "documenttemplate")
        ].options["constraints"]

    def _in_values(self, constraints, constraint_name):
        constraint = next(
            item for item in constraints if item.name == constraint_name
        )
        lookup = {
            "doc_template_approval_status": "approval_status__in",
            "doc_template_borrower_type": "borrower_type__in",
        }[constraint_name]
        return self._lookup_value(constraint.check, lookup)

    def _lookup_value(self, condition, lookup):
        for child in condition.children:
            if isinstance(child, Q):
                try:
                    return self._lookup_value(child, lookup)
                except LookupError:
                    continue
            elif child[0] == lookup:
                return child[1]
        raise LookupError(f"Missing {lookup} in {condition!r}")
