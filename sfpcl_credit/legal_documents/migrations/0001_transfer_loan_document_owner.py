"""Transfer the retained loan_documents table to its source-defined app owner."""

from django.db import migrations, models


CONSTRAINT_NAME = "loan_document_account_requires_epic_009"


class TransferLoanDocumentOwner(migrations.operations.base.Operation):
    """Move migration state between apps without creating or copying the table."""

    reduces_to_sql = False
    reversible = True

    def state_forwards(self, app_label, state):
        model_state = state.models[("documents", "loandocument")].clone()
        state.remove_model("documents", "loandocument")
        model_state.app_label = app_label
        model_state.options = {
            **model_state.options,
            "constraints": [
                *model_state.options.get("constraints", []),
                models.CheckConstraint(
                    check=models.Q(loan_account_id__isnull=True),
                    name=CONSTRAINT_NAME,
                ),
            ],
        }
        state.add_model(model_state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, "LoanDocument")
        constraint = next(
            item for item in model._meta.constraints if item.name == CONSTRAINT_NAME
        )
        schema_editor.add_constraint(model, constraint)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, "LoanDocument")
        constraint = next(
            item for item in model._meta.constraints if item.name == CONSTRAINT_NAME
        )
        schema_editor.remove_constraint(model, constraint)

    def describe(self):
        return "Transfer retained loan_documents ownership to legal_documents"


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("documents", "0004_loandocument"),
    ]

    operations = [TransferLoanDocumentOwner()]
