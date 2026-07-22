# Execution Plan

Selected slice: 011E-recovery-decision-approval
Mode: same-worktree repair
Failed validator: `backend-coverage-results.md`

## Bounded repair plan

1. Preserve the existing 011E candidate and reproduce the reported
   `CreditModelOwnershipMigrationTests` historical-app lookup failure with the focused Django test
   command using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
2. Inspect only the migration graph and candidate migration changes that can affect that historical
   state; rank and test falsifiable causes without reopening 011E product behavior.
3. Add the smallest regression assertion needed for the migration-state failure if the existing
   failing migration test is not already a sufficient regression seam, then make the minimal
   migration-domain correction.
4. Re-run the focused migration test, the relevant migration-sync/check probes, and the exact failed
   backend coverage validator until it passes. Preserve RED/GREEN output under this repair run's
   `evidence/terminal-logs/` directory.
5. Inspect targeted diff/status output for scope, protected paths, and debug residue. Complete the
   risk assessment and review packet, setting the final result exactly to
   `Ready for independent validation`.

## Permission boundary

- Allowed repair writes: `sfpcl_credit/**` and `.ralph/runs/**`.
- Protected/forbidden files will not be modified, including `scripts/**`, Ralph configuration,
  workflow policy files, and `docs/source/**`.
- No git add, commit, or push will be invoked.
