import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0001_initial"),
        ("documents", "0003_documenttemplateidentity"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoanDocument",
            fields=[
                ("loan_document_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("loan_account_id", models.UUIDField(blank=True, db_index=True, null=True)),
                ("document_type", models.CharField(db_index=True, max_length=100)),
                ("document_category", models.CharField(db_index=True, max_length=80)),
                ("party_required", models.CharField(blank=True, max_length=80, null=True)),
                ("output_format", models.CharField(max_length=20)),
                ("generation_status", models.CharField(db_index=True, max_length=60)),
                ("execution_status", models.CharField(db_index=True, max_length=60)),
                ("verification_status", models.CharField(db_index=True, max_length=60)),
                ("stamp_status", models.CharField(blank=True, db_index=True, max_length=60, null=True)),
                ("notarisation_status", models.CharField(blank=True, db_index=True, max_length=60, null=True)),
                ("custody_location", models.CharField(blank=True, max_length=255, null=True)),
                ("retention_until_date", models.DateField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("document", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="generated_loan_documents", to="documents.documentfile")),
                ("document_template", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="loan_documents", to="documents.documenttemplate")),
                ("loan_application", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="loan_documents", to="applications.loanapplication")),
                ("verified_by_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="verified_loan_documents", to="identity.user")),
            ],
            options={
                "db_table": "loan_documents",
                "ordering": ["-created_at", "-loan_document_id"],
                "indexes": [
                    models.Index(fields=["loan_application", "document_type"], name="idx_loan_doc_app_type"),
                    models.Index(fields=["document_category", "generation_status"], name="idx_loan_doc_cat_gen"),
                    models.Index(fields=["execution_status", "verification_status"], name="idx_loan_doc_exec_verify"),
                ],
                "constraints": [models.UniqueConstraint(fields=("loan_application", "document_template", "output_format"), name="unique_loan_doc_generation_replay")],
            },
        )
    ]
