import uuid

from django.db import migrations, models


def seed_existing_template_identities(apps, schema_editor):
    DocumentTemplate = apps.get_model("documents", "DocumentTemplate")
    DocumentTemplateIdentity = apps.get_model(
        "documents", "DocumentTemplateIdentity"
    )
    identities = {
        (row["document_type"], row["borrower_type"] or "__global__")
        for row in DocumentTemplate.objects.values("document_type", "borrower_type")
    }
    DocumentTemplateIdentity.objects.bulk_create(
        [
            DocumentTemplateIdentity(
                document_type=document_type,
                borrower_variant_key=borrower_variant_key,
            )
            for document_type, borrower_variant_key in sorted(identities)
        ]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0002_documenttemplate"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentTemplateIdentity",
            fields=[
                (
                    "document_template_identity_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("document_type", models.CharField(max_length=100)),
                ("borrower_variant_key", models.CharField(max_length=60)),
            ],
            options={
                "db_table": "document_template_identities",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("document_type", "borrower_variant_key"),
                        name="unique_document_template_identity",
                    )
                ],
            },
        ),
        migrations.RunPython(
            seed_existing_template_identities,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
