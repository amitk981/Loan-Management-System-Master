# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 610418
Lines: 10329
SHA-256: d399cd3f1fa873d172d07b614b9b9a9caf6f26976fa71c513641946336a0993d
Session ID: 019f8405-2675-7820-95df-a13f4bf857ef
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+++ b/.ralph/runs/2026-07-21_150232_repair/risk-assessment.md
@@ -1,7 +1,38 @@
 # Risk Assessment
 
-Risk level: To be completed by the selected agent.
+- Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`
+- Mode: repair
+- Risk level: High
+- Repair domain: generic communication-worker provider-acceptance crash recovery
+
+## Material risks
+
+- **External side-effect duplication:** rolling back accepted provider identity after the provider has
+  accepted a message permits a later worker to send the same communication again.
+- **Transaction boundary:** removing an encompassing atomic block must not remove the narrow locks
+  used for job claims, immutable provider evidence, reminder serviceability, or final completion.
+- **Final-attempt truth:** accepted provider evidence must coexist truthfully with a failed/exhausted
+  local job and its operator exception when post-acceptance finalisation crashes.
+- **Regression breadth:** the repair affects the generic worker used by reminders and ordinary
+  communications, although it changes only the transaction wrapper around existing explicit atomic
+  phases.
 
-- Selected slice: CR-015-epic-010-terminal-servicing-owner-finalizer
-- Mode: repair
-- Manual review required: yes until agent completes this file.
+## Controls and evidence
+
+- Existing public-seam tests went RED before the repair for both non-final and final accepted-crash
+  recovery; logs are `communication-nonfinal-accepted-probe.log` and
+  `communication-final-accepted-red.log`.
+- The exact failed test and the non-final companion both pass after the one-line boundary change.
+- All 36 communication-worker runtime tests pass (6 PostgreSQL-only cases skipped by the local
+  SQLite-focused run), covering claim, retry, provider failure, crash, exception, and resolution
+  paths.
+- Django system check and migration consistency pass; no schema, frontend, API, or policy change was
+  made.
+- The orchestrator must still run the authoritative complete-suite coverage and trusted PostgreSQL
+  gates before committing. No local complete-suite result is claimed.
+
+## Residual risk
+
+Low after independent validation. The narrow atomic phases remain intact, and the outer transaction
+was the direct cause of losing database evidence for an irreversible external effect. The retained
+provider evidence now becomes durable before later payload/finalisation work can fail.
diff --git a/sfpcl_credit/communications/modules/communication_dispatcher.py b/sfpcl_credit/communications/modules/communication_dispatcher.py
index 619f46c61949f41d1f4d35ed688df9a1e0da6141..9c17f1a806d3416c36c61ccf127ec3b62369e226
--- a/sfpcl_credit/communications/modules/communication_dispatcher.py
+++ b/sfpcl_credit/communications/modules/communication_dispatcher.py
@@ -1463,7 +1463,6 @@
         )
 
     @classmethod
-    @transaction.atomic
     def execute_generic_job(
         cls,
         job_id,

tokens used
145,902
Ready for independent validation.

The repair removed the outer transaction around `CommunicationDispatcher.execute_generic_job`. Accepted provider evidence now commits before fallible post-delivery processing, preventing redispatch after a worker crash while preserving the narrower claim, serviceability, evidence, and finalization transactions.

Validation completed:

- Previously failing exact test: PASS
- Non-final accepted-crash recovery test: PASS
- Communication worker runtime: 36 tests passed, 6 PostgreSQL-only tests skipped locally
- Django system check: PASS
- Migration consistency: PASS
- Required closure validator: `PASS: validated semantic closure for 3 finding(s) and 5 acceptance id(s).`

Artifacts:

- [Repaired dispatcher](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl_credit/communications/modules/communication_dispatcher.py:1466)
- [Review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/.ralph/runs/2026-07-21_150232_repair/review-packet.md)
- [Risk assessment](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/.ralph/runs/2026-07-21_150232_repair/risk-assessment.md)
- [Final summary](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/.ralph/runs/2026-07-21_150232_repair/final-summary.md)

The orchestrator still owns authoritative complete-suite coverage, trusted PostgreSQL acceptance, bookkeeping, and commit/merge/push. No git or orchestrator-owned state operations were performed.
