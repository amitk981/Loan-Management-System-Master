from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("approvals", "0006_approvalcase_configuration_snapshot")]

    operations = [
        migrations.AddField(
            model_name="approvalcase", name="amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name="approvalcase", name="excluded_approvers_json",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="approvalcase", name="related_entity_type",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="approvalcase", name="related_entity_id",
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="approvalcase", name="reason_for_approval",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="approvalcase", name="exception_condition_code",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="approvalcase", name="exception_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="approvalcase", name="matrix_projection_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="approvalcase", name="committee_projection_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="approvalcase", name="loan_limit_provenance_json",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
