from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("identity", "0003_portal_member_auth"),
    ]

    operations = [
        migrations.AddField(
            model_name="auditlog",
            name="selector_manifest_json",
            field=models.TextField(blank=True, db_default="", default=""),
        ),
        migrations.AddField(
            model_name="auditlog",
            name="selector_manifest_sha256",
            field=models.CharField(blank=True, db_default="", default="", max_length=64),
        ),
    ]
