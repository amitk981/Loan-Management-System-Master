# Review Packet: 2026-07-22_225137_normal_run

## Result
Ready for independent validation

## Slice
011I-security-return-and-cdsl-unpledge-tracking

## Delivered

- Added one versioned security-return aggregate per financial closure, four derived item records, append-only request/idempotency evidence, immutable mutation guards, and one migration.
- Added POST `/api/v1/loan-closures/{id}/security-return/` with Company Secretary/authorised Compliance authority, closed-loan scope, exact replay, changed replay/stale conflict, and audited denial handling.
- Added the existing-security-owner release seam for SH-4, blank cheque, PoA, and CDSL identity/state validation without changing custody records or claiming external DP execution.
- Added physical recipient/time/acknowledgement rules and detailed CDSL PSN/URF/partial-full/DP/auto-unpledge/completion evidence with masked BO projections.
- Added exactly two PostgreSQL race tests under the slice-declared acceptance label and documented the maintained API contract.

## Traceability

| Source requirement | Implementation | Verification |
|---|---|---|
| API contracts §36.4 and data model §22.3 require one post-close security-return record with SH-4, cheque, PoA, CDSL and acknowledgement facts. | `closure.modules.security_return` owns one aggregate, four items, request ledger, route, and verified application-scoped documents. | `SecurityReturnApiTests` no-security, PoA, CDSL, missing-owner, and missing-ack tests. |
| User flows §33 and screen S60 say applicable security must be returned/unpledged before full checklist completion. | Applicability comes from the existing package; the requirement advances only when all applicable items succeed and acknowledgement exists. | Pending-to-complete and CDSL-completion tests; 78-test final regression lane. |
| Component spec §§18.3-18.4 requires custody/recipient/pending evidence and PSN/URF/DP/auto-unpledge result details. | Physical and CDSL evidence fields are retained item-by-item; rejected/pending states cannot complete. | PoA and CDSL behavior tests plus owner reverse-consumer suites. |
| Auth permissions §§12.11, 20.2, 25.9, 26.7 require critical CS/authorised Compliance mutation and read-only Credit/Auditor behavior. | Role, permission, closed-loan, application, and Compliance-team scope checks run server-side; denials are audited. | Forged-applicability/wrong-role test and closure/NOC reverse suites. |
| Slice race/replay contract requires zero-write exact replay and monotonic PostgreSQL races. | Closure locking, unique aggregate/request constraints, payload digests, expected versions, and terminal item states enforce it. | Two final PostgreSQL passes, 2/2 tests each; replay and progressive-version tests. |

## Evidence

- RED/GREEN logs: `evidence/terminal-logs/security-return-*-red.log` and matching `*-green.log` files.
- Final focused/reverse lane: `evidence/terminal-logs/security-return-final-regression.log` — 78 tests passed, 8 expected SQLite-only skips.
- PostgreSQL acceptance: `evidence/terminal-logs/postgresql-security-return-final-1.log` and `postgresql-security-return-final-2.log` — 2 tests passed on each isolated database.
- Checks/migration sync: `evidence/terminal-logs/backend-check-and-migrations.log`.
- Contract examples: `evidence/api-examples.md`.

## Review Notes

- No protected file, source document, frontend file, dependency, or orchestrator-owned mechanical state/status file was changed.
- Product changes are within the 2,000-line, 30-file, and one-migration limits.
- The agent did not run the complete backend suite; High-risk complete coverage belongs to independent validation.

## Recommended Next Action
Run the orchestrator's independent High-risk complete-suite coverage, migration, protected-path, runtime-capability, and artifact gates; commit only if all pass.
