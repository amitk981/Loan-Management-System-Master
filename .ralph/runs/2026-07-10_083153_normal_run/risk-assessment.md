# Risk Assessment

Risk level: High

- Selected slice: 006D-loan-limit-snapshot-storage
- Mode: normal_run
- Standing approval: present; no owner veto is recorded.

## Risk factors

- Financial eligibility evidence is persisted and exposed through a new authenticated API.
- A database migration adds historical policy-source snapshot columns to an existing one-to-one
  assessment table.
- Successful recalculation replaces financial snapshot values and audit old/new metadata.
- Incorrect mutable-row reads could silently rewrite the apparent historical loan-limit basis.

## Controls and residual risk

- GET uses `applications.loan_application.read` plus the existing object-access boundary and writes
  no audit/workflow evidence.
- Serializer, warning derivation, and audit snapshots use only the stored assessment row; tests
  mutate every relevant live source before readback.
- Calculate remains transaction-atomic. Tests prove successful replacement preserves the UUID and
  invalid-state, missing-source, permission, and object-scope failures preserve the prior snapshot.
- The migration is additive and reversible. New calculations always populate policy UUID/name/Board
  reference. A-048 documents honest null output for untouched pre-006D rows instead of unsafe
  backfill from mutable configuration.
- Full backend/frontend gates, migration sync, 95% coverage, diff checks, and independent standards
  and spec reviews passed.

Residual risk: Medium. A deployed database containing pre-006D assessment rows will show null
policy-source metadata until an authorized successful rerun; it will not fabricate historical
policy facts. No external service, deployment, communication, or destructive data action occurs.
