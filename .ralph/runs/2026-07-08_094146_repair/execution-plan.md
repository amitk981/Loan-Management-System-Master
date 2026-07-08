# Execution Plan

Selected slice: 004B-member-profile-api-and-ui

Mode: repair

## Diagnosis
- Previous attempt: `.ralph/worktrees/2026-07-08_090617_normal_run`.
- Functional gates passed, but `diff-limits-results.md` failed because changed lines were 2142,
  exceeding the 2000-line Ralph limit.
- Repair strategy: reimplement the same masked member profile capability with tighter tests/docs and
  avoid broad documentation churn.

## Permission Check
- Allowed edit areas confirmed in `.ralph/permissions.json`: `sfpcl_credit/**`,
  `sfpcl-lms/src/**`, `docs/working/**`, `docs/slices/**`, and `.ralph/runs/**`.
- Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`,
  `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, guarded working policy files,
  and `docs/source/**`.

## Plan
1. Backend TDD: add a focused failing integration test for
   `GET /api/v1/members/{member_id}/` covering masked PAN/Aadhaar, profile shell, actions, 404,
   401, and 403.
2. Backend implementation: reuse `sfpcl_credit.members`, add only the profile shell models/migration
   needed for §13.3 detail serialization, add the detail route/view/service, and keep sensitive
   reveal deferred.
3. Frontend TDD: add tests for `memberProfileApi` and `MemberProfileView` states proving API data,
   masked identifiers, error states, and deferred tabs render without mock fallback.
4. Frontend implementation: rewire the existing `MemberProfile` page to the backend using current
   design patterns, remove backend-wired `mockData` dependency, and preserve empty/deferred tab
   states for unimplemented endpoints.
5. Documentation/evidence: update the API contract, assumptions, prototype tracking, digest, state,
   progress, handoff, slice status, risk assessment, changed-files, review packet, final summary,
   API examples, and terminal logs.
6. Gates: run backend check/tests/migration check/coverage with the required Ralph venv Python,
   frontend typecheck/lint/tests/build, `git diff --check`, protected-paths review, and diff-limit
   review.
