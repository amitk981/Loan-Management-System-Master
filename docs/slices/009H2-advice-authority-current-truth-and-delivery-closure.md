# Slice 009H2: Advice Authority, Current Truth, and Delivery Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Send the stable 009G2 borrower-advice intent exactly once under the source role matrix, while making
canonical contact, rendered content, template, adapter acceptance, and audit evidence current.

## Depends On
- 009G2
- 009H

## Runtime Capabilities

postgresql-five-race-acceptance

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/api-contracts.md` §§31.4-31.5 and 39
- `docs/source/integrations.md` §§9.1-9.2, 10, 19.3, and 21
- `docs/source/auth-permissions.md` §§15.3, 15.6-15.7, 19.2-19.3, 26.5, and 30
- `docs/source/codebase-design.md` §§16.4, 20.6, 22, 26, 36, and 42
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_164724_architecture_review`

## Concrete Requirements
1. Correct the production catalogue and action scope to auth §26.5: active Senior Manager Finance
   with the exact disbursement/SAP relation or Credit Manager with canonical active-loan/application
   scope may send advice when granted; a CFC-only authority cannot. Effective multi-role users act
   only through a source-authorised role, and permission/role/raw id alone never grants scope.
2. Consume the exact stable pending communication/outbox identity created by 009G2. Do not create a
   second communication. Reconcile current transfer/register evidence, current canonical borrower
   email, approved/effective template identity/version/declared variables, rendered subject/body,
   provider identity/status/time, sender role/team, request/network context, audit, and workflow.
3. Compare the supplied normalized email with the current canonical address before both first send
   and replay. A changed member email, content/template snapshot, recipient, provider evidence,
   action/audit/workflow, or upstream transfer/register fact makes replay conflict; never return a
   stale historical delivery as current.
4. Make adapter idempotency survive a fresh adapter instance and a transaction failure after provider
   acceptance. Use a stable communication/delivery identity and provider/outbox key whose canonical
   payload does not change across retries. A forced post-acceptance rollback/retry must not create a
   second logical provider message; rejection keeps the intent pending and creates no sent truth.
5. Audit only a masked/digested recipient plus the protected communication/member identity; do not
   copy the full email into general audit/workflow evidence. Preserve the full address only in the
   protected communication record needed for delivery.

## Test Cases
- Public role matrix: Senior Finance and correctly scoped Credit Manager success; CFC-only, wrong
  active-loan/application scope, inactive, missing grant, role-only, and permission-only denial.
- First send/replay assert exact template merge, stable pending identity becoming sent, one provider
  message, safe audit/workflow, no money/register/checklist mutation, and no full email/UTR leakage.
- Change canonical email, rendered subject/body, template variables/version/effective state,
  recipient, provider id/status/time, audit/workflow, or transfer/register evidence one at a time;
  replay conflicts without resend or new ledgers.
- Force adapter acceptance followed by database rollback, construct a fresh Manual/Fake adapter,
  retry, and prove the same logical provider identity and one sent communication. Twice run the
  PostgreSQL five-caller race with the same assertions.

## Evidence Required
The four retained architecture probes plus Credit Manager coverage; delivery rollback/retry trace;
safe audit manifest; role matrix; twice-run PostgreSQL race; focused tests/check/migrations/full gates.

## Risk Level
High

## Acceptance Criteria
- Advice authority exactly matches the source role matrix and current object scope.
- Exact replay cannot bless changed canonical contact, rendered/template/provider, transfer, or
  ledger evidence.
- Provider acceptance is idempotent across rollback/retry and no audit/workflow leaks the full email.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator after gates
