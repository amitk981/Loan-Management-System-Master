import django.db.models.deletion
import uuid

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("communications", "0010_worker_claim_lease_and_recovery"),
        ("identity", "0003_portal_member_auth"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommunicationException",
            fields=[
                (
                    "communication_exception_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True,
                        serialize=False,
                    ),
                ),
                ("provider_code", models.CharField(max_length=255)),
                ("job_type", models.CharField(max_length=40)),
                ("related_entity_type", models.CharField(max_length=80)),
                ("related_entity_id", models.UUIDField()),
                ("last_error_code", models.CharField(max_length=80)),
                ("retry_count", models.PositiveSmallIntegerField()),
                ("resolution_action", models.CharField(blank=True, max_length=80)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("resolution_version", models.PositiveIntegerField(default=1)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "assigned_owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="assigned_communication_exceptions",
                        to="identity.user",
                    ),
                ),
                (
                    "job",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="delivery_exception",
                        to="communications.communicationdeliveryjob",
                    ),
                ),
                (
                    "resolved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="resolved_communication_exceptions",
                        to="identity.user",
                    ),
                ),
            ],
            options={
                "db_table": "communication_exceptions",
                "ordering": ["-created_at", "-communication_exception_id"],
            },
        ),
        migrations.AddConstraint(
            model_name="communicationexception",
            constraint=models.CheckConstraint(
                check=(
                    ~models.Q(provider_code="")
                    & ~models.Q(job_type="")
                    & ~models.Q(related_entity_type="")
                    & ~models.Q(last_error_code="")
                    & models.Q(retry_count__gte=1)
                ),
                name="communication_exception_complete",
            ),
        ),
        migrations.AddConstraint(
            model_name="communicationexception",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        resolution_action="",
                        resolved_by__isnull=True,
                        resolved_at__isnull=True,
                    )
                    | (
                        ~models.Q(resolution_action="")
                        & models.Q(
                            resolved_by__isnull=False,
                            resolved_at__isnull=False,
                        )
                    )
                ),
                name="communication_exception_resolution_complete",
            ),
        ),
    ]
