# Execution Plan

Selected slice: 012G-critical-e2e-uat-smoke-scenarios

## Demonstrated Failure Domain

- Preserve the existing 012G candidate and repair only the trusted-browser acceptance failure.
- The authoritative first browser run launched successfully and reached the application. It failed
  at `critical-uat-smoke.e2e.spec.ts:227` because the subsidiary repayment request returned HTTP
  409 while the scenario expected HTTP 200.
- Missing screenshot manifests are downstream consequences of that post-launch assertion failure.

## Diagnosis Loop

1. Read the binding frontend design rules before changing the E2E spec.
2. Use the exact trusted browser command from the authoritative log as the original repro:
   `RALPH_EVIDENCE_DIR=... E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/critical-uat-smoke.e2e.spec.ts`.
3. Inspect the failed response payload and the public repayment contract plus deterministic seed
   state. Rank falsifiable hypotheses before changing the candidate.
4. Make the smallest E2E/fixture correction that preserves public API behavior, role permissions,
   deterministic isolation, and the declared UAT mapping. Do not add endpoints or bypass business
   rules.
5. Rerun the exact slice-specific trusted browser command until it passes and produces both declared
   screenshots, then run it again against a fresh deterministic seed to prove replay safety.

## Focused Validation

- Retain the current deterministic seed and production-isolation tests.
- If seed support changes, run its focused frontend and backend tests using
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Run frontend typecheck, lint, and build after the browser repair.
- Save current-run browser output, screenshot hashes, focused test output, and diagnosis evidence
  under `.ralph/runs/2026-07-25_082003_repair/evidence/`.
- Do not run the complete backend suite or full coverage; independent validation owns that lane.

## Permissions Check

- Candidate edits may be made only under `sfpcl-lms/**`, `sfpcl_credit/**` if the demonstrated
  fixture contract requires it, and `.ralph/runs/2026-07-25_082003_repair/**`.
- These paths are allowed by `.ralph/permissions.json`.
- Protected and forbidden paths, orchestrator-owned state/progress/status/changed-files facts, and
  `docs/source/**` will not be modified.

## Completion

- Update `risk-assessment.md`, `review-packet.md`, and `final-summary.md` with current-run evidence.
- Set the review packet Result exactly to `Ready for independent validation` only after the exact
  trusted-browser repro and focused gates are green.
