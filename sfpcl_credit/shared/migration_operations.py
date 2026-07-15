from django.db import migrations


class AddFieldToAppModel(migrations.AddField):
    """Add a field to a model owned by an app other than the migration."""

    def __init__(self, target_app_label, *args, **kwargs):
        self.target_app_label = target_app_label
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, args, kwargs = super().deconstruct()
        kwargs["target_app_label"] = self.target_app_label
        return name, args, kwargs

    def state_forwards(self, app_label, state):
        super().state_forwards(self.target_app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        super().database_forwards(
            self.target_app_label,
            schema_editor,
            from_state,
            to_state,
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        super().database_backwards(
            self.target_app_label,
            schema_editor,
            from_state,
            to_state,
        )
