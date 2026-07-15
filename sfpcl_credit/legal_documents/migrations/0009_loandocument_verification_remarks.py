from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("legal_documents", "0008_securitypackage_powerofattorney_and_more")]

    operations = [
        migrations.AddField(
            model_name="loandocument",
            name="verification_remarks",
            field=models.TextField(blank=True, null=True),
        ),
    ]
