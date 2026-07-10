# Execution Plan

Selected slice: 006E3-appraisal-history-and-review-authority-hardening

## Boundaries

- Implement only the 006E3 corrective appraisal scope; no frontend, sanction, approval, or lock-order work.
- Keep `AppraisalWorkflow.review(...)` as the sole public mutation seam.
- Use one additive credit migration for the review-decision table, conservative provenance repair,
  and latest-only legacy review backfill.
- Preserve metadata-only generic audit/workflow evidence and all existing appraisal projections.

## Test-first sequence

1. Add a public API tracer proving return → maker revision → resubmit → final review retains two
   immutable decision rows and exposes their ordered history while current appraisal fields project
   only the latest decision. Capture the focused failing run before implementation.
2. Add reviewed/rejected and forced-failure transaction regressions proving exactly one history row
   per successful decision and all related writes roll back together. Capture RED, implement the
   smallest workflow/model changes, then capture GREEN.
3. Add the authority matrix regression: an in-scope non-Credit-Manager owner with
   `credit.appraisal.review` receives `PERMISSION_DENIED` and writes no appraisal/history/audit/
   workflow/rejection evidence; a scoped Credit Manager succeeds. Capture RED then GREEN.
4. Add migration-executor fixtures for positive audit proof, missing proof, later reruns, timestamps
   after preparation, mismatched application/IDs, pre-existing legacy-unverified rows, and legacy
   latest-only review backfill. Prove forward and reverse behavior with the mandated interpreter.
5. Add evidence-redaction assertions showing audit/workflow metadata includes the decision-history
   ID but excludes comments, return reason, rejection detail, and frozen free text.

## Implementation

- Add an appraisal-owned immutable review-decision model with appraisal, decision, non-blank
  comments, reviewer, decision time, from/to states, and explicit legacy provenance metadata.
- In the review transaction, enforce both the exact permission and active `credit_manager` role,
  create the history row, and reference its ID from audit/workflow metadata.
- Repair legacy `verified` provenance only when both exact prerequisite IDs have positive success
  audits no later than preparation, no later success audit, source timestamps no later than
  preparation, and same-application ownership; otherwise downgrade without altering copied JSON.
- Backfill only the latest reconstructable legacy decision and mark it latest-only.
- Update the appraisal API contract summary and Epic 006 digest to match implemented behavior.

## Verification and closeout

- Run focused appraisal and migration suites, forward/reverse proof, Django check, migration sync,
  full backend coverage, and all frontend lint/typecheck/test/build gates.
- Save red/green and gate logs under `evidence/terminal-logs/`, plus self-contained provenance,
  history, authority, and migration evidence.
- Record changed files and risk/review/final summaries; sharpen 006F3 and 006G only from sources
  already opened; update slice status, state, progress, and handoff. Do not stage or commit.
