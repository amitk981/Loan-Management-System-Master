"""Independent failing probes for the 2026-07-19 architecture review."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")

import django

django.setup()

from django.test.runner import DiscoverRunner
from django.utils import timezone

from sfpcl_credit.communications.models import CommunicationDeliveryJob
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.identity.models import Permission, RolePermission
from sfpcl_credit.tests import test_communications_api as communication_fixtures
from sfpcl_credit.tests.test_communication_receipt_owner_migration import (
    LegacyAdviceTemplateProvenanceMigrationTests,
)
from sfpcl_credit.tests.test_communication_worker_runtime import (
    CommunicationWorkerQueueTests,
)


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


class IncompleteQueuedSnapshotProbe(LegacyAdviceTemplateProvenanceMigrationTests):
    """Internally checksummed but incomplete snapshot facts must remain legacy."""

    def test_blank_required_snapshot_is_not_verified(self):
        old_apps = self._migrate(self.migrate_from)
        Outbox = old_apps.get_model("communications", "CommunicationDeliveryOutbox")
        outbox, _job = self._queued_outbox_with_job(old_apps, "blank-snapshot")
        Outbox.objects.filter(pk=outbox.pk).update(template_name_snapshot="")
        outbox.refresh_from_db()
        Outbox.objects.filter(pk=outbox.pk).update(
            template_checksum_sha256=_snapshot_checksum(outbox)
        )

        current_apps = self._migrate(self.migrate_to)
        migrated = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        ).objects.get(pk=outbox.pk)

        self.assertEqual(migrated.template_provenance_status, "legacy_partial")
        self.assertEqual(migrated.template_provenance_origin, "ambiguous_legacy")


class ExceptionJobAuthorityProbe(CommunicationWorkerQueueTests):
    """Exception access must retain the permission for its exact job kind."""

    def _generic_exception(self):
        with patch("sfpcl_credit.processes.tasks.execute_communication_delivery_job.signature"):
            response = self.client.post(
                communication_fixtures.COMMUNICATION_SEND_URL,
                data=self._send_payload(),
                content_type="application/json",
                headers=self._auth_headers(idempotency_key="review-job-authority"),
            )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(attempts=2)
        CommunicationDispatcher.start_job(job.pk)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            lease_expires_at=timezone.now()
        )
        CommunicationDispatcher.retry_failed(limit=1)
        exception = job.delivery_exception

        RolePermission.objects.filter(
            role=self.role,
            permission__permission_code="communications.communication.send",
        ).delete()
        advice_permission, _ = Permission.objects.get_or_create(
            permission_code="finance.disbursement.send_advice",
            defaults={
                "permission_name": "Send disbursement advice",
                "module_name": "finance",
                "risk_level": "high",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.role, permission=advice_permission
        )
        return exception

    def test_generic_exception_rejects_advice_only_permission_on_read(self):
        exception = self._generic_exception()
        response = self.client.get(
            f"/api/v1/communication-exceptions/{exception.pk}/",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 403, response.content)

    def test_generic_exception_rejects_advice_only_permission_on_resolution(self):
        exception = self._generic_exception()
        response = self.client.post(
            f"/api/v1/communication-exceptions/{exception.pk}/resolve/",
            {"resolution_action": "manual_closed", "resolution_version": 1},
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 403, response.content)


def main() -> int:
    runner = DiscoverRunner(verbosity=2, interactive=False)
    runner.setup_test_environment()
    old_config = runner.setup_databases()
    try:
        suite = unittest.TestSuite(
            [
                IncompleteQueuedSnapshotProbe(
                    "test_blank_required_snapshot_is_not_verified"
                ),
                ExceptionJobAuthorityProbe(
                    "test_generic_exception_rejects_advice_only_permission_on_read"
                ),
                ExceptionJobAuthorityProbe(
                    "test_generic_exception_rejects_advice_only_permission_on_resolution"
                ),
            ]
        )
        result = runner.run_suite(suite)
        return len(result.failures) + len(result.errors)
    finally:
        runner.teardown_databases(old_config)
        runner.teardown_test_environment()


if __name__ == "__main__":
    raise SystemExit(main())
