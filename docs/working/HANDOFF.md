# Ralph Handoff

## Last Run
2026-07-13_041602_repair

## Current Status

006Z10's quarantined implementation has a fourth narrow repair. Both independent trusted runs
passed the first three scenarios and completed submit/refetch/reload, then exposed that the routed
limit view never rendered the server's retained calculation date and rule version. The existing
three-card view now shows those two server-authored provenance fields with its existing text pattern.

## Validation

Repair evidence is under `.ralph/runs/2026-07-13_041602_repair/`. Frontend build/typecheck/lint and
207 tests pass. Backend check/migration sync and 500 tests pass with 93% coverage. Playwright
collects the four declared trusted scenarios; local Chromium is sandbox-denied before page creation,
so independent validation owns both browser runs and the four screenshots. No backend, schema,
dependency, source, protected, or approved-design file changed by this repair.

## Next Run

Run `007A-approval-matrix-configuration`. It is sharpened with effective-date, permission, immutable
projection, concurrency, complete zero-write evidence, and historical decision-date requirements.
