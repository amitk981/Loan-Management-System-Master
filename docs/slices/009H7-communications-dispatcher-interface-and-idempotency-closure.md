# Slice 009H7: Communications Dispatcher Interface and Idempotency Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Provide the source-defined generic communications interface and make generic/advice sends share one
honest, explicit idempotency and delivery policy without a hidden process/app cycle.

## Depends On
- 009H5
- 009H6

## Source / Review References
- `docs/source/codebase-design.md` §§20.2-20.6, 22.2, 36.1-36.2, and 40.1-40.2
- `docs/source/integrations.md` §§7.3, 10.2-10.6, 19.3, 21, 22, and 33.3
- `docs/source/api-contracts.md` §§3, 6-8, 31.5, and 45
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-18_152831_architecture_review`
- Review probe `evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. Expose the exact deep interface named by source §40.1: `create_from_template`, idempotent
   `send(communication_id, idempotency_key)`, and `retry_failed`. Generic communication HTTP and
   disbursement advice must cross that same interface; advice-specific preparation/finalization may
   remain private implementation, not public caller knowledge.
2. Require a nonblank bounded `Idempotency-Key` for generic Email/SMS send and §31.5 advice send as
   integrations §21.1 directs. Bind it to the exact communication/advice/payload/current actor;
   exact replay returns retained truth and changed/missing/cross-object key use writes nothing.
3. Replace the advice-only job interface with one generic communications-owned job identity while
   preserving every 009H5 row/id/status/attempt. Do not create a parallel generic job table or put
   template/provider policy in scheduler/shared/process callers. Preserve H6's immutable
   `legacy_0005` versus `frozen_before_dispatch` origin/status contract; legacy-partial outboxes
   cannot be attached to a generalized send job, replayed, or upgraded as part of job migration.
4. Remove the lazy `disbursements -> processes -> disbursements` cycle. HTTP/task entrypoints call
   the top-level process coordinator; each business app exposes only its owner decision interface
   and imports neither the other app nor the coordinator that imports it.
5. A manual/no-provider adapter must never fabricate provider acceptance or `sent`. Fake remains
   test-only; configured external adapters alone return accepted provider truth. A manual mode, if
   retained, records a pending operator confirmation through an explicit owner action.

## Test Cases
- Copy the missing-`send` review probe failing first; generic and advice public tests assert the
  same create/send/retry owner with explicit missing/exact/changed/key-reuse matrices.
- Static and runtime import-graph tests reject direct, lazy, callback, registry, and package-level
  cycles; tests exercise only public owner/process interfaces.
- Manual/default mode cannot create provider acceptance, sent Communication, issued portal advice,
  or M08-FR-010 truth. Fake/configured adapters preserve exact replay and safe failure evidence.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
At most one communications migration to generalize the retained job without changing ids/history.

## Risk Level
High

## Acceptance Criteria
- Generic and advice sends use the source-shaped dispatcher and explicit idempotency contract.
- No configuration-free path fabricates delivery, and runtime dependency direction is acyclic.

## Done Checklist
- [ ] Execution plan written
- [ ] Dispatcher/idempotency/cycle probes written failing first
- [ ] Generic deep interface and retained job migration implemented
- [ ] Manual/provider truth made honest
- [ ] Public matrices and PostgreSQL races green twice
- [ ] Risk, evidence, handoff, state, contract, assumption, and digest updated
- [ ] Commit delegated to the orchestrator after gates
