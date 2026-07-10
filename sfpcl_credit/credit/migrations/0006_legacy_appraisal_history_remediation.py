from django.db import migrations


DECISION_DESTINATIONS = {
    "reviewed": "reviewed",
    "returned": "draft",
    "rejected": "rejected",
}


def backfill_missing_latest_review(apps, schema_editor):
    Appraisal = apps.get_model("credit", "LoanAppraisalNote")
    Decision = apps.get_model("credit", "AppraisalReviewDecision")

    for appraisal in Appraisal.objects.all().iterator():
        if appraisal.prerequisite_provenance != "legacy_unverified":
            continue
        to_state = DECISION_DESTINATIONS.get(appraisal.last_review_decision)
        if (
            to_state is None
            or not appraisal.review_comments.strip()
            or appraisal.reviewed_by_user_id is None
            or appraisal.reviewed_at is None
        ):
            continue

        latest_projection_exists = Decision.objects.filter(
            loan_appraisal_note_id=appraisal.pk,
            decision=appraisal.last_review_decision,
            review_comments=appraisal.review_comments,
            reviewer_user_id=appraisal.reviewed_by_user_id,
            decided_at=appraisal.reviewed_at,
            from_state="review_pending",
            to_state=to_state,
        ).exists()
        if latest_projection_exists:
            continue

        Decision.objects.create(
            loan_appraisal_note_id=appraisal.pk,
            decision=appraisal.last_review_decision,
            review_comments=appraisal.review_comments,
            reviewer_user_id=appraisal.reviewed_by_user_id,
            decided_at=appraisal.reviewed_at,
            from_state="review_pending",
            to_state=to_state,
            history_provenance="legacy_latest_only",
        )


def preserve_history_on_reverse(apps, schema_editor):
    # This correction is forward-only: immutable historical evidence is not deleted.
    pass


class Migration(migrations.Migration):
    dependencies = [("credit", "0005_appraisalreviewdecision")]

    operations = [
        migrations.RunPython(
            backfill_missing_latest_review,
            preserve_history_on_reverse,
        )
    ]
