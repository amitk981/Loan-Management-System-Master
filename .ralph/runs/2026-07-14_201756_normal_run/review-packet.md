# Review Packet: 2026-07-14_201756_normal_run

## Result
Ready for independent validation

## Slice
008F2-security-instrument-boundary-and-poa-lifecycle-closure

## Standards Review

- Ownership: `SecurityPackage` and `PowerOfAttorney` now have one model owner in
  `security_instruments`; retained table names/ids/relations remain unchanged. An AST import guard
  proves `legal_documents` has no reverse dependency on security policy.
- Module shape: package scope/create/read/serialization moved into the prescribed
  `security_instruments.modules.security_package`; PoA policy remains in its sibling module.
- Dependency judgment: security policy consumes approval-owned canonical facts and legal-owned
  evidence selectors as required by this corrective slice. Those imports are one-way consumer
  seams; moving approval or legal policy into security would violate ownership more severely.
- Review fixes: replaced textual dependency scanning with AST inspection, tied checklist scope to
  immutable approval-case/sanction-decision creation ids, and narrowed evidence freezing to an
  exact `documents.execution.consumed` ledger instead of mutable document status alone.
- Test fixture reuse follows the established repository Stage-4 pattern. No production duplication
  or reverse import was found after the package-module extraction.

## Spec Review

- Fixed the initial reviewer finding that secondary Company Secretary roles were rejected:
  attorney/checker decisions now use effective active role codes, with a primary-non-CS test.
- Fixed stale-cycle checklist acceptance by requiring its one creation audit to match canonical
  latest approval/sanction ids; a newer terminal decision invalidates the old scope.
- Fixed over-broad mutation freezing by guarding only legal documents consumed by a terminal PoA.
- Extended migration proof from package-only to a fully linked active retained PoA, including all
  protected FKs and honest legacy activation attribution.
- Exact active replay, changed activation, downgrade, purpose clauses, projection rollback,
  current maker handoff, public document generation, and role/permission matrices are covered.

## Traceability

| Requirement | Implementation | Evidence |
|---|---|---|
| Source ownership/table preservation | state-only transfer migration, boundary modules | `28-review-fixes-focused-green.txt` |
| Canonical terminal sanction scope | package policy + checklist creation-cycle audit ids | `10-poa-suite-green.txt`, `28-review-fixes-focused-green.txt` |
| Maker/checker terminal activation | PoA module, evidence snapshot, DB constraint | lifecycle RED/GREEN logs, `32-backend-full-coverage-final.txt` |
| Upstream evidence immutability | exact document-consumption ledger guards | Stage-4 regression and full-suite logs |
| Five-worker races twice | PostgreSQL activation/downgrade tests | `29-postgresql-review-pass1.txt`, `30-postgresql-review-pass2.txt` |

## Recommended Next Action
Run independent Ralph validation; if green, commit/merge this slice into `staging`, then run 008H.
