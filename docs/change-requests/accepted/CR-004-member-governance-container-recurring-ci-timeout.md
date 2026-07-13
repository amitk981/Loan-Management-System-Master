# Member governance container still exceeds the GitHub CI test timeout

## Type
bug-frontend

## Severity
High

## What Is Happening
The `staging` push workflow for commit `aacb9b3` failed again because
`MemberGovernanceForm.container.test.tsx` exceeded Vitest's 5000 ms per-test timeout in the test
`routes Directory registration into canonical Profile readback with the exact create ledger`.
The backend job passed. CR-002 reduced bulk form-entry cost and CR-003 split the original combined
create/update journey, but the remaining mounted create journey is still sensitive to GitHub-hosted
runner scheduling and full-suite contention. The exact commit passed Ralph's complete local frontend
gate, so a fast local run is still able to certify a repair that later flakes in GitHub Actions.

## Expected Behaviour
The mounted production-container assertions must pass reliably on both `push` and `pull_request`
GitHub Actions runs, including slower hosted runners. CI reliability must not depend on every
integration-style test completing inside Vitest's unit-test-oriented 5000 ms default, and the repair
must not weaken, skip, or quarantine the production journey coverage.

## Steps To Reproduce
1. Push commit `aacb9b3` to `staging` with `.github/workflows/ci.yml` running the complete frontend
   gate.
2. Open the resulting GitHub Actions workflow run used by PR #5.
3. Observe the frontend job fail after 4m52s while the backend job succeeds.
4. Open the frontend annotations.
5. Observe `MemberGovernanceForm.container.test.tsx:26` report `Test timed out in 5000ms` for the
   exact create-ledger mounted journey.
6. Compare the committed Ralph evidence for the same head: all 208 frontend tests passed locally,
   the container file took 2637 ms, and the affected test took 1423 ms.

## Where It Appears
`sfpcl-lms/src/pages/members/MemberGovernanceForm.container.test.tsx`, the `npm test` step in
`.github/workflows/ci.yml`, staging push CI for commit `aacb9b3`, and PR #5's required frontend
check.

## Source Document Reference
`docs/slices/006Y11-member-form-container-and-error-matrix-closure.md` requires mounted production
container coverage. `docs/change-requests/accepted/CR-002-member-governance-container-ci-timeout.md`
and `docs/change-requests/accepted/CR-003-member-governance-container-pr-ci-timeout.md` record the
two incomplete timing repairs. `.github/workflows/ci.yml` requires the full frontend suite on both
push and pull-request events.

## Acceptance Criteria
- Preserve the mounted create journey's authenticated App navigation, member registration, exact
  POST ledger, canonical profile refetch, mutation-response non-disclosure, and cleanup assertions.
- Add a targeted timing policy for integration-style container tests, or equivalently isolate their
  CI execution, so they do not inherit an inappropriate 5000 ms unit-test ceiling; do not raise the
  timeout globally for all frontend tests.
- Make CI worker/concurrency behavior explicit if full-suite contention is part of the failure, and
  save a CI-shaped command that exercises the affected test under the resulting configuration.
- Establish RED evidence against the pre-repair configuration using the exact mounted journey and a
  constrained or contention-shaped execution, then save GREEN evidence for the repaired command.
- Run the affected mounted journey repeatedly and together with the complete frontend suite; no test
  may be skipped, quarantined, or reduced to superficial assertions.
- Frontend typecheck, lint, complete tests, and build pass; backend check, migrations, tests, and
  coverage remain green.
- The resulting `staging` push completes successfully and PR #5 receives a green frontend required
  check at the repaired head before merge.
