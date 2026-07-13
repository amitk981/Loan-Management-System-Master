# Review Packet: 2026-07-13_055322_architecture_review

## Result
Success

## Slice
architecture-review

## Review Window

`git diff 23331d5...955cfc1`: 006Z11, 006Z12, 007A2, and 007A3.

## Outcome

No production code changed. The review accepted the production corrections for permission/scope
separation, immutable evidence makers, the complete portal denial ledger, retained configuration
history, committee authority, pagination, and sequential governed activation. It created two
corrective boundaries:

- 006Z13: database-enforce member scope and prove every action/calculation entry path.
- 007A4: restore governed PostgreSQL races, canonical authority errors, proposal access, complete
  lifecycle matrices, and open-case/loser snapshots.

007B now depends on 007A4.

## Traceability

- 007A3 requires a competing approval-time activation, but the PostgreSQL suite still calls create/
  supersede as the activation. Retained A2 logs predate proposal migration 0005. 007A4 owns the
  current-interface races twice on PostgreSQL.
- Auth CFG-007 requires open approval cases to remain unchanged; 007A3 tests contain no ApprovalCase
  fixture and omit proposals/cases from loser snapshots. 007A4 owns exact equality proof.
- API contracts §7.1 defines `APPROVAL_AUTHORITY_REQUIRED`; 007A3 introduced a different code.
- Object Access is a must-be-deep module. 006Z11's persisted assignment has only model-level shape
  validation and a partial public action matrix. 006Z13 owns database and behavior closure.
- Full standards/spec findings and requirement-ID disposition are in
  `docs/working/REVIEW_FINDINGS.md`.

## Validation

- Slice queue lint and `git diff --check`: pass; no protected/source/production diff.
- Frontend: build, typecheck, lint, and 207/207 tests pass.
- Backend: check and migration sync pass; 527 tests pass with 16 PostgreSQL-only skips; coverage is
  93% against the 85% floor.
- Focused current concurrency collection applies proposal migration 0005 and skips all four races on
  SQLite. This review does not claim governed PostgreSQL acceptance.

## Recommended Next Action
Run 006Z13, then 007A4 before 007B.
