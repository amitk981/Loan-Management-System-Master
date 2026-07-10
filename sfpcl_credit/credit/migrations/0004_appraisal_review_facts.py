from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("credit", "0003_appraisal_prerequisite_snapshots"),
    ]

    operations = [
        migrations.AddField(
            model_name="loanappraisalnote",
            name="last_review_decision",
            field=models.CharField(blank=True, max_length=60),
        ),
        migrations.AddField(
            model_name="loanappraisalnote",
            name="review_comments",
            field=models.TextField(blank=True),
        ),
    ]
