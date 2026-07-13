import uuid

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("applications", "0012_witness_verification_evidence"), ("identity", "0001_initial")]

    operations = [
        migrations.AddField(model_name="witness", name="updated_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="witness", name="version", field=models.PositiveIntegerField(db_default=1, default=1)),
        migrations.AddField(model_name="witness", name="updated_by_user", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="updated_witnesses", to="identity.user")),
        migrations.CreateModel(
            name="WitnessChangeHistory",
            fields=[
                ("witness_change_history_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("witness_version", models.PositiveIntegerField()),
                ("changed_fields", models.JSONField(default=list)),
                ("old_value_json", models.JSONField(default=dict)),
                ("new_value_json", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("actor_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="witness_changes", to="identity.user")),
                ("witness", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="change_history", to="applications.witness")),
            ],
            options={"db_table": "witness_change_history", "ordering": ["created_at", "witness_change_history_id"]},
        ),
    ]
