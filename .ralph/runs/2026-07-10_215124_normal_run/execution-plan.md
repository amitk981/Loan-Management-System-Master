# Execution Plan

Selected slice: `006E4-legacy-appraisal-remediation-and-history-backfill`

## Scope and constraints

- Implement only the corrective legacy appraisal migration and the existing explicit
  prerequisite-revalidation action.
- Keep the HTTP view thin and all repair rules behind `AppraisalWorkflow`.
- Preserve recommendation, repayment, risk, TAT, frozen history, and free-text facts; audit and
  workflow evidence stays metadata-only.
- Do not alter frontend code, protected files, or `docs/source/`.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.

## TDD sequence

1. Add one migration test for a returned-then-resubmitted legacy appraisal whose latest returned
   projection is complete but whose current state is `review_pending`; run it RED, then add a
   forward-only corrective migration and run it GREEN.
2. Add migration cases incrementally for reviewed-then-submitted, already-backfilled, incomplete
   latest projections, and multiple historical cycles. Prove at most one latest-only row is added,
   destination state derives from the decision, reverse is non-destructive, and a second forward
   application is idempotent.
3. Add one API/module test for `review_pending` revalidation; run it RED, then extend
   `AppraisalWorkflow.revalidate_prerequisites` so verified current projections are pinned while
   the appraisal remains independently reviewable.
4. Add behavior tests one at a time for reviewed, draft, rejected, and submitted legacy rows.
   Reviewed remediation must preserve immutable history, clear only current review authority,
   return to draft, and fail sanction until maker resubmission plus a new Credit Manager review.
   Terminal states remain unchanged and quarantined.
5. Add denial, malformed-payload, audit-failure, and workflow-failure rollback assertions through
   the public endpoint/module interface. Confirm no partial projection, state, history, audit, or
   workflow writes.

## Verification and evidence

- Save every focused RED and GREEN command output under
  `evidence/terminal-logs/`, including migration forward/reverse/idempotency evidence.
- Run Django check, focused tests, full coverage suite with the configured 85% floor, and
  `makemigrations --check` using the mandated interpreter.
- Run configured frontend lint, typecheck, tests, and build even though no frontend files change.
- Record changed files, risk assessment, review packet, final summary, state/progress/handoff,
  slice completion, and sharpen the next one or two Not Started slices using only already-opened
  source material.
