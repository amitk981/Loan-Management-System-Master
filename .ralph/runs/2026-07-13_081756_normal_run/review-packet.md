# Review Packet: 2026-07-13_081756_normal_run

## Result
Complete; all local gates pass.

## Slice
007A4-approval-governance-concurrency-and-case-snapshot-closure

## Review Focus

- `decide_proposal` is now the exercised concurrency seam: two valid pending proposals race two
  distinct eligible checkers for all four rule/committee create/supersede paths.
- Proposal detail uses maker, persisted checker authority, or `approvals.matrix.read`; it no longer
  exposes Critical reasons and actor/action facts to arbitrary sessions.
- `ApprovalCase` has explicit immutable configuration snapshot columns and a positive version.
  A real open case stays byte-for-byte identical through rejection, successful supersession,
  resolver calls, and proposal reads.
- Both resource kinds have independent malformed/unknown/non-finite, inactive-resolution,
  persisted committee authority, stale/replay/reject, and approval-time revalidation coverage.

## Traceability

Auth §§31.1-31.2 says Approval Matrix is Critical and CFG-007 says later matrix changes must not
alter open cases; the model/migration store the rule/committee/approver/date/version projection and
`test_open_case_configuration_snapshot_is_immutable_across_governed_decisions` asserts complete
before/after equality. API contract §7.1 says `APPROVAL_AUTHORITY_REQUIRED`; production, tests, and
`API_CONTRACTS.md` use only that code. Codebase-design §22.3 requires lock-bound config activation;
`ApprovalMatrixConcurrencyTests` proves governed one-winner behavior twice on PostgreSQL.

## Validation

- RED/GREEN: proposal-detail access, canonical authority code, and missing case snapshot fields.
- Sequential approval matrix/case suite: 23 passed on SQLite (4 expected PostgreSQL skips).
- PostgreSQL: four governed race tests passed twice after proposal migration `0005`; the final run
  had no unapplied migrations and includes case snapshot migration `0006`.
- Backend: check and migration sync pass; 535 tests pass, 16 expected skips, 93% coverage.
- Frontend: build, typecheck, lint, and 208 tests pass.

## Recommended Next Action

Allow independent Ralph validation and commit/merge/push to staging, then run 007B.
