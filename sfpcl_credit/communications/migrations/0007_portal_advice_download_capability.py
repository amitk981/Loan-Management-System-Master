from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("communications", "0006_communication_delivery_job")]

    operations = [
        migrations.AddField(
            model_name="communicationdeliveryoutbox",
            name="portal_capability_consumed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryoutbox",
            name="portal_capability_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryoutbox",
            name="portal_capability_version",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
