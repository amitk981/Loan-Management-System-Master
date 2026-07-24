import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor

from django.db import close_old_connections, connection
from django.test import TransactionTestCase
from django.test.utils import override_settings

from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.reports.models import ReportExportJob
from sfpcl_credit.reports.modules.report_export import (
    execute_export_job,
    request_export,
)
from sfpcl_credit.reports.storage import LocalReportExportStorage


class RegisterExportPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_five_concurrent_requests_and_workers_create_one_job_and_file(self):
        if connection.vendor != "postgresql":
            self.skipTest("Authoritative five-race acceptance requires PostgreSQL.")
        role = Role.objects.create(
            role_code="postgres_exporter",
            role_name="PostgreSQL Exporter",
        )
        actor = User.objects.create(
            full_name="PostgreSQL Exporter",
            email="postgres.exporter@sfpcl.example",
            primary_role=role,
            password_hash="unused",
        )
        for code in ("reports.application_pipeline.read", "reports.export"):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="reports",
                risk_level="medium",
            )
            RolePermission.objects.create(role=role, permission=permission)

        request_barrier = threading.Barrier(5)

        def request_once():
            close_old_connections()
            try:
                local_actor = User.objects.get(pk=actor.pk)
                request_barrier.wait()
                job, _ = request_export(
                    actor=local_actor,
                    payload={
                        "report_code": "application-pipeline",
                        "format": "json",
                        "filters": {},
                    },
                    idempotency_key="five-race-export",
                )
                return str(job.pk)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            job_ids = list(pool.map(lambda _: request_once(), range(5)))

        self.assertEqual(len(set(job_ids)), 1)
        self.assertEqual(ReportExportJob.objects.count(), 1)

        with tempfile.TemporaryDirectory() as storage_root, override_settings(
            REPORT_EXPORT_STORAGE_ROOT=storage_root,
        ):
            storage_entered = threading.Event()
            storage_release = threading.Event()

            class BlockingStorage(LocalReportExportStorage):
                def store(self, **kwargs):
                    storage_entered.set()
                    storage_release.wait(timeout=10)
                    return super().store(**kwargs)

            def blocking_work():
                close_old_connections()
                try:
                    return execute_export_job(
                        job_ids[0],
                        storage=BlockingStorage(storage_root),
                    )
                finally:
                    close_old_connections()

            with ThreadPoolExecutor(max_workers=1) as pool:
                running_worker = pool.submit(blocking_work)
                self.assertTrue(storage_entered.wait(timeout=10))
                self.assertEqual(
                    ReportExportJob.objects.get(pk=job_ids[0]).state,
                    ReportExportJob.STATE_RUNNING,
                )

                worker_barrier = threading.Barrier(4)

                def work_once():
                    close_old_connections()
                    try:
                        worker_barrier.wait()
                        return execute_export_job(job_ids[0])["status"]
                    finally:
                        close_old_connections()

                with ThreadPoolExecutor(max_workers=4) as duplicate_pool:
                    duplicates = list(duplicate_pool.map(lambda _: work_once(), range(4)))
                self.assertEqual(duplicates, ["running"] * 4)
                storage_release.set()
                self.assertEqual(running_worker.result(timeout=10)["status"], "completed")

            worker_barrier = threading.Barrier(5)

            def retry_once():
                close_old_connections()
                try:
                    worker_barrier.wait()
                    return execute_export_job(job_ids[0])["status"]
                finally:
                    close_old_connections()

            with ThreadPoolExecutor(max_workers=5) as pool:
                statuses = list(pool.map(lambda _: retry_once(), range(5)))

            self.assertEqual(statuses, ["completed"] * 5)
            files = list(
                __import__("pathlib").Path(storage_root).glob("report-exports/*")
            )
            self.assertEqual(len(files), 1)
            job = ReportExportJob.objects.get()
            self.assertEqual(job.state, ReportExportJob.STATE_COMPLETED)
            self.assertEqual(job.checksum_sha256, __import__("hashlib").sha256(
                files[0].read_bytes()
            ).hexdigest())
