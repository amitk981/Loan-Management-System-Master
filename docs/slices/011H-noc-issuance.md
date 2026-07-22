# Slice 011H: NOC Issuance

## Status
Complete

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Generate, retain, and deliver one No Objection Certificate only for an eligible full-repayment closure.

## User Value
Borrowers receive authoritative no-dues evidence promptly after financial closure.

## Depends On
- 011G

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.NocIssuancePostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/api-contracts.md` §36.3
- `docs/source/data-model.md` §22.2
- `docs/source/functional-spec.md` M13-FR-004-005
- `docs/source/screen-spec.md` S59
- `docs/source/component-spec.md` §18.2
- `docs/source/auth-permissions.md` §§12.11, 20.2, 25.9, 26.7
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011H

## Scope
- Add one `NocRecord` per closure and `LoanClosureModule.generate_noc` behind POST
  `/api/v1/loan-closures/{id}/noc/`.
- Require a retained eligible full-repayment closure and canonical borrower/loan/application/amount/
  repayment facts. Use the existing document template/generation/storage owner; the request may
  reference a valid generated document but may not supply certificate facts.
- Retain issued-by/time, governed signatory, document, delivery mode/status, and closure linkage.
  Hand delivery to the existing communications dispatcher and preserve honest queued/sent/failed truth.
- Exact replay returns the same NOC; delivery retry must not generate another certificate.

## Permissions and Audit
- Critical `closure.noc.issue` for Compliance/Company Secretary; Credit/borrower-own/Auditor receive
  scoped read/download only as allowed. Signed download remains audited.
- Generation, issue, delivery handoff/result, download, and denied attempts are correlated without
  exposing document contents in logs.

## Acceptance and Negative Tests
- Eligible full-repayment closure produces one document/NOC and a truthful delivery chain.
- Reject pre-close/unready, foreign closure/document/template, recovery/write-off without explicit
  eligibility, wrong signatory/role/scope, missing document, changed replay, and duplicate issue.
- PostgreSQL concurrent issue yields one NOC/document/outbox chain; provider/publish failure preserves
  retryable truth rather than claiming delivery.
- Reverse consumers: 011G closure snapshot remains immutable; document generation/download and
  communications idempotency suites remain green; borrower can access only own issued NOC.

## Non-Goals
New template/communication/provider infrastructure, security return, archive, NOC wording changes,
or member portal UI (011NA).

## Evidence
RED/GREEN eligibility/API/document/communication/permission tests; migration and race proof; delivery
failure/replay evidence; audit/download trace; full backend gate and NOC metadata example.

## Risk Level
Medium

## Acceptance Criteria
- `CLOSE-AC-003`, `MOD-CLOSURE-004-005`, and `API-CLOSE-003` pass.
- NOC identity, eligibility, provenance, delivery truth, and object scope are backend enforced.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] NOC persistence/module/API and owner integrations completed
- [ ] Eligibility, idempotency/race, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
