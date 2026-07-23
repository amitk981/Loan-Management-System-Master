# Execution Plan

Selected slice: 011O-auditor-read-only-views

## Repair boundary

Preserve the current 011O candidate and repair only the trusted-browser validation domain recorded in
`.ralph/runs/2026-07-23_210407_normal_run/failure-summary.md`. The saved validator output proves that
Chromium launched and the empty-state scenario passed, while the populated scenario matched unrelated
read-only navigation buttons and the missing-scope scenario could not reach the auditor view through
its UI navigation path.

Do not change backend/business rules, permissions, schemas, dependencies, source documents,
orchestrator-owned mechanical facts, or unrelated frontend behavior.

## Permission check

- Product/e2e and current-run evidence paths are allowed by `.ralph/permissions.json`.
- Protected and forbidden paths will not be edited.
- `docs/working/FRONTEND_DESIGN_RULES.md` has been read; any repair will preserve the existing visual
  system and alter only browser-test targeting or the minimum role/visibility behavior proven wrong.

## Feedback loop and repair sequence

1. Re-run the exact trusted command for
   `e2e/auditor-read-only-epic-011.e2e.spec.ts` with the repair run's screenshot directory and retain
   the red output.
2. Inspect the existing Playwright spec, auditor route/view, navigation guard, and focused component
   tests only far enough to distinguish test-selector error from product route/permission error.
3. Fix the minimum demonstrated cause. Keep the mutation assertion scoped to the auditor content
   surface and make the unauthorised scenario enter the existing guarded route deterministically,
   without weakening the assertion that operational actions and mutation requests are absent.
4. Re-run the exact validator command until all three scenarios and all exact screenshots pass.
5. Run the focused auditor component/route test, then frontend typecheck, lint, and build because the
   repaired domain is frontend/browser acceptance. Save focused and gate logs under the repair run.
6. Verify the required screenshot files and hashes, inspect the screenshot outputs, review targeted
   diffs, and finish `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.

## Success condition

The exact slice-specific Playwright spec passes with populated, empty, and unauthorised screenshots,
no operational mutation controls or mutation requests appear in the auditor content surface, and the
review packet Result is exactly `Ready for independent validation`.
