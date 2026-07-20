from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "configurations",
            "0006_interestrateconfig_borrowerratenoticeobligation_and_more",
        )
    ]

    operations = [
        migrations.AddConstraint(
            model_name="interestrateconfig",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        status="proposed",
                        approved_by_user__isnull=True,
                        activated_at__isnull=True,
                        activation_idempotency_key__isnull=True,
                        activation_payload_digest="",
                    )
                    | (
                        models.Q(
                            status="active",
                            approved_by_user__isnull=False,
                            activated_at__isnull=False,
                            activation_idempotency_key__isnull=False,
                            activation_payload_digest__regex=r"^[0-9a-f]{64}$",
                        )
                        & ~models.Q(activation_idempotency_key="")
                        & ~models.Q(approved_by_user=models.F("created_by_user"))
                    )
                ),
                name="rate_status_approval_coherent",
            ),
        ),
        migrations.AlterModelOptions(
            name="interestrateconfig",
            options={
                "base_manager_name": "objects",
                "ordering": ["-effective_from", "-interest_rate_config_id"],
            },
        ),
    ]
