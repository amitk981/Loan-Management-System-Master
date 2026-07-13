from django.db import migrations, models


def backfill_exact_case_read_actors(apps, schema_editor):
    ApprovalCase = apps.get_model("approvals", "ApprovalCase")
    ReadActor = apps.get_model("approvals", "ApprovalCaseRequiredApprover")
    ApprovalAction = apps.get_model("approvals", "ApprovalAction")
    ReadActor.objects.all().delete()
    rows = []
    for case in ApprovalCase.objects.all().iterator(chunk_size=200):
        required = case.required_approvers_json
        excluded_ids = {
            str(item.get("user_id"))
            for item in case.excluded_approvers_json
            if isinstance(item, dict) and item.get("user_id")
        }
        committee = case.committee_projection_json or {}
        director_candidates = [
            str(user_id) for user_id in committee.get("director_user_ids", [])
        ]
        actor_ids = set()
        used_ids = set()
        if isinstance(required, list):
            for approver in required:
                if not isinstance(approver, dict) or not approver.get("user_id"):
                    continue
                user_id = str(approver["user_id"])
                actor_ids.add(user_id)
                if user_id not in excluded_ids and user_id not in used_ids:
                    used_ids.add(user_id)
                    continue
                if approver.get("role_code") != "director":
                    continue
                replacement_id = next(
                    (
                        candidate_id
                        for candidate_id in director_candidates
                        if candidate_id not in excluded_ids
                        and candidate_id not in used_ids
                    ),
                    None,
                )
                if replacement_id:
                    actor_ids.add(replacement_id)
                    used_ids.add(replacement_id)
        actor_ids.update(
            str(user_id)
            for user_id in ApprovalAction.objects.filter(
                approval_case_id=case.pk
            ).values_list("approver_user_id", flat=True)
        )
        rows.extend(
            ReadActor(approval_case_id=case.pk, user_id=user_id)
            for user_id in sorted(actor_ids)
        )
    ReadActor.objects.bulk_create(rows, batch_size=500)


class Migration(migrations.Migration):
    dependencies = [("approvals", "0012_approvalconflictdeclaration_and_more")]

    operations = [
        migrations.RemoveConstraint(
            model_name="approvalconflictdeclaration",
            name="approval_conflict_reason_nonblank",
        ),
        migrations.AddConstraint(
            model_name="approvalconflictdeclaration",
            constraint=models.CheckConstraint(
                check=models.Q(reason__regex=r"\S"),
                name="approval_conflict_reason_nonblank",
            ),
        ),
        migrations.RunPython(
            backfill_exact_case_read_actors,
            migrations.RunPython.noop,
        ),
    ]
