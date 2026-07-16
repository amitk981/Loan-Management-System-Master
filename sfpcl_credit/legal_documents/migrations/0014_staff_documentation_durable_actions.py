import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("legal_documents", "0013_application_evidence_state_anchor"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffDocumentReviewAction",
            fields=[
                ("staff_document_review_action_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("workspace_action_id", models.CharField(max_length=128, unique=True)),
                ("action_type", models.CharField(db_index=True, max_length=80)),
                ("approval_stage", models.CharField(max_length=80)),
                ("reason", models.TextField()),
                ("prior_state", models.CharField(max_length=80)),
                ("current_state", models.CharField(max_length=80)),
                ("actor_user_name_snapshot", models.CharField(max_length=200)),
                ("canonical_role_code", models.CharField(max_length=80)),
                ("actor_team_codes_json", models.JSONField(default=list)),
                ("request_id", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("actor_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="staff_document_review_actions", to="identity.user")),
                ("audit_log", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="staff_document_review_action", to="identity.auditlog")),
                ("checklist_item", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="staff_review_actions", to="legal_documents.checklistitem")),
                ("document_checklist", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="staff_review_actions", to="legal_documents.documentchecklist")),
                ("loan_document", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="staff_review_actions", to="legal_documents.loandocument")),
                ("version_history", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="staff_document_review_action", to="configurations.versionhistory")),
                ("workflow_event", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="staff_document_review_action", to="workflows.workflowevent")),
            ],
            options={
                "db_table": "staff_document_review_actions",
                "ordering": ["created_at", "staff_document_review_action_id"],
                "indexes": [models.Index(fields=["document_checklist", "action_type", "created_at"], name="idx_staff_review_scope")],
                "constraints": [models.CheckConstraint(check=models.Q(("action_type__in", ["request_correction", "return_for_correction", "add_condition"])), name="staff_review_action_type_bounded")],
            },
        ),
        migrations.CreateModel(
            name="StaffSignedDocumentCopy",
            fields=[
                ("staff_signed_document_copy_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("workspace_action_id", models.CharField(max_length=128, unique=True)),
                ("checksum_sha256", models.CharField(max_length=128)),
                ("remarks", models.TextField()),
                ("request_id", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("audit_log", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="staff_signed_document_copy", to="identity.auditlog")),
                ("document", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="staff_signed_document_copy", to="documents.documentfile")),
                ("loan_application", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="staff_signed_document_copies", to="applications.loanapplication")),
                ("loan_document", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="staff_signed_copies", to="legal_documents.loandocument")),
                ("resolves_review_action", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="resolved_by_signed_copy", to="legal_documents.staffdocumentreviewaction")),
                ("supersedes", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="successor", to="legal_documents.staffsigneddocumentcopy")),
                ("uploader_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="uploaded_staff_signed_document_copies", to="identity.user")),
                ("version_history", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="staff_signed_document_copy", to="configurations.versionhistory")),
                ("workflow_event", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="staff_signed_document_copy", to="workflows.workflowevent")),
            ],
            options={
                "db_table": "staff_signed_document_copies",
                "ordering": ["created_at", "staff_signed_document_copy_id"],
                "indexes": [models.Index(fields=["loan_application", "loan_document", "created_at"], name="idx_staff_signed_current")],
            },
        ),
    ]
