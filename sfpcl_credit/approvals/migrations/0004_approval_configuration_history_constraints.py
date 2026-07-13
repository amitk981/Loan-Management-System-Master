from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("approvals", "0003_approvalmatrixrule_sanctioncommittee")]

    operations = [
        migrations.AddIndex(
            model_name="sanctioncommittee",
            index=models.Index(fields=["status", "effective_from", "effective_to"], name="idx_committee_effective"),
        ),
        migrations.AddConstraint(
            model_name="approvalmatrixrule",
            constraint=models.CheckConstraint(check=models.Q(("status__in", ["active", "superseded", "inactive"])), name="approval_rule_valid_status"),
        ),
        migrations.AddConstraint(
            model_name="approvalmatrixrule",
            constraint=models.CheckConstraint(check=models.Q(("effective_to__isnull", True), ("effective_to__gte", models.F("effective_from")), _connector="OR"), name="approval_rule_valid_dates"),
        ),
        migrations.AddConstraint(
            model_name="approvalmatrixrule",
            constraint=models.CheckConstraint(check=models.Q(("amount_min__isnull", True), ("amount_max__isnull", True), ("amount_max__gte", models.F("amount_min")), _connector="OR"), name="approval_rule_valid_amounts"),
        ),
        migrations.AddConstraint(
            model_name="sanctioncommittee",
            constraint=models.CheckConstraint(check=models.Q(("status__in", ["active", "superseded", "inactive"])), name="committee_valid_status"),
        ),
        migrations.AddConstraint(
            model_name="sanctioncommittee",
            constraint=models.CheckConstraint(check=models.Q(("effective_to__isnull", True), ("effective_to__gte", models.F("effective_from")), _connector="OR"), name="committee_valid_dates"),
        ),
        migrations.AddConstraint(
            model_name="sanctioncommittee",
            constraint=models.CheckConstraint(check=models.Q(models.Q(("cfo_user", models.F("director_1_user")), _negated=True), models.Q(("cfo_user", models.F("director_2_user")), _negated=True), models.Q(("director_1_user", models.F("director_2_user")), _negated=True)), name="committee_distinct_members"),
        ),
    ]
