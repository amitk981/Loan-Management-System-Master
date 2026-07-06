import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("identity", "0002_permission_rolepermission_and_more"),
        ("tracer", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="WorkflowEvent",
                    fields=[
                        (
                            "workflow_event_id",
                            models.UUIDField(
                                default=uuid.uuid4,
                                editable=False,
                                primary_key=True,
                                serialize=False,
                            ),
                        ),
                        (
                            "workflow_name",
                            models.CharField(db_index=True, max_length=100),
                        ),
                        (
                            "entity_type",
                            models.CharField(db_index=True, max_length=100),
                        ),
                        ("entity_id", models.UUIDField(db_index=True)),
                        (
                            "from_state",
                            models.CharField(blank=True, max_length=100, null=True),
                        ),
                        (
                            "to_state",
                            models.CharField(db_index=True, max_length=100),
                        ),
                        ("trigger_reason", models.TextField(blank=True)),
                        (
                            "created_at",
                            models.DateTimeField(
                                db_index=True, default=django.utils.timezone.now
                            ),
                        ),
                        (
                            "triggered_by_user",
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.PROTECT,
                                to="identity.user",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "workflow_events",
                        "ordering": ["created_at"],
                    },
                ),
            ],
        ),
    ]
