# Execution Plan

Selected slice: 006X8-credit-executed-object-scope-regression-closure

## Scope and Constraints

- Change only the backend credit action parity regression harness and required Ralph artifacts/docs.
- Preserve all production credit behavior and existing HTTP `403` non-disclosure coverage.
- Use only public eligibility, loan-limit, appraisal, and sanction projection/write interfaces.
- Record a row only after its six-field disabled projection, matching public write denial,
  `OBJECT_ACCESS_DENIED` category, and complete before/after evidence equality all succeed.

## TDD Sequence

1. Replace the metadata completeness assertion with tests describing an executed result ledger and
   focused failures for each omitted phase; run the focused inventory test and save RED output.
2. Introduce the smallest test-harness ledger/row-runner seam and migrate one object-scope row at a
   time from decorator metadata to an executed result emitted after all assertions.
3. Run the focused matrix until the exact eight-action ledger and incomplete-row mutation checks are
   GREEN; save the exact row table and focused HTTP object-denial output.
4. Run dependency scanning plus configured backend and frontend gates using the mandated interpreter.
5. Save evidence and Ralph completion artifacts; update the slice, state, progress, handoff, epic
   digest, and sharpen the next one or two Not Started slices using already-open requirements.

## Verification

- Focused: `sfpcl_credit.tests.test_credit_action_parity_matrix`.
- HTTP non-disclosure: focused eligibility/limit/application and appraisal/sanction API denial tests.
- Backend: Django check, migrations sync, full coverage suite at configured threshold.
- Frontend: build, typecheck, lint, and vitest (no frontend source changes expected).
- Static dependency scan and protected-path/changed-file review.
