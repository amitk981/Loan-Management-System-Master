# Ralph Handoff

## Last Run
2026-07-13_222951_architecture_review

## Current Status

The architecture review of 007F2, CR-004, 007G2, and 007H2 is complete. Production code was not
changed. Exception routing, General Meeting current/frozen evidence, document attribution, sanction
generation, and object-scoped decision/register reads are substantive, but one High frozen-history
defect remains: canonical case validity still compares frozen case provenance with the mutable live
appraisal snapshot.

Two public review probes changed only the live appraisal policy name. Pending case detail changed
from 200 to 404 while its stored coherence/index remained unchanged. After terminal approval, case
detail still returned 404 while the same actor's sanction decision and Credit Sanction Register
returned 200/one row. `007H3-frozen-case-provenance-and-read-scope-parity-closure` is queued and
`007I` now depends on it.

The independent review also noted that CR-004's mandatory hosted staging/PR green criterion is not
retained in repository evidence. Its local repair is substantive, but the owner/orchestrator must
confirm the external check before promotion. A-085 remains the explicit source-silent sensitivity
decision; no narrower compliance matrix was invented. 007J no longer proposes wiring borrower
MP12 to the internal sanction-decision endpoint; A-089 records the safe boundary.

## Validation

Independent Standards and Spec reviews, production/test hunk inspection, retained slice evidence,
functional IDs M05-FR-003/006/009/012, context truth, and Blocked-slice state were checked. Frontend
build/typecheck/lint and all 208 tests pass. Backend check/migration sync and all 677 tests pass with
19 expected PostgreSQL-only SQLite skips; coverage is 93% against the 85% floor. Queue/state/path
checks and final Ralph artifact validation remain for the orchestrator.

## Next Run

Run `007H3-frozen-case-provenance-and-read-scope-parity-closure`, then
`007I-sanction-workbench-ui`. Do not start 007I until old/new cycle reads and
detail/action/decision/register scope parity pass through frozen case facts only.
