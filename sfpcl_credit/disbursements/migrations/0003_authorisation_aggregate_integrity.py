from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("disbursements", "0002_cfc_authorisation_evidence")]

    operations = [
        migrations.AlterField(
            model_name="disbursement",
            name="authorisation_comments",
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.RemoveConstraint(
            model_name="disbursement",
            name="disb_auth_terminal_evidence",
        ),
        migrations.AddConstraint(
            model_name="disbursement",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        authorisation_status="pending",
                        authorised_by_user__isnull=True,
                        authorised_at__isnull=True,
                        authorisation_comments__isnull=True,
                        checker_role_code__isnull=True,
                        checker_team_codes_json__isnull=True,
                        authorisation_action_id__isnull=True,
                        authorisation_evidence_digest__isnull=True,
                        authorisation_request_id__isnull=True,
                        authorisation_ip_address__isnull=True,
                        authorisation_user_agent__isnull=True,
                        authorisation_audit__isnull=True,
                        authorisation_workflow_event__isnull=True,
                    )
                    | models.Q(
                        authorisation_status__in=("approved", "rejected"),
                        authorised_by_user__isnull=False,
                        authorised_at__isnull=False,
                        authorisation_comments__isnull=False,
                        checker_role_code="chief_financial_controller",
                        checker_team_codes_json__isnull=False,
                        authorisation_action_id__isnull=False,
                        authorisation_evidence_digest__isnull=False,
                        authorisation_request_id__isnull=False,
                        authorisation_ip_address__isnull=False,
                        authorisation_user_agent__isnull=False,
                        authorisation_audit__isnull=False,
                        authorisation_workflow_event__isnull=False,
                    )
                )
                & (
                    models.Q(authorisation_comments__isnull=True)
                    | ~models.Q(authorisation_comments="")
                ),
                name="disb_auth_terminal_evidence",
            ),
        ),
        migrations.AddConstraint(
            model_name="disbursement",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(authorisation_status="approved")
                    | models.Q(
                        bank_transfer_status="pending",
                        bank_reference_number__isnull=True,
                        disbursed_at__isnull=True,
                        disbursement_advice_communication__isnull=True,
                        loan_register_updated_flag=False,
                    )
                ),
                name="disb_transfer_requires_approval",
            ),
        ),
    ]
