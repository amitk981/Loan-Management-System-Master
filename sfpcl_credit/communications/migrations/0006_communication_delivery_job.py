import django.db.models.deletion
import django.utils.timezone
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("communications", "0005_advice_evidence_and_legacy_replay_closure")]

    operations = [
        migrations.CreateModel(
            name="CommunicationDeliveryJob",
            fields=[
                ("communication_job_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("advice_intent_id", models.UUIDField(unique=True)),
                ("actor_id", models.UUIDField()),
                ("actor_role_code", models.CharField(max_length=80)),
                ("actor_team_codes", models.JSONField(default=list)),
                ("request_id", models.CharField(max_length=255)),
                ("ip_address", models.CharField(blank=True, max_length=64)),
                ("user_agent", models.CharField(blank=True, max_length=255)),
                ("request_payload_digest", models.CharField(max_length=64)),
                ("status", models.CharField(db_index=True, default="queued", max_length=40)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("max_attempts", models.PositiveSmallIntegerField(default=3)),
                ("next_attempt_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("last_failure_code", models.CharField(blank=True, max_length=80)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("outbox", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="delivery_job", to="communications.communicationdeliveryoutbox")),
            ],
            options={
                "db_table": "communication_delivery_jobs",
                "indexes": [models.Index(fields=["status", "next_attempt_at"], name="communicati_status_7c0f6a_idx")],
                "constraints": [models.CheckConstraint(check=models.Q(models.Q(("actor_role_code", ""), _negated=True), models.Q(("request_id", ""), _negated=True), models.Q(("request_payload_digest", ""), _negated=True), ("status__in", ("queued", "running", "retrying", "sent", "failed")), ("max_attempts__gte", 1), ("attempts__lte", models.F("max_attempts"))), name="communication_delivery_job_complete")],
            },
        )
    ]
