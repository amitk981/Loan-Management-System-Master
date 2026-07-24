from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportexportjob",
            name="authority_snapshot",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="reportexportjob",
            name="classification",
            field=models.CharField(default="confidential", max_length=40),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="reportexportjob",
            name="permitted_columns",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="reportexportjob",
            name="requested_columns",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="reportexportjob",
            name="sensitive_export",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="reportexportjob",
            name="sensitive_reason_digest",
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
