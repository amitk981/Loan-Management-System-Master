from django.db import migrations, models


def normalize_exception_provider_vocabulary(apps, schema_editor):
    Communication = apps.get_model("communications", "Communication")
    Exception = apps.get_model("communications", "CommunicationException")
    for row in Exception.objects.select_related("job__outbox").all().iterator():
        if row.job.outbox_id:
            provider_code = row.job.outbox.channel
        else:
            provider_code = Communication.objects.only("channel").get(
                pk=row.job.communication_id
            ).channel
        if provider_code not in {"email", "sms"}:
            raise RuntimeError(
                "Retained communication exception has no supported source channel."
            )
        row.provider_code = provider_code
        row.save(update_fields=["provider_code"])


class Migration(migrations.Migration):
    dependencies = [("communications", "0012_generic_provider_evidence")]

    operations = [
        migrations.RunPython(
            normalize_exception_provider_vocabulary,
            migrations.RunPython.noop,
        ),
        migrations.RemoveConstraint(
            model_name="communicationexception",
            name="communication_exception_complete",
        ),
        migrations.AddConstraint(
            model_name="communicationexception",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(provider_code__in=("email", "sms"))
                    & ~models.Q(job_type="")
                    & ~models.Q(related_entity_type="")
                    & ~models.Q(last_error_code="")
                    & models.Q(retry_count__gte=1)
                ),
                name="communication_exception_complete",
            ),
        ),
    ]
