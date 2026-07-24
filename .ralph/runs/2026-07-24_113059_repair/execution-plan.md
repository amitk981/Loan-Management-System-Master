# Execution Plan

Selected slice: `012E-operational-dashboard-hardening`

Mode: same-worktree repair of run `2026-07-24_103525_normal_run`

## Demonstrated failure and boundary

- Preserve the existing uncommitted 012E candidate.
- Repair only the trusted browser acceptance domain named by
  `.ralph/runs/2026-07-24_103525_normal_run/failure-summary.md`.
- The browser contract and infrastructure probe passed. The first exact trusted run launched
  Chrome; populated, empty, and forbidden passed, while the error state failed on an ambiguous
  shared helper locator before its screenshot was captured.
- Do not revisit passing backend, frontend unit, typecheck, lint, build, API, or architecture work.

## Permission and safety check

- `sfpcl-lms/e2e/**` and `.ralph/runs/2026-07-24_113059_repair/**` are writable under
  `.ralph/permissions.json`.
- Protected scripts/configuration, `docs/source/**`, workflow state/progress, selected-slice status,
  and mechanical handoff files will not be edited.
- No dependency, migration, API, business-rule, or visual-design change is planned.

## Diagnosis and repair loop

1. Reproduce with the exact validator Playwright invocation and evidence environment.
2. Compare the passing browser probe with the failing dashboard config/spec and rank falsifiable
   causes before changing anything.
3. Minimise the failing launch path, changing only the E2E test/config domain if the reproduced
   failure demonstrates a candidate defect; do not modify protected validator/runtime scripts.
4. Rerun the exact named validator command until both independent browser runs pass and each produces
   verified populated, empty, error, and forbidden PNG manifests.
5. Save focused terminal evidence in the current repair run, inspect the screenshot files, and check
   the bounded diff for protected or unrelated changes.

## Completion evidence

- Record the diagnosis, exact passing command, and screenshot manifests.
- Complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Set the review packet Result exactly to `Ready for independent validation`.
- Leave full independent revalidation and all commit/state/status bookkeeping to the orchestrator.

## Completion status

- The exact failing validator log was retained in the repair run and reduced to one strict-locator
  collision in the error-state scenario.
- The shared E2E shell-readiness locator was minimally repaired with `exact: true`.
- Playwright successfully loads and lists the exact four declared tests.
- The coding-agent browser rerun reached the documented macOS sandbox launch boundary; no
  screenshot was fabricated. The repair run's trusted preflight probe is green, so the orchestrator
  must now perform the two authoritative browser runs and screenshot-manifest checks.
