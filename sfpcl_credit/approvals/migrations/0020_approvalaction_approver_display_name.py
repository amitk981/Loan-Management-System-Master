from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approvals", "0019_register_source_facts"),
    ]

    operations = [
        migrations.AddField(
            model_name="approvalaction",
            name="approver_display_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
