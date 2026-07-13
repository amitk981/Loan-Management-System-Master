# Risk Assessment

Risk level: High

- Selected slice: 007C2-approval-case-read-scope-and-snapshot-contract-closure
- Mode: normal_run
- Standing approval: applicable; no revoked entry was present.

## Security and business risk

- The slice changes who can enumerate/retrieve high-sensitivity sanction cases. Failure could leak
  unrelated borrower/credit facts, so permission possession is now separated from persisted
  object scope and direct denials use `OBJECT_ACCESS_DENIED` without read audit writes.
- The slice decides whether a frozen approval route is actionable. The validator therefore checks
  every stored rule/committee/authority/credit-provenance relationship and defaults malformed
  history to hidden/non-actionable instead of reconstructing live authority.
- Exact replay is tightened to reject changed reviewed or policy provenance with 409 and complete
  no-write ledgers. Valid historical snapshots remain stable across later governed configuration.

## Change and rollback characteristics

- No schema, migration, frontend, dependency, external integration, or communication change.
- The behavior is conservative: previously globally visible cases become inaccessible to
  unassigned read-permission holders. Rollback would reintroduce a known object-disclosure defect
  and is not recommended; corrective work should extend persisted scope explicitly.
- Diff remains within configured limits and touches no protected or forbidden path.

## Verification

- RED/GREEN public HTTP tests cover unassigned readers, maker, arbitrary role, assigned and acted
  authority, contradiction categories, exact replay fields, and serializer parity.
- Final backend suite: 585 tests, 16 expected PostgreSQL-only skips, 93% coverage.
- Frontend build/typecheck/lint and 208 tests pass; Django check and migration sync pass.
