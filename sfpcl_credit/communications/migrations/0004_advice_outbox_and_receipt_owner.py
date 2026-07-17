import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class MoveReceiptState(migrations.operations.base.Operation):
    """Transfer Django state ownership without touching the retained table."""

    reversible = True
    reduces_to_sql = False

    def state_forwards(self, app_label, state):
        model_state = state.models.pop(
            ("disbursements", "disbursementadvicedeliveryreceipt")
        )
        model_state.app_label = "communications"
        state.models[("communications", model_state.name_lower)] = model_state
        state.reload_models(
            {
                ("disbursements", "disbursementadviceintent"),
                ("communications", model_state.name_lower),
            },
            delay=True,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        return None

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return None

    def describe(self):
        return "Move advice delivery receipt state ownership to communications"

    @property
    def migration_name_fragment(self):
        return "move_advice_receipt_state"


class Migration(migrations.Migration):
    dependencies = [
        ("communications", "0003_notification"),
        (
            "disbursements",
            "0007_remove_disbursement_disb_success_evidence_complete_and_more",
        ),
    ]

    operations = [
        MoveReceiptState(),
        migrations.CreateModel(
            name="CommunicationDeliveryOutbox",
            fields=[
                (
                    "outbox_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("communication_id", models.UUIDField(unique=True)),
                ("idempotency_key", models.CharField(max_length=255, unique=True)),
                ("channel", models.CharField(max_length=40)),
                ("recipient_address", models.CharField(max_length=255)),
                ("recipient_digest", models.CharField(max_length=64)),
                ("template_code_snapshot", models.CharField(max_length=120)),
                ("template_version_snapshot", models.CharField(max_length=40)),
                ("template_checksum_sha256", models.CharField(max_length=64)),
                ("subject_snapshot", models.CharField(max_length=255)),
                ("body_snapshot", models.TextField()),
                ("payload_digest", models.CharField(max_length=64)),
                ("related_entity_type", models.CharField(max_length=80)),
                ("related_entity_id", models.UUIDField()),
                (
                    "delivery_status",
                    models.CharField(default="pending", max_length=40),
                ),
                (
                    "provider_external_message_id",
                    models.CharField(
                        blank=True, max_length=120, null=True, unique=True
                    ),
                ),
                (
                    "provider_delivery_status",
                    models.CharField(blank=True, max_length=40, null=True),
                ),
                (
                    "provider_accepted_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "advice_intent",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="communication_outbox",
                        to="disbursements.disbursementadviceintent",
                    ),
                ),
                (
                    "content_template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="delivery_outboxes",
                        to="communications.contenttemplate",
                    ),
                ),
            ],
            options={
                "db_table": "communication_delivery_outboxes",
                "indexes": [
                    models.Index(
                        fields=["related_entity_type", "related_entity_id"],
                        name="communicati_related_0839f1_idx",
                    ),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="communicationdeliveryoutbox",
            constraint=models.CheckConstraint(
                check=(
                    ~models.Q(idempotency_key="")
                    & ~models.Q(channel="")
                    & ~models.Q(recipient_address="")
                    & ~models.Q(recipient_digest="")
                    & ~models.Q(template_code_snapshot="")
                    & ~models.Q(template_version_snapshot="")
                    & ~models.Q(template_checksum_sha256="")
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
                        delivery_status="pending",
                        provider_accepted_at__isnull=True,
                        provider_delivery_status__isnull=True,
                        provider_external_message_id__isnull=True,
                    )
                    | (
                        models.Q(
                            delivery_status="sent",
                            provider_accepted_at__isnull=False,
                            provider_delivery_status__isnull=False,
                            provider_external_message_id__isnull=False,
                        )
                        & ~models.Q(provider_external_message_id="")
                        & ~models.Q(provider_delivery_status="")
                    )
                ),
                name="communication_outbox_provider_result_complete",
            ),
        ),
    ]
