# Slice CR-006: Register decision timestamps depend on the runner timezone

## Status
Not Started

## Origin
Change request (maintenance stage), accepted 2026-07-15 from docs/change-requests/accepted/CR-006-register-date-time-timezone-determinism.md.

## Risk Level
Medium

## Change Request (verbatim)

# Register decision timestamps depend on the runner timezone

## Type
bug-frontend

## Severity
Medium

## What Is Happening
The Credit Sanction Register renders approval decision timestamps in the host machine's local timezone. The same stored instant displays as `13 Jul 2026, 14:30` on an Asia/Kolkata workstation but as `13 Jul 2026, 09:00` on GitHub's UTC runner. This makes `RegistersHub.test.tsx` fail in GitHub Actions even though it passes locally, and it makes the business-facing register display depend on where the browser or test process runs.

## Expected Behaviour
Register and approval decision timestamps must display in the configured SFPCL business timezone, Asia/Kolkata, while stored instants remain UTC. The rendered value and its regression tests must be identical under UTC and Asia/Kolkata host environments.

## Steps To Reproduce
1. Check out staging commit `a9a518a8`.
2. From `sfpcl-lms`, run `npm test` with the process timezone set to UTC, as on GitHub Actions.
3. Observe `src/pages/registers/RegistersHub.test.tsx` line 53 expect `13 Jul 2026, 14:30` but receive `13 Jul 2026, 09:00`.
4. Run the same test from an Asia/Kolkata workstation and observe it pass.

## Where It Appears
Credit Sanction Register approval decision details in `sfpcl-lms/src/pages/registers/ApprovalRegisterPanels.tsx`, covered by `sfpcl-lms/src/pages/registers/RegistersHub.test.tsx`; GitHub Actions CI run 29410873806 frontend job.

## Source Document Reference
`docs/source/deployment-ops.md` timezone guidance: store UTC and display Asia/Kolkata where applicable; `docs/source/test-plan.md` COMP DateInput coverage requires timezone display verification.

## Acceptance Criteria
The shared register date-time formatter explicitly renders approval decision timestamps in Asia/Kolkata; the Credit Sanction Register regression test passes with `TZ=UTC` and `TZ=Asia/Kolkata`; the full frontend test, typecheck, lint, and build gates pass; GitHub Actions frontend CI is green for the resulting staging commit.

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
