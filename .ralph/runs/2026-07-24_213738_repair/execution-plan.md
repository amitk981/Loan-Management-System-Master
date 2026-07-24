# Execution Plan

Selected slice: 011PA-default-case-notes-frontend-wiring

Mode: same-worktree repair

## Demonstrated Failure Domain

The preserved candidate failed only trusted browser acceptance. The declared Playwright spec did not
start because the centrally selected Chrome process closed during launch; the prior infrastructure
probe passed. The failed first run consequently produced neither the required screenshot nor its
manifest, and the validator correctly deferred the second run.

## Permission Check

- Allowed repair evidence: `.ralph/runs/2026-07-24_213738_repair/**`.
- Allowed product paths if the reproducer proves a candidate defect:
  `sfpcl-lms/e2e/**` and `sfpcl-lms/src/**`.
- Protected and forbidden paths remain untouched, including `scripts/**`, Ralph configuration,
  workflow policy, and `docs/source/**`.
- No package installation, Git metadata mutation, or state/status bookkeeping is required.

## Feedback Loop

Run the slice-declared spec with the shared localhost Playwright profile and an isolated evidence
directory. The command is red-capable because it launches the same browser, drives the S53-S55
screen, checks the S56-S57 blocker, and writes `default-case-workbench.png`.

## Repair Steps

1. Inspect the trusted-browser helper and candidate spec/config only far enough to reconstruct the
   exact validator command and distinguish infrastructure launch failure from a spec defect.
2. Reproduce the declared browser contract. If launch succeeds and exposes a product/spec failure,
   fix only that browser-acceptance failure and add or retain the narrow regression assertion.
3. Run the exact declared browser contract twice with isolated screenshot directories and retain
   non-empty logs, screenshots, and SHA-256 manifests in this repair run.
4. Run only impacted frontend tests, typecheck, lint, and build if candidate code changes; otherwise
   retain the browser rerun evidence and leave the candidate unchanged.
5. Remove any temporary debugging artifacts, verify protected paths remain unchanged, and complete
   `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.

## Stop Conditions

Stop only for a protected/forbidden edit, the same trusted-browser failure after the bounded repair,
or another Ralph hard stop. Independent orchestration remains responsible for full validation and
mechanical bookkeeping.
