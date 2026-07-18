import hashlib
import json

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


def _digest(job, communication, adapter_kind):
    facts = {
        "job_id": str(job.pk),
        "communication_id": str(job.communication_id),
        "channel": communication.channel,
        "payload_digest": job.request_payload_digest,
        "idempotency_key": job.idempotency_key,
        "actor_id": str(job.actor_id),
        "adapter_kind": adapter_kind,
        "provider_external_message_id": job.provider_external_message_id,
        "provider_delivery_status": job.provider_delivery_status,
        "provider_accepted_at": job.provider_accepted_at.isoformat(),
    }
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def backfill_generic_provider_evidence(apps, schema_editor):
    Job = apps.get_model("communications", "CommunicationDeliveryJob")
    Communication = apps.get_model("communications", "Communication")
    Evidence = apps.get_model("communications", "CommunicationProviderEvidence")
    for job in Job.objects.filter(
        job_kind="generic", provider_external_message_id__isnull=False
    ).iterator():
        communication = Communication.objects.get(pk=job.communication_id)
        adapter_kind = "legacy:retained-generic-acceptance"
        Evidence.objects.create(
            job_id=job.pk,
            communication_id=job.communication_id,
            channel=communication.channel,
            payload_digest=job.request_payload_digest,
            idempotency_key=job.idempotency_key,
            actor_id=job.actor_id,
            adapter_kind=adapter_kind,
            provider_external_message_id=job.provider_external_message_id,
            provider_delivery_status=job.provider_delivery_status,
            provider_accepted_at=job.provider_accepted_at,
            evidence_digest=_digest(job, communication, adapter_kind),
        )


class Migration(migrations.Migration):
    dependencies = [("communications", "0011_communication_exception_queue")]

    operations = [
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="original_response_json",
            field=models.JSONField(default=dict),
        ),
        migrations.CreateModel(
            name="CommunicationProviderEvidence",
            fields=[
                (
                    "provider_evidence_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("communication_id", models.UUIDField()),
                ("channel", models.CharField(max_length=40)),
                ("payload_digest", models.CharField(max_length=64)),
                ("idempotency_key", models.CharField(max_length=255)),
                ("actor_id", models.UUIDField()),
                ("adapter_kind", models.CharField(max_length=255)),
                (
                    "provider_external_message_id",
                    models.CharField(max_length=120),
                ),
                ("provider_delivery_status", models.CharField(max_length=40)),
                ("provider_accepted_at", models.DateTimeField()),
                ("evidence_digest", models.CharField(max_length=64, unique=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "job",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="provider_evidence",
                        to="communications.communicationdeliveryjob",
                    ),
                ),
            ],
            options={"db_table": "communication_provider_evidence"},
        ),
        migrations.AddConstraint(
            model_name="communicationproviderevidence",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(("channel__in", ("email", "sms")))
                    & ~models.Q(("payload_digest", ""))
                    & ~models.Q(("idempotency_key", ""))
                    & ~models.Q(("adapter_kind", ""))
                    & ~models.Q(("provider_external_message_id", ""))
                    & models.Q(("provider_delivery_status", "sent"))
                    & ~models.Q(("evidence_digest", ""))
                ),
                name="communication_provider_evidence_complete",
            ),
        ),
        migrations.RunPython(backfill_generic_provider_evidence, migrations.RunPython.noop),
    ]
