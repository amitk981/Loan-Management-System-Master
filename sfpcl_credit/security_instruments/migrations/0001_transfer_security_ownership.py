import django.db.models.deletion
from django.db import migrations, models


def _active_constraint():
    return models.CheckConstraint(
        check=(
            models.Q(status="draft")
            | (
                models.Q(
                    status="active",
                    execution_status="executed",
                    effective_from__isnull=False,
                    verified_by_user__isnull=False,
                )
                & (
                    models.Q(
                        legacy_activation_evidence=False,
                        activation_workflow_event_id__isnull=False,
                    )
                    | models.Q(
                        legacy_activation_evidence=True,
                        activation_workflow_event_id__isnull=True,
                    )
                )
            )
        ),
        name="active_poa_has_execution_verifier",
    )


class TransferSecurityOwnership(migrations.operations.base.Operation):
    """Transfer model state without recreating the retained tables."""

    reduces_to_sql = False
    reversible = True

    def _field_operations(self):
        return (
            migrations.AddField(
                "powerofattorney",
                "activation_workflow_event_id",
                models.UUIDField(blank=True, null=True),
            ),
            migrations.AddField(
                "powerofattorney",
                "activation_evidence_json",
                models.JSONField(blank=True, default=dict),
            ),
            migrations.AddField(
                "powerofattorney",
                "legacy_activation_evidence",
                models.BooleanField(default=False),
            ),
        )

    def state_forwards(self, app_label, state):
        package = state.models[("legal_documents", "securitypackage")].clone()
        poa = state.models[("legal_documents", "powerofattorney")].clone()
        state.remove_model("legal_documents", "powerofattorney")
        state.remove_model("legal_documents", "securitypackage")
        package.app_label = "security_instruments"
        poa.app_label = "security_instruments"
        package_field = poa.fields["security_package"].clone()
        package_field.remote_field.model = (
            "security_instruments.securitypackage"
        )
        poa.fields["security_package"] = package_field
        state.add_model(package)
        state.add_model(poa)
        for operation in self._field_operations():
            operation.state_forwards("security_instruments", state)
        migrations.RemoveConstraint(
            "powerofattorney", "active_poa_has_execution_verifier"
        ).state_forwards("security_instruments", state)
        migrations.AddConstraint(
            "powerofattorney", _active_constraint()
        ).state_forwards("security_instruments", state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        old_model = from_state.apps.get_model("legal_documents", "PowerOfAttorney")
        model = to_state.apps.get_model("security_instruments", "PowerOfAttorney")
        old_constraint = next(
            item for item in old_model._meta.constraints
            if item.name == "active_poa_has_execution_verifier"
        )
        schema_editor.remove_constraint(old_model, old_constraint)
        table = schema_editor.quote_name(model._meta.db_table)
        if schema_editor.connection.vendor == "sqlite":
            # SQLite would enforce the strengthened constraint before retained
            # active rows can be marked as legacy if its schema editor remade
            # the table after each field.
            schema_editor.execute(
                f"ALTER TABLE {table} ADD COLUMN activation_workflow_event_id char(32) NULL"
            )
            schema_editor.execute(
                f"ALTER TABLE {table} ADD COLUMN activation_evidence_json text NOT NULL DEFAULT '{{}}'"
            )
            schema_editor.execute(
                f"ALTER TABLE {table} ADD COLUMN legacy_activation_evidence bool NOT NULL DEFAULT 0"
            )
        else:
            for operation in self._field_operations():
                schema_editor.add_field(model, model._meta.get_field(operation.name))
        schema_editor.execute(
            f"UPDATE {table} SET legacy_activation_evidence = %s WHERE status = %s",
            [True, "active"],
        )
        schema_editor.add_constraint(model, _active_constraint())

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model("security_instruments", "PowerOfAttorney")
        old_model = to_state.apps.get_model("legal_documents", "PowerOfAttorney")
        if schema_editor.connection.vendor == "sqlite":
            schema_editor._remake_table(old_model)
            return
        schema_editor.remove_constraint(model, _active_constraint())
        table = schema_editor.quote_name(model._meta.db_table)
        for name in (
            "activation_evidence_json",
            "activation_workflow_event_id",
            "legacy_activation_evidence",
        ):
            schema_editor.execute(f"ALTER TABLE {table} DROP COLUMN {name}")
        old_constraint = next(
            item for item in old_model._meta.constraints
            if item.name == "active_poa_has_execution_verifier"
        )
        schema_editor.add_constraint(old_model, old_constraint)

    def describe(self):
        return "Transfer retained security models and add activation evidence"


class Migration(migrations.Migration):
    dependencies = [("legal_documents", "0010_stage4_maker_checker_constraints")]
    operations = [TransferSecurityOwnership()]
