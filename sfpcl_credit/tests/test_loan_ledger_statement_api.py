import csv
import io
import json
from tempfile import TemporaryDirectory

from django.test import Client, TestCase, override_settings


class LoanLedgerStatementApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.test_loan_account_reads_api import (
            ActiveLoanAccountReadApiTests,
        )

        fixture = ActiveLoanAccountReadApiTests(
            "test_exact_transfer_projects_active_funded_amounts_and_activation_time"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.client = Client()
        self.auth = fixture.auth
        permission, _ = Permission.objects.get_or_create(
            permission_code="reports.export",
            defaults={
                "permission_name": "Export reports",
                "module_name": "reports",
                "risk_level": "high",
            },
        )
        RolePermission.objects.get_or_create(
            role=fixture.reader.primary_role,
            permission=permission,
        )
        self.storage = TemporaryDirectory()
        self.settings = override_settings(DOCUMENT_STORAGE_ROOT=self.storage.name)
        self.settings.enable()

    def tearDown(self):
        self.settings.disable()
        self.storage.cleanup()

    def test_staff_downloads_parseable_csv_reconciled_to_canonical_ledger(self):
        ledger = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger/",
            **self.auth,
        )
        self.assertEqual(ledger.status_code, 200, ledger.content)
        canonical = ledger.json()["data"]

        requested = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger-statements/",
            data=json.dumps(
                {
                    "format": "csv",
                    "from_date": canonical[0]["transaction_date"],
                    "to_date": canonical[-1]["transaction_date"],
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="statement-first-tracer",
            HTTP_X_REQUEST_ID="req-statement-first-tracer",
            **self.auth,
        )

        self.assertEqual(requested.status_code, 200, requested.content)
        job = requested.json()["data"]
        self.assertEqual(job["status"], "succeeded")
        self.assertEqual(job["format"], "csv")
        self.assertEqual(job["row_count"], len(canonical))
        self.assertEqual(job["opening_balance"], "0.00")
        self.assertEqual(job["closing_balance"], canonical[-1]["total_outstanding"])

        status = self.client.get(
            f"/api/v1/loan-ledger-statements/{job['statement_job_id']}/",
            **self.auth,
        )
        self.assertEqual(status.status_code, 200, status.content)
        descriptor = status.json()["data"]
        self.assertEqual(descriptor["checksum_sha256"], job["checksum_sha256"])
        self.assertNotIn("storage_key", descriptor)

        download = self.client.get(descriptor["download_url"], **self.auth)
        self.assertEqual(download.status_code, 200, download.content)
        self.assertEqual(download["Content-Type"], "text/csv; charset=utf-8")
        rows = list(csv.DictReader(io.StringIO(download.content.decode("utf-8"))))
        self.assertEqual(len(rows), len(canonical))
        self.assertEqual(rows[0]["transaction_type"], canonical[0]["transaction_type"])
        self.assertEqual(rows[0]["debit"], canonical[0]["debit"])
        self.assertEqual(rows[0]["credit"], canonical[0]["credit"])
        self.assertEqual(rows[0]["total_outstanding"], canonical[0]["total_outstanding"])

    def test_exact_request_replay_returns_one_job_artifact_and_checksum(self):
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.scheduler.models import ScheduledJob

        documents_before = DocumentFile.objects.count()
        transaction_date = self.fixture.disbursed_at.date().isoformat()
        payload = json.dumps(
            {"format": "csv", "from_date": transaction_date, "to_date": transaction_date}
        )
        responses = [
            self.client.post(
                f"/api/v1/loan-accounts/{self.account.pk}/ledger-statements/",
                data=payload,
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="statement-exact-replay",
                **self.auth,
            )
            for _ in range(2)
        ]

        self.assertEqual([response.status_code for response in responses], [200, 200])
        self.assertEqual(responses[0].json()["data"], responses[1].json()["data"])
        self.assertEqual(ScheduledJob.objects.filter(job_type="report_export").count(), 1)
        self.assertEqual(DocumentFile.objects.count(), documents_before + 1)

    def test_statement_job_is_private_to_requester_even_for_another_portfolio_reader(self):
        transaction_date = self.fixture.disbursed_at.date().isoformat()
        created = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger-statements/",
            data=json.dumps(
                {"format": "csv", "from_date": transaction_date, "to_date": transaction_date}
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="statement-private-job",
            **self.auth,
        )
        self.assertEqual(created.status_code, 200, created.content)

        user_fixture = self.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.owner.fixture
        other = user_fixture._user("accounts_head", "Other Portfolio Reader")
        user_fixture._grant(other, "finance.loan_account.read")
        user_fixture._grant(other, "reports.export")
        guessed = self.client.get(
            f"/api/v1/loan-ledger-statements/{created.json()['data']['statement_job_id']}/",
            **auth_fixture._auth(other),
        )

        self.assertEqual(guessed.status_code, 404, guessed.content)

    def test_tampered_download_denial_is_audited_without_rows_urls_or_bank_data(self):
        from sfpcl_credit.identity.models import AuditLog

        transaction_date = self.fixture.disbursed_at.date().isoformat()
        created = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger-statements/",
            data=json.dumps(
                {"format": "csv", "from_date": transaction_date, "to_date": transaction_date}
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="statement-denial-audit",
            **self.auth,
        )
        status = self.client.get(
            f"/api/v1/loan-ledger-statements/{created.json()['data']['statement_job_id']}/",
            **self.auth,
        )
        denied = self.client.get(f"{status.json()['data']['download_url']}tampered", **self.auth)

        self.assertEqual(denied.status_code, 404, denied.content)
        audit = AuditLog.objects.filter(action="loans.ledger_statement.downloaded").latest(
            "created_at"
        )
        self.assertEqual(audit.new_value_json["outcome"], "denied")
        serialized = json.dumps(audit.new_value_json)
        self.assertNotIn("download_url", serialized)
        self.assertNotIn("storage_key", serialized)
        self.assertNotIn("RBL-READ-UTR-001", serialized)
        self.assertNotIn("rows", serialized)

    def test_portal_borrower_can_download_only_own_masked_statement(self):
        from sfpcl_credit.identity.models import (
            Permission,
            PortalAccount,
            Role,
            RolePermission,
            User,
        )

        role, _ = Role.objects.get_or_create(
            role_code="borrower_portal_user",
            defaults={"role_name": "Borrower Portal User", "status": "active"},
        )
        borrower = User.objects.create(
            full_name="Portal Statement Borrower",
            email="portal.statement@sfpcl.example",
            status="active",
            primary_role=role,
            password_hash="",
        )
        password = "PortalStatement123!"
        borrower.set_password(password)
        borrower.save(update_fields=["password_hash"])
        PortalAccount.objects.create(
            member=self.account.member,
            user=borrower,
            status=PortalAccount.STATUS_ACTIVE,
        )
        for code in ("portal.loan_account.read_own", "reports.export"):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "portal" if code.startswith("portal.") else "reports",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)
        login = self.client.post(
            "/api/v1/auth/login/",
            data=json.dumps({"email": borrower.email, "password": password}),
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200, login.content)
        auth = {
            "HTTP_AUTHORIZATION": f"Bearer {login.json()['data']['access_token']}"
        }
        transaction_date = self.fixture.disbursed_at.date().isoformat()
        created = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger-statements/",
            data=json.dumps(
                {"format": "csv", "from_date": transaction_date, "to_date": transaction_date}
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="portal-own-statement",
            **auth,
        )
        self.assertEqual(created.status_code, 200, created.content)
        status = self.client.get(
            f"/api/v1/loan-ledger-statements/{created.json()['data']['statement_job_id']}/",
            **auth,
        )
        downloaded = self.client.get(status.json()["data"]["download_url"], **auth)
        body = downloaded.content.decode("utf-8")
        self.assertEqual(downloaded.status_code, 200, downloaded.content)
        self.assertNotIn("RBL-READ-UTR-001", body)
        self.assertIn("****", body)
