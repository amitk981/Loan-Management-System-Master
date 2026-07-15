import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentTemplate",
            fields=[
                (
                    "document_template_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("template_code", models.CharField(max_length=120, unique=True)),
                ("template_name", models.CharField(max_length=255)),
                ("document_type", models.CharField(db_index=True, max_length=100)),
                (
                    "borrower_type",
                    models.CharField(blank=True, db_index=True, max_length=60, null=True),
                ),
                ("template_version", models.CharField(max_length=40)),
                ("merge_fields_json", models.JSONField(blank=True, null=True)),
                ("approval_status", models.CharField(db_index=True, max_length=60)),
                ("effective_from", models.DateField()),
                ("effective_to", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "supersedes",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="successor",
                        to="documents.documenttemplate",
                    ),
                ),
                (
                    "template_file",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="document_templates",
                        to="documents.documentfile",
                    ),
                ),
            ],
            options={
                "db_table": "document_templates",
                "ordering": [
                    "-effective_from",
                    "-created_at",
                    "-document_template_id",
                ],
                "constraints": [
                    models.CheckConstraint(
                        check=models.Q(("effective_to__isnull", True), ("effective_to__gte", models.F("effective_from")), _connector="OR"),
                        name="doc_template_effective_dates",
                    ),
                    models.CheckConstraint(
                        check=models.Q(("approval_status__in", {"approved", "draft", "retired"})),
                        name="doc_template_approval_status",
                    ),
                    models.CheckConstraint(
                        check=models.Q(("borrower_type__isnull", True), ("borrower_type__in", {"fpc", "fpo", "individual_farmer"}), _connector="OR"),
                        name="doc_template_borrower_type",
                    ),
                    models.UniqueConstraint(
                        fields=("document_type", "borrower_type", "template_version"),
                        name="unique_doc_template_variant_version",
                    ),
                ],
            },
        ),
    ]
