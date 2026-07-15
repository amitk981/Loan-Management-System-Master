from django.db import migrations, models


def mark_legacy_null_makers(apps, schema_editor):
    StampDutyRecord = apps.get_model("legal_documents", "StampDutyRecord")
    NotarisationRecord = apps.get_model("legal_documents", "NotarisationRecord")
    SignatureRecord = apps.get_model("legal_documents", "SignatureRecord")
    StampDutyRecord.objects.filter(prepared_by_user__isnull=True).update(
        legacy_maker_attribution=True
    )
    NotarisationRecord.objects.filter(prepared_by_user__isnull=True).update(
        legacy_maker_attribution=True
    )
    SignatureRecord.objects.filter(captured_by_user__isnull=True).update(
        legacy_maker_attribution=True
    )


class Migration(migrations.Migration):
    dependencies = [("legal_documents", "0009_loandocument_verification_remarks")]

    operations = [
        migrations.AddField(
            model_name="stampdutyrecord",
            name="legacy_maker_attribution",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="notarisationrecord",
            name="legacy_maker_attribution",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="signaturerecord",
            name="legacy_maker_attribution",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(mark_legacy_null_makers, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="stampdutyrecord",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(legacy_maker_attribution=True)
                    | ~models.Q(status__in=["adequate", "insufficient"])
                    | (
                        models.Q(
                            prepared_by_user__isnull=False,
                            verified_by_user__isnull=False,
                        )
                        & ~models.Q(
                            prepared_by_user=models.F("verified_by_user")
                        )
                    )
                ),
                name="stamp_verification_distinct_maker_checker",
            ),
        ),
        migrations.AddConstraint(
            model_name="notarisationrecord",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(legacy_maker_attribution=True)
                    | ~models.Q(status__in=["completed", "rejected"])
                    | (
                        models.Q(
                            prepared_by_user__isnull=False,
                            verified_by_user__isnull=False,
                        )
                        & ~models.Q(
                            prepared_by_user=models.F("verified_by_user")
                        )
                    )
                ),
                name="notary_verification_distinct_maker_checker",
            ),
        ),
        migrations.AddConstraint(
            model_name="signaturerecord",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(legacy_maker_attribution=True)
                    | models.Q(mismatch_resolution_type__isnull=True)
                    | (
                        models.Q(
                            captured_by_user__isnull=False,
                            verified_by_user__isnull=False,
                        )
                        & ~models.Q(
                            captured_by_user=models.F("verified_by_user")
                        )
                    )
                ),
                name="signature_resolution_distinct_maker_checker",
            ),
        ),
    ]
