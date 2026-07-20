from django.db import migrations, models


def create_postgresql_immutability_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        CREATE FUNCTION interest_policy_immutable_guard() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'Approved calculation configuration is immutable.'
                USING ERRCODE = '23514';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    schema_editor.execute(
        """
        CREATE TRIGGER interest_policy_immutable_guard
        BEFORE UPDATE OR DELETE ON interest_invoice_configurations
        FOR EACH ROW EXECUTE FUNCTION interest_policy_immutable_guard();
        """
    )


def drop_postgresql_immutability_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        "DROP TRIGGER IF EXISTS interest_policy_immutable_guard "
        "ON interest_invoice_configurations;"
    )
    schema_editor.execute(
        "DROP FUNCTION IF EXISTS interest_policy_immutable_guard();"
    )


class Migration(migrations.Migration):
    dependencies = [("interest", "0004_interest_accounting_owner")]

    operations = [
        migrations.AddField(
            model_name="interestinvoiceconfiguration",
            name="monetary_precision",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=8, null=True
            ),
        ),
        migrations.AddField(
            model_name="interestinvoiceconfiguration",
            name="monetary_rounding_mode",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="interestinvoiceconfiguration",
            name="rounding_application_boundary",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddConstraint(
            model_name="interestinvoiceconfiguration",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(monetary_rounding_mode__isnull=True)
                    | models.Q(
                        monetary_rounding_mode__in=(
                            "half_up",
                            "half_even",
                            "half_down",
                            "down",
                            "up",
                        )
                    )
                ),
                name="interest_policy_rounding_mode_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="interestinvoiceconfiguration",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(monetary_precision__isnull=True)
                    | models.Q(monetary_precision="0.010000")
                ),
                name="interest_policy_money_precision_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="interestinvoiceconfiguration",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(rounding_application_boundary__isnull=True)
                    | models.Q(rounding_application_boundary="whole_decision")
                ),
                name="interest_policy_round_boundary_valid",
            ),
        ),
        migrations.AddField(
            model_name="interestinvoice",
            name="monetary_precision",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=8, null=True
            ),
        ),
        migrations.AddField(
            model_name="interestinvoice",
            name="monetary_rounding_mode",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="interestinvoice",
            name="rounding_application_boundary",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="accrualentry",
            name="monetary_precision",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=8, null=True
            ),
        ),
        migrations.AddField(
            model_name="accrualentry",
            name="monetary_rounding_mode",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="accrualentry",
            name="rounding_application_boundary",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="interestcapitalisation",
            name="calculation_policy_json",
            field=models.JSONField(default=dict),
        ),
        migrations.RunPython(
            create_postgresql_immutability_trigger,
            drop_postgresql_immutability_trigger,
        ),
    ]
