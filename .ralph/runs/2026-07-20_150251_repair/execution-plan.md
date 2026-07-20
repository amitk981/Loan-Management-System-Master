# Execution Plan

Selected slice: `010H2-interest-calculation-payment-and-replay-owner-closure`

## Repair boundary

- Preserve the quarantined product, migration, and test implementation byte-for-byte.
- Fix only the trusted failure from run `2026-07-20_145726_repair`: the current repair run is
  missing the required `review-closure-evidence.md` artifact.
- Limit edits to this run's `.ralph/runs/2026-07-20_150251_repair/` evidence and handoff files;
  `.ralph/permissions.json` allows that path, while protected/source paths remain untouched.

## Feedback loop

1. Use `test -s .ralph/runs/2026-07-20_150251_repair/review-closure-evidence.md` as the tight
   reproducer for the demonstrated missing-artifact failure.
2. Materialize the machine-readable finding and AC-INT-1 through AC-INT-7 mappings in the current
   run, with exact `path::selector` test specifications and retained current-run evidence.
3. Run `ralph_validate_review_finding_closure` directly and require an explicit PASS/zero exit;
   capture the focused red/green outputs under this run's `evidence/terminal-logs/` directory.

## Evidence and completion

- Verify the artifact maps the fixed-point Finding ID, Root ID, and all seven Acceptance IDs.
- Refresh `risk-assessment.md`, `review-packet.md`, and `final-summary.md` for this exact repair.
- Set the review packet result to exactly `Ready for independent validation`.
- Leave complete backend, coverage, migration, and PostgreSQL revalidation to the orchestrator.
