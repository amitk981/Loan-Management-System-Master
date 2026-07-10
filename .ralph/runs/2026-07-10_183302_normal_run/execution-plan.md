# Execution Plan

Selected slice: `006F-credit-manager-review`

## Scope and constraints

- Add only Credit Manager reviewed/returned decisions for an existing `review_pending` appraisal.
- Extend the public `AppraisalWorkflow.review(...)` seam and a thin application API adapter.
- Persist reviewer, review time, comments, and last decision with one additive migration.
- Preserve frozen prerequisite, recommendation, risk, repayment, submission, and TAT facts.
- Require verified prerequisite provenance, review permission, credit-domain object access, and maker-checker separation.
- Write metadata-only audit/workflow evidence atomically. Do not create sanction, approval, exception, rejection-note, or frontend behavior.

## TDD sequence

1. Inspect the existing appraisal public API, workflow, models, permissions, evidence services, tests, and migration conventions.
2. RED→GREEN: add one public API tracer test for a successful `reviewed` decision, then implement the smallest model/workflow/view/route path and migration.
3. RED→GREEN incrementally cover `returned`, required comments/strict payload, invalid/repeated states, maker-checker, permission/object scope, and unverified provenance.
4. RED→GREEN prove returned appraisals can be revised/resubmitted/reviewed and that frozen appraisal/risk/TAT/submission facts survive current-assessment reruns unchanged.
5. Extend static boundary coverage so review is positively routed through `AppraisalWorkflow` and concrete assessment imports remain forbidden.
6. Update the internal API contract and epic digest, then run focused tests and save red/green logs plus response examples.

## Verification and handoff

1. Run backend check, focused/full coverage suite, and migration-sync with the mandated Ralph virtualenv interpreter.
2. Run frontend lint, typecheck, tests, and build even though this slice has no frontend scope.
3. Review the diff for protected paths, scope, migration count, metadata-only evidence, and diff limits.
4. Save changed-files, risk assessment, review packet, final summary, and terminal evidence.
5. Mark the slice complete; update Ralph state/progress/handoff; sharpen the next one or two Not Started slices using only already-opened source material.
