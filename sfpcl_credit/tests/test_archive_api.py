import json
from datetime import UTC, date, datetime

from django.db import IntegrityError, models, transaction
from django.test import Client, TestCase

from sfpcl_credit.closure.models import LoanClosure
from sfpcl_credit.identity.models import AuditLog


class ArchiveRecordApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_noc_api import NocIssuanceApiTests

        fixture = NocIssuanceApiTests(
            "test_eligible_full_repayment_closure_issues_one_noc_and_queues_delivery"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.account = fixture.account
        self.closure = fixture.closure
        self.actor = fixture.issuer
        self.fixture.fixture._grant(
            self.actor,
            "closure.security_return.record",
            "closure.archive.create",
            "closure.archive.read",
        )
        self.auth = self.fixture.fixture._auth(self.actor)
        self.client = Client()
        issued = fixture._issue("archive-fixture-noc")
        self.assertEqual(issued.status_code, 200, issued.content)
        returned = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="archive-fixture-security-return",
            **self.auth,
        )
        self.assertEqual(returned.status_code, 200, returned.content)

    def test_eligible_closure_archives_once_with_server_calculated_retention(self):
        from sfpcl_credit.closure.models import ArchiveRecord, ClosureRequirement

        response = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/archive/",
            data=json.dumps(
                {
                    "file_location_physical": "Archive Room / Rack A / Box 12",
                    "file_location_digital": "governed://loan-archive/manifest-25",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="archive-record-001",
            HTTP_X_REQUEST_ID="req-archive-record-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        archive = ArchiveRecord.objects.get(loan_closure=self.closure)
        self.assertEqual(data["archive_record_id"], str(archive.pk))
        self.assertEqual(data["loan_closure_id"], str(self.closure.pk))
        self.assertEqual(data["loan_account_id"], str(self.account.pk))
        self.assertEqual(data["file_location_physical"], "Archive Room / Rack A / Box 12")
        self.assertEqual(
            data["file_location_digital"], "governed://loan-archive/manifest-25"
        )
        self.assertEqual(archive.retention_start_date, self.closure.closed_at.date())
        self.assertGreaterEqual(
            archive.retention_until_date,
            date(self.closure.closed_at.year + 8, self.closure.closed_at.month, self.closure.closed_at.day),
        )
        self.assertFalse(data["destruction_eligible"])
        self.assertFalse(data["idempotency_replayed"])
        self.assertEqual(
            ClosureRequirement.objects.get(
                loan_closure=self.closure,
                requirement_type=ClosureRequirement.TYPE_ARCHIVE,
            ).requirement_status,
            ClosureRequirement.STATUS_COMPLETED,
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="closure.archive.created", entity_id=archive.pk
            ).count(),
            1,
        )

    def test_authorised_detail_read_returns_manifest_and_audits_without_locations(self):
        created = self._archive("archive-read-fixture")
        self.assertEqual(created.status_code, 200, created.content)

        response = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/archive/",
            HTTP_X_REQUEST_ID="req-archive-read-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["file_location_physical"], "Archive Room / Rack A / Box 12")
        self.assertEqual(
            data["file_location_digital"], "governed://loan-archive/manifest-25"
        )
        audit = AuditLog.objects.get(
            action="closure.archive.manifest_accessed",
            entity_id=data["archive_record_id"],
        )
        serialized_audit = json.dumps(audit.new_value_json)
        self.assertNotIn("Archive Room", serialized_audit)
        self.assertNotIn("governed://", serialized_audit)

    def test_authorised_manifest_search_finds_archived_loan_without_logging_query(self):
        created = self._archive("archive-search-fixture")
        self.assertEqual(created.status_code, 200, created.content)

        response = self.client.get(
            "/api/v1/archive-records/",
            {"search": self.account.loan_account_number},
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            response.json()["data"][0]["archive_record_id"],
            created.json()["data"]["archive_record_id"],
        )
        audit = AuditLog.objects.get(action="closure.archive.manifest_searched")
        self.assertNotIn(self.account.loan_account_number, json.dumps(audit.new_value_json))

    def test_short_or_forged_retention_is_rejected_then_exact_replay_is_read_only(self):
        from sfpcl_credit.closure.models import ArchiveRecord

        closure_date = self.closure.closed_at.date()
        short = self._archive(
            "archive-short-retention",
            retention_until_date=closure_date.replace(year=closure_date.year + 7).isoformat(),
        )
        self.assertEqual(short.status_code, 409, short.content)
        self.assertFalse(ArchiveRecord.objects.exists())
        wrong_start = self._archive(
            "archive-wrong-start",
            retention_start_date=date(closure_date.year, 1, 1).isoformat(),
        )
        self.assertEqual(wrong_start.status_code, 409, wrong_start.content)
        self.assertFalse(ArchiveRecord.objects.exists())

        first = self._archive("archive-exact-replay")
        replay = self._archive("archive-exact-replay")
        changed = self._archive(
            "archive-exact-replay",
            file_location_physical="Archive Room / Rack B / Box 99",
        )
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(ArchiveRecord.objects.count(), 1)

    def test_leap_day_closure_keeps_the_eight_year_calendar_anniversary(self):
        from sfpcl_credit.closure.models import ArchiveRecord
        from sfpcl_credit.loans.models import LoanAccount

        leap_close = datetime(2024, 2, 29, 10, 30, tzinfo=UTC)
        models.QuerySet.update(
            LoanClosure.objects.filter(pk=self.closure.pk), closed_at=leap_close
        )
        models.QuerySet.update(
            LoanAccount.objects.filter(pk=self.account.pk), closed_at=leap_close
        )

        response = self._archive("archive-leap-day")

        self.assertEqual(response.status_code, 200, response.content)
        archive = ArchiveRecord.objects.get()
        self.assertEqual(archive.retention_start_date, date(2024, 2, 29))
        self.assertEqual(archive.retention_until_date, date(2032, 2, 29))

    def test_archive_waits_for_noc_and_every_applicable_security_return(self):
        from sfpcl_credit.closure.models import ArchiveRecord, ClosureRequirement

        noc_requirement = ClosureRequirement.objects.get(
            loan_closure=self.closure,
            requirement_type=ClosureRequirement.TYPE_NOC,
        )
        models.QuerySet.update(
            ClosureRequirement.objects.filter(pk=noc_requirement.pk),
            requirement_status=ClosureRequirement.STATUS_PENDING,
        )
        missing_noc = self._archive("archive-missing-noc")
        self.assertEqual(missing_noc.status_code, 409, missing_noc.content)
        self.assertFalse(ArchiveRecord.objects.exists())

        models.QuerySet.update(
            ClosureRequirement.objects.filter(pk=noc_requirement.pk),
            requirement_status=ClosureRequirement.STATUS_COMPLETED,
        )
        security_requirement = ClosureRequirement.objects.get(
            loan_closure=self.closure,
            requirement_type=ClosureRequirement.TYPE_SECURITY_RETURN,
        )
        models.QuerySet.update(
            ClosureRequirement.objects.filter(pk=security_requirement.pk),
            requirement_status=ClosureRequirement.STATUS_PENDING,
        )
        missing_return = self._archive("archive-missing-security-return")
        self.assertEqual(missing_return.status_code, 409, missing_return.content)
        self.assertFalse(ArchiveRecord.objects.exists())

    def test_auditor_reads_but_borrower_cannot_read_or_create_archive(self):
        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

        created = self._archive("archive-read-authority")
        self.assertEqual(created.status_code, 200, created.content)
        auditor = self.fixture.fixture._user("internal_auditor", "Archive Auditor")
        self.fixture.fixture._grant(auditor, "closure.archive.read")
        ApprovalCaseReadScopeGrant.objects.create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        )
        auditor_read = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/archive/",
            **self.fixture.fixture._auth(auditor),
        )
        self.assertEqual(auditor_read.status_code, 200, auditor_read.content)

        borrower = self.fixture.fixture._user(
            "borrower_portal_user", "Archive Borrower"
        )
        self.fixture.fixture._grant(
            borrower, "closure.archive.read", "closure.archive.create"
        )
        borrower_auth = self.fixture.fixture._auth(borrower)
        denied_read = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/archive/", **borrower_auth
        )
        denied_create = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/archive/",
            data=json.dumps({"file_location_physical": "Borrower supplied path"}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="borrower-archive-denied",
            **borrower_auth,
        )
        self.assertEqual(denied_read.status_code, 403, denied_read.content)
        self.assertEqual(denied_create.status_code, 403, denied_create.content)
        denied_audits = AuditLog.objects.filter(
            action__in=("closure.archive.read_denied", "closure.archive.create_denied")
        )
        self.assertEqual(denied_audits.count(), 2)
        self.assertNotIn(
            "Borrower supplied path",
            json.dumps(list(denied_audits.values()), default=str),
        )

    def test_archive_model_rejects_location_change_deletion_and_early_destruction(self):
        from sfpcl_credit.closure.models import ArchiveRecord

        created = self._archive("archive-immutable")
        self.assertEqual(created.status_code, 200, created.content)
        archive = ArchiveRecord.objects.get()
        archive.file_location_physical = "Changed Rack"
        with self.assertRaisesMessage(ValueError, "Archive records are read-only"):
            archive.save()
        with self.assertRaisesMessage(ValueError, "Archive records are read-only"):
            ArchiveRecord.objects.filter(pk=archive.pk).update(
                file_location_physical="Changed Rack"
            )
        with self.assertRaisesMessage(
            ValueError, "cannot be destroyed through this contract"
        ):
            archive.delete()
        with self.assertRaises(IntegrityError), transaction.atomic():
            models.QuerySet.update(
                ArchiveRecord.objects.filter(pk=archive.pk),
                destruction_eligible_flag=True,
            )

    def _archive(self, key, **overrides):
        return self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/archive/",
            data=json.dumps(
                {
                    "file_location_physical": "Archive Room / Rack A / Box 12",
                    "file_location_digital": "governed://loan-archive/manifest-25",
                    **overrides,
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            **self.auth,
        )


class ArchivePermissionCatalogueTests(TestCase):
    def test_compliance_cs_and_auditor_receive_only_their_archive_authorities(self):
        from sfpcl_credit.identity.catalogue import ROLE_PERMISSIONS

        self.assertIn("closure.archive.create", ROLE_PERMISSIONS["company_secretary"])
        self.assertIn("closure.archive.read", ROLE_PERMISSIONS["company_secretary"])
        self.assertIn("closure.archive.create", ROLE_PERMISSIONS["compliance_team_member"])
        self.assertIn("closure.archive.read", ROLE_PERMISSIONS["compliance_team_member"])
        self.assertIn("closure.archive.read", ROLE_PERMISSIONS["internal_auditor"])
        self.assertNotIn("closure.archive.create", ROLE_PERMISSIONS["internal_auditor"])
