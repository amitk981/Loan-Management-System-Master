# Execution Plan

Selected slice: 011M2-member-portal-kyc-correction-request

Mode: same-worktree repair

## Demonstrated Failure Boundary

The prior independent `backend-coverage` validators exposed three deterministic boundaries:

1. The new `members.0016` leaf pulled later application state into two historical migration
   projections, first hiding `applications.EligibilityAssessment` and later exposing
   `Witness.verification_folio_number` before its migration boundary.
2. A global-search no-echo assertion scanned volatile timestamp/identifier fields, so the Aadhaar
   suffix `9012` could collide with unrelated response metadata.
3. Fail-fast complete-suite runs revealed those failures one at a time near the end of a
   1,699-test suite.

The complete 011M2 candidate must remain preserved while the migration-test and deterministic
assertion seams are corrected together.

## Plan

1. Verify the intended repair paths are writable under `.ralph/permissions.json` and are not
   protected.
2. Retain the exact focused RED/GREEN reproducers for each observed failure.
3. Inventory every migration test that projects current graph leaves and run all eight affected
   modules together without fail-fast.
4. Correct only the historical projections actually affected by the new `members` leaf and make
   the global-search no-echo assertion ignore volatile metadata rather than raw response JSON.
5. Run the 47-test migration matrix, then one complete 1,699-test coverage validator with the 85%
   floor.
6. Record the diagnosis, validator evidence, residual risk, and independent-validation handoff in
   `risk-assessment.md` and `review-packet.md`; leave orchestrator-owned mechanical files untouched.

## Allowed Repair Scope

- `sfpcl_credit/tests/test_credit_model_ownership_migration.py`
- `sfpcl_credit/tests/test_witness_evidence_migration.py`
- `sfpcl_credit/tests/test_global_search_api.py`
- `.ralph/runs/2026-07-23_111735_repair/**` for this run's evidence and review artifacts.

## Required Completion Signal

- The combined migration matrix passes all 47 tests.
- The exact prior `backend-coverage` validator passes all 1,699 tests and its 85% floor.
- Frontend tests, typecheck, lint, build, migration synchronization, trusted browser evidence, and
  diff integrity remain green.
- `review-packet.md` Result is exactly `Ready for independent validation`.
