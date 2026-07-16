from django.db import migrations
from django.db.migrations.operations.base import Operation
from django.db.migrations.utils import resolve_relation


class TransferSapModelState(Operation):
    """Relocate SAP model state without touching either physical table."""

    reduces_to_sql = False
    reversible = True

    model_names = ("sapcustomercode", "sapcustomerprofilerequest")

    def state_forwards(self, app_label, state):
        self._transfer(state, source="finance", destination="sap_workflow")

    def state_backwards(self, app_label, state):
        self._transfer(state, source="sap_workflow", destination="finance")

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def describe(self):
        return "Transfer SAP model ownership in Django state only"

    def migration_name_fragment(self):
        return "sap_model_owner_state"

    def _transfer(self, state, *, source, destination):
        moved_states = {
            model_name: state.models[(source, model_name)].clone()
            for model_name in self.model_names
        }
        relation_targets = {
            (source, model_name): f"{destination}.{model_state.name}"
            for model_name, model_state in moved_states.items()
        }

        for model_state in state.models.values():
            for field_name, field in tuple(model_state.fields.items()):
                if not field.is_relation or field.remote_field.model == "self":
                    continue
                target = resolve_relation(
                    field.remote_field.model,
                    model_state.app_label,
                    model_state.name,
                )
                replacement = relation_targets.get(target)
                if replacement is None:
                    continue
                changed_field = field.clone()
                changed_field.remote_field.model = replacement
                model_state.fields[field_name] = changed_field

        moved_states = {
            model_name: state.models[(source, model_name)].clone()
            for model_name in self.model_names
        }
        for model_name in self.model_names:
            state.remove_model(source, model_name)
        for model_state in moved_states.values():
            model_state.app_label = destination
            state.add_model(model_state)

        # Direct cross-app relocation is deliberately atomic. Rebuild Django's
        # derived registries from the now-complete state instead of exposing an
        # intermediate state with dangling Finance relations.
        state._relations = None
        state.__dict__.pop("apps", None)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("loans", "0001_initial"),
    ]

    operations = [
        TransferSapModelState(),
    ]
