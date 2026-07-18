import hashlib
import json

from django.db import migrations, models


LEGACY_ADAPTER_KINDS = ("legacy:pre-outbox", "legacy:retained-outbox")


def _has_complete_frozen_provenance(outbox):
    required = (
        outbox.content_template_id,
        outbox.template_code_snapshot,
        outbox.template_name_snapshot,
        outbox.template_type_snapshot,
        outbox.template_audience_snapshot,
        outbox.template_version_snapshot,
        outbox.template_approval_status_snapshot,
        outbox.template_effective_from_snapshot,
        outbox.template_variables_snapshot,
        outbox.subject_template_snapshot,
        outbox.body_template_snapshot,
        outbox.template_checksum_sha256,
    )
    if any(value is None for value in required):
        return False
    facts = {
        "content_template_id": str(outbox.content_template_id),
        "template_code": outbox.template_code_snapshot,
        "template_name": outbox.template_name_snapshot,
        "template_type": outbox.template_type_snapshot,
        "language_code": outbox.template_language_code_snapshot,
        "audience": outbox.template_audience_snapshot,
        "template_version": outbox.template_version_snapshot,
        "approval_status": outbox.template_approval_status_snapshot,
        "effective_from": outbox.template_effective_from_snapshot.isoformat(),
        "effective_to": (
            outbox.template_effective_to_snapshot.isoformat()
            if outbox.template_effective_to_snapshot
            else None
        ),
        "variables": sorted(outbox.template_variables_snapshot or []),
        "subject_template": outbox.subject_template_snapshot,
        "body_template": outbox.body_template_snapshot,
    }
    checksum = hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return checksum == outbox.template_checksum_sha256


def mark_legacy_template_provenance(apps, schema_editor):
    Attempt = apps.get_model("communications", "CommunicationProviderAttempt")
    Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
    legacy_outbox_ids = set(Attempt.objects.filter(
        adapter_kind__in=LEGACY_ADAPTER_KINDS,
    ).values_list("outbox_id", flat=True))
    post_0005_candidate_ids = set(Attempt.objects.exclude(
        adapter_kind__in=LEGACY_ADAPTER_KINDS,
    ).values_list("outbox_id", flat=True)) - legacy_outbox_ids
    post_0005_outbox_ids = {
        row.pk
        for row in Outbox.objects.filter(pk__in=post_0005_candidate_ids).iterator()
        if _has_complete_frozen_provenance(row)
    }
    Outbox.objects.update(
        template_provenance_status="legacy_partial",
        template_provenance_origin="ambiguous_legacy",
    )
    Outbox.objects.filter(pk__in=post_0005_outbox_ids).update(
        template_provenance_status="verified",
        template_provenance_origin="frozen_before_dispatch",
    )
    Outbox.objects.filter(pk__in=legacy_outbox_ids).update(
        template_provenance_status="legacy_partial",
        template_provenance_origin="legacy_0005",
    )
    Outbox.objects.filter(template_provenance_status="legacy_partial").update(
        content_template_id=None,
        template_code_snapshot=None,
        template_name_snapshot=None,
        template_type_snapshot=None,
        template_language_code_snapshot=None,
        template_audience_snapshot=None,
        template_version_snapshot=None,
        template_approval_status_snapshot=None,
        template_effective_from_snapshot=None,
        template_effective_to_snapshot=None,
        template_variables_snapshot=None,
        subject_template_snapshot=None,
        body_template_snapshot=None,
        template_checksum_sha256=None,
    )


def reverse_legacy_template_provenance(apps, schema_editor):
    Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
    if Outbox.objects.exclude(
        template_provenance_origin="frozen_before_dispatch"
    ).exists():
        raise RuntimeError(
            "Cannot reverse communications 0008 while legacy template provenance exists."
        )


class Migration(migrations.Migration):
    dependencies = [("communications", "0007_portal_advice_download_capability")]

    operations = [
        migrations.RemoveConstraint(
            model_name="communicationdeliveryoutbox",
            name="communication_outbox_complete",
        ),
        migrations.RemoveConstraint(
            model_name="communicationdeliveryoutbox",
            name="communication_outbox_provenance_complete",
        ),
        migrations.AlterField(
            model_name="communicationdeliveryoutbox",
            name="content_template",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name="delivery_outboxes",
                to="communications.contenttemplate",
            ),
        ),
        migrations.AlterField(
            model_name="communicationdeliveryoutbox",
            name="template_code_snapshot",
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name="communicationdeliveryoutbox",
            name="template_version_snapshot",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name="communicationdeliveryoutbox",
            name="template_checksum_sha256",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="communicationdeliveryoutbox",
            name="template_provenance_origin",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.RunPython(
            mark_legacy_template_provenance,
            reverse_legacy_template_provenance,
        ),
        migrations.AlterField(
            model_name="communicationdeliveryoutbox",
            name="template_provenance_origin",
            field=models.CharField(max_length=40),
        ),
        migrations.AddConstraint(
            model_name="communicationdeliveryoutbox",
            constraint=models.CheckConstraint(
                check=(
                    ~models.Q(idempotency_key="")
                    & ~models.Q(channel="")
                    & ~models.Q(recipient_address="")
                    & ~models.Q(recipient_digest="")
                    & models.Q(
                        template_provenance_status__in=("verified", "legacy_partial")
                    )
                    & ~models.Q(subject_snapshot="")
                    & ~models.Q(body_snapshot="")
                    & ~models.Q(payload_digest="")
                    & ~models.Q(related_entity_type="")
                    & models.Q(delivery_status__in=("pending", "sent"))
                ),
                name="communication_outbox_complete",
            ),
        ),
        migrations.AddConstraint(
            model_name="communicationdeliveryoutbox",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        template_provenance_status="verified",
                        template_provenance_origin="frozen_before_dispatch",
                        content_template__isnull=False,
                        template_code_snapshot__isnull=False,
                        template_name_snapshot__isnull=False,
                        template_type_snapshot__isnull=False,
                        template_audience_snapshot__isnull=False,
                        template_version_snapshot__isnull=False,
                        template_approval_status_snapshot__isnull=False,
                        template_effective_from_snapshot__isnull=False,
                        template_variables_snapshot__isnull=False,
                        subject_template_snapshot__isnull=False,
                        body_template_snapshot__isnull=False,
                        template_checksum_sha256__isnull=False,
                    )
                    | models.Q(
                        template_provenance_status="legacy_partial",
                        template_provenance_origin__in=(
                            "legacy_0005",
                            "ambiguous_legacy",
                        ),
                        content_template__isnull=True,
                        template_code_snapshot__isnull=True,
                        template_name_snapshot__isnull=True,
                        template_type_snapshot__isnull=True,
                        template_language_code_snapshot__isnull=True,
                        template_audience_snapshot__isnull=True,
                        template_version_snapshot__isnull=True,
                        template_approval_status_snapshot__isnull=True,
                        template_effective_from_snapshot__isnull=True,
                        template_effective_to_snapshot__isnull=True,
                        template_variables_snapshot__isnull=True,
                        subject_template_snapshot__isnull=True,
                        body_template_snapshot__isnull=True,
                        template_checksum_sha256__isnull=True,
                    )
                ),
                name="communication_outbox_provenance_complete",
            ),
        ),
        migrations.AddConstraint(
            model_name="communicationdeliveryoutbox",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(
                        template_provenance_origin="legacy_0005",
                        template_provenance_status="legacy_partial",
                    )
                    | models.Q(
                        template_provenance_origin="frozen_before_dispatch",
                        template_provenance_status="verified",
                    )
                    | models.Q(
                        template_provenance_origin="ambiguous_legacy",
                        template_provenance_status="legacy_partial",
                    )
                ),
                name="communication_outbox_provenance_origin",
            ),
        ),
    ]
