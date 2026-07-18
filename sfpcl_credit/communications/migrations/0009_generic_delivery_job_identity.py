from django.db import migrations, models
import django.db.models.deletion


def preserve_advice_job_identity(apps, schema_editor):
    Job = apps.get_model("communications", "CommunicationDeliveryJob")
    for job in Job.objects.select_related("outbox").all().iterator():
        outbox = job.outbox
        if not (
            outbox.template_provenance_status == "verified"
            and outbox.template_provenance_origin == "frozen_before_dispatch"
        ):
            raise RuntimeError(
                "Legacy-partial communication outboxes cannot be attached to delivery jobs."
            )
        job.communication_id = outbox.communication_id
        job.job_kind = "advice"
        job.idempotency_key = outbox.idempotency_key
        job.save(
            update_fields=["communication_id", "job_kind", "idempotency_key"]
        )


class Migration(migrations.Migration):
    dependencies = [("communications", "0008_legacy_template_provenance_closure")]

    operations = [
        migrations.RemoveConstraint(
            model_name="communicationdeliveryjob",
            name="communication_delivery_job_complete",
        ),
        migrations.AlterField(
            model_name="communicationdeliveryjob",
            name="outbox",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="delivery_job",
                to="communications.communicationdeliveryoutbox",
            ),
        ),
        migrations.AlterField(
            model_name="communicationdeliveryjob",
            name="advice_intent_id",
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="communication_id",
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="idempotency_key",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="job_kind",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="provider_accepted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="provider_delivery_status",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryjob",
            name="provider_external_message_id",
            field=models.CharField(
                blank=True, max_length=120, null=True, unique=True
            ),
        ),
        migrations.RunPython(preserve_advice_job_identity, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="communicationdeliveryjob",
            name="communication_id",
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name="communicationdeliveryjob",
            name="idempotency_key",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="communicationdeliveryjob",
            name="job_kind",
            field=models.CharField(max_length=40),
        ),
        migrations.AddConstraint(
            model_name="communicationdeliveryjob",
            constraint=models.CheckConstraint(
                check=(
                    ~models.Q(idempotency_key="")
                    & ~models.Q(actor_role_code="")
                    & ~models.Q(request_id="")
                    & ~models.Q(request_payload_digest="")
                    & models.Q(
                        status__in=("queued", "running", "retrying", "sent", "failed")
                    )
                    & models.Q(max_attempts__gte=1)
                    & models.Q(attempts__lte=models.F("max_attempts"))
                    & (
                        models.Q(
                            job_kind="advice",
                            outbox__isnull=False,
                            advice_intent_id__isnull=False,
                        )
                        | models.Q(
                            job_kind="generic",
                            outbox__isnull=True,
                            advice_intent_id__isnull=True,
                        )
                    )
                ),
                name="communication_delivery_job_complete",
            ),
        ),
        migrations.AddConstraint(
            model_name="communicationdeliveryjob",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        provider_external_message_id__isnull=True,
                        provider_delivery_status__isnull=True,
                        provider_accepted_at__isnull=True,
                    )
                    | (
                        models.Q(
                            job_kind="generic",
                            provider_external_message_id__isnull=False,
                            provider_delivery_status="sent",
                            provider_accepted_at__isnull=False,
                        )
                        & ~models.Q(provider_external_message_id="")
                    )
                ),
                name="communication_job_provider_result_complete",
            ),
        ),
    ]
