from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("approvals", "0017_exceptionregisterentry_supporting_documents_json"),
    ]

    operations = [
        migrations.AddField(
            model_name="creditsanctionregisterentry",
            name="source_review_facts_json",
            field=models.JSONField(default=dict),
        ),
    ]
