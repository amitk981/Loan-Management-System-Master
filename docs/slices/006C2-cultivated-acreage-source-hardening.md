# Slice 006C2: Cultivated Acreage Source Hardening

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Close the financial-correctness finding from architecture review
`2026-07-10_092630_architecture_review`: prevent BR-020 land limits from silently treating all
selected owned acreage as acreage under cultivation when the crop/profile evidence differs.

## User Value
Loan limits cannot be overstated by calculating against land that is owned but not evidenced as
being cultivated for the application.

## Depends On
- 005I4
- 006D

## Source / Review References
- `docs/source/functional-spec.md` BR-020/BR-022 and M04-FR-006
- `docs/source/api-contracts.md` §23.1-§23.3
- `docs/source/data-model.md` §10.2, §11.7-§11.8, §14.2, and §35.1
- `docs/source/test-plan.md` MOD-LIMIT-002/MOD-LIMIT-008/MOD-LIMIT-009/MOD-LIMIT-010
- `docs/working/ASSUMPTIONS.md` A-049
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_092630_architecture_review`

## Source Ambiguity / Safe Boundary
- Source calls BR-020's input “land area under cultivation”, while the schema separately exposes
  selected `LandHolding.area_acres`, `CropPlan.planned_area_acres`, and nullable
  `IndividualMemberProfile.land_area_under_cultivation_acres`; it does not define how disagreement
  among them is resolved.
- Do not invent a min/max/priority formula. Until source confirmation, calculation may proceed only
  when the applicable acreage evidence agrees. A disagreement returns a structured validation
  blocker and preserves any existing snapshot/evidence unchanged.

## Backend / API Scope
- Resolve three explicit evidence values: total selected verified land-holding acreage, the selected
  application-linked verified crop plan's planned acreage, and the individual profile's cultivated
  acreage when that profile/value exists.
- Require selected land holdings and crop plan to be verified and owned by the application member;
  the crop plan must be linked to this application rather than null or another application.
- If applicable values disagree after decimal normalization, return `400 VALIDATION_ERROR` with a
  stable `cultivated_acreage` field/code such as `CULTIVATED_ACREAGE_UNRESOLVED`. Persist no new
  assessment/audit/workflow evidence and leave an existing 006D snapshot unchanged.
- Normalize all three acreage facts with the existing Decimal path before equality comparison;
  string formatting differences such as `5`, `5.0`, and `5.00` are equal and must not trigger the
  unresolved blocker.
- When all applicable values agree, use that value as snapshotted `land_area_acres`; retain the
  source-backed scale-of-finance multiplication and lower-of-two calculation unchanged.
- Keep policy percentages/caps, overrides, appraisal, and frontend wiring out of scope.

## Snapshot / Audit Requirements
- Audit old/new metadata records only the accepted acreage snapshot and source record UUIDs, not
  land document contents or profile free text.
- GET remains a stored read: later land/crop/profile mutation cannot change it without a successful
  rerun. Failed disagreement/verification reruns preserve the prior response and evidence counts.

## Test Cases
- Red/green mismatch: 20 verified owned acres and 5 planned/cultivated acres are blocked instead of
  producing a 20-acre land limit.
- Equal verified selected-land, crop-plan, and profile evidence calculates the expected land limit.
- Missing profile acreage does not invent a value; selected-land and crop-plan evidence must agree.
- Pending/rejected land or crop facts, null/wrong application crop link, cross-member IDs, and
  mismatch paths produce no success evidence.
- The no-success-evidence assertion covers the assessment row/UUID and serialized GET response,
  `loan_limit.calculated` audit count, and `loan_limit_assessment` workflow-event count.
- Successful rerun replaces the current one-to-one snapshot; every failed rerun preserves it.

## Evidence Required
Backend red/green logs, API examples for matched/mismatched acreage, immutable-rerun evidence, and
all standard quality gates.

## Risk Level
High

## Acceptance Criteria
- BR-020 never calculates from unverified or unresolved cultivated-acreage evidence.
- No new business selector formula is invented; disagreement is an explicit blocker.
- Snapshot and no-side-effect guarantees remain intact.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed, if needed
- [ ] Permissions and audit tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
