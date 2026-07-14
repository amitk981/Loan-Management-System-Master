import uuid

from django.db import migrations, models

import sfpcl_credit.approvals.models


def populate_register_source_fields(apps, schema_editor):
    register = apps.get_model("approvals", "CreditSanctionRegisterEntry")
    communication_model = apps.get_model("communications", "Communication")
    audit_model = apps.get_model("identity", "AuditLog")
    for row in register.objects.select_related(
        "approval_case", "sanction_decision"
    ).iterator():
        row.entry_number = f"CSR-{row.pk}"
        row.approver_decisions_json = [
            {
                "approval_action_id": str(action.pk),
                "user_id": str(action.approver_user_id),
                "full_name": action.approver_user.full_name,
                "role_code": action.approver_role_code,
                "decision": action.decision,
                "comments": action.comments or "",
                "acted_at": action.acted_at.isoformat().replace("+00:00", "Z"),
            }
            for action in row.approval_case.actions.select_related(
                "approver_user"
            ).filter(decision__in=("approved", "rejected"))
        ]
        communication = communication_model.objects.filter(
            related_entity_type="approval_case",
            related_entity_id=row.approval_case_id,
        ).first()
        row.communication_json = (
            {
                "communication_id": str(communication.pk),
                "status": communication.delivery_status,
                "sent_at": (
                    communication.sent_at.isoformat().replace("+00:00", "Z")
                    if communication.sent_at else None
                ),
            }
            if communication else None
        )
        row.terminal_facts_json = {
            "rejection_reason": (
                row.reasons if row.decision == "rejected" else None
            ),
            "conditions": (
                row.sanction_decision.conditions_precedent or None
                if row.sanction_decision_id else None
            ),
        }
        row.save(update_fields=[
            "entry_number", "approver_decisions_json", "communication_json",
            "terminal_facts_json",
        ])

    exception_register = apps.get_model("approvals", "ExceptionRegisterEntry")
    for row in exception_register.objects.select_related("approval_case").iterator():
        facts = row.approval_case.appraisal_facts_json or {}
        audit = audit_model.objects.filter(
            action="exception_register.created", entity_id=row.pk
        ).select_related("actor_user").first()
        row.source_facts_json = {
            "borrower_name": (facts.get("borrower") or {}).get("name"),
            "financial_impact": (facts.get("loan_amounts") or {}).get(
                "recommended_amount"
            ),
            "requested_by": (
                {
                    "user_id": str(audit.actor_user_id),
                    "full_name": audit.actor_user.full_name,
                }
                if audit and audit.actor_user_id else None
            ),
        }
        row.save(update_fields=["source_facts_json"])


class Migration(migrations.Migration):
    dependencies = [
        ("approvals", "0018_creditsanctionregisterentry_source_review_facts_json"),
        ("communications", "0003_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="creditsanctionregisterentry",
            name="entry_number",
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="creditsanctionregisterentry",
            name="approver_decisions_json",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="creditsanctionregisterentry",
            name="communication_json",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="creditsanctionregisterentry",
            name="terminal_facts_json",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="exceptionregisterentry",
            name="source_facts_json",
            field=models.JSONField(default=dict),
        ),
        migrations.RunPython(
            populate_register_source_fields, migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="creditsanctionregisterentry",
            name="entry_number",
            field=models.CharField(
                default=sfpcl_credit.approvals.models.generate_credit_sanction_register_entry_number,
                editable=False,
                max_length=40,
                unique=True,
            ),
        ),
    ]
