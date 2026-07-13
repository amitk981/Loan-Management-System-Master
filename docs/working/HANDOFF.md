# Ralph Handoff

## Last Run
2026-07-13_182512_normal_run

## Current Status

007G adds immutable application-level General Meeting evidence for Director, Director-relative,
and Sanction Committee member borrowing. The §25.11 POST requires the Critical record permission,
canonical current-case read scope, and existing document-download authority; notice, minutes, and
resolution must be distinct existing metadata. Exact replay is zero-write and changed evidence
creates a linked superseding row with attributable audit/workflow history.

The locked final-approval transaction evaluates meeting evidence only after conflict, assignment,
version, and distinct effective authority. Missing, pending, and rejected current outcomes return
dedicated zero-write 409 contracts. Successful final approval freezes the approved record on that
case/cycle; return freezes the then-applicable record without requiring approval, so later
application supersession cannot rewrite historical cycles. Conflict denials and 007F Exception
Register identities/status projection remain unchanged.

Canonical approval collection/detail/action projections now expose the nullable frozen meeting
object beside the unchanged route/effective/action authority ledger. A-085 records the source-
silent document/case access and immutable supersession defaults. 007H and 007I are sharpened to
consume only the case-frozen reference.

## Validation

Retained RED/GREEN logs cover HTTP creation, idempotent supersession, missing final evidence,
rejected/approved outcome gating, exact document/permission failures, and returned-cycle history.
The full gate initially exposed a historical witness migration-test interaction; the new migration
dependency was narrowed from applications 0014 to the already-sufficient 0011 leaf, and the exact
three-test repro plus migration sync now pass.

Frontend build/typecheck/lint and all 208 tests pass. Backend check and migration sync pass; the
full 664-test suite passes with 19 expected PostgreSQL-only SQLite skips and 93% coverage.

## Next Run

Run `007H-credit-sanction-register` next. It is sharpened to take the General Meeting reference
only from the terminal case's frozen 007G relation and the Exception reference only from that
same case's 007F one-to-one entry. Then run 007I in dependency order.
