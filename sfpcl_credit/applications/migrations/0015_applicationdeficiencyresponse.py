import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0014_witness_contact_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApplicationDeficiencyResponse",
            fields=[
                (
                    "application_deficiency_response_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("response_remark", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "deficiency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="portal_responses",
                        to="applications.applicationdeficiency",
                    ),
                ),
                (
                    "document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="application_deficiency_response",
                        to="documents.documentfile",
                    ),
                ),
                (
                    "portal_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="deficiency_responses",
                        to="identity.portalaccount",
                    ),
                ),
                (
                    "supersedes",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="successor",
                        to="applications.applicationdeficiencyresponse",
                    ),
                ),
                (
                    "uploader_member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="portal_deficiency_responses",
                        to="members.member",
                    ),
                ),
            ],
            options={
                "db_table": "application_deficiency_responses",
                "ordering": ["created_at", "application_deficiency_response_id"],
                "indexes": [
                    models.Index(fields=["deficiency", "created_at"], name="idx_def_response_history")
                ],
            },
        ),
        migrations.CreateModel(
            name="ApplicationDeficiencyResponseDraft",
            fields=[
                (
                    "application_deficiency_response_draft_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("response_remark", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "deficiency",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portal_response_draft",
                        to="applications.applicationdeficiency",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="portal_deficiency_response_drafts",
                        to="members.member",
                    ),
                ),
                (
                    "portal_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="deficiency_response_drafts",
                        to="identity.portalaccount",
                    ),
                ),
            ],
            options={"db_table": "application_deficiency_response_drafts"},
        ),
    ]
