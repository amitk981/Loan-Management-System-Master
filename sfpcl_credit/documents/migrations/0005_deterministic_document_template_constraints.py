from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0004_loandocument"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="documenttemplate",
            name="doc_template_approval_status",
        ),
        migrations.RemoveConstraint(
            model_name="documenttemplate",
            name="doc_template_borrower_type",
        ),
        migrations.AddConstraint(
            model_name="documenttemplate",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("approval_status__in", ("draft", "approved", "retired"))
                ),
                name="doc_template_approval_status",
            ),
        ),
        migrations.AddConstraint(
            model_name="documenttemplate",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("borrower_type__isnull", True),
                    (
                        "borrower_type__in",
                        ("individual_farmer", "fpc", "fpo"),
                    ),
                    _connector="OR",
                ),
                name="doc_template_borrower_type",
            ),
        ),
    ]
