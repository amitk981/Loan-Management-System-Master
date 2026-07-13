from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("credit", "0006_legacy_appraisal_history_remediation")]

    operations = [
        migrations.AddField(
            model_name="eligibilityassessment",
            name="active_member_snapshot",
            field=models.JSONField(default=dict),
        ),
    ]
