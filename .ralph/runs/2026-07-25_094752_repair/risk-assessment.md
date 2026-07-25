# Risk Assessment

## Classification

Medium, unchanged from slice 012G.

## Repair scope

- The retained repair changes only the critical-UAT E2E expectation for a historical DPD cutoff.
- No production financial calculation, API, permission, model, migration, or product UI behavior
  changed.
- The assertion now distinguishes current principal after a `2026-07-25` repayment from overdue
  principal as of `2026-07-01`.

## Regression exposure

- The canonical public DPD timing regression and guarded critical-UAT seed/public-API tests pass
  (3 tests).
- Frontend seed selection passes (5 tests).
- Typecheck, lint, production build, Django system check, and migration drift checks pass.
- The candidate remains below configured changed-file and changed-line limits, and
  `git diff --check` passes.

## Browser infrastructure

Two unchanged exact browser attempts and the dedicated launch probe ended during Chrome launch
before a page existed. This is not evidence of an application regression, and no screenshot was
fabricated. The candidate previously exposed the application assertion only after a successful
launch; independent trusted validation must rerun the exact spec and produce both declared
screenshot manifests.

## Residual risk

The current agent environment could not provide fresh post-launch browser evidence. The
orchestrator must therefore decide browser acceptance from its trusted environment and retain the
candidate only if both fresh deterministic runs and screenshot checks pass.
