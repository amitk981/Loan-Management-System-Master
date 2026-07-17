# Slice CR-009: Make field-encryption tamper coverage deterministic

## Status
Complete

## Completion Evidence

- Two focused RED/GREEN cycles:
  `.ralph/runs/2026-07-17_174605_normal_run/evidence/terminal-logs/tdd-summary.md`.
- Five exact stable coverage reports and comparison:
  `.ralph/runs/2026-07-17_174605_normal_run/evidence/field-encryption-coverage-run-*.json` and
  `.ralph/runs/2026-07-17_174605_normal_run/evidence/terminal-logs/field-encryption-coverage-comparison.log`.
- Focused module, Django check, migration sync, and frontend gates are retained in the run evidence.

## Origin
Change request (maintenance stage), accepted 2026-07-17 from docs/change-requests/accepted/CR-009-deterministic-field-encryption-tamper-coverage.md.

## Risk Level
Medium

## Change Request (verbatim)

# Make field-encryption tamper coverage deterministic

## Type
bug-backend

## Severity
Low

## What Is Happening
The field-encryption tamper regression creates a random AES-GCM token and replaces its final Base64 character with `A` or `B`. Depending on the random ciphertext, that mutation either fails canonical Base64 parsing or remains canonical and fails authentication. Both executions correctly raise `InvalidCiphertext`, but they cover different branches in `sfpcl_credit/shared/encryption.py`. A 2026-07-17 serial-versus-six-worker shadow run therefore passed all 1,095 tests with the same 62 skips and zero failures/errors, yet failed exact coverage equivalence because lines 127, 128, and 171 ran only in the serial control.

## Expected Behaviour
Security regression inputs must deterministically exercise malformed/noncanonical Base64 rejection and validly encoded authenticated-ciphertext tampering as separate cases. Repeating the same tests under serial or parallel scheduling must cover the same encryption branches while continuing to reject every tampered token.

## Steps To Reproduce
1. From the repository root, run `./scripts/ralph-shadow-parallel-coverage.sh 6 /private/tmp/ralph-shadow-coverage-6`.
2. Observe that serial and parallel lanes both discover and run 1,095 tests, skip 62, and report zero failures/errors.
3. Compare `sequential-coverage.json` with `parallel-coverage.json`.
4. Observe that `sfpcl_credit/shared/encryption.py` lines 127, 128, and 171 may be executed in only one lane because the random last-character mutation sometimes remains canonical Base64.

## Where It Appears
`sfpcl_credit/tests/test_field_encryption.py`, especially `FieldEncryptionTests.test_tamper_wrong_key_and_inactive_version_fail_closed`, and `sfpcl_credit/shared/encryption.py` Base64/token parsing branches.

## Source Document Reference
unknown — this is deterministic security-test and coverage-gate behavior, not a product contract change.

## Acceptance Criteria
- Add a deterministic focused regression that fails against the current random final-character mutation and proves repeated runs select the same intended rejection branches.
- Use explicit deterministic token mutations to test noncanonical Base64 rejection and canonical ciphertext/authentication tampering separately.
- Every malformed or tampered token still raises `InvalidCiphertext`; no encryption production behavior, key policy, masking behavior, or public API changes.
- The focused field-encryption test module passes repeatedly with stable exact line coverage.
- The normal backend suite and configured coverage floor remain green.
- Preserve a separate owner-run serial-versus-parallel shadow pilot after the corrective slice merges; parallel coverage is not enabled from a failed equivalence report.

## Mandatory First Step: Impact Analysis
Before changing ANY code, write impact-analysis.md in the run folder covering:
- Affected backend models/endpoints/services, with grep evidence.
- Affected frontend screens/components/routes.
- Blast radius: every OTHER module that consumes the affected pieces.
- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module.
- FRONTEND_DESIGN_RULES compliance note for any UI change.
Validation fails this run if impact-analysis.md is missing.

## Acceptance Criteria
- The change request's own acceptance criteria are met.
- Regression tests added for every module named in the impact analysis.
- All quality gates pass.

## Done Checklist

- [x] Impact analysis written before code/test edits
- [x] Execution plan written before code/test edits
- [x] Failing-first tests captured
- [x] Deterministic regression helpers and assertions implemented
- [x] Production encryption behavior unchanged
- [x] Focused repeated coverage stable
- [x] Local scoped/backend and frontend gates passed
- [x] Evidence, risk assessment, review packet, and final summary saved
- [x] Handoff, progress, state, and slice status updated
- [x] Commit delegated to the orchestrator after independent gates
