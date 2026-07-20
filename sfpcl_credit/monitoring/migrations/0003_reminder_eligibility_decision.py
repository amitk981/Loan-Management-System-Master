from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("monitoring", "0002_reminder_queue"),
    ]

    operations = [
        migrations.AddField(
            model_name="reminder",
            name="eligibility_decision_json",
            field=models.JSONField(default=dict),
        ),
    ]
