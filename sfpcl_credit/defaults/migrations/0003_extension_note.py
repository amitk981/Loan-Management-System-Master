import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


def grant_extension_permission(apps, schema_editor):
    Permission = apps.get_model("identity", "Permission")
    Role = apps.get_model("identity", "Role")
    RolePermission = apps.get_model("identity", "RolePermission")
    permission, _ = Permission.objects.get_or_create(
        permission_code="defaults.extension.grant",
        defaults={
            "permission_name": "Grant one-year extension",
            "module_name": "defaults",
            "risk_level": "critical",
        },
    )
    for role in Role.objects.filter(role_code="credit_manager"):
        RolePermission.objects.get_or_create(role=role, permission=permission)


def revoke_extension_permission(apps, schema_editor):
    RolePermission = apps.get_model("identity", "RolePermission")
    RolePermission.objects.filter(
        role__role_code="credit_manager",
        permission__permission_code="defaults.extension.grant",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("defaults", "0002_grace_period_assessment"),
        ("legal_documents", "0015_checklist_constraint_state_owner_anchor"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExtensionNote",
            fields=[
                ("extension_note_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("extension_reason", models.TextField()),
                ("extension_start_date", models.DateField()),
                ("extension_end_date", models.DateField(db_index=True)),
                ("status", models.CharField(db_index=True, max_length=60)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("approved_by_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="approved_extension_notes", to="identity.user")),
                ("default_case", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="owned_extension_note", to="defaults.defaultcase")),
                ("loan_account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="extension_notes", to="loans.loanaccount")),
                ("loan_document", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="extension_notes", to="legal_documents.loandocument")),
                ("prepared_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="prepared_extension_notes", to="identity.user")),
            ],
            options={"db_table": "extension_notes", "ordering": ["-created_at", "-extension_note_id"]},
        ),
        migrations.AddField(
            model_name="defaultcase",
            name="extension_note",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="current_for_cases", to="defaults.extensionnote"),
        ),
        migrations.AddConstraint(
            model_name="extensionnote",
            constraint=models.CheckConstraint(check=models.Q(("status__in", ("draft", "approved", "active", "expired"))), name="extension_note_status_bounded"),
        ),
        migrations.AddConstraint(
            model_name="extensionnote",
            constraint=models.CheckConstraint(check=models.Q(("extension_end_date__gt", models.F("extension_start_date"))), name="extension_note_dates_ordered"),
        ),
        migrations.AddConstraint(
            model_name="extensionnote",
            constraint=models.CheckConstraint(check=models.Q(("extension_reason", ""), _negated=True), name="extension_note_reason_required"),
        ),
        migrations.RunPython(grant_extension_permission, revoke_extension_permission),
    ]
