from datetime import datetime, timedelta, timezone
import hashlib
import json
import uuid
from types import SimpleNamespace

from django.db import IntegrityError, connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone as django_timezone

from sfpcl_credit.processes.advice_evidence_migration import _template_values


class LegacyAdviceTemplateProvenanceContractTests(TransactionTestCase):
    def test_legacy_template_provenance_is_not_upgraded_from_current_template(self):
        template = SimpleNamespace(
            pk=uuid.uuid4(),
            template_code="disbursement_advice_email_v1",
            template_name="Mutable current name",
            template_type="email",
            language_code="en",
            audience="borrower",
            template_version="v1",
            approval_status="approved",
            effective_from=django_timezone.localdate(),
            effective_to=None,
            variables_json=["borrower_name"],
            subject_template="Advice {{ borrower_name }}",
            body_template="Body {{ borrower_name }}",
        )

        self.assertEqual(
            _template_values(template)["template_provenance_status"],
            "legacy_partial",
            "Missing historical provenance cannot be reconstructed from a later template row.",
        )


class LegacyAdviceTemplateProvenanceMigrationTests(TransactionTestCase):
    reset_sequences = True
    migrate_from = [("communications", "0007_portal_advice_download_capability")]
    migrate_to = [("communications", "0008_legacy_template_provenance_closure")]

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_template_drift_downgrades_only_0005_legacy_attempts(self):
        old_apps = self._migrate(self.migrate_from)
        Template = old_apps.get_model("communications", "ContentTemplate")
        Communication = old_apps.get_model("communications", "Communication")
        template = Template.objects.create(
            template_code="disbursement_advice_email_v1",
            template_name="Original delivery template",
            template_type="email",
            language_code="en",
            audience="borrower",
            subject_template="Original subject {{ borrower_name }}",
            body_template="Original body {{ borrower_name }}",
            variables_json=["borrower_name"],
            approval_status="approved",
            template_version="v1",
            effective_from=django_timezone.localdate(),
        )
        legacy_id = uuid.uuid4()
        Communication.objects.create(
            communication_id=legacy_id,
            related_entity_type="disbursement",
            related_entity_id=uuid.uuid4(),
            recipient_party_type="borrower",
            recipient_address="legacy.borrower@example.com",
            channel="email",
            content_template=template,
            subject_snapshot="Original subject Borrower",
            body_snapshot="Original body Borrower",
            sent_at=django_timezone.now(),
            delivery_status="sent",
            external_message_id="manual:legacy-template-drift",
        )
        Template.objects.filter(pk=template.pk).update(
            template_name="Later mutable template",
            subject_template="Later subject {{ borrower_name }}",
            body_template="Later body {{ borrower_name }}",
            variables_json=["borrower_name", "loan_account_number"],
        )
        template.refresh_from_db()

        legacy = self._accepted_outbox(
            old_apps,
            template=template,
            outbox_id=legacy_id,
            adapter_kind="legacy:pre-outbox",
        )
        verified = self._accepted_outbox(
            old_apps,
            template=template,
            outbox_id=uuid.uuid4(),
            adapter_kind="sfpcl_credit.communications.adapters.FakeEmailDeliveryAdapter",
        )
        retained_legacy = self._accepted_outbox(
            old_apps,
            template=template,
            outbox_id=uuid.uuid4(),
            adapter_kind="legacy:retained-outbox",
        )
        historical_pending = self._make_pending_without_attempt(
            old_apps,
            self._accepted_outbox(
                old_apps,
                template=template,
                outbox_id=uuid.uuid4(),
                adapter_kind="temporary:test-setup",
            ),
        )
        new_pending = self._make_pending_without_attempt(
            old_apps,
            self._accepted_outbox(
                old_apps,
                template=template,
                outbox_id=uuid.uuid4(),
                adapter_kind="temporary:test-setup",
            ),
        )
        malformed = self._accepted_outbox(
            old_apps,
            template=template,
            outbox_id=uuid.uuid4(),
            adapter_kind="legacy:retained-outbox",
        )
        OldOutbox = old_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        OldOutbox.objects.filter(pk=malformed.pk).update(
            delivery_status="pending",
            provider_external_message_id=None,
            provider_delivery_status=None,
            provider_accepted_at=None,
            accepted_provider_attempt_id=None,
        )
        unfrozen_post_0005 = self._accepted_outbox(
            old_apps,
            template=template,
            outbox_id=uuid.uuid4(),
            adapter_kind="sfpcl_credit.communications.adapters.FakeEmailDeliveryAdapter",
        )
        OldOutbox.objects.filter(pk=unfrozen_post_0005.pk).update(
            template_checksum_sha256="0" * 64
        )
        legacy_before = self._history_values(old_apps, legacy.pk)
        verified_before = self._stable_outbox_values(old_apps, verified.pk)

        current_apps = self._migrate(self.migrate_to)
        CurrentOutbox = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        corrected = CurrentOutbox.objects.get(pk=legacy.pk)
        untouched = CurrentOutbox.objects.get(pk=verified.pk)

        self.assertEqual(corrected.template_provenance_status, "legacy_partial")
        self.assertEqual(corrected.template_provenance_origin, "legacy_0005")
        self.assertIsNone(corrected.content_template_id)
        self.assertIsNone(corrected.template_name_snapshot)
        self.assertIsNone(corrected.template_variables_snapshot)
        self.assertIsNone(corrected.subject_template_snapshot)
        self.assertIsNone(corrected.body_template_snapshot)
        self.assertIsNone(corrected.template_checksum_sha256)
        self.assertEqual(
            self._history_values(current_apps, corrected.pk), legacy_before
        )
        self.assertEqual(self._stable_outbox_values(current_apps, untouched.pk), verified_before)
        self.assertEqual(
            untouched.template_provenance_origin, "frozen_before_dispatch"
        )
        self.assertEqual(
            CurrentOutbox.objects.get(pk=retained_legacy.pk).template_provenance_status,
            "legacy_partial",
        )
        self.assertEqual(
            CurrentOutbox.objects.get(pk=historical_pending.pk).template_provenance_status,
            "legacy_partial",
        )
        self.assertEqual(
            CurrentOutbox.objects.get(pk=historical_pending.pk).template_provenance_origin,
            "ambiguous_legacy",
        )
        self.assertEqual(
            CurrentOutbox.objects.get(pk=malformed.pk).template_provenance_status,
            "legacy_partial",
        )
        self.assertEqual(
            CurrentOutbox.objects.get(pk=new_pending.pk).template_provenance_status,
            "legacy_partial",
        )
        self.assertEqual(
            CurrentOutbox.objects.get(pk=new_pending.pk).template_provenance_origin,
            "ambiguous_legacy",
        )
        self.assertEqual(
            CurrentOutbox.objects.get(
                pk=unfrozen_post_0005.pk
            ).template_provenance_origin,
            "ambiguous_legacy",
        )
        with self.assertRaises(IntegrityError):
            CurrentOutbox.objects.filter(pk=legacy.pk).update(
                template_provenance_status="verified"
            )
        with self.assertRaisesRegex(
            RuntimeError, "Cannot reverse communications 0008"
        ):
            self._migrate(self.migrate_from)
        current_apps = MigrationExecutor(connection).loader.project_state(
            self.migrate_to
        ).apps
        self.assertEqual(
            self._history_values(current_apps, corrected.pk), legacy_before
        )

    def test_coherent_queued_job_preserves_frozen_provenance_to_current(self):
        old_apps = self._migrate(self.migrate_from)
        Job = old_apps.get_model("communications", "CommunicationDeliveryJob")
        outbox, job = self._queued_outbox_with_job(old_apps, "preserved")
        before_outbox = self._stable_outbox_values(old_apps, outbox.pk)
        before_job = Job.objects.filter(pk=job.pk).values().get()

        current_leaves = MigrationExecutor(connection).loader.graph.leaf_nodes()
        current_apps = self._migrate(current_leaves)
        CurrentOutbox = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        CurrentJob = current_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        )
        migrated_outbox = CurrentOutbox.objects.get(pk=outbox.pk)
        migrated_job = CurrentJob.objects.get(pk=job.pk)

        self.assertEqual(migrated_outbox.template_provenance_status, "verified")
        self.assertEqual(
            migrated_outbox.template_provenance_origin,
            "frozen_before_dispatch",
        )
        self.assertEqual(
            self._stable_outbox_values(current_apps, outbox.pk), before_outbox
        )
        for field, value in before_job.items():
            self.assertEqual(getattr(migrated_job, field), value, field)
        self.assertEqual(migrated_job.communication_id, outbox.communication_id)
        self.assertEqual(migrated_job.idempotency_key, outbox.idempotency_key)
        self.assertEqual(migrated_job.job_kind, "advice")
        current_outbox_manifest = self._all_outbox_values(
            current_apps, outbox.pk
        )
        current_job_manifest = CurrentJob.objects.filter(pk=job.pk).values().get()

        reversed_apps = self._migrate(self.migrate_from)
        self.assertEqual(
            self._stable_outbox_values(reversed_apps, outbox.pk), before_outbox
        )
        ReversedJob = reversed_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        )
        self.assertEqual(
            ReversedJob.objects.filter(pk=job.pk).values().get(), before_job
        )

        reapplied_apps = self._migrate(current_leaves)
        self.assertEqual(
            self._all_outbox_values(reapplied_apps, outbox.pk),
            current_outbox_manifest,
        )
        ReappliedJob = reapplied_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        )
        self.assertEqual(
            ReappliedJob.objects.filter(pk=job.pk).values().get(),
            current_job_manifest,
        )

    def test_blank_required_queued_snapshot_is_not_verified_with_recomputed_checksum(self):
        old_apps = self._migrate(self.migrate_from)
        Outbox = old_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        outbox, _job = self._queued_outbox_with_job(old_apps, "blank-snapshot")
        Outbox.objects.filter(pk=outbox.pk).update(template_name_snapshot="")
        outbox.refresh_from_db()
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
        Outbox.objects.filter(pk=outbox.pk).update(
            template_checksum_sha256=hashlib.sha256(
                json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )

        current_apps = self._migrate(self.migrate_to)
        migrated = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        ).objects.get(pk=outbox.pk)

        self.assertEqual(migrated.template_provenance_status, "legacy_partial")
        self.assertEqual(migrated.template_provenance_origin, "ambiguous_legacy")
        self.assertIsNone(migrated.template_name_snapshot)
        self.assertIsNone(migrated.template_checksum_sha256)
        current_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        ).objects.filter(outbox_id=outbox.pk).delete()

    def test_every_drifted_queued_snapshot_fact_and_malformed_variables_stay_legacy(self):
        old_apps = self._migrate(self.migrate_from)
        Outbox = old_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        mutations = {
            "template_code_snapshot": "different_advice_v1",
            "template_name_snapshot": "Different queued advice",
            "template_type_snapshot": "sms",
            "template_language_code_snapshot": "mr",
            "template_audience_snapshot": "staff",
            "template_version_snapshot": "v2",
            "template_approval_status_snapshot": "draft",
            "template_effective_from_snapshot": (
                django_timezone.localdate() - timedelta(days=1)
            ),
            "template_effective_to_snapshot": django_timezone.localdate(),
            "template_variables_snapshot": ["borrower_name", "loan_account_number"],
            "subject_template_snapshot": "Different {{ borrower_name }}",
            "body_template_snapshot": "Different body {{ borrower_name }}",
        }
        drifted = {}
        for field, value in mutations.items():
            outbox, _job = self._queued_outbox_with_job(old_apps, field[:20])
            Outbox.objects.filter(pk=outbox.pk).update(**{field: value})
            outbox.refresh_from_db()
            Outbox.objects.filter(pk=outbox.pk).update(
                template_checksum_sha256=self._snapshot_checksum(outbox)
            )
            drifted[field] = outbox.pk

        template_target, _ = self._queued_outbox_with_job(
            old_apps, "template-target"
        )
        template_drift, _ = self._queued_outbox_with_job(
            old_apps, "template-id-drift"
        )
        Outbox.objects.filter(pk=template_drift.pk).update(
            content_template_id=template_target.content_template_id
        )
        template_drift.refresh_from_db()
        Outbox.objects.filter(pk=template_drift.pk).update(
            template_checksum_sha256=self._snapshot_checksum(template_drift)
        )
        drifted["content_template_id"] = template_drift.pk

        malformed = {}
        for label, variables in {
            "not-list": "borrower_name",
            "blank-item": ["borrower_name", " "],
            "duplicate": ["borrower_name", "borrower_name"],
            "non-string": ["borrower_name", 7],
        }.items():
            outbox, _job = self._queued_outbox_with_job(old_apps, label)
            Outbox.objects.filter(pk=outbox.pk).update(
                template_variables_snapshot=variables,
                template_checksum_sha256="a" * 64,
            )
            malformed[label] = outbox.pk

        current_apps = self._migrate(self.migrate_to)
        CurrentOutbox = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        for label, outbox_id in {**drifted, **malformed}.items():
            with self.subTest(label=label):
                migrated = CurrentOutbox.objects.get(pk=outbox_id)
                self.assertEqual(migrated.template_provenance_status, "legacy_partial")
                self.assertEqual(
                    migrated.template_provenance_origin, "ambiguous_legacy"
                )
                self.assertIsNone(migrated.content_template_id)
                self.assertIsNone(migrated.template_variables_snapshot)
                self.assertIsNone(migrated.template_checksum_sha256)
        current_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        ).objects.filter(outbox_id__in={*drifted.values(), *malformed.values()}).delete()
        current_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        ).objects.filter(outbox_id=template_target.pk).delete()

    @staticmethod
    def _snapshot_checksum(outbox):
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
        return hashlib.sha256(
            json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def test_only_exact_queued_job_relationship_is_verified(self):
        old_apps = self._migrate(self.migrate_from)
        Outbox = old_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        Job = old_apps.get_model("communications", "CommunicationDeliveryJob")

        unlinked, _ = self._queued_outbox_with_job(
            old_apps, "unlinked", create_job=False
        )
        drifted = {"unlinked": unlinked.pk}
        mutations = {
            "job": ("job", {"attempts": 1}),
            "outbox": ("outbox", {"communication_id": uuid.uuid4()}),
            "advice": ("job", {"advice_intent_id": uuid.uuid4()}),
            "payload": ("job", {"request_payload_digest": "d" * 64}),
            "actor": ("job", {"actor_id": uuid.UUID(int=0)}),
            "request": ("job", {"request_id": " "}),
            "status": ("job", {"status": "failed"}),
            "checksum": ("outbox", {"template_checksum_sha256": "0" * 64}),
            "snapshot": (
                "outbox",
                {"body_template_snapshot": "Changed after queue"},
            ),
        }
        for label, (model_name, values) in mutations.items():
            outbox, job = self._queued_outbox_with_job(old_apps, label)
            model = Job if model_name == "job" else Outbox
            target = job.pk if model_name == "job" else outbox.pk
            model.objects.filter(pk=target).update(**values)
            drifted[label] = outbox.pk

        current_apps = self._migrate(self.migrate_to)
        CurrentOutbox = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        for label, outbox_id in drifted.items():
            with self.subTest(label=label):
                migrated = CurrentOutbox.objects.get(pk=outbox_id)
                self.assertEqual(
                    migrated.template_provenance_status, "legacy_partial"
                )
                self.assertEqual(
                    migrated.template_provenance_origin, "ambiguous_legacy"
                )
                self.assertIsNone(migrated.template_checksum_sha256)
        CurrentJob = current_apps.get_model(
            "communications", "CommunicationDeliveryJob"
        )
        CurrentJob.objects.filter(outbox_id__in=drifted.values()).delete()

    def test_reverse_refuses_legacy_history_and_clean_reapply_preserves_verified_rows(
        self,
    ):
        old_apps = self._migrate(self.migrate_from)
        Template = old_apps.get_model("communications", "ContentTemplate")
        template = Template.objects.create(
            template_code="disbursement_advice_email_v1",
            template_name="Frozen new template",
            template_type="email",
            language_code="en",
            audience="borrower",
            subject_template="Advice {{ borrower_name }}",
            body_template="Body {{ borrower_name }}",
            variables_json=["borrower_name"],
            approval_status="approved",
            template_version="v1",
            effective_from=django_timezone.localdate(),
        )
        verified = self._accepted_outbox(
            old_apps,
            template=template,
            outbox_id=uuid.uuid4(),
            adapter_kind="sfpcl_credit.communications.adapters.FakeEmailDeliveryAdapter",
        )
        before = self._stable_outbox_values(old_apps, verified.pk)

        self._migrate(self.migrate_to)
        reversed_apps = self._migrate(self.migrate_from)
        self.assertEqual(self._stable_outbox_values(reversed_apps, verified.pk), before)
        reapplied_apps = self._migrate(self.migrate_to)
        self.assertEqual(self._stable_outbox_values(reapplied_apps, verified.pk), before)

    def _accepted_outbox(self, apps, *, template, outbox_id, adapter_kind):
        Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
        Attempt = apps.get_model("communications", "CommunicationProviderAttempt")
        accepted_at = django_timezone.now()
        template_facts = {
            "content_template_id": str(template.pk),
            "template_code": template.template_code,
            "template_name": template.template_name,
            "template_type": template.template_type,
            "language_code": template.language_code,
            "audience": template.audience,
            "template_version": template.template_version,
            "approval_status": template.approval_status,
            "effective_from": template.effective_from.isoformat(),
            "effective_to": (
                template.effective_to.isoformat() if template.effective_to else None
            ),
            "variables": sorted(template.variables_json or []),
            "subject_template": template.subject_template,
            "body_template": template.body_template,
        }
        template_checksum = hashlib.sha256(
            json.dumps(
                template_facts, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        outbox = Outbox.objects.create(
            outbox_id=outbox_id,
            advice_intent=outbox_id,
            communication_id=outbox_id,
            idempotency_key=f"disbursement-advice:{outbox_id}",
            channel="email",
            recipient_address="legacy.borrower@example.com",
            recipient_digest=hashlib.sha256(b"legacy.borrower@example.com").hexdigest(),
            content_template=template,
            template_code_snapshot=template.template_code,
            template_provenance_status="verified",
            template_name_snapshot=template.template_name,
            template_type_snapshot=template.template_type,
            template_language_code_snapshot=template.language_code,
            template_audience_snapshot=template.audience,
            template_version_snapshot=template.template_version,
            template_approval_status_snapshot=template.approval_status,
            template_effective_from_snapshot=template.effective_from,
            template_effective_to_snapshot=template.effective_to,
            template_variables_snapshot=template.variables_json,
            subject_template_snapshot=template.subject_template,
            body_template_snapshot=template.body_template,
            template_checksum_sha256=template_checksum,
            subject_snapshot="Frozen advice subject",
            body_snapshot="Frozen advice body",
            payload_digest="b" * 64,
            related_entity_type="disbursement",
            related_entity_id=uuid.uuid4(),
            delivery_status="pending",
        )
        attempt = Attempt.objects.create(
            outbox=outbox,
            advice_intent_id=outbox.advice_intent,
            communication_id=outbox.communication_id,
            idempotency_key=outbox.idempotency_key,
            payload_digest=outbox.payload_digest,
            adapter_kind=adapter_kind,
            outcome="accepted",
            provider_external_message_id=f"manual:{outbox_id}",
            provider_delivery_status="sent",
            provider_accepted_at=accepted_at,
            attempted_at=accepted_at,
            evidence_digest="c" * 64,
        )
        Outbox.objects.filter(pk=outbox.pk).update(
            delivery_status="sent",
            provider_external_message_id=attempt.provider_external_message_id,
            provider_delivery_status="sent",
            provider_accepted_at=accepted_at,
            accepted_provider_attempt_id=attempt.pk,
        )
        return Outbox.objects.get(pk=outbox.pk)

    def _queued_outbox_with_job(self, apps, label, *, create_job=True):
        Template = apps.get_model("communications", "ContentTemplate")
        Job = apps.get_model("communications", "CommunicationDeliveryJob")
        template = Template.objects.create(
            template_code=f"queued_advice_{label}_v1",
            template_name=f"Queued advice {label}",
            template_type="email",
            language_code="en",
            audience="borrower",
            subject_template="Advice {{ borrower_name }}",
            body_template="Queued for {{ borrower_name }}",
            variables_json=["borrower_name"],
            approval_status="approved",
            template_version="v1",
            effective_from=django_timezone.localdate(),
        )
        outbox = self._make_pending_without_attempt(
            apps,
            self._accepted_outbox(
                apps,
                template=template,
                outbox_id=uuid.uuid4(),
                adapter_kind=(
                    "sfpcl_credit.communications.adapters.FakeEmailDeliveryAdapter"
                ),
            ),
        )
        if not create_job:
            return outbox, None
        job = Job.objects.create(
            outbox=outbox,
            advice_intent_id=outbox.advice_intent,
            actor_id=uuid.uuid4(),
            actor_role_code="credit_manager",
            actor_team_codes=["credit"],
            request_id=f"queued-advice-{label}",
            request_payload_digest=outbox.payload_digest,
            status="queued",
        )
        return outbox, job

    def _history_values(self, apps, outbox_id):
        Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
        return Outbox.objects.filter(pk=outbox_id).values(
            "outbox_id",
            "advice_intent",
            "communication_id",
            "idempotency_key",
            "channel",
            "recipient_address",
            "recipient_digest",
            "subject_snapshot",
            "body_snapshot",
            "payload_digest",
            "related_entity_type",
            "related_entity_id",
            "delivery_status",
            "provider_external_message_id",
            "provider_delivery_status",
            "provider_accepted_at",
            "accepted_provider_attempt_id",
            "delivery_receipt_id",
            "final_communication_id",
            "created_at",
        ).get()

    def _stable_outbox_values(self, apps, outbox_id):
        values = self._all_outbox_values(apps, outbox_id)
        values.pop("template_provenance_origin", None)
        return values

    def _make_pending_without_attempt(self, apps, outbox):
        Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
        Attempt = apps.get_model("communications", "CommunicationProviderAttempt")
        Outbox.objects.filter(pk=outbox.pk).update(
            delivery_status="pending",
            provider_external_message_id=None,
            provider_delivery_status=None,
            provider_accepted_at=None,
            accepted_provider_attempt_id=None,
        )
        Attempt.objects.filter(outbox_id=outbox.pk).delete()
        return Outbox.objects.get(pk=outbox.pk)

    def _all_outbox_values(self, apps, outbox_id):
        Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
        return Outbox.objects.filter(pk=outbox_id).values().get()

    def _migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps


class CommunicationReceiptOwnerMigrationTests(TransactionTestCase):
    reset_sequences = True

    migrate_from = [
        ("communications", "0003_notification"),
        (
            "disbursements",
            "0007_remove_disbursement_disb_success_evidence_complete_and_more",
        ),
    ]
    migrate_to = [
        ("communications", "0004_advice_outbox_and_receipt_owner"),
        (
            "disbursements",
            "0007_remove_disbursement_disb_success_evidence_complete_and_more",
        ),
    ]

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_receipt_row_and_schema_survive_forward_reverse_and_reapply(self):
        from sfpcl_credit.tests.test_disbursement_advice_api import (
            DisbursementAdviceApiTests,
        )

        self._migrate(self.migrate_from)
        fixture = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()

        old_apps = MigrationExecutor(connection).loader.project_state(
            self.migrate_from
        ).apps
        OldReceipt = old_apps.get_model(
            "disbursements", "DisbursementAdviceDeliveryReceipt"
        )
        retained = OldReceipt.objects.create(
            advice_intent_id=fixture.row.advice_intent.pk,
            idempotency_key="migration-receipt-owner-key",
            payload_digest="a" * 64,
            external_message_id="manual-migration-receipt-owner",
            delivery_status="sent",
            accepted_at=datetime(2026, 7, 18, 8, 50, tzinfo=timezone.utc),
            created_at=datetime(2026, 7, 18, 8, 51, tzinfo=timezone.utc),
        )
        retained_id = str(retained.pk)
        retained_values = self._receipt_values(OldReceipt)
        before = self._receipt_signature()

        moved_apps = self._migrate(self.migrate_to)
        MovedReceipt = moved_apps.get_model(
            "communications", "DisbursementAdviceDeliveryReceipt"
        )
        self.assertEqual(str(MovedReceipt.objects.get().pk), retained_id)
        self.assertEqual(self._receipt_values(MovedReceipt), retained_values)
        self.assertEqual(self._receipt_signature(), before)
        self.assertEqual(self._outbox_table_count(), 1)
        current_apps = self._migrate(
            [
                (
                    "communications",
                    "0005_advice_evidence_and_legacy_replay_closure",
                )
            ]
        )
        self.assertEqual(
            current_apps.get_model(
                "communications", "CommunicationDeliveryOutbox"
            ).objects.count(),
            0,
        )
        self.assertEqual(
            current_apps.get_model(
                "communications", "CommunicationProviderAttempt"
            ).objects.count(),
            0,
        )

        reversed_apps = self._migrate(self.migrate_from)
        ReversedReceipt = reversed_apps.get_model(
            "disbursements", "DisbursementAdviceDeliveryReceipt"
        )
        self.assertEqual(str(ReversedReceipt.objects.get().pk), retained_id)
        self.assertEqual(self._receipt_values(ReversedReceipt), retained_values)
        self.assertEqual(self._receipt_signature(), before)
        self.assertEqual(self._outbox_table_count(), 0)

        reapplied_apps = self._migrate(self.migrate_to)
        ReappliedReceipt = reapplied_apps.get_model(
            "communications", "DisbursementAdviceDeliveryReceipt"
        )
        self.assertEqual(str(ReappliedReceipt.objects.get().pk), retained_id)
        self.assertEqual(self._receipt_values(ReappliedReceipt), retained_values)
        self.assertEqual(self._receipt_signature(), before)
        self.assertEqual(self._outbox_table_count(), 1)
        self._migrate(
            [
                (
                    "communications",
                    "0005_advice_evidence_and_legacy_replay_closure",
                )
            ]
        )

    def _migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def _receipt_signature(self):
        table = "disbursement_advice_delivery_receipts"
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, table)
            description = connection.introspection.get_table_description(
                cursor, table
            )
        return {
            "table": table,
            "columns": tuple(sorted(field.name for field in description)),
            "constraints": tuple(sorted(constraints)),
        }

    def _receipt_values(self, model):
        row = model.objects.values(
            "delivery_receipt_id",
            "advice_intent_id",
            "idempotency_key",
            "payload_digest",
            "external_message_id",
            "delivery_status",
            "accepted_at",
            "created_at",
        ).get()
        return {
            **row,
            "delivery_receipt_id": str(row["delivery_receipt_id"]),
            "advice_intent_id": str(row["advice_intent_id"]),
        }

    def _outbox_table_count(self):
        return connection.introspection.table_names().count(
            "communication_delivery_outboxes"
        )


class CommunicationAdviceEvidenceMigrationTests(TransactionTestCase):
    reset_sequences = True
    migrate_from = [("communications", "0004_advice_outbox_and_receipt_owner")]
    migrate_to = [
        ("communications", "0005_advice_evidence_and_legacy_replay_closure")
    ]

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_coherent_legacy_delivery_survives_forward_reverse_and_reapply(self):
        from sfpcl_credit.tests.test_disbursement_advice_api import (
            DisbursementAdviceApiTests,
        )

        old_apps = self._migrate(self.migrate_from)
        fixture = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()
        Intent = old_apps.get_model("disbursements", "DisbursementAdviceIntent")
        Disbursement = old_apps.get_model("disbursements", "Disbursement")
        Communication = old_apps.get_model("communications", "Communication")
        Receipt = old_apps.get_model(
            "communications", "DisbursementAdviceDeliveryReceipt"
        )
        Audit = old_apps.get_model("identity", "AuditLog")
        Workflow = old_apps.get_model("workflows", "WorkflowEvent")
        action_id = uuid.uuid4()
        accepted_at = datetime(2026, 7, 18, 9, 30, tzinfo=timezone.utc)
        communication_id = fixture.row.advice_intent.pk
        audit = Audit.objects.create(
            actor_user_id=fixture.actor.pk,
            actor_type="user",
            action="disbursement.advice_sent",
            entity_type="disbursement",
            entity_id=fixture.row.pk,
            old_value_json={"disbursement_advice_communication_id": None},
            new_value_json={
                "action_id": str(action_id),
                "communication_id": str(communication_id),
            },
        )
        workflow = Workflow.objects.create(
            workflow_name="DisbursementAdviceSent",
            entity_type="disbursement",
            entity_id=fixture.row.pk,
            from_state="transfer_successful",
            to_state="advice_sent",
            triggered_by_user_id=fixture.actor.pk,
            trigger_reason=(
                f"action_id={action_id};communication_id={communication_id}"
            ),
        )
        Intent.objects.filter(pk=communication_id).update(
            delivery_status="sent",
            delivery_action_id=action_id,
            delivery_evidence_digest="e" * 64,
            delivery_audit_id=audit.pk,
            delivery_workflow_event_id=workflow.pk,
        )
        Communication.objects.create(
            communication_id=communication_id,
            related_entity_type="disbursement",
            related_entity_id=fixture.row.pk,
            recipient_party_type="borrower",
            recipient_party_id=fixture.row.member_id,
            recipient_address="borrower.advice@example.com",
            channel="email",
            content_template_id=fixture.template.pk,
            subject_snapshot="Frozen legacy advice subject",
            body_snapshot="Frozen legacy advice body",
            sent_by_user_id=fixture.actor.pk,
            sent_at=accepted_at,
            delivery_status="sent",
            external_message_id="manual:coherent-legacy-advice",
        )
        Disbursement.objects.filter(pk=fixture.row.pk).update(
            disbursement_advice_communication_id=communication_id
        )
        receipt = Receipt.objects.create(
            advice_intent_id=communication_id,
            idempotency_key=f"disbursement-advice:{communication_id}",
            payload_digest="p" * 64,
            external_message_id="manual:coherent-legacy-advice",
            delivery_status="sent",
            accepted_at=accepted_at,
            created_at=accepted_at,
        )
        old_apps.get_model("communications", "ContentTemplate").objects.filter(
            pk=fixture.template.pk
        ).update(
            template_name="Later mutable legacy template",
            subject_template="Later mutable subject {{ borrower_name }}",
            body_template="Later mutable body {{ borrower_name }}",
        )
        retained_ids = {
            "communication": str(communication_id),
            "receipt": str(receipt.pk),
            "audit": str(audit.pk),
            "workflow": str(workflow.pk),
            "action": str(action_id),
        }
        receipt_before = self._manifest("disbursement_advice_delivery_receipts")
        outbox_before = self._manifest("communication_delivery_outboxes")

        current_apps = self._migrate(self.migrate_to)
        first = self._current_values(current_apps)
        self.assertEqual(first["retained_ids"], retained_ids)
        self.assertEqual(first["outbox_id"], retained_ids["communication"])
        self.assertEqual(first["adapter_kind"], "legacy:pre-outbox")
        self.assertEqual(first["provider_outcome"], "accepted")
        self.assertEqual(first["template_provenance_status"], "legacy_partial")
        self.assertEqual(first["template_name"], "Later mutable legacy template")
        self.assertEqual(first["template_variables"], sorted(fixture.template.variables_json))
        self.assertEqual(first["primitive_outbox_intent"], retained_ids["communication"])
        self.assertEqual(first["primitive_receipt_intent"], retained_ids["communication"])
        receipt_after = self._manifest("disbursement_advice_delivery_receipts")
        forward_manifests = {
            table: self._manifest(table)
            for table in (
                "disbursement_advice_delivery_receipts",
                "communication_delivery_outboxes",
                "communication_provider_attempts",
            )
        }
        self.assertEqual(receipt_after["columns"], receipt_before["columns"])
        self.assertFalse(
            any(
                (value.get("foreign_key") or (None,))[0]
                == "disbursement_advice_intents"
                for value in receipt_after["constraints"].values()
            )
        )

        reversed_apps = self._migrate(self.migrate_from)
        self.assertEqual(
            reversed_apps.get_model(
                "communications", "DisbursementAdviceDeliveryReceipt"
            ).objects.count(),
            1,
        )
        self.assertEqual(
            reversed_apps.get_model(
                "communications", "CommunicationDeliveryOutbox"
            ).objects.count(),
            0,
        )
        self.assertNotIn(
            "communication_provider_attempts",
            connection.introspection.table_names(),
        )
        self.assertEqual(
            self._manifest("disbursement_advice_delivery_receipts"),
            receipt_before,
        )
        self.assertEqual(
            self._manifest("communication_delivery_outboxes"), outbox_before
        )

        reapplied_apps = self._migrate(self.migrate_to)
        self.assertEqual(self._current_values(reapplied_apps), first)
        self.assertEqual(
            {
                table: self._manifest(table)
                for table in (
                    "disbursement_advice_delivery_receipts",
                    "communication_delivery_outboxes",
                    "communication_provider_attempts",
                )
            },
            forward_manifests,
        )
        corrected_apps = self._migrate(
            [("communications", "0008_legacy_template_provenance_closure")]
        )
        corrected = {
            **first,
            "template_name": None,
            "template_variables": None,
        }
        self.assertEqual(
            self._current_values(corrected_apps),
            corrected,
        )
        with self.assertRaisesRegex(
            RuntimeError, "Cannot reverse communications 0008"
        ):
            self._migrate(self.migrate_to)
        current_apps = MigrationExecutor(connection).loader.project_state(
            [("communications", "0008_legacy_template_provenance_closure")]
        ).apps
        self.assertEqual(self._current_values(current_apps), corrected)

    def test_accepted_pending_and_no_advice_rows_reapply_without_fabrication(self):
        from sfpcl_credit.tests.test_disbursement_advice_api import (
            DisbursementAdviceApiTests,
        )

        old_apps = self._migrate(self.migrate_from)
        fixture = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()
        Outbox = old_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        accepted_at = datetime(2026, 7, 18, 10, 30, tzinfo=timezone.utc)
        accepted_id = uuid.uuid4()
        accepted = Outbox.objects.create(
            outbox_id=accepted_id,
            advice_intent_id=fixture.row.advice_intent.pk,
            communication_id=fixture.row.advice_intent.pk,
            idempotency_key=f"disbursement-advice:{fixture.row.advice_intent.pk}",
            channel="email",
            recipient_address="borrower.advice@example.com",
            recipient_digest=hashlib.sha256(
                b"borrower.advice@example.com"
            ).hexdigest(),
            content_template_id=fixture.template.pk,
            template_code_snapshot=fixture.template.template_code,
            template_version_snapshot=fixture.template.template_version,
            template_checksum_sha256="t" * 64,
            subject_snapshot="Accepted crash subject",
            body_snapshot="Accepted crash body",
            payload_digest="d" * 64,
            related_entity_type="disbursement",
            related_entity_id=fixture.row.pk,
            delivery_status="sent",
            provider_external_message_id="manual:accepted-not-finalized",
            provider_delivery_status="sent",
            provider_accepted_at=accepted_at,
            created_at=accepted_at,
        )
        accepted_values = dict(
            Outbox.objects.values(
                "outbox_id",
                "advice_intent_id",
                "communication_id",
                "idempotency_key",
                "payload_digest",
                "provider_external_message_id",
                "provider_delivery_status",
                "provider_accepted_at",
            ).get(pk=accepted.pk)
        )

        current_apps = self._migrate(self.migrate_to)
        CurrentOutbox = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        Attempt = current_apps.get_model(
            "communications", "CommunicationProviderAttempt"
        )
        current = CurrentOutbox.objects.get(pk=accepted_id)
        self.assertEqual(current.accepted_provider_attempt_id, Attempt.objects.get().pk)
        self.assertEqual(Attempt.objects.get().adapter_kind, "legacy:retained-outbox")
        self.assertEqual(current.template_name_snapshot, fixture.template.template_name)

        reversed_apps = self._migrate(self.migrate_from)
        ReversedOutbox = reversed_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        reversed_values = dict(
            ReversedOutbox.objects.values(*accepted_values).get(pk=accepted_id)
        )
        self.assertEqual(reversed_values, accepted_values)
        ReversedOutbox.objects.filter(pk=accepted_id).delete()
        pending_id = uuid.uuid4()
        pending_values = {
            **accepted_values,
            "outbox_id": pending_id,
            "delivery_status": "pending",
            "provider_external_message_id": None,
            "provider_delivery_status": None,
            "provider_accepted_at": None,
        }
        ReversedOutbox.objects.create(
            **pending_values,
            channel="email",
            recipient_address="borrower.advice@example.com",
            recipient_digest=hashlib.sha256(
                b"borrower.advice@example.com"
            ).hexdigest(),
            content_template_id=fixture.template.pk,
            template_code_snapshot=fixture.template.template_code,
            template_version_snapshot=fixture.template.template_version,
            template_checksum_sha256="t" * 64,
            subject_snapshot="Pending subject",
            body_snapshot="Pending body",
            related_entity_type="disbursement",
            related_entity_id=fixture.row.pk,
            created_at=accepted_at,
        )

        pending_apps = self._migrate(self.migrate_to)
        PendingOutbox = pending_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        self.assertEqual(PendingOutbox.objects.get().delivery_status, "pending")
        self.assertEqual(
            pending_apps.get_model(
                "communications", "CommunicationProviderAttempt"
            ).objects.count(),
            0,
        )
        no_advice_apps = self._migrate(self.migrate_from)
        no_advice_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        ).objects.all().delete()
        final_apps = self._migrate(self.migrate_to)
        self.assertEqual(
            final_apps.get_model(
                "communications", "CommunicationDeliveryOutbox"
            ).objects.count(),
            0,
        )
        self.assertEqual(
            final_apps.get_model(
                "communications", "CommunicationProviderAttempt"
            ).objects.count(),
            0,
        )

    def _migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def _current_values(self, apps):
        Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
        Attempt = apps.get_model("communications", "CommunicationProviderAttempt")
        Receipt = apps.get_model(
            "communications", "DisbursementAdviceDeliveryReceipt"
        )
        Communication = apps.get_model("communications", "Communication")
        Intent = apps.get_model("disbursements", "DisbursementAdviceIntent")
        outbox = Outbox.objects.get()
        attempt = Attempt.objects.get()
        receipt = Receipt.objects.get()
        intent = Intent.objects.get(pk=outbox.advice_intent)
        return {
            "retained_ids": {
                "communication": str(
                    Communication.objects.get(pk=outbox.communication_id).pk
                ),
                "receipt": str(receipt.pk),
                "audit": str(intent.delivery_audit_id),
                "workflow": str(intent.delivery_workflow_event_id),
                "action": str(intent.delivery_action_id),
            },
            "outbox_id": str(outbox.pk),
            "attempt_id": str(attempt.pk),
            "adapter_kind": attempt.adapter_kind,
            "provider_outcome": attempt.outcome,
            "template_provenance_status": outbox.template_provenance_status,
            "template_name": outbox.template_name_snapshot,
            "template_variables": outbox.template_variables_snapshot,
            "primitive_outbox_intent": str(outbox.advice_intent),
            "primitive_receipt_intent": str(receipt.advice_intent),
        }

    def _manifest(self, table):
        with connection.cursor() as cursor:
            description = connection.introspection.get_table_description(
                cursor, table
            )
            constraints = connection.introspection.get_constraints(cursor, table)
            objects = ()
            if connection.vendor == "sqlite":
                cursor.execute(
                    "SELECT type, name, sql FROM sqlite_master "
                    "WHERE tbl_name = %s AND sql IS NOT NULL ORDER BY type, name",
                    [table],
                )
                objects = tuple(cursor.fetchall())
        return {
            "table": table,
            "columns": tuple(sorted(
                (
                    field.name,
                    str(field.type_code),
                    field.null_ok,
                    field.default,
                )
                for field in description
            )),
            "constraints": {
                name: {
                    key: tuple(value) if isinstance(value, list) else value
                    for key, value in sorted(details.items())
                }
                for name, details in sorted(constraints.items())
            },
            "definitions": objects,
        }
