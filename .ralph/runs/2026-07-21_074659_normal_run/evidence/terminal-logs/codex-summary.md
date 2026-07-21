# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 3090543
Lines: 71206
SHA-256: ecae18843ca034d1c945a9acb4fe56b2eb56ecbae43cee66d6147d46b19a1782
Session ID: 019f8276-ba37-7963-9e05-537720deca1d
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+            status="active",
+            primary_role=role,
+            password_hash="",
+        )
+        password = "PortalStatement123!"
+        borrower.set_password(password)
+        borrower.save(update_fields=["password_hash"])
+        PortalAccount.objects.create(
+            member=self.account.member,
+            user=borrower,
+            status=PortalAccount.STATUS_ACTIVE,
+        )
+        for code in ("portal.loan_account.read_own", "reports.export"):
+            permission, _ = Permission.objects.get_or_create(
+                permission_code=code,
+                defaults={
+                    "permission_name": code,
+                    "module_name": "portal" if code.startswith("portal.") else "reports",
+                    "risk_level": "high",
+                },
+            )
+            RolePermission.objects.get_or_create(role=role, permission=permission)
+        login = self.client.post(
+            "/api/v1/auth/login/",
+            data=json.dumps({"email": borrower.email, "password": password}),
+            content_type="application/json",
+        )
+        self.assertEqual(login.status_code, 200, login.content)
+        auth = {
+            "HTTP_AUTHORIZATION": f"Bearer {login.json()['data']['access_token']}"
+        }
+        transaction_date = self.fixture.disbursed_at.date().isoformat()
+        created = self.client.post(
+            f"/api/v1/loan-accounts/{self.account.pk}/ledger-statements/",
+            data=json.dumps(
+                {"format": "csv", "from_date": transaction_date, "to_date": transaction_date}
+            ),
+            content_type="application/json",
+            HTTP_IDEMPOTENCY_KEY="portal-own-statement",
+            **auth,
+        )
+        self.assertEqual(created.status_code, 200, created.content)
+        status = self.client.get(
+            f"/api/v1/loan-ledger-statements/{created.json()['data']['statement_job_id']}/",
+            **auth,
+        )
+        downloaded = self.client.get(status.json()["data"]["download_url"], **auth)
+        body = downloaded.content.decode("utf-8")
+        self.assertEqual(downloaded.status_code, 200, downloaded.content)
+        self.assertNotIn("RBL-READ-UTR-001", body)
+        self.assertIn("****", body)

tokens used
228,711
Implemented slice `010K2-loan-ledger-statements-and-export` and marked the review packet exactly:

`Ready for independent validation`

Delivered:

- CSV loan-ledger statement request, status, and signed-download endpoints.
- Canonical 010A ledger reuse with no duplicate financial calculations or ledger table.
- Existing `ScheduledJob`, `DocumentFile`, storage, checksum, and audit infrastructure reuse.
- Deterministic idempotent replay returning the same job, artifact, and checksum.
- Staff permission/object scoping and requester-private export jobs.
- Borrower-own loan scoping with masked transaction references.
- Short-lived, actor/job/loan/document/checksum-bound download capabilities.
- Superseded capability revocation and nondisclosing invalid-download responses.
- Metadata-only request, generation, successful-download, and denied-download audits.
- Updated API contract and retained reconciliation/security evidence.

Validation completed:

- 15 focused statement and reverse-consumer ledger tests passed.
- Django system check passed.
- Migration synchronization check passed with no changes detected.
- Python compilation and `git diff --check` passed.
- RED/GREEN evidence, risk assessment, review packet, and final summary were saved under [.ralph/runs/2026-07-21_074659_normal_run](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_074659_normal_run/.ralph/runs/2026-07-21_074659_normal_run).

No frontend, dependency, migration, protected-file, source-document, git metadata, or orchestrator-owned state changes were made. The orchestrator can now run independent complete-suite and coverage validation.
