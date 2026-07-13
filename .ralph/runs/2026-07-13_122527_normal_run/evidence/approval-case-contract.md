# Approval-Case Contract Evidence

## RED → GREEN map

- Object scope: `01-object-scope-red.log` exposes the permission-implied global list;
  `02-object-scope-green.log` proves scoped list/detail plus acted-history access.
- Snapshot coherence: `03-injected-snapshot-red.log` exposes an injected approver entering the
  queue; `05-routing-snapshot-matrix-green.log` proves independently named injection, duplicate,
  role/count, amount/condition, joint, and register losers are hidden without writes.
- Replay provenance: `08-provenance-replay-red.log` exposes a changed assessment replay returning
  200; `09-provenance-replay-green.log` and `10-provenance-replay-matrix-green.log` prove stable
  409 responses for changed assessment, policy, reviewed date, and exception provenance.
- §25.2 projection: `06-current-status-red.log` captures missing `current_status`, while
  `07-current-status-green.log` proves it. `11-serializer-parity-red.log` captures divergent list
  provenance, and `12-serializer-parity-green.log` proves enrichment/list/detail parity.
- Governed immutability: `13-real-enrichment-governance-green.log` executes submit → enrich →
  canonical read, rejected supersession, later approved supersession, exact winner evidence, loser
  omission, and complete case/public-projection equality.

## Complete ledger assertions

Public negative rows snapshot the entire approval case, action, non-auth audit, and workflow
ledgers before list/detail/replay and assert exact equality afterward. The governance row snapshots
the enriched case, action rows, case-targeted audit evidence, workflow identity, and canonical
detail projection; configuration governance changes only its attributable proposal/resource/
VersionHistory/`config.changed` facts.

## Gate evidence

- `16-focused-contract-closure-green.log`: 49 focused contract tests.
- `15-focused-approval-suite-green.log`: 74 broader approval tests, five expected PostgreSQL skips.
- `17-backend-check.log` and `18-migrations-check.log`: Django clean; no migration changes.
- `26-backend-final-full-suite.log` and `27-backend-final-coverage.log`: 585 tests, 16 expected
  PostgreSQL-only skips, 93% coverage.
- `21-frontend-build.log` through `24-frontend-tests.log`: build, typecheck, lint, and 208 tests.
