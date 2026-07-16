import django.db.models.deletion
from django.db import migrations, models
from django.db.models.functions import Lower, Trim


class Migration(migrations.Migration):

    dependencies = [
        ("communications", "0003_notification"),
        ("finance", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sapcustomercode",
            name="confirmation_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="sapcustomerprofilerequest",
            name="completion_reused_existing_code",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sapcustomerprofilerequest",
            name="sanction_decision_id_snapshot",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sapcustomerprofilerequest",
            name="sanction_approval_case_id_snapshot",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sapcustomerprofilerequest",
            name="sap_customer_code",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="completed_profile_requests",
                to="finance.sapcustomercode",
            ),
        ),
        migrations.AddField(
            model_name="sapcustomerprofilerequest",
            name="sent_communication",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sap_customer_profile_requests",
                to="communications.communication",
            ),
        ),
        migrations.AddField(
            model_name="sapcustomerprofilerequest",
            name="sent_remarks",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="sapcustomerprofilerequest",
            name="sent_task",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sap_customer_profile_requests",
                to="communications.notification",
            ),
        ),
        migrations.AddConstraint(
            model_name="sapcustomercode",
            constraint=models.CheckConstraint(
                check=~models.Q(sap_customer_code=""),
                name="sap_customer_code_not_blank",
            ),
        ),
        migrations.AddConstraint(
            model_name="sapcustomercode",
            constraint=models.UniqueConstraint(
                Lower(Trim("sap_customer_code")), name="uniq_sap_customer_code_ci"
            ),
        ),
        migrations.AddConstraint(
            model_name="sapcustomerprofilerequest",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        request_status="draft",
                        sent_at__isnull=True,
                        sent_communication__isnull=True,
                        sent_task__isnull=True,
                        completed_at__isnull=True,
                        sap_customer_code__isnull=True,
                        completion_reused_existing_code__isnull=True,
                    )
                    | models.Q(
                        request_status="sent",
                        sent_at__isnull=False,
                        sent_communication__isnull=False,
                        sent_task__isnull=False,
                        completed_at__isnull=True,
                        sap_customer_code__isnull=True,
                        completion_reused_existing_code__isnull=True,
                    )
                    | models.Q(
                        request_status="completed",
                        sent_at__isnull=False,
                        sent_communication__isnull=False,
                        sent_task__isnull=False,
                        completed_at__isnull=False,
                        sap_customer_code__isnull=False,
                        completion_reused_existing_code__isnull=False,
                    )
                ),
                name="sap_request_lifecycle_evidence",
            ),
        ),
    ]
