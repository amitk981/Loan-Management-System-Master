from django.db import migrations, models
from django.utils import timezone


def _local_iso(value):
    return timezone.localtime(value).isoformat() if value is not None else None


def _utc_iso(value):
    return value.isoformat().replace("+00:00", "Z") if value is not None else None


def _eligibility_projection(assessment):
    return {
        "eligibility_assessment_id": str(assessment.pk),
        "loan_application_id": str(assessment.loan_application_id),
        "member_active_check": assessment.member_active_check,
        "default_check": assessment.default_check,
        "document_check": assessment.document_check,
        "terms_acceptance_check": assessment.terms_acceptance_check,
        "purpose_check": assessment.purpose_check,
        "nominee_check": assessment.nominee_check,
        "overall_result": assessment.overall_result,
        "assessment_notes": assessment.assessment_notes,
        "assessed_by_user_id": str(assessment.assessed_by_user_id),
        "assessed_at": _local_iso(assessment.assessed_at),
    }


def _loan_limit_projection(assessment):
    exception_required = assessment.exception_required_flag
    return {
        "loan_limit_assessment_id": str(assessment.pk),
        "loan_application_id": str(assessment.loan_application_id),
        "member_id": str(assessment.member_id),
        "shareholding_id": (
            str(assessment.shareholding_id) if assessment.shareholding_id else None
        ),
        "number_of_shares": assessment.number_of_shares,
        "valuation_per_share": f"{assessment.valuation_per_share:.2f}",
        "share_limit_percentage": (
            f"{assessment.share_limit_percentage:.4f}"
            if assessment.share_limit_percentage is not None
            else None
        ),
        "per_share_cap_amount": (
            f"{assessment.per_share_cap_amount:.2f}"
            if assessment.per_share_cap_amount is not None
            else None
        ),
        "shareholding_based_limit_amount": (
            f"{assessment.shareholding_based_limit_amount:.2f}"
        ),
        "land_area_acres": f"{assessment.land_area_acres:.2f}",
        "scale_of_finance_per_acre_amount": (
            f"{assessment.scale_of_finance_per_acre_amount:.2f}"
        ),
        "land_based_limit_amount": f"{assessment.land_based_limit_amount:.2f}",
        "final_eligible_loan_amount": f"{assessment.final_eligible_loan_amount:.2f}",
        "requested_amount": f"{assessment.requested_amount:.2f}",
        "amount_within_limit_flag": assessment.amount_within_limit_flag,
        "exception_required_flag": exception_required,
        "calculation_rule_version": assessment.calculation_rule_version,
        "calculated_by_user_id": (
            str(assessment.calculated_by_user_id)
            if assessment.calculated_by_user_id
            else None
        ),
        "calculated_at": _utc_iso(assessment.calculated_at),
        "configuration_source": {
            "type": "loan_policy_config",
            "loan_policy_config_id": (
                str(assessment.policy_config_id_snapshot)
                if assessment.policy_config_id_snapshot
                else None
            ),
            "policy_name": assessment.policy_name_snapshot or None,
            "board_approval_reference": (
                assessment.board_approval_reference_snapshot or None
            ),
        },
        "warnings": (
            [
                {
                    "code": "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
                    "message": "Requested amount exceeds final eligible loan amount.",
                }
            ]
            if exception_required
            else []
        ),
    }


def pin_safe_legacy_appraisals(apps, schema_editor):
    Appraisal = apps.get_model("credit", "LoanAppraisalNote")
    Eligibility = apps.get_model("credit", "EligibilityAssessment")
    LoanLimit = apps.get_model("credit", "LoanLimitAssessment")
    AuditLog = apps.get_model("identity", "AuditLog")

    for appraisal in Appraisal.objects.all().iterator():
        eligibility = Eligibility.objects.filter(
            pk=appraisal.eligibility_assessment_id_snapshot,
            loan_application_id=appraisal.loan_application_id,
        ).first()
        loan_limit = LoanLimit.objects.filter(
            pk=appraisal.loan_limit_assessment_id_snapshot,
            loan_application_id=appraisal.loan_application_id,
        ).first()
        if eligibility is None or loan_limit is None:
            continue
        later_success = AuditLog.objects.filter(
            action__in=("eligibility.assessed", "loan_limit.calculated"),
            entity_id__in=(eligibility.pk, loan_limit.pk),
            created_at__gt=appraisal.prepared_at,
        ).exists()
        source_time_after_create = (
            eligibility.assessed_at > appraisal.prepared_at
            or loan_limit.calculated_at > appraisal.prepared_at
        )
        if later_success or source_time_after_create:
            continue
        appraisal.eligibility_snapshot_json = _eligibility_projection(eligibility)
        appraisal.loan_limit_snapshot_json = _loan_limit_projection(loan_limit)
        appraisal.prerequisite_provenance = "verified"
        appraisal.save(
            update_fields=(
                "eligibility_snapshot_json",
                "loan_limit_snapshot_json",
                "prerequisite_provenance",
            )
        )


class Migration(migrations.Migration):
    dependencies = [("credit", "0002_riskassessment_loanappraisalnote")]

    operations = [
        migrations.AddField(
            model_name="loanappraisalnote",
            name="eligibility_snapshot_json",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="loanappraisalnote",
            name="loan_limit_snapshot_json",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="loanappraisalnote",
            name="prerequisite_provenance",
            field=models.CharField(
                db_index=True, default="legacy_unverified", max_length=60
            ),
        ),
        migrations.AddField(
            model_name="loanappraisalnote",
            name="repayment_capacity_notes",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="loanappraisalnote",
            name="submission_remarks",
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(pin_safe_legacy_appraisals, migrations.RunPython.noop),
    ]
