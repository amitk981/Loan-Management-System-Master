# Risk Assessment

Risk level: High.

- Selected slice: 011M2-member-portal-kyc-correction-request
- Mode: repair
- Manual review required: Ralph independent validation remains authoritative before integration.

## Root cause

`members.0016_kyc_correction_request` is a current migration leaf with dependencies on compliance,
documents, identity, and the existing members chain. Two historical migration tests built their
pre-migration state by projecting every current leaf except a hard-coded set of later owners.
Because `members` was absent from those sets, the projection advanced application state beyond the
test's declared historical boundary. Adding `members` to the two affected exclusions restores the
declared state without changing production migrations.

The complete suite also exposed a separate deterministic-test defect: the global-search no-echo
assertion searched serialized volatile timestamps and identifiers for the numeric Aadhaar suffix.
It now removes only volatile echo fields before checking the stable response surface.

## Evidence

- Focused credit-ownership and witness migration reproducers: RED before their boundary corrections
  and GREEN afterward in this run's terminal evidence.
- Combined migration projection matrix: 47/47 passed in
  `evidence/terminal-logs/backend-red-migration-projection-matrix.log`.
- Complete backend coverage gate: 1,699 passed, 173 expected skips, 89% coverage against an 85%
  floor in `evidence/terminal-logs/backend-full-coverage-consolidated.log`.
- Django system check and migration synchronization passed.
- Frontend: 52 files and 415 tests passed; typecheck, lint, and production build passed.
- Trusted browser acceptance already passed twice after the PAN-label correction, with matching
  `portal-kyc-correction-decision.png` hashes.
- Candidate integrity: 18 files, 1,972/2,000 lines, one migration, no protected/source changes,
  and clean `git diff --check`.

## Residual risk

Only 28 changed lines remain under the slice limit. The integration run should not introduce
additional product or test changes. The six other migration modules using current leaf projections
passed in the combined matrix and therefore were not modified.
