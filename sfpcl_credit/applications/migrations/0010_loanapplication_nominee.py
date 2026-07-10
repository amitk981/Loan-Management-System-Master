from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0009_loan_limit_policy_snapshot"),
        ("members", "0008_cancelledcheque_bankaccount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="loanapplication",
            name="nominee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="selected_for_loan_applications",
                to="members.nominee",
            ),
        ),
    ]
