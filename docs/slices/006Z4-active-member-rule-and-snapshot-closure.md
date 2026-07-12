# Slice 006Z4: Active-Member Rule and Snapshot Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Complete the documented active-member public module so continuity, service/relaxation routes, dated
evidence, verification, credit snapshots, and portal explanations share one correct result.

## Depends On
- 006Z3

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Source / Review References
- `docs/source/functional-spec.md` BR-003 through BR-007 and M02-FR-004 through M02-FR-006
- `docs/source/screen-spec.md` S16
- `docs/source/data-model.md` §10.2-§10.3, §11.5-§11.6, and §34
- `docs/source/codebase-design.md` §10.2, §26.1-§26.3, and §42.2
- `docs/slices/006Z3-active-member-supply-evidence-boundary-hardening.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_141135_architecture_review`

## Scope

- Correct financial-year continuity to measure an uninterrupted run; separated clusters may not be
  added across gaps. Add the known regression where six qualifying years in three clusters currently
  report five although the longest run is three. The assertion must retain the six classified rows,
  report `continuous_years = 3`, and keep every non-qualifying/gap explanation visible.
- Make `as_of_date` authoritative: exclude future/not-yet-complete supply facts and return a dated,
  immutable evidence projection. Credit must persist the complete result/evidence snapshot used for
  the application rather than copying only three status strings.
- Implement the source-backed individual and producer-institution four-year routes, BR-006's
  continuous three-year service/employment route, and recorded one-year relaxation/manual-evidence
  routes without inventing an approver. Cover service false/missing and all member types.
- Complete `members.modules.active_member_status` as the public calculate/verify seam. Capture and
  verification authority, maker-checker, optimistic locking, reason/permission, dated result, and
  audit/history facts must not remain split across generic services.
- Portal/staff consumers use the same row projections and expose each row's `qualifying` flag and
  stable `non_qualifying_reason`; pending, malformed, future, wrong-entity/route, and evidence-free
  rows remain visible but never contribute to continuity or totals.
- Preserve PortalAccount-only scope and keep protected/member IDs and staff actions out of portal
  responses. Update API contracts for any added dated/snapshot/classification fields.

## Test Cases

- Public-module table covers gap clusters, exact four-year boundary, `as_of_date` future exclusion,
  individual/institution service true/false, BR-006 three-year service, direct/Producer Institution
  routes, pending/malformed/evidence-free rows, inactive member, and recorded relaxation.
- Credit readback retains the exact dated row/result snapshot even after member supply facts change.
- Verify projection/write matrix covers permission, object scope, maker-checker, stale version/result,
  repeated decision, reason, and zero loser evidence under PostgreSQL concurrency.
- Portal response classifies every row and totals only qualifying rows with no cross-member data.

## Evidence Required

Failing-first continuity and boundary logs, green public-module matrix, immutable credit snapshot,
portal API examples, two PostgreSQL verification-race logs, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- BR-003 through BR-007 cannot pass from gaps, future rows, missing service facts, or an unsupported
  member route, and every accepted result is dated and reviewable.
- Credit and portal consume one member-owned verified projection with no duplicated rule logic.

## Run-Ahead Sharpening Review (006Y11, 2026-07-12)

- Mount consumers through the public active-member module boundary, not mocked calculation wrappers.
  Success must read one canonical dated projection; permission, maker-checker, stale, and repeated
  decision failures make one write with no retry/refetch/local merge and display exact server facts.
- The PostgreSQL acceptance must assert the winning verification's complete dated row/result snapshot
  and zero audit/history/result evidence from each loser, not only the final status.
