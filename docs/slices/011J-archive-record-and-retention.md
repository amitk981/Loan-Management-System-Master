# Slice 011J: Archive Record and Retention

## Status
Complete

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Create one searchable, access-controlled archive manifest for an eligible closed loan with a
server-calculated retention date of at least eight years.

## User Value
Compliance and auditors can locate the complete loan file and prove retention obligations.

## Depends On
- 011I

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.ArchiveRecordPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/api-contracts.md` §36.5
- `docs/source/data-model.md` §22.4
- `docs/source/product-requirements.md` §11.28
- `docs/source/screen-spec.md` S61
- `docs/source/component-spec.md` §18.5
- `docs/source/security-privacy.md` §§26, 34
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011J

## Scope
- Add one `ArchiveRecord` per loan and `LoanClosureModule.archive` behind POST
  `/api/v1/loan-closures/{id}/archive/`, plus scoped manifest/detail read.
- Require the retained closure plus NOC and all applicable security-return/unpledge completion before
  terminal `archived` truth. Preserve the earlier financial-close record even when archive is blocked.
- Retain physical and/or digital location, start date derived from closure, archive actor/time, and
  `retention_until_date` calculated by the server no earlier than eight calendar years later.
- Keep archived records searchable/read-only for authorised users; document access still routes through
  existing classification/download audit. `destruction_eligible` is informational only.
- Exact replay returns the retained archive; location correction, destruction, and certificate flows
  require separately governed future contracts rather than silent mutation.

## Permissions and Audit
- `closure.archive.create` for Compliance/CS after prerequisites; `closure.archive.read` for scoped
  authorised users and Auditor. Borrower receives only explicitly allowed closure/NOC facts.
- Archive creation, manifest/download access, and denied attempts are audited without paths or
  sensitive document contents in general logs.

## Acceptance and Negative Tests
- Eligible loan archives once with exact locations and >=8-year calendar retention; boundary dates
  include leap-day cases.
- Reject pre-close, missing NOC/applicable return, foreign closure/path/evidence, owner-supplied short
  retention, wrong role/scope, duplicate/change replay, direct archive mutation, and early destruction.
- PostgreSQL concurrent archive yields one manifest and one terminal status/history chain.
- Reverse consumers: 011G-I histories stay immutable; document access/masking/download audits remain
  green; archived loan rejects all ordinary loan/default/recovery mutations.

## Non-Goals
Physical storage automation, data deletion/destruction approval, retention-policy reduction, report
exports (Epic 012), or archive frontend (011P).

## Evidence
RED/GREEN prerequisite/date/API/permission tests; migration and race proof; archived-read-only matrix;
document-access/audit regressions; full backend gate and manifest example.

## Risk Level
Medium

## Acceptance Criteria
- `CLOSE-AC-006`, `MOD-CLOSURE-009-010`, and `API-CLOSE-005` pass.
- No archive can precede closure evidence, shorten retention, mutate ordinary records, or bypass access audit.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Archive persistence/module/API and read scope completed
- [ ] Prerequisite, date, race, read-only, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
