from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("disbursements", "0008_initial_loan_payment_sap_posting"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="initialloanpaymentsapposting",
            name="initial_sap_posting_lifecycle",
        ),
        migrations.AddConstraint(
            model_name="initialloanpaymentsapposting",
            constraint=models.CheckConstraint(
                check=models.Q(
                    posting_status="pending",
                    sap_posting_reference__isnull=True,
                    posted_at__isnull=True,
                ),
                name="initial_sap_posting_lifecycle",
            ),
        ),
    ]
