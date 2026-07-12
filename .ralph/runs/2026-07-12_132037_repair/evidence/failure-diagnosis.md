# Failure Diagnosis

## Exact Symptom

The original independent logs reported `Found 6 test(s).`, `Ran 6 tests`, and `OK`, but
`postgresql_acceptance_log_passes` requires the fixed capability contract markers `Found 5` and
`Ran 5`. It therefore returned non-zero and prevented the environment probe.

## Root Cause

006X5 added the required stale-enabled sanction projection/write race as a separately discovered
test method. The three acceptance classes previously contained five tests and the protected Ralph
predicate deliberately fixes that cardinality.

## Repair

The existing duplicate-sanction race now captures the six-field projected sanction action before
launching its two concurrent public writes. It asserts the projection is enabled, one writer wins,
the stale loser receives the exact invalid-state denial, and no loser audit evidence exists. This
keeps both behaviors in one cohesive race and restores the five-test acceptance contract.

## Verification

- Red predicate: `terminal-logs/red-postgresql-acceptance-predicate.log`
- Green predicate: `terminal-logs/green-postgresql-acceptance-predicate.log`
- Independent repetitions: `terminal-logs/postgresql-acceptance-1.log` and
  `terminal-logs/postgresql-acceptance-2.log`
- Environment: `postgresql-environment.md`
