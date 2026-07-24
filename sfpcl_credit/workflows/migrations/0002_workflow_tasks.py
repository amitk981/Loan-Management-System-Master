import django.db.models.deletion
import django.utils.timezone
import sfpcl_credit.workflows.models
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("identity", "0001_initial"),
        ("workflows", "0001_canonical_workflow_event"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkflowTask",
            fields=[
                ("workflow_task_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("task_reference", models.CharField(default=sfpcl_credit.workflows.models.workflow_task_reference, max_length=40, unique=True)),
                ("task_type", models.CharField(db_index=True, max_length=80)),
                ("linked_entity_type", models.CharField(db_index=True, max_length=100)),
                ("linked_entity_id", models.UUIDField(db_index=True)),
                ("title", models.CharField(max_length=255)),
                ("borrower_name", models.CharField(blank=True, max_length=255)),
                ("borrower_type", models.CharField(blank=True, db_index=True, max_length=80)),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ("special_case", models.BooleanField(db_index=True, default=False)),
                ("exception_required", models.BooleanField(db_index=True, default=False)),
                ("assigned_role_code", models.CharField(db_index=True, max_length=80)),
                ("assigned_team_code", models.CharField(blank=True, db_index=True, max_length=80)),
                ("priority", models.CharField(db_index=True, default="normal", max_length=20)),
                ("status", models.CharField(db_index=True, default="open", max_length=20)),
                ("current_status", models.CharField(db_index=True, max_length=100)),
                ("due_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("overdue_days", models.PositiveIntegerField(default=0)),
                ("blocked", models.BooleanField(db_index=True, default=False)),
                ("blocked_reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("assigned_to_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="assigned_workflow_tasks", to="identity.user")),
            ],
            options={"db_table": "workflow_tasks", "ordering": ["-priority", "due_at", "task_reference"]},
        ),
        migrations.CreateModel(
            name="WorkflowTaskComment",
            fields=[
                ("workflow_task_comment_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("comment", models.TextField()),
                ("created_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("author_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="workflow_task_comments", to="identity.user")),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="comments", to="workflows.workflowtask")),
            ],
            options={"db_table": "workflow_task_comments", "ordering": ["created_at", "workflow_task_comment_id"]},
        ),
        migrations.AddIndex(model_name="workflowtask", index=models.Index(fields=["assigned_role_code", "status", "due_at"], name="idx_task_role_status_due")),
        migrations.AddIndex(model_name="workflowtask", index=models.Index(fields=["assigned_to_user", "status", "due_at"], name="idx_task_user_status_due")),
        migrations.AddIndex(model_name="workflowtask", index=models.Index(fields=["linked_entity_type", "linked_entity_id"], name="idx_task_linked_entity")),
        migrations.AddConstraint(model_name="workflowtask", constraint=models.UniqueConstraint(condition=models.Q(("status", "open")), fields=("linked_entity_type", "linked_entity_id", "task_type"), name="uniq_open_workflow_task")),
        migrations.AddConstraint(model_name="workflowtask", constraint=models.CheckConstraint(check=models.Q(("task_type__in", ("appraisal", "completeness_check", "default_review", "disbursement", "document_verification", "repayment_posting", "sanction", "sap_setup"))), name="workflow_task_type_valid")),
        migrations.AddConstraint(model_name="workflowtask", constraint=models.CheckConstraint(check=models.Q(("priority__in", ("critical", "high", "normal"))), name="workflow_task_priority_valid")),
        migrations.AddConstraint(model_name="workflowtask", constraint=models.CheckConstraint(check=models.Q(("status__in", ("closed", "open"))), name="workflow_task_status_valid")),
        migrations.AddConstraint(model_name="workflowtask", constraint=models.CheckConstraint(check=models.Q(models.Q(("closed_at__isnull", True), ("status", "open")), models.Q(("closed_at__isnull", False), ("status", "closed")), _connector="OR"), name="workflow_task_closed_at_coherent")),
    ]
