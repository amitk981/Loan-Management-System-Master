# Slice 011I: Security Return and CDSL Unpledge Tracking

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Track applicable SH-4, blank-cheque, PoA, and demat-pledge release through acknowledged completion
after closure, without bypassing existing custody and CDSL owners.

## User Value
Borrowers recover held security with a complete, auditable chain instead of an unchecked boolean.

## Depends On
- 011H

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.SecurityReturnPostgreSQLAcceptanceTests`
- Expected tests: 2

## Source References
- `docs/source/api-contracts.md` §36.4
- `docs/source/data-model.md` §22.3
- `docs/source/user-flows.md` §33
- `docs/source/screen-spec.md` S60
- `docs/source/component-spec.md` §§18.3-18.4
- `docs/source/auth-permissions.md` §§12.11, 20.2, 25.9, 26.7
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011I

## Scope
- Add one security-return aggregate per closure plus item-level evidence sufficient to distinguish not
  applicable, pending, returned/released, rejected, and completed outcomes.
- Implement POST `/api/v1/loan-closures/{id}/security-return/`; derive applicable instruments and
  custody/pledge identity from the existing security package. Do not trust submitted applicability.
- For SH-4/cheque/PoA retain item, custody, returned/released by/to/time, pending reason, and governed
  acknowledgement. For CDSL retain PSN, URF, partial/full, pledgor and pledgee DP dates/outcome,
  auto-unpledge flag, completion time, and evidence through the existing CDSL module.
- Do not mark aggregate complete while an applicable item is pending/rejected or acknowledgement is
  absent. Exact replay is zero-write; changed replay is rejected.

## Permissions and Audit
- Critical `closure.security_return.record` for Company Secretary/authorised Compliance after closure;
  Credit, borrower-own status, and Auditor read only.
- Every item transition, CDSL owner handoff/result, acknowledgement/download, and denied action is
  auditable; BO/account details remain masked under the existing sensitive-data boundary.

## Acceptance and Negative Tests
- Physical-only, demat-only, mixed, and no-security fixtures derive the correct required items and
  complete only after all applicable evidence exists.
- Reject pre-close, foreign/mismatched package/item/PSN/evidence, caller-declared not-applicable,
  missing recipient/acknowledgement, completion after rejected DP action, wrong role/scope, duplicate/
  changed replay, and stale concurrent updates.
- PostgreSQL item/aggregate races preserve one return and monotonic state; external-owner failure
  cannot falsely complete local truth.
- Reverse consumers: SH-4/CDSL/cheque/PoA custody, reveal masking, signed download, 011G closure, and
  011H NOC suites remain green; closed loan allows only this controlled mutation.

## Non-Goals
Performing real DP requests, deciding physical-return/PoA policy not present in source, changing
security custody, archive (011J), or portal/staff aggregate UI.

## Evidence
RED/GREEN item-state/API/permission tests; migration and PostgreSQL races; CDSL owner rollback/masking
proof; audited acknowledgement evidence; full backend gate and API examples.

## Risk Level
High

## Acceptance Criteria
- `CLOSE-AC-004-005`, `MOD-CLOSURE-006-008`, and `API-CLOSE-004` pass.
- Completion cannot be forged, skip an applicable instrument, or expose restricted security data.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Return aggregate/API and security-owner integrations completed
- [ ] Applicability, masking, race/rollback, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
