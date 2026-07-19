# Slice 011L: Section 186 and NBFC Test Trackers

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Persist exact quarterly Section 186 and NBFC principal-business calculations with evidence, review,
boundary warnings, and one result per period.

## User Value
CFO and Board receive reproducible statutory-limit and registration-risk evidence instead of spreadsheets.

## Depends On
- 011K

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_compliance_postgresql_acceptance.StatutoryTrackerPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/api-contracts.md` §§37.5-37.6
- `docs/source/data-model.md` §§23.4-23.5
- `docs/source/product-requirements.md` §11.29
- `docs/source/codebase-design.md` §§19.2-19.3
- `docs/source/screen-spec.md` S63-S64
- `docs/source/test-plan.md` §§21.2-21.3
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011L

## Scope
- Add `Section186TrackerModule` and `NbfcPrincipalBusinessTestModule` plus their period-unique models,
  migrations, create/read APIs, K evidence/review linkage, and audit.
- Section 186 uses Decimal arithmetic: 60% of `(paid-up capital + free reserves + securities premium)`,
  100% of `(free reserves + securities premium)`, higher applicable limit, exposure/headroom, within-
  limit flag, and special-resolution-required when exposure exceeds the limit.
- NBFC computes financial-assets/total-assets and financial-income/gross-income ratios. Trigger only
  when both are strictly `>50%`; one ratio above is warning/no trigger. Preserve a configurable
  early-warning threshold without changing the statutory trigger.
- Server calculates all derived values from validated inputs and freezes period/input/result/reviewer/
  evidence snapshots. Existing-period exact replay returns retained truth; changed replay conflicts.
- Integrate quarterly due/review tasks through 011K without duplicating its scheduler or evidence policy.

## Permissions and Audit
- Critical `compliance.section186.create` and `compliance.nbfc_test.create` for CFO/delegate source
  owners; exact read permissions for authorised management/Auditor. Review is distinct and audited.
- Inputs, calculations, review, Board presentation/evidence, warnings, and denied access are traceable.

## Acceptance and Negative Tests
- Table-driven formula tests cover higher-of-two outcomes, equal/over exposure, Decimal rounding, and
  exact 50%, one-ratio-over, both-over NBFC boundaries.
- Reject negative values, zero denominators, invalid FY/quarter, client-derived outputs, foreign/
  missing evidence, self-review when checker required, changed replay, and duplicate period.
- PostgreSQL concurrent create yields one tracker per type/period; no float math appears in policy code.
- Reverse consumers: 011K task/evidence ownership stays singular; approval/Board document access,
  dashboard summary, and audit suites remain green; calculators do not mutate source finance records.

## Non-Goals
Legal interpretation of Section 186 exemptions, RBI registration action, source-finance integration,
generic compliance task changes, frontend wiring (011P), or report exports.

## Evidence
RED/GREEN formula/boundary/API/permission tests; migration and PostgreSQL uniqueness proof; Decimal/
static policy checks; evidence/review trace; full backend gate and response examples.

## Risk Level
Medium

## Acceptance Criteria
- `COMP-AC-002-003`, `MOD-COMP-001-005`, `API-COMP-001-002`, and test-plan §§21.2-21.3 pass.
- Stored outputs are deterministic, period-unique, reviewable, and never caller calculated.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Both calculators/models/APIs and 011K integration completed
- [ ] Formula boundaries, race, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
