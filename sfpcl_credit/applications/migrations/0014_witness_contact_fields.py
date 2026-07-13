from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("applications", "0013_witness_correction")]
    operations = [
        migrations.AddField(model_name="witness", name="address", field=models.CharField(blank=True, default="", max_length=500)),
        migrations.AddField(model_name="witness", name="mobile", field=models.CharField(blank=True, default="", max_length=20)),
    ]
