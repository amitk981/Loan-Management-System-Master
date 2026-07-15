from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("identity", "0003_portal_member_auth"),
        ("legal_documents", "0005_signature_records"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stampdutyrecord",
            name="verified_by_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="verified_stamp_duty_records",
                to="identity.user",
            ),
        ),
        migrations.AddField(
            model_name="stampdutyrecord",
            name="prepared_by_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="prepared_stamp_duty_records",
                to="identity.user",
            ),
        ),
        migrations.AlterField(
            model_name="notarisationrecord",
            name="verified_by_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="verified_notarisation_records",
                to="identity.user",
            ),
        ),
        migrations.AddField(
            model_name="notarisationrecord",
            name="prepared_by_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="prepared_notarisation_records",
                to="identity.user",
            ),
        ),
    ]
