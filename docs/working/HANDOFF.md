# Ralph Handoff

## Last Run

2026-07-15_213859_repair

## Current Status

CR-008 is complete. Both migration-facing `DocumentTemplate` constraints now use deterministic
ordered tuples in current model state. Historical migration `documents.0002` remains untouched;
forward migration `0005` removes and recreates the same two named constraints with the same exact
approval-status and borrower-type values. No endpoint, service, permission, frontend, or business
behavior changed.

## Validation

Evidence is in `.ralph/runs/2026-07-15_213859_repair/evidence/`. The focused migration-state test
captured RED for both unordered model and terminal migration values, then GREEN after the forward
migration. Migration checks report `No changes detected` for hash seeds 0, 1, 42, 123456, and
random. Frontend lint, typecheck, all 305 tests, and build pass; Django check and migration drift
pass; all 900 backend tests pass with 46 expected capability skips at 91% coverage.

## Next Run

Run the sharpened `008M-documentation-hub-frontend-wiring`; it must reuse L4's latest-current
selector/signed capability and one server snapshot without reading portal submission rows or
duplicating document audit events. CR-008 adds no frontend work: the existing template statuses and
borrower variants remain unchanged. After 008M, 009A remains concrete.
