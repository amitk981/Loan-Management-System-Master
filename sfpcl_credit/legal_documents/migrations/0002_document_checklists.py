import django.db.models.deletion
import uuid

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("legal_documents", "0001_transfer_loan_document_owner"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentChecklist",
            fields=[
                ("document_checklist_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("loan_account_id", models.UUIDField(blank=True, null=True)),
                ("checklist_status", models.CharField(db_index=True, default="in_progress", max_length=80)),
                ("company_secretary_signature_id", models.UUIDField(blank=True, null=True)),
                ("credit_manager_signature_id", models.UUIDField(blank=True, null=True)),
                ("sanction_committee_signature_id", models.UUIDField(blank=True, null=True)),
                ("senior_manager_finance_signature_id", models.UUIDField(blank=True, null=True)),
                ("remarks", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("loan_application", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="legal_document_checklist", to="applications.loanapplication")),
            ],
            options={
                "db_table": "document_checklists",
                "ordering": ["created_at", "document_checklist_id"],
                "indexes": [models.Index(fields=["loan_application", "checklist_status"], name="idx_doc_check_app_status")],
                "constraints": [
                    models.CheckConstraint(check=models.Q(("checklist_status__in", ["in_progress", "cs_approved", "ready"])), name="document_checklist_valid_status"),
                    models.CheckConstraint(check=models.Q(("loan_account_id__isnull", True)), name="checklist_account_requires_epic_009"),
                    models.CheckConstraint(check=models.Q(("company_secretary_signature_id__isnull", True), ("credit_manager_signature_id__isnull", True), ("sanction_committee_signature_id__isnull", True), ("senior_manager_finance_signature_id__isnull", True)), name="checklist_signatures_require_008k"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ChecklistItem",
            fields=[
                ("checklist_item_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("item_code", models.CharField(max_length=120)),
                ("item_label", models.CharField(max_length=255)),
                ("display_order", models.PositiveSmallIntegerField()),
                ("required_flag", models.BooleanField()),
                ("applicable_flag", models.BooleanField()),
                ("completion_status", models.CharField(db_index=True, max_length=60)),
                ("applicability_source", models.CharField(max_length=160)),
                ("applicability_blocker", models.CharField(blank=True, max_length=160, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("remarks", models.TextField(blank=True)),
                ("document_checklist", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="items", to="legal_documents.documentchecklist")),
                ("loan_document", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="checklist_items", to="legal_documents.loandocument")),
                ("verified_by_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="verified_checklist_items", to="identity.user")),
            ],
            options={
                "db_table": "checklist_items",
                "ordering": ["display_order", "checklist_item_id"],
                "indexes": [models.Index(fields=["document_checklist", "completion_status"], name="idx_check_item_list_status")],
                "constraints": [
                    models.UniqueConstraint(fields=("document_checklist", "item_code"), name="unique_checklist_item_code"),
                    models.UniqueConstraint(fields=("document_checklist", "display_order"), name="unique_checklist_item_order"),
                    models.CheckConstraint(check=models.Q(("item_code__in", ["witness_pan_aadhaar", "cancelled_cheque", "blank_dated_cheque", "poa", "tri_party_agreement", "sh4", "cdsl_pledge", "term_sheet", "loan_agreement", "bank_verification_letter", "final_checklist"])), name="checklist_item_valid_code"),
                    models.CheckConstraint(check=models.Q(models.Q(("applicability_blocker__isnull", True), ("applicable_flag", True), ("completion_status__in", ["pending", "complete"]), ("required_flag", True)), models.Q(("applicable_flag", False), ("completion_status", "not_applicable"), ("required_flag", False)), _connector="OR"), name="checklist_item_consistent_state"),
                    models.CheckConstraint(check=models.Q(("completion_status", "complete"), models.Q(("verified_by_user__isnull", True), ("verified_at__isnull", True)), _connector="OR"), name="checklist_item_pending_unverified"),
                ],
            },
        ),
    ]
