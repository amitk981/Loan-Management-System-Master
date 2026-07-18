# Architecture Review Evidence Summary

## Fixed Point

- Previous architecture-review commit: `fb380227`
- Reviewed head: `e3d965ad`
- Exact comparison: `git diff fb380227...e3d965ad`

## Retained Regression Check

The mandated backend interpreter ran 43 focused migration, API, worker-runtime, queue, and CR-011
tests. All 43 pass in 50.004 seconds. Raw output:
`terminal-logs/retained-focused-tests.log`.

## Independent Contract Probes

`review-probes/review_contract_probes.py` contains three read-only defect reproductions:

1. a complete queued H5 outbox/job must migrate from communications 0007 through current leaves;
2. an expired running job at the retry cap must become terminal and not be returned due; and
3. SMS must never call the Email adapter.

All three reach the current defect. Django reports two assertion failures and two errors because
the migration 0009 exception occurs both in the first probe and in its mandatory leaf-restoring
cleanup. Raw output: `terminal-logs/review-contract-probes.log`.

These failures are the evidence for corrective slices 009H9A, 009H9B, and 009H9C. They are not
acceptance-test failures for a production change in this documentation-only architecture review.
