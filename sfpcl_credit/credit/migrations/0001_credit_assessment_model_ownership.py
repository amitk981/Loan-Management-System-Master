from django.db import migrations
from django.db.migrations.operations.base import Operation


class MoveCreditAssessmentModelState(Operation):
    """Transfer historical model state without issuing database operations."""

    reduces_to_sql = False
    reversible = True

    def state_forwards(self, app_label, state):
        for model_name in ("eligibilityassessment", "loanlimitassessment"):
            model_state = state.models[("applications", model_name)].clone()
            state.remove_model("applications", model_name)
            model_state.app_label = "credit"
            state.add_model(model_state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def describe(self):
        return "Move credit assessment model ownership in Django state only"


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0010_loanapplication_nominee"),
    ]

    operations = [
        MoveCreditAssessmentModelState(),
    ]
