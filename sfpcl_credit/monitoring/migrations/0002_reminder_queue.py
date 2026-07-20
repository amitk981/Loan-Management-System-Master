import django.db.models.deletion
import uuid

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0017_bank_decision_terminal_sanction_snapshots"),
        ("communications", "0013_exception_provider_vocabulary"),
        ("identity", "0004_auditlog_selector_manifest_sha256"),
        ("loans", "0008_subsidiary_deduction_reconciliation"),
        ("members", "0014_remove_memberscopeassignment_uniq_member_scope_assignment_and_more"),
        ("monitoring", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reminder",
            fields=[
                ("reminder_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("quarter_end_date", models.DateField(db_index=True)),
                ("reminder_type", models.CharField(db_index=True, max_length=80)),
                ("origin", models.CharField(db_index=True, max_length=20)),
                ("channel", models.CharField(db_index=True, max_length=60)),
                ("message_body", models.TextField(blank=True)),
                ("delivery_status", models.CharField(db_index=True, max_length=60)),
                ("status_reason", models.CharField(blank=True, max_length=120)),
                ("contacted_person", models.CharField(blank=True, max_length=80)),
                ("call_outcome", models.TextField(blank=True)),
                ("next_follow_up_date", models.DateField(blank=True, db_index=True, null=True)),
                ("sent_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("communication", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="monitoring_reminder", to="communications.communication")),
                ("content_template", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="monitoring_reminders", to="communications.contenttemplate")),
                ("created_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_reminders", to="identity.user")),
                ("dpd_status", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="reminders", to="monitoring.dpdstatus")),
                ("loan_account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="reminders", to="loans.loanaccount")),
                ("loan_application", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="reminders", to="applications.loanapplication")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="reminders", to="members.member")),
            ],
            options={"db_table": "reminders", "ordering": ["-quarter_end_date", "loan_account_id", "channel"]},
        ),
        migrations.AddIndex(model_name="reminder", index=models.Index(fields=["quarter_end_date", "delivery_status"], name="idx_reminder_quarter_status")),
        migrations.AddIndex(model_name="reminder", index=models.Index(fields=["member", "created_at"], name="idx_reminder_member_date")),
        migrations.AddConstraint(model_name="reminder", constraint=models.UniqueConstraint(condition=models.Q(("origin", "automatic")), fields=("loan_account", "quarter_end_date", "reminder_type", "channel"), name="uniq_reminder_loan_quarter_reason_channel")),
        migrations.AddConstraint(model_name="reminder", constraint=models.CheckConstraint(check=models.Q(("origin__in", ("automatic", "manual"))), name="reminder_origin_bounded")),
        migrations.AddConstraint(model_name="reminder", constraint=models.CheckConstraint(check=models.Q(("channel__in", ("sms", "email", "phone"))), name="reminder_channel_bounded")),
        migrations.AddConstraint(model_name="reminder", constraint=models.CheckConstraint(check=models.Q(("delivery_status__in", ("queued", "sent", "failed", "cancelled", "call_logged"))), name="reminder_status_bounded")),
        migrations.AddConstraint(
            model_name="reminder",
            constraint=models.CheckConstraint(
                check=(
                    ~models.Q(message_body="")
                    & (
                        (
                            models.Q(
                                channel="phone",
                                content_template__isnull=True,
                                communication__isnull=True,
                                delivery_status="call_logged",
                                sent_at__isnull=False,
                            )
                            & ~models.Q(call_outcome="")
                            & ~models.Q(contacted_person="")
                        )
                        | models.Q(
                            channel__in=("sms", "email"),
                            content_template__isnull=False,
                            communication__isnull=False,
                            delivery_status__in=("queued", "sent", "failed", "cancelled"),
                        )
                    )
                ),
                name="reminder_channel_evidence_complete",
            ),
        ),
    ]
