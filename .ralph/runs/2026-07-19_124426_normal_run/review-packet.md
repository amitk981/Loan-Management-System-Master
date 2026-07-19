# Review Packet: 2026-07-19_124426_normal_run

## Result
Ready for independent validation

## Slice
009L5-epic-009-exact-selector-and-consumer-parity-closure

## Recommended Next Action
Run Ralph's independent protected-path, full backend coverage, migration, and artifact gates; commit
only if they pass.

## Outcome

- Exact Loan Account selection now rejects non-queryable lifecycle actor-role evidence before
  count, total pages, offset, and projection.
- Exact SAP account and S37 selectors bind the persisted completion/send digest to the immutable
  owner evidence before pagination.
- Exact pending-CFC selection validates the initiation comment digest and retained initiation,
  task, transfer-pending, and unfunded-account relations before pagination; four-row overscan is
  removed from CFC and Loan Account collections.
- Member-portal pre-payment stages require the same member/application/customer-code edge as the
  SAP account owner.
- Single-row and bounded-bulk lifecycle resolution share one scalar evidence validator.
- Loan Account portfolio fixtures no longer read or copy Django private `_state`; they use the
  public model constructor through a bounded test factory.
- The working API contract records the exact selector/no-overscan behavior, and PostgreSQL
  `pgcrypto` is enabled for the exact SHA-256 selector.

## TDD Evidence

- `portal-sap-edge-red.log` -> `portal-sap-edge-green.log`: another application's completion was
  incorrectly accepted, then rejected.
- `loan-account-exact-count-red.log` -> `loan-account-exact-count-green.log`: lifecycle drift
  reported `total_count: 1`, then `0`.
- `sap-completion-exact-count-red.log` -> `sap-completion-exact-count-green.log`: completion digest
  drift reported `1`, then `0`.
- `s37-exact-count-red.log` -> `s37-exact-count-green.log`: send checksum drift reported `1`, then
  `0`.
- `cfc-exact-count-red.log` -> `cfc-exact-count-green.log`: initiation drift reported `1`, then `0`.
- `long-drift-pagination-green.log`: six consecutive newer drifted identities leave exact total 21,
  a full first page, and the stable original row on page two.

All paths above are relative to this run's `evidence/terminal-logs/` directory.

## Verification

- Impacted backend: 45 tests passed.
- Reverse consumers: 179 tests passed, 14 expected skips.
- Refactor/probe set: 17 tests passed.
- Django system check: green.
- Migration sync: no changes detected.
- New extension migration smoke: green on the configured local test database.
- `git diff --check`: green.
- The complete backend suite and coverage were deliberately not run by the agent; Ralph owns that
  authoritative gate. No frontend files changed, so no agent-side frontend gate was required.

## Traceability

- `functional-spec.md` M07-FR-010 says disbursement remains blocked until the SAP customer code is
  confirmed. The SAP/portal selectors now require the requested member/application/code edge,
  verified by `PortalCanonicalSapEdgeTests` and the active Loan Account completion-drift test.
- `functional-spec.md` M08-FR-003 and M08-FR-006 require truthful blockers before initiation and CFC
  routing. The exact pending-CFC identity filter excludes stale initiation evidence before count,
  verified by `test_stale_initiation_affects_neither_total_nor_page`.
- `api-contracts.md` sections 29-31 and `auth-permissions.md` sections 19.3, 25.7, 26.5, and 34.7
  assign SAP, Loan Account, Senior Finance, and CFC behavior to their current owners. The changes
  deepen those existing interfaces and do not infer authority from mutable role/status labels.
- `codebase-design.md` sections 16, 26, and 42 require owner modules, interface tests, selectors for
  complex reads, and centralized workflow rules. Lifecycle validation is now single-sourced and
  the retained regressions exercise public HTTP/module behavior.

## Scope Review

- No protected file, `docs/source/`, state, progress, HANDOFF, or slice status was edited.
- No frontend styling/component/browser work, SAP posting-confirmation authority, or Epic 010
  behavior was added.
- No git add, commit, merge, or push was attempted.
