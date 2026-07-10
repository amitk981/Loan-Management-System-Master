import django.db.models.deletion
from django.db import migrations, models


def backfill_witness_evidence(apps, schema_editor):
    Witness = apps.get_model("applications", "Witness")
    AuditLog = apps.get_model("identity", "AuditLog")
    Shareholding = apps.get_model("members", "Shareholding")

    for witness in Witness.objects.filter(verification_shareholding__isnull=True).iterator():
        audits = AuditLog.objects.filter(
            action="applications.witness.created",
            entity_type="witness",
            entity_id=witness.witness_id,
        ).order_by("created_at", "audit_log_id")
        folios = {
            payload.get("folio_number")
            for payload in audits.values_list("new_value_json", flat=True)
            if isinstance(payload, dict) and payload.get("folio_number")
        }
        if len(folios) != 1:
            continue
        folio_number = next(iter(folios))
        matches = list(
            Shareholding.objects.filter(
                member_id=witness.member_id,
                folio_number=folio_number,
            ).values_list("shareholding_id", flat=True)[:2]
        )
        if len(matches) != 1:
            continue
        Witness.objects.filter(pk=witness.pk, verification_shareholding__isnull=True).update(
            verification_shareholding_id=matches[0],
            verification_folio_number=folio_number,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0011_witness"),
        ("identity", "0003_portal_member_auth"),
        ("members", "0008_cancelledcheque_bankaccount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="witness",
            name="verification_folio_number",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="witness",
            name="verification_shareholding",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="verified_witnesses",
                to="members.shareholding",
            ),
        ),
        migrations.AlterField(
            model_name="witness",
            name="loan_application",
            field=models.ForeignKey(
                db_index=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="witnesses",
                to="applications.loanapplication",
            ),
        ),
        migrations.AlterField(
            model_name="witness",
            name="pan_hash",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="witness",
            name="aadhaar_hash",
            field=models.CharField(max_length=128),
        ),
        migrations.RunPython(backfill_witness_evidence, migrations.RunPython.noop),
    ]
