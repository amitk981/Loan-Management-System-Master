from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("approvals", "0005_approvalconfigurationproposal")]

    operations = [
        migrations.AddField(
            model_name="approvalcase",
            name="approval_matrix_rule",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="snapshotted_approval_cases", to="approvals.approvalmatrixrule",
            ),
        ),
        migrations.AddField(
            model_name="approvalcase", name="approval_matrix_rule_version",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="approvalcase", name="sanction_committee",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="snapshotted_approval_cases", to="approvals.sanctioncommittee",
            ),
        ),
        migrations.AddField(
            model_name="approvalcase", name="sanction_committee_version",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="approvalcase", name="required_approvers_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="approvalcase", name="decision_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="approvalcase", name="version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddConstraint(
            model_name="approvalcase",
            constraint=models.CheckConstraint(
                check=models.Q(version__gte=1), name="approval_case_version_positive"
            ),
        ),
    ]
