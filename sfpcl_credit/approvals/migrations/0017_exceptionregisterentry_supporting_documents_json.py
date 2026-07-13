from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("approvals", "0016_creditsanctionregisterentry")]

    operations = [
        migrations.AddField(
            model_name="exceptionregisterentry",
            name="supporting_documents_json",
            field=models.JSONField(default=list),
        ),
    ]
