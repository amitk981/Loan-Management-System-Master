# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 12160220
Lines: 258117
SHA-256: a6a4f490290ad72f3b502b058b569f1891bad7e340dd70e30fa69a4434e30be4
Session ID: 019f756f-525a-7d30-8370-f5bbcb11a985
Raw retention: operator-local, at most 20 runs or 14 days.

## Final Excerpt

+                gate.wait(timeout=15)
+                try:
+                    return execute_communication_job(
+                        self.job_id, adapter=adapter
+                    )["delivery_status"]
+                except CommunicationDispatchConflict:
+                    return "clean_loser"
+            finally:
+                connections["default"].close()
+
+        with ThreadPoolExecutor(max_workers=5) as pool:
+            outcomes = list(pool.map(contender, range(5)))
+        self.assertIn("sent", outcomes)
+        self.assertEqual(self.provider_calls, 1)
+        job = CommunicationDeliveryJob.objects.get(pk=self.job_id)
+        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_SENT)
+        self.assertEqual(job.attempts, 1)
+
+    def _run_stale_recovery_race(self):
+        CommunicationDispatcher.start_job(self.job_id)
+        CommunicationDeliveryJob.objects.filter(pk=self.job_id).update(
+            lease_expires_at=timezone.now() - timedelta(seconds=1)
+        )
+        self.provider_calls = 0
+        self.call_lock = Lock()
+        adapter = self._adapter()
+        gate = Barrier(5)
+
+        def contender(_index):
+            close_old_connections()
+            try:
+                gate.wait(timeout=15)
+                due = CommunicationDispatcher.retry_failed(limit=1)
+                if self.job_id not in due:
+                    return "not_due"
+                try:
+                    return execute_communication_job(
+                        self.job_id, adapter=adapter
+                    )["delivery_status"]
+                except CommunicationDispatchConflict:
+                    return "clean_loser"
+            finally:
+                connections["default"].close()
+
+        with ThreadPoolExecutor(max_workers=5) as pool:
+            outcomes = list(pool.map(contender, range(5)))
+        self.assertIn("sent", outcomes)
+        self.assertEqual(self.provider_calls, 1)
+        job = CommunicationDeliveryJob.objects.get(pk=self.job_id)
+        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_SENT)
+        self.assertEqual(job.attempts, 2)
+        self.assertEqual(job.recovery_count, 1)

tokens used
399,237
Slice `009H8-communications-worker-runtime-and-crash-recovery-closure` is complete and ready for independent Ralph validation.

Implemented:

- Discoverable Celery application with explicit execution and periodic recovery tasks.
- Commit-only asynchronous publication; rollback emits nothing.
- Environment-configured broker, result backend, provider adapter, beat interval, lease, and batch size.
- Durable fenced worker claims with stale-running recovery.
- Accepted-provider replay without redispatch.
- H6 legacy-partial exclusion and safe `operator_blocked` evidence.
- Migration `0010` preserving existing job history.
- Safe retry exhaustion with one reachable operator notification.

Verification completed:

- Focused backend suite: 37 passed; 4 expected PostgreSQL-only skips.
- PostgreSQL acceptance: all 10 queue, worker-claim, and stale-recovery races passed twice.
- Frontend: typecheck and lint passed; 331 tests passed; production build passed.
- Django check, migration synchronization, compilation, JSON validation, and diff checks passed.
- No real provider or external network transport was invoked.
- Full backend coverage remains delegated to the Ralph orchestrator as required.

State, progress, handoff, API contracts, assumptions, Epic 009 digest, slice status, evidence, risk assessment, review packet, final summary, and changed-files manifest are updated. The architecture-review cadence is now due before `009I2`.

No git add, commit, or push was run.
