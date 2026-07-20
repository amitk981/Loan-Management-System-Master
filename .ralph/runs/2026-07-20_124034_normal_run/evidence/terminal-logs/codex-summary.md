# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 8346349
Lines: 192093
SHA-256: 537c07de955959f25dbf22405e1c04f925885af841447c88e1478012578a87a1
Session ID: 019f7e5d-197a-76d0-b933-51acfd4cddfd
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+            loan_account_id=self.fixture.account.pk,
+            calculation_date=date(2026, 8, 31),
+        )
+        invalid = build_interest_rate_proposal(
+            fixture=self.fixture,
+            version="CONSUMED-BACKDATE",
+            effective_from=date(2026, 8, 15),
+        )
+        with self.assertRaises(InterestRateConflict):
+            activate_interest_rate(
+                fixture=self.fixture,
+                proposal=invalid,
+                idempotency_key="consumed-backdate",
+            )
+
+        proposals = [
+            build_interest_rate_proposal(
+                fixture=self.fixture,
+                version=f"BOUNDARY-SUCCESSOR-{suffix}",
+                effective_from=date(2026, 9, 1),
+                rate="9.7500",
+            )
+            for suffix in ("A", "B")
+        ]
+        keys = ["boundary-successor-a", "boundary-successor-b"]
+        outcomes = race_interest_rate_activations(
+            fixture=self.fixture,
+            proposals=proposals,
+            idempotency_keys=keys,
+        )
+        winner_index = outcomes.index("success")
+        winner = proposals[winner_index]
+        winner_key = keys[winner_index]
+
+        self.assertEqual(sorted(outcomes), ["conflict", "success"])
+        predecessor.refresh_from_db()
+        self.assertEqual(predecessor.effective_to, date(2026, 8, 31))
+        replay = activate_interest_rate(
+            fixture=self.fixture,
+            proposal=winner,
+            idempotency_key=winner_key,
+        )
+        self.assertTrue(replay["idempotency_replayed"])
+        with self.assertRaises(InterestRateConflict):
+            activate_interest_rate(
+                fixture=self.fixture,
+                proposal=winner,
+                idempotency_key="changed-winner-key",
+            )
+        self.assertEqual(
+            VersionHistory.objects.filter(
+                versioned_entity_type="interest_rate_config",
+                versioned_entity_id=winner.pk,
+            ).count(),
+            1,
+        )

tokens used
366,333
Implemented `010E4-rate-effective-date-and-write-boundary-closure` and marked it ready for independent validation.

Key outcomes:

- Closed active-rate ORM and bulk-write bypasses with coherent database approval constraints.
- Prevented future-effective rates from changing the loan’s current-rate projection early.
- Added a locked, permission-checked, idempotent, audited due-date convergence facade.
- Routed loan, invoice, and accrual consumers through public rate decisions.
- Replaced affected cross-`TestCase` fixtures with public servicing builders.
- Added the exact four-test PostgreSQL acceptance class.

Validation completed:

- Exact PostgreSQL acceptance: 4 tests passed twice.
- Prior PostgreSQL owner regressions: 8 tests passed.
- Focused reverse-consumer suite: 43 tests passed.
- Public-builder API suite: 7 tests passed.
- Django check, migration sync, compilation, and diff checks passed.
- No frontend, dependency, protected-file, source-document, state, or handoff changes.

Artifacts are available in [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_124034_normal_run/.ralph/runs/2026-07-20_124034_normal_run/review-packet.md) and [review-closure-evidence.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_124034_normal_run/.ralph/runs/2026-07-20_124034_normal_run/review-closure-evidence.md). The orchestrator still owns the complete backend coverage gate, commit, merge, and bookkeeping.
