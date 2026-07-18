# Slice 009H5: Communications Dispatcher Job and Dependency Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Consolidate template/send/retry behavior behind the source-defined communications dispatcher and
make disbursement advice a durable asynchronous communication job without a runtime app cycle.

## Depends On
- 009H4

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/api-contracts.md` §§31.5, 39, and 45
- `docs/source/integrations.md` §§10.2-10.6, 19.3, 21, and 33.3
- `docs/source/codebase-design.md` §§8, 16.4, 20.2-20.6, 22.2, 26.3, 36.1-36.2,
  40.1-40.2, and 42.4
- `docs/working/ASSUMPTIONS.md` A-027 and A-098
- `docs/working/REVIEW_FINDINGS.md` entry for
  `2026-07-18_104345_architecture_review`

## Concrete Requirements
1. Provide the canonical `communications.modules.communication_dispatcher` interface named by the
   source: template creation/render preparation, idempotent send, and retry-failed. Existing generic
   communication APIs and disbursement advice must delegate to this owner; remove duplicated
   approved/effective template lookup, merge validation, rendering, Communication creation,
   delivery-status, provider, and audit policy from legacy services/modules.
2. Move cross-owner advice orchestration to a shallow top-level process coordinator. Disbursements
   alone resolves authority and locked financial/current context; communications alone owns job,
   template, provider, delivery, retry, and communication evidence. Neither app imports the other's
   models/modules, and shared code imports no business app.
3. `POST /api/v1/disbursements/{id}/send-advice/` must durably create/reconcile one communication job
   and return the source-aligned queued result without invoking a provider in the request. Freeze the
   actor/role/team/request/network and 009H4 advice identity needed for later re-authorisation and
   nondisclosing execution; exact replay returns the same job, changed replay conflicts.
4. Execute the job through the project's pinned asynchronous worker boundary. Manual/Fake adapters
   run through the same task contract as Future. Provider failure records a safe bounded failure,
   applies bounded backoff, and remains retryable; accepted truth finalizes once. Exhaustion is
   honest failed state with an operator-visible task and no fabricated sent advice. Never call a
   real external provider in tests or local evidence.
5. Use the 009H4 immutable provider ledger as the integration-event truth required by the source,
   and expose queued/running/retrying/sent/failed lifecycle without raw recipient, rendered advice,
   full UTR/bank data, provider id, or exception payload in general job/audit/log evidence.
6. Update the public/working API contract and 009I owner projection for queued-versus-issued truth.
   M08-FR-010 is complete only after the worker records accepted/finalized delivery; queue creation
   alone must not make advice available to the borrower.

## Test Cases
- Generic content-template/send API and disbursement-advice tests traverse the same dispatcher
  interface; static dependency/source tests reject duplicate render/send policy and every runtime
  communications↔disbursements or shared→business edge.
- Request test proves zero provider calls, one durable job, exact replay, changed replay conflict,
  safe response, and no sent/financial/downstream truth.
- Eager-worker contract tests cover Manual/Fake/Future success, timeout/rejection, malformed result,
  bounded retry/backoff, exhaustion, crash before/after provider acceptance, restart, and exact
  009H4 finalization. Safe evidence contains no protected payload/provider/error values.
- Two PostgreSQL five-caller queue races and two five-worker execution races run twice: one job,
  one logical provider identity, one terminal chain, clean losers, and no duplicate communication.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
At most one communications-owned job migration. Reuse the scheduler shell where its generic
contract is sufficient; do not put disbursement-specific payload/policy into scheduler or shared.
Pin the source-required worker dependency if it is not already present; the orchestrator installs
from the lock/requirements file before independent validation.

## Risk Level
High

## Acceptance Criteria
- HTTP requests queue rather than synchronously send advice; exact retry and bounded worker retry
  cannot duplicate a borrower communication.
- One source-shaped dispatcher owns generic and advice template/send/retry policy, and app/runtime
  dependency direction is acyclic.
- Borrower advice becomes available only from one immutable accepted/finalized worker result, with
  safe lifecycle/audit evidence and complete public/current-truth regressions.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing dispatcher/dependency/job/retry tests written first
- [ ] Canonical dispatcher and shallow process coordinator implemented
- [ ] Durable asynchronous job and bounded retry lifecycle implemented
- [ ] API contract and downstream 009I projection updated
- [ ] Twice-run queue and worker PostgreSQL races green
- [ ] Backend checks, migration sync, and relevant worker/task tests green
- [ ] Risk assessment, handoff, state, digest, and evidence updated
- [ ] Commit delegated to the orchestrator after gates
