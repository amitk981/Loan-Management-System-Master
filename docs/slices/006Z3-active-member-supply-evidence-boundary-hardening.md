# Slice 006Z3: Active-Member Supply Evidence Boundary Hardening

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Prevent invalid or legacy flag-only supply facts from satisfying BR-004/BR-007, and move the
active-member rule behind the documented member-owned public module boundary.

## Depends On
- 006Z

## Source / Review References
- `docs/source/functional-spec.md` BR-004, BR-006, BR-007, and M02-FR-004
- `docs/source/screen-spec.md` S16
- `docs/source/data-model.md` §11.6 and §34
- `docs/source/codebase-design.md` §10.2, §26.1-§26.3, and §42.2
- `docs/slices/006Z-produce-supply-history-persistence.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_125256_architecture_review`

## Scope

- Introduce/use `members.modules.active_member_status` as the public calculation/verification seam.
  Credit eligibility consumes its immutable result/projection and must not import member models or
  test private `_active_member_check` helpers.
- Require actual persisted service-usage evidence plus qualifying verified supply rows for the
  normal BR-004/BR-007 path. A legacy `active_member_status=active` flag/timestamp may not substitute
  for a false/missing service fact. Preserve explicitly recorded relaxation as manual evidence until
  governance resolves the exact relaxation approval mechanism.
- Strictly validate capture payloads: object-only/known fields, canonical financial year, eligible
  entity type, direct versus Producer Institution route consistency, referenced entity/member UUIDs,
  non-negative decimal quantity/value, and evidence reference. Only source-eligible entity/route
  rows may contribute to continuity.
- Require the current member/resource version for capture as sharpened by 006Z, and retain row
  version/maker-checker locking for verification. Map malformed ORM inputs to standard errors.
- Share one financial-year continuity implementation between staff eligibility and portal summary;
  totals and status must clearly distinguish verified qualifying rows from pending/non-qualifying rows.

## Test Cases

- Public-module tests cover individual/institution services true/false, four continuous qualifying
  years, gaps, malformed years, ineligible entities/routes, pending rows, and relaxation.
- An active legacy flag plus timestamp with `services_availed_flag=false` cannot pass.
- Capture `400`, permission/object `403`, stale `409`, and competing verify/capture paths preserve
  record/history/audit cardinality.
- Portal and staff projections use the same qualifying rows and expose no cross-member data.

## Evidence Required

Failing-first boundary/business-rule logs, green public-module matrix, exact API examples, metadata-
only audit examples, concurrency log, dependency scan proving credit has no member-model import,
and all configured gates.

## Risk Level
High

## Acceptance Criteria

- BR-004/BR-007 cannot pass without persisted service and qualifying supply evidence.
- Active-member logic is member-owned, publicly testable, strictly validated, and shared by credit
  and portal projections.

