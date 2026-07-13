# Member governance container remains flaky on pull-request CI

## Type
bug-frontend

## Severity
High

## What Is Happening
Commit `b8b9ef5` passed push CI #223, but pull-request CI #224 failed because
`MemberGovernanceForm.container.test.tsx` again exceeded Vitest's 5000 ms timeout. CR-002 reduced
the normal local and push-run duration, but the complete create/read/update/read mounted journey is
still sensitive to GitHub runner performance. A green push run and red pull-request run for the same
head commit prove that the test is still nondeterministic rather than permanently repaired.

## Expected Behaviour
The frontend suite must pass reliably under both `push` and `pull_request` GitHub Actions events.
Mounted production-container coverage must retain registration, navigation, exact request bodies,
canonical create readback, ordinary update, and canonical update readback without depending on a
fast runner or leaking asynchronous work into the following test.

## Steps To Reproduce
1. Push commit `b8b9ef5` to `staging` and observe push CI #223 pass.
2. Open PR #5 from `staging` into `main` so the same head commit runs under `pull_request`.
3. Open pull-request CI #224.
4. Observe the frontend job fail at `MemberGovernanceForm.container.test.tsx:26` after 5000 ms.
5. Observe the backend pull-request job pass, proving the blocking failure is isolated to the
   frontend container test.

## Where It Appears
`sfpcl-lms/src/pages/members/MemberGovernanceForm.container.test.tsx`, GitHub Actions CI #224, and
PR #5's `CI / frontend (pull_request)` required check.

## Source Document Reference
`docs/slices/006Y11-member-form-container-and-error-matrix-closure.md` requires mounted production
container coverage. `docs/change-requests/accepted/CR-002-member-governance-container-ci-timeout.md`
records the first repair and its preserved assertions. `.github/workflows/ci.yml` requires the full
frontend suite to pass for both push and pull-request events.

## Acceptance Criteria
- Establish and save a red-capable stress or repetition command that exercises the exact mounted
  journey and can expose its timing sensitivity before the repair.
- Restructure or split the oversized timing-sensitive journey while preserving registration,
  navigation, exact POST/PATCH request bodies, canonical create readback, ordinary update, canonical
  update readback, and cleanup coverage across the resulting focused tests.
- Keep genuinely human-like `userEvent` interaction coverage in an appropriately small focused test;
  bulk fixture preparation must remain deterministic and observable through labeled controls.
- The affected coverage passes at least 20 consecutive focused executions, including execution with
  the immediately following parameterized case so leaked asynchronous work is detected.
- No test is skipped, quarantined, reduced to superficial assertions, or repaired solely by raising
  the global timeout.
- Frontend typecheck, lint, the complete test suite, and build all pass locally; backend gates remain
  green.
- The next `staging` push check and PR #5 `pull_request` frontend and backend checks all complete
  successfully before the PR is merged.
