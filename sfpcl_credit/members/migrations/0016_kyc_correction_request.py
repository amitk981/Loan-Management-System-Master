from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("compliance", "0003_kyc_review_tracker"),
        ("documents", "0005_deterministic_document_template_constraints"),
        ("identity", "0004_auditlog_selector_manifest_sha256"),
        ("members", "0015_member_aadhaar_last4"),
    ]

    operations = [
        migrations.CreateModel(
            name="KycCorrectionRequest",
            fields=[
                (
                    "kyc_correction_request_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("requested_fields_json", models.JSONField(default=list)),
                ("proposed_values_json", models.JSONField(default=dict)),
                ("reason", models.TextField()),
                ("status", models.CharField(db_index=True, default="submitted", max_length=40)),
                ("rejection_reason", models.TextField(blank=True)),
                ("internal_notes", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("review_started_at", models.DateTimeField(blank=True, null=True)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "identity_change_request",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="portal_kyc_correction",
                        to="members.memberidentitychangerequest",
                    ),
                ),
                (
                    "kyc_review",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="correction_requests",
                        to="compliance.kycreview",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="kyc_correction_requests",
                        to="members.member",
                    ),
                ),
                (
                    "portal_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="kyc_correction_requests",
                        to="identity.portalaccount",
                    ),
                ),
                (
                    "reviewed_by_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reviewed_kyc_correction_requests",
                        to="identity.user",
                    ),
                ),
                (
                    "evidence_documents",
                    models.ManyToManyField(
                        related_name="kyc_correction_requests", to="documents.documentfile"
                    ),
                ),
            ],
            options={
                "db_table": "kyc_correction_requests",
                "ordering": ["-submitted_at", "-kyc_correction_request_id"],
            },
        ),
        migrations.AddConstraint(
            model_name="kyccorrectionrequest",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("status__in", ("submitted", "under_review", "approved", "rejected"))
                ),
                name="kyc_correction_status_bounded",
            ),
        ),
        migrations.AddIndex(
            model_name="kyccorrectionrequest",
            index=models.Index(
                fields=["member", "status"], name="idx_kyc_corr_member_status"
            ),
        ),
    ]
