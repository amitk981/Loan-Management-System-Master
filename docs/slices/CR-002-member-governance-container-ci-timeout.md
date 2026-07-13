# Slice CR-002: Member governance container test repeatedly times out in GitHub CI

## Status
Complete

## Origin
Change request (maintenance stage), accepted 2026-07-13 from docs/change-requests/accepted/CR-002-member-governance-container-ci-timeout.md.

## Risk Level
High

## Change Request (verbatim)

# Member governance container test repeatedly times out in GitHub CI

## Type
bug-frontend

## Severity
High

## What Is Happening
The `staging` GitHub Actions workflow has failed repeatedly from CI run #207 through #222 even
though Ralph's local frontend gate passes. The real failure is
`src/pages/members/MemberGovernanceForm.container.test.tsx` test `routes Directory registration
into canonical Profile readback before an ordinary update readback`, which exceeds Vitest's default
5000 ms timeout on the standard GitHub Ubuntu runner. After that timeout, unfinished asynchronous UI
work can leak into the following parameterized test, which then reports that it cannot find the
`Membership Start Date` label while the DOM is still showing a member profile. Ralph's archived
local results consistently place the mounted journey at roughly 3.0-3.2 seconds, leaving too little
margin for the slower CI runner.

The backend `pip-audit` exit-code annotation and GitHub Actions Node-runtime deprecation notices are
separate report-only warnings and are not the cause of the red workflow.

## Expected Behaviour
The complete frontend CI job should pass reliably on GitHub's standard Ubuntu runner. The mounted
member registration/create/readback/update/readback test must preserve its behavioral assertions,
finish within a safe deterministic budget, and leave no asynchronous work or DOM state that can
affect the following test.

## Steps To Reproduce
1. Push the current `staging` branch to GitHub so `.github/workflows/ci.yml` runs `npm test` under the
   frontend job.
2. Open a recent failed run such as CI #222 for commit `fb6de5b`.
3. Observe the 5000 ms timeout at `MemberGovernanceForm.container.test.tsx:26`.
4. In runs where execution continues far enough, observe the next test fail to find
   `Membership Start Date` while stale profile UI remains in the DOM.
5. Compare with `.ralph/runs/2026-07-13_061140_normal_run/test-results.md`, where the same journey
   passes locally in 3103 ms.

## Where It Appears
`sfpcl-lms/src/pages/members/MemberGovernanceForm.container.test.tsx`, the frontend `npm test` step
in `.github/workflows/ci.yml`, and GitHub Actions CI runs on `staging`.

## Source Document Reference
`docs/slices/006Y11-member-form-container-and-error-matrix-closure.md` requires mounted production
container coverage for canonical create/update readback and exact error behavior. `.github/workflows/ci.yml`
requires the full frontend test suite to pass before build. The repair must retain those gates and
assertions rather than skip the test or globally weaken CI.

## Acceptance Criteria
- The focused mounted registration/create/readback/update/readback test passes repeatedly without
  approaching or depending on Vitest's 5000 ms default timeout.
- Bulk fixture entry is made deterministic and efficient while real navigation, submit, canonical
  readback, and update interactions remain asserted.
- A timeout or failure in one test cannot leave pending asynchronous work or DOM state that changes
  the result of the following member-governance container test.
- No test is skipped, quarantined, or converted into a superficial assertion; no global test timeout
  is raised merely to hide avoidable per-character fixture cost.
- Frontend typecheck, lint, the complete frontend test suite, and build all pass locally.
- The next pushed `staging` commit produces a green GitHub Actions frontend job; the backend job
  remains green. Report-only audit findings may remain visible without failing the workflow.

## Mandatory First Step: Impact Analysis
Before changing ANY code, write impact-analysis.md in the run folder covering:
- Affected backend models/endpoints/services, with grep evidence.
- Affected frontend screens/components/routes.
- Blast radius: every OTHER module that consumes the affected pieces.
- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module.
- FRONTEND_DESIGN_RULES compliance note for any UI change.
Validation fails this run if impact-analysis.md is missing.

## Acceptance Criteria
- The change request's own acceptance criteria are met.
- Regression tests added for every module named in the impact analysis.
- All quality gates pass.
