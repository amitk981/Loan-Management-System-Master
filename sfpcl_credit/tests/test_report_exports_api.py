import csv
import io
import json
import tempfile
import zipfile
from datetime import date
from unittest.mock import patch

from django.test import Client, TestCase
from django.utils import timezone
from pypdf import PdfReader

from sfpcl_credit.applications.models import LoanApplication, LoanRequestRegisterEntry
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member


class ReportExportApiTests(TestCase):
    password = "ReportExportPass123!"

    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(
            role_code="report_exporter",
            role_name="Report Exporter",
        )
        self.actor = User.objects.create(
            full_name="Report Exporter",
            email="report.exporter@sfpcl.example",
            primary_role=self.role,
            password_hash="",
        )
        self.actor.set_password(self.password)
        self.actor.save(update_fields=["password_hash"])
        for code in ("reports.application_pipeline.read", "reports.export"):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="reports",
                risk_level="medium",
            )
            RolePermission.objects.create(role=self.role, permission=permission)

    def test_request_and_replay_return_one_queued_job_for_canonical_identity(self):
        auth = self._auth()
        payload = {
            "report_code": "application-pipeline",
            "format": "csv",
            "filters": {"to_date": "2026-06-30", "from_date": "2026-04-01"},
        }

        first = self.client.post(
            "/api/v1/reports/exports/",
            payload,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="register-export-1",
            **auth,
        )
        replay = self.client.post(
            "/api/v1/reports/exports/",
            {
                **payload,
                "filters": {
                    "from_date": "2026-04-01",
                    "to_date": "2026-06-30",
                },
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="register-export-1",
            **auth,
        )

        self.assertEqual(first.status_code, 202, first.content)
        self.assertEqual(replay.status_code, 202, replay.content)
        self.assertEqual(
            first.json()["data"]["export_job_id"],
            replay.json()["data"]["export_job_id"],
        )
        self.assertEqual(first.json()["data"]["status"], "queued")
        self.assertFalse(first.json()["data"]["idempotency_replayed"])
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])

        from sfpcl_credit.reports.models import ReportExportJob

        job = ReportExportJob.objects.get()
        self.assertEqual(
            job.canonical_filters,
            {"from_date": "2026-04-01", "to_date": "2026-06-30"},
        )

    def test_worker_completes_csv_and_status_issues_an_expiring_download(self):
        self._create_application_register_row()
        auth = self._auth()
        with tempfile.TemporaryDirectory() as storage_root, self.settings(
            REPORT_EXPORT_STORAGE_ROOT=storage_root,
            REPORT_EXPORT_DOWNLOAD_TTL_MINUTES=15,
            REPORT_EXPORT_RETENTION_HOURS=24,
        ):
            response = self.client.post(
                "/api/v1/reports/exports/",
                {
                    "report_code": "application-pipeline",
                    "format": "csv",
                    "filters": {"from_date": "2026-04-01"},
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="register-export-csv",
                **auth,
            )
            job_id = response.json()["data"]["export_job_id"]

            from sfpcl_credit.reports.modules.report_export import execute_export_job

            result = execute_export_job(job_id)
            status = self.client.get(
                f"/api/v1/reports/exports/{job_id}/",
                **auth,
            )

            self.assertEqual(result["status"], "completed")
            self.assertEqual(status.status_code, 200, status.content)
            data = status.json()["data"]
            self.assertEqual(data["status"], "completed")
            self.assertEqual(len(data["checksum_sha256"]), 64)
            self.assertIn("token=", data["download_url"])
            self.assertIsNotNone(data["expires_at"])

            download = self.client.get(data["download_url"], **auth)
            self.assertEqual(download.status_code, 200, download.content)
            content = download.content.decode("utf-8")
            rows = list(csv.reader(io.StringIO(content)))
            self.assertIn(["report_code", "application-pipeline"], rows)
            self.assertIn(["generated_by", str(self.actor.pk)], rows)
            self.assertIn(["filter.from_date", "2026-04-01"], rows)
            self.assertIn("LR-EXPORT-001", content)

            from sfpcl_credit.identity.models import AuditLog

            audit = AuditLog.objects.get(
                action="report.export.downloaded",
                entity_id=job_id,
            )
            self.assertNotIn("LR-EXPORT-001", str(audit.new_value_json))

    def test_supported_format_matrix_produces_parseable_reconciled_files(self):
        self._create_application_register_row()
        auth = self._auth()
        with tempfile.TemporaryDirectory() as storage_root, self.settings(
            REPORT_EXPORT_STORAGE_ROOT=storage_root,
        ):
            parsed_text = {}
            for export_format in ("csv", "json", "xlsx", "pdf"):
                response = self.client.post(
                    "/api/v1/reports/exports/",
                    {
                        "report_code": "application-pipeline",
                        "format": export_format,
                        "filters": {"from_date": "2026-04-01"},
                    },
                    content_type="application/json",
                    HTTP_IDEMPOTENCY_KEY=f"format-{export_format}",
                    **auth,
                )
                self.assertEqual(response.status_code, 202, response.content)
                job_id = response.json()["data"]["export_job_id"]

                from sfpcl_credit.reports.modules.report_export import execute_export_job

                execute_export_job(job_id)
                status = self.client.get(
                    f"/api/v1/reports/exports/{job_id}/",
                    **auth,
                ).json()["data"]
                download = self.client.get(status["download_url"], **auth)
                self.assertEqual(download.status_code, 200, download.content)
                parsed_text[export_format] = self._parse_export(
                    export_format,
                    download.content,
                )

            for export_format, content in parsed_text.items():
                with self.subTest(export_format=export_format):
                    self.assertIn("application-pipeline", content)
                    self.assertIn(str(self.actor.pk), content)
                    self.assertIn("2026-04-01", content)
                    self.assertIn("LR-EXPORT-001", content)

    def test_expired_export_cleanup_removes_file_and_old_grant_is_denied(self):
        auth = self._auth()
        with tempfile.TemporaryDirectory() as storage_root, self.settings(
            REPORT_EXPORT_STORAGE_ROOT=storage_root,
        ):
            response = self.client.post(
                "/api/v1/reports/exports/",
                {
                    "report_code": "application-pipeline",
                    "format": "json",
                    "filters": {},
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="expired-export",
                **auth,
            )
            job_id = response.json()["data"]["export_job_id"]

            from sfpcl_credit.reports.models import ReportExportJob
            from sfpcl_credit.reports.modules.report_export import (
                cleanup_expired_exports,
                execute_export_job,
            )

            execute_export_job(job_id)
            old_url = self.client.get(
                f"/api/v1/reports/exports/{job_id}/",
                **auth,
            ).json()["data"]["download_url"]
            ReportExportJob.objects.filter(pk=job_id).update(
                download_expires_at=timezone.now() - timezone.timedelta(seconds=1)
            )

            cleanup = cleanup_expired_exports()
            status = self.client.get(
                f"/api/v1/reports/exports/{job_id}/",
                **auth,
            )
            expired_download = self.client.get(old_url, **auth)

            self.assertEqual(cleanup["deleted_count"], 1)
            self.assertEqual(status.status_code, 200, status.content)
            self.assertTrue(status.json()["data"]["download_expired"])
            self.assertIsNone(status.json()["data"]["download_url"])
            self.assertEqual(expired_download.status_code, 410)
            job = ReportExportJob.objects.get(pk=job_id)
            self.assertIsNotNone(job.file_deleted_at)
            self.assertEqual(job.state, ReportExportJob.STATE_COMPLETED)

    def test_export_permission_denial_is_audited_without_filter_values(self):
        RolePermission.objects.filter(
            role=self.role,
            permission__permission_code="reports.export",
        ).delete()

        response = self.client.post(
            "/api/v1/reports/exports/",
            {
                "report_code": "application-pipeline",
                "format": "csv",
                "filters": {"from_date": "2099-12-31"},
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="denied-export",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 403, response.content)
        from sfpcl_credit.identity.models import AuditLog

        audit = AuditLog.objects.get(action="report.export.denied")
        self.assertEqual(audit.new_value_json["report_code"], "application-pipeline")
        self.assertEqual(audit.new_value_json["outcome"], "denied")
        self.assertNotIn("2099-12-31", str(audit.new_value_json))
        self.assertNotIn("denied-export", str(audit.new_value_json))

    def test_generation_failure_is_terminal_observable_and_retry_safe(self):
        auth = self._auth()
        response = self.client.post(
            "/api/v1/reports/exports/",
            {
                "report_code": "application-pipeline",
                "format": "csv",
                "filters": {},
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="failed-export",
            **auth,
        )
        job_id = response.json()["data"]["export_job_id"]

        class FailingStorage:
            calls = 0

            def store(self, **kwargs):
                self.calls += 1
                raise OSError("private storage detail")

        storage = FailingStorage()
        from sfpcl_credit.reports.modules.report_export import execute_export_job

        failed = execute_export_job(job_id, storage=storage)
        retry = execute_export_job(job_id, storage=storage)
        status = self.client.get(
            f"/api/v1/reports/exports/{job_id}/",
            **auth,
        )

        self.assertEqual(failed["status"], "failed")
        self.assertEqual(retry["status"], "failed")
        self.assertEqual(storage.calls, 1)
        self.assertEqual(status.status_code, 200, status.content)
        data = status.json()["data"]
        self.assertEqual(data["failure_code"], "STORAGE_ERROR")
        self.assertIsNotNone(data["started_at"])
        self.assertIsNotNone(data["completed_at"])
        self.assertNotIn("private storage detail", str(data))
        self.assertNotIn("download_url", data)

    def test_request_status_authentication_validation_and_not_found_contracts(self):
        auth = self._auth()
        missing_auth = self.client.post(
            "/api/v1/reports/exports/",
            {},
            content_type="application/json",
        )
        missing_key = self.client.post(
            "/api/v1/reports/exports/",
            {
                "report_code": "application-pipeline",
                "format": "csv",
                "filters": {},
            },
            content_type="application/json",
            **auth,
        )
        invalid_filter = self.client.post(
            "/api/v1/reports/exports/",
            {
                "report_code": "application-pipeline",
                "format": "csv",
                "filters": {"from_date": "01-04-2026"},
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="invalid-filter",
            **auth,
        )
        unsupported = self.client.post(
            "/api/v1/reports/exports/",
            {
                "report_code": "audit-log-export",
                "format": "xml",
                "filters": {},
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="unsupported",
            **auth,
        )
        missing_job = self.client.get(
            "/api/v1/reports/exports/00000000-0000-0000-0000-000000000001/",
            **auth,
        )

        self.assertEqual(missing_auth.status_code, 401)
        self.assertEqual(missing_key.status_code, 400)
        self.assertIn("idempotency_key", missing_key.json()["error"]["field_errors"])
        self.assertEqual(invalid_filter.status_code, 400)
        self.assertIn("filters.from_date", invalid_filter.json()["error"]["field_errors"])
        self.assertEqual(unsupported.status_code, 400)
        self.assertIn("report_code", unsupported.json()["error"]["field_errors"])
        self.assertIn("format", unsupported.json()["error"]["field_errors"])
        self.assertEqual(missing_job.status_code, 404)

    def test_celery_entry_points_are_registered_thin_module_wrappers(self):
        from sfpcl_credit.processes.tasks import (
            cleanup_expired_report_exports,
            execute_report_export_job,
        )

        self.assertEqual(execute_report_export_job.name, "reports.execute_export_job")
        self.assertEqual(
            cleanup_expired_report_exports.name,
            "reports.cleanup_expired_exports",
        )
        with patch(
            "sfpcl_credit.processes.tasks.execute_export_job",
            return_value={"status": "completed"},
        ) as execute:
            self.assertEqual(
                execute_report_export_job.run("job-id"),
                {"status": "completed"},
            )
            execute.assert_called_once_with("job-id")
        with patch(
            "sfpcl_credit.processes.tasks.cleanup_expired_exports",
            return_value={"deleted_count": 0},
        ) as cleanup:
            self.assertEqual(
                cleanup_expired_report_exports.run(),
                {"deleted_count": 0},
            )
            cleanup.assert_called_once_with()

    def _parse_export(self, export_format, content):
        if export_format == "csv":
            return "\n".join(",".join(row) for row in csv.reader(io.StringIO(content.decode())))
        if export_format == "json":
            return json.dumps(json.loads(content), sort_keys=True)
        if export_format == "xlsx":
            with zipfile.ZipFile(io.BytesIO(content)) as workbook:
                return workbook.read("xl/worksheets/sheet1.xml").decode()
        if export_format == "pdf":
            return "\n".join(
                page.extract_text() or ""
                for page in PdfReader(io.BytesIO(content)).pages
            )
        raise AssertionError(f"Unexpected format: {export_format}")

    def _create_application_register_row(self):
        member = Member.objects.create(
            member_number="MEM-EXPORT-001",
            member_type="individual_farmer",
            legal_name="Export Member",
            display_name="Export Member",
            folio_number="FOL-EXPORT-001",
            membership_status="active",
            pan_encrypted="encrypted-export-pan",
            pan_hash="export-pan-hash",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.actor,
        )
        application = LoanApplication.objects.create(
            application_reference_number="LR-EXPORT-001",
            member=member,
            borrower_type=member.member_type,
            application_date=date(2026, 4, 1),
            received_by_user=self.actor,
            created_by_user=self.actor,
            required_loan_amount="250000.00",
            declared_purpose="Crop finance",
            purpose_category="crop_production",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_REFERENCE_GENERATED,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
        )
        return LoanRequestRegisterEntry.objects.create(
            loan_application=application,
            application_reference_number="LR-EXPORT-001",
            member=member,
            date_received=date(2026, 4, 1),
            reference_generated_date=date(2026, 4, 2),
            received_channel="assisted_digital",
            received_by_user=self.actor,
            register_status="reference_generated",
            requested_amount="250000.00",
            declared_purpose="Crop finance",
            purpose_category="crop_production",
            borrower_name="Export Member",
            folio_number="FOL-EXPORT-001",
            member_type="individual_farmer",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            current_owner_role="credit_manager",
        )

    def _auth(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": self.actor.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": (
                f"Bearer {response.json()['data']['access_token']}"
            )
        }
