# Execution Plan

Selected slice: 011M2-member-portal-kyc-correction-request

Mode: same-worktree repair

## Fixed repair boundary

- Preserve the existing 011M2 candidate.
- Repair only the demonstrated complete-backend-validator failure recorded in
  `.ralph/runs/2026-07-23_104026_repair/failure-summary.md`.
- Do not change protected paths, source documents, queue/state bookkeeping, or unrelated product
  behavior.

## Permissions check

- Candidate repair paths under `sfpcl_credit/**` and this run's `.ralph/runs/**` evidence are
  allowed by `.ralph/permissions.json`.
- No protected, approval-required, or forbidden path is required.

## Feedback loop and repair steps

1. [x] Reproduce the named migration-test boundary with the mandated Ralph virtualenv interpreter
   and retain the existing RED evidence plus a current focused GREEN run.
2. [x] Inspect only the failing test's migration targets and the relevant applications/credit
   migration graph; rank and falsify the bounded hypotheses.
3. [x] Preserve the already-applied minimal regression correction from the immediately preceding
   same-worktree repair; do not alter production migrations or product behavior.
4. [x] Rerun the exact named test until green, then rerun the exact authoritative complete backend
   coverage validator named by the failure summary.
5. [x] Save repair evidence, complete the risk assessment and review packet, and set the packet
   result exactly to `Ready for independent validation`.

## Outcome

- Focused migration test: 1 passed.
- Authoritative backend validator: 1,699 passed, 173 expected skips, 89% coverage against an 85%
  floor.
- Candidate integrity: `git diff --check` passed; no debug instrumentation or additional product
  changes were introduced in this repair run.
