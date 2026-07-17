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
