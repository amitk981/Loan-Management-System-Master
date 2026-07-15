from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("legal_documents", "0002_document_checklists")]

    operations = [
        migrations.AddField(
            model_name="loandocument",
            name="renderer_contract_version",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="loandocument",
            name="renderer_validated_document_id",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="loandocument",
            name="renderer_validated_checksum_sha256",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddConstraint(
            model_name="loandocument",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        renderer_contract_version__isnull=True,
                        renderer_validated_document_id__isnull=True,
                        renderer_validated_checksum_sha256__isnull=True,
                    )
                    | models.Q(
                        renderer_contract_version__isnull=False,
                        renderer_validated_document_id__isnull=False,
                        renderer_validated_checksum_sha256__isnull=False,
                    )
                ),
                name="loan_document_renderer_provenance_complete",
            ),
        ),
    ]
