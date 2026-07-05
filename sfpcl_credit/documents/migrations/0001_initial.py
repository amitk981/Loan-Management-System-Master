import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("identity", "0002_permission_rolepermission_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentFile",
            fields=[
                (
                    "document_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("file_name", models.CharField(max_length=255)),
                ("file_extension", models.CharField(blank=True, max_length=20, null=True)),
                ("mime_type", models.CharField(blank=True, max_length=100, null=True)),
                ("file_size_bytes", models.BigIntegerField(blank=True, null=True)),
                ("storage_provider", models.CharField(max_length=80)),
                ("storage_key", models.TextField()),
                ("checksum_sha256", models.CharField(blank=True, max_length=128, null=True)),
                (
                    "uploaded_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("sensitivity_level", models.CharField(db_index=True, max_length=60)),
                ("retention_until_date", models.DateField(blank=True, null=True)),
                (
                    "uploaded_by_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="uploaded_document_files",
                        to="identity.user",
                    ),
                ),
            ],
            options={
                "db_table": "document_files",
                "ordering": ["-uploaded_at", "-document_id"],
            },
        ),
    ]
