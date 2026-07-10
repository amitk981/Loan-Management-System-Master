# Execution Plan

Selected slice: 004C-individual-farmer-and-fpc-profile-details

## Scope

- Extend the existing 004B profile tables and read-only member-detail response; do not add
  member mutations, reveal-sensitive endpoints, or unrelated member/KYC tables.
- Add the remaining source-backed individual fields: first, middle, and last name, gender,
  date of birth, occupation, and employment/service years.
- Preserve the existing non-sensitive producer/FPC profile response. Authorised-signatory PAN
  and Aadhaar remain absent because the §13.5 reason, expiry, audit, and no-cache reveal controls
  are outside this slice.
- Enforce profile/member-type compatibility at the model/service boundary.
- Render the additional type-specific data in the existing Member Profile overview composition,
  with the existing empty-value treatment and no new styling or mock-data dependency.

## TDD Sequence

1. Add one backend API test for complete individual-profile serialization and capture RED.
   Add the model fields, migration, and serializer changes; capture GREEN.
2. Add producer/FPC serialization and sensitive-leakage assertions. Keep sensitive fields absent.
3. Add model-boundary tests for individual and producer profile member-type mismatches; implement
   `clean()` validation and save-time enforcement, then rerun the focused backend tests.
4. Add frontend rendering tests for individual and producer/FPC type-specific fields plus missing
   profile behavior; update the API type and existing overview rendering; capture RED/GREEN.

## Verification and Evidence

- Run focused backend and frontend tests during implementation.
- Run Django check, full backend tests, migration sync check, backend coverage, frontend typecheck,
  lint, full tests, build, and `git diff --check`.
- Save red/green and final gate logs under this run's `evidence/terminal-logs/`.
- Save self-contained API response examples and frontend visual evidence in the run folder.
- Update API contracts, the Epic 004 digest, Ralph assumptions only if needed, the next one or two
  Not Started slices, slice status, progress, state, handoff, changed-files, risk assessment,
  review packet, and final summary.
