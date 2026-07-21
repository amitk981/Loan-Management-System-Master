# Review Packet: 2026-07-22_034151_normal_run

## Result
Ready for independent validation

## Slice
010N5-terminal-servicing-recurrence-owner-closure

## Outcome

The staff direct-repayment client now invokes only
`POST /api/v1/loan-accounts/{id}/direct-repayment-command/`. A response must contain exactly the
server-owned `replayed`, `capture`, and non-null `allocation` result; capture-only, null-allocation,
or other malformed truth fails visibly after the one request. The client no longer calls SAP-posting
or allocation substeps and no longer supplies `principal_first` policy.

The permanent backend command regression now covers complete replay, changed-payload conflict,
forced allocation-crash rollback, and equal-key convergence. It passed on PostgreSQL. The inherited
MIS and reminder tests and their current reproducer commands remain green; the exact five reminder
cases passed twice on PostgreSQL.

## Traceability

- The source boundary says financial workflow rules belong behind a module interface and frontend
  pages must not implement business rules (`docs/source/codebase-design.md` §§17.3, 26, 42). The
  service now validates and returns only the composite owner result; verified by
  `servicingApi.test.ts::rejects capture-only composite truth after one server-owned request`.
- The retained API contract says the composite endpoint owns capture, SAP posting, principal-first
  allocation, exact replay, and the complete response (`docs/working/API_CONTRACTS.md`, “Epic 010
  terminal servicing owner contracts”). The public command matrix verifies one retained backend
  outcome across replay, conflict, crash, and concurrency.
- Epic 010 digest invariants require backend-owned money/policy, atomic balance evidence, and exact
  replay. The client sends receipt and SAP evidence only; allocation policy is absent from its body,
  and PostgreSQL tests prove one backend result.

## Evidence Reviewed

- Machine closure preflight: PASS for 3 findings and 4 acceptance IDs.
- Frontend service/page tests: 22 passed; typecheck, lint, and build passed.
- Backend focused command tests: 4 passed on SQLite and 4 passed on PostgreSQL.
- Trusted reminder acceptance: exactly 5 passed twice on PostgreSQL.
- Django check and migration sync: passed.
- RED/GREEN, replay, PostgreSQL, and focused-gate logs are indexed by
  `review-closure-evidence.md` and `evidence/terminal-logs/`.

## Review Notes

- No protected file, source document, schema, migration, dependency, or visual design was changed.
- The only prior-run evidence edits normalize two command headings required by the trusted closure
  validator; their commands and historical results are unchanged.
- The prior CR-015 browser-coordinator probe expects the superseded five-call compatibility flow and
  therefore is not the selected slice's fixed-point reproducer. The selected 010N5 composite-owner
  reproducer was replayed exactly and is green.

## Recommended Next Action

Run independent Ralph validation. Product gates must leave the recurrence episode awaiting a later
independent architecture review of all three inherited finding/root pairs.
