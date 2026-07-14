from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("identity", "0003_portal_member_auth"),
        ("legal_documents", "0006_stamp_notary_preparer_identity"),
        ("workflows", "0001_canonical_workflow_event"),
    ]

    operations = [
        migrations.AddField(
            model_name="signaturerecord",
            name="captured_by_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="captured_signature_records",
                to="identity.user",
            ),
        ),
        migrations.AlterField(
            model_name="signaturerecord",
            name="verified_by_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="verified_signature_records",
                to="identity.user",
            ),
        ),
        migrations.AddField(
            model_name="signaturerecord",
            name="mismatch_resolution_workflow_event",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="signature_mismatch_resolution",
                to="workflows.workflowevent",
            ),
        ),
    ]
