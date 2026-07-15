import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("identity", "0003_portal_member_auth"),
        ("legal_documents", "0011_final_documentation_approval_sequence"),
        ("members", "0014_remove_memberscopeassignment_uniq_member_scope_assignment_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PortalDocumentationSubmission",
            fields=[
                ("portal_documentation_submission_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("action_code", models.CharField(max_length=120)),
                ("notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("document", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="portal_documentation_submission", to="documents.documentfile")),
                ("loan_application", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="portal_documentation_submissions", to="applications.loanapplication")),
                ("portal_account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="documentation_submissions", to="identity.portalaccount")),
                ("supersedes", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="successor", to="legal_documents.portaldocumentationsubmission")),
                ("uploader_member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="portal_documentation_submissions", to="members.member")),
            ],
            options={
                "db_table": "portal_documentation_submissions",
                "ordering": ["created_at", "portal_documentation_submission_id"],
                "indexes": [models.Index(fields=["loan_application", "action_code", "created_at"], name="idx_portal_doc_app_action")],
                "constraints": [models.CheckConstraint(check=models.Q(("action_code__in", ["cancelled_cheque", "poa", "tri_party_agreement", "sh4", "term_sheet", "loan_agreement", "bank_verification_letter"])), name="portal_doc_action_code_bounded")],
            },
        ),
    ]
