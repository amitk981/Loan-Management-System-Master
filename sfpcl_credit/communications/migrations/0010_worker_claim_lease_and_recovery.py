import uuid
from datetime import timedelta

from django.db import migrations, models
from django.utils import timezone


def preserve_running_jobs_as_expired_claims(apps, schema_editor):
    Job = apps.get_model("communications", "CommunicationDeliveryJob")
    expired_at = timezone.now() - timedelta(seconds=1)
    for job in Job.objects.filter(status="running").iterator():
        job.claim_token = uuid.uuid4()
        job.lease_expires_at = expired_at
        job.save(update_fields=["claim_token", "lease_expires_at"])


class Migration(migrations.Migration):
    dependencies = [("communications", "0009_generic_delivery_job_identity")]

    operations = [
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="claim_token",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="lease_expires_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="recovery_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="last_recovered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(
            preserve_running_jobs_as_expired_claims,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="communicationdeliveryjob",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        status="running",
                        claim_token__isnull=False,
                        lease_expires_at__isnull=False,
                    )
                    | (
                        ~models.Q(status="running")
                        & models.Q(
                            claim_token__isnull=True,
                            lease_expires_at__isnull=True,
                        )
                    )
                ),
                name="communication_job_claim_lease_complete",
            ),
        ),
    ]
