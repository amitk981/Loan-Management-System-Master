# Ralph Handoff

## Last Run
2026-07-13_120630_normal_run

## Current Status

007A6 is complete. The four governed rule/committee create/supersede races now prove the sole new
VersionHistory and `config.changed` rows contain the exact winning resource/version, maker,
distinct checker, reason, proposal/request provenance, approval timestamp/reference, effective
dates, and old/new configuration values. Discriminating loser reason/request/version facts are
explicitly absent from winner evidence.

VersionHistory now stores generic approval evidence through nullable old/new JSON and dedicated
approval reference/time fields. Supersession evidence retains the predecessor's pre-activation old
value and exact closed projection; creation is predecessor-free. Activation remains behind
`decide_proposal` and the shared configuration lock, and open cases remain unchanged.

## Validation

Evidence is under `.ralph/runs/2026-07-13_120630_normal_run/`. RED captures missing closed-
predecessor audit evidence and missing VersionHistory approval content; GREEN includes two
independent four-test PostgreSQL runs with zero skips and 26 focused approval tests. Frontend
build/typecheck/lint and 208 tests pass. Backend check/migration sync and 568 tests pass with 16
expected PostgreSQL-only skips and 93% coverage. No frontend change was introduced.

## Next Run

Run `007C2-approval-case-read-scope-and-snapshot-contract-closure`, then
`007D-approval-action-api-approve-reject-return`. Both are sharpened and execution-ready; 007C2
closes object scope/snapshot coherence before 007D writes immutable approval actions.
