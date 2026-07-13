from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("configurations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="versionhistory",
            name="approval_reference",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="versionhistory",
            name="approved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionhistory",
            name="old_value_json",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionhistory",
            name="new_value_json",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
