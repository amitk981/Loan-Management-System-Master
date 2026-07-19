# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 3100007
Lines: 54574
SHA-256: 6f96bcedb9b6c970f4c9aff273ab41f67a85d7f828d1e6395321a6fd2fdde01b
Session ID: 019f7bcf-2506-78d2-87e7-3740e7bb44ad
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+Reproducer: `.ralph/runs/2026-07-20_004623_architecture_review/evidence/review-probes/ledger-pagination-inspection.log`.
+
+## AR-010-SERVICING-SEAM-001 — servicing evidence and tests bypass public owner seams
+
+Root: ROOT-010-SERVICING-OWNER-SEAM
+
+Severity: Medium
+Disposition: New
+Reviewed boundary: `0b5be35c...6883816b` (010A–010D)
+
+The allocation owner discards its mandatory reason instead of retaining it in immutable decision
+evidence; repayment capture constructs a communications-owned Notification directly; and servicing
+modules repeat low-level AuditLog manifest construction instead of consuming narrow owner facades.
+All five new test modules instantiate other `TestCase` classes, invoke their `setUp`/private helpers,
+and traverse deep fixture chains. Assertions are substantive and public-HTTP-facing, but the fixture
+and owner coupling makes future refactors unsafe. Consolidate these seams with the admitted 010C2/
+010D2 work and the Epic 010 closure; no separate leaf corrective is warranted.
+
+Reproducer: `.ralph/runs/2026-07-20_004623_architecture_review/evidence/review-probes/servicing-seam-inspection.log`.
+
 ## Targeted closure review 2026-07-19_193824_architecture_review — Epic 009 generation 2
 
 Reviewed product commit: `4f8febd3` (009L7), relative to successful architecture-review commit
diff --git a/docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md b/docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md
index 77e34fb64e2668a37e1fbe0424514c374f3a4da4..9755e749a441ea97a54e2f50e2150fa7f8009572
--- a/docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md
+++ b/docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md
@@ -42,6 +42,12 @@
    do not imply mutation. Portal users see only authenticated-member projections.
 10. High-contention financial operations require a real PostgreSQL race test in addition to unit/API
     tests. Exact replay must have one retained result and one financial effect.
+11. M09-FR-010 and direct-repayment flow §27 order the principal/interest balance transition after
+    the retained SAP posting decision. A captured or evidence-matched receipt alone cannot admit an
+    ordinary financial allocation.
+12. `bank_statement_line_id` is a canonical relationship, not a caller-asserted UUID. Subsidiary
+    auto-match requires both borrower name and loan application number under M09-FR-007; one fact or
+    an account number alone is insufficient.
 
 ## Dependency and ownership boundaries
 
@@ -85,6 +91,9 @@
 
 - Model manual statement imports/lines; match exact, high-confidence UTR/amount/date/borrower/loan
   facts, retain ambiguous/missing facts in an unmatched queue, and audit authorised manual matches.
+- Keep one referentially coherent statement-line/receipt owner; import and automatic/manual match
+  apply the same permission and loan-object scope. For subsidiary evidence, borrower name and loan
+  application number are both mandatory rather than alternative narration hints.
 - A statement line cannot be consumed twice. Matching does not allocate or alter balances.
 - Sources: flow §27.4; functional M09-FR-008/009; roadmap §§15.2–15.4; tests API-REP-006/007.
 

tokens used
313,803
Architecture review is complete and marked **Ready for independent validation** in the [review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_004623_architecture_review/.ralph/runs/2026-07-20_004623_architecture_review/review-packet.md).

Key outcomes:

- High: allocation permits balance changes before SAP posting and after an unapproved manual-match exception. It also lacks the required allocation idempotency contract.
- High: bank-statement evidence can contain orphaned or contradictory links, and import-time matching bypasses the match permission/object-scope boundary.
- Medium: ledger pagination materializes full repayment history.
- Medium: servicing audit, communications, and test fixtures bypass stable owner seams.
- No production code or protected files were modified.

Corrective work:

- Existing [010C2](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_004623_architecture_review/docs/slices/010C2-manual-allocation-and-financial-reversal-controls.md) now owns allocation admission closure.
- New grouped [010D2](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_004623_architecture_review/docs/slices/010D2-statement-evidence-owner-and-scope-closure.md) owns the statement-evidence boundary.
- `010E` now depends on `010D2`.

Convergence metrics:

- Findings closed: 0
- New Critical: 0
- New High: 2
- New Medium: 2
- New Low: 0
- Corrective slices added: 1
- Existing corrective slice: 010C2

Four review-only public assertions reproduced the two High roots. Final path-scope, semantic-manifest, corrective-admission, convergence, dependency-graph, diff-limit, and artifact checks passed. Evidence is recorded in the [validation log](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_004623_architecture_review/.ralph/runs/2026-07-20_004623_architecture_review/evidence/terminal-logs/review-validation.log) and [active findings ledger](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_00462
