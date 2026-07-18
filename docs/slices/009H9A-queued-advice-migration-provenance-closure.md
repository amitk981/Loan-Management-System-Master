# Slice 009H9A: Queued Advice Migration Provenance Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make the deployed communications 0007-to-current migration preserve a genuine frozen queued H5
advice job instead of downgrading its outbox and then failing in migration 0009.

## Depends On
- 009H8

## Source / Review References
- `docs/source/codebase-design.md` §§26.1-26.3, 35.2, 36.1-36.2, and 42
- `docs/source/data-model.md` §34
- `docs/source/integrations.md` §§10.2-10.6, 21, 22, and 33.3
- `docs/slices/009H6-legacy-advice-template-provenance-closure.md` requirements 1-4
- `docs/slices/009H7-communications-dispatcher-interface-and-idempotency-closure.md` requirement 3
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-18_204305_architecture_review`
- Review probe `.ralph/runs/2026-07-18_204305_architecture_review/evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. Starting at communications 0007, a pending outbox with complete internally checksummed frozen
   template facts and one coherent retained H5 `CommunicationDeliveryJob` is classified as
   `verified` / `frozen_before_dispatch` by 0008. Applying 0009 and every current leaf must succeed
   and preserve the exact outbox/job ids, status, attempts, actor, request, payload digest,
   idempotency key, template snapshots, and timestamps.
2. The job is evidence only when its outbox/advice/actor/request/payload/status relationships are
   singular and exact. An attempt-less row without that complete job, a mismatched job, a legacy
   adapter attempt, malformed checksum, duplicate/cross-linked identity, or incomplete snapshot
   remains `legacy_partial` / `ambiguous_legacy`; do not reconstruct missing facts.
3. Correct the already-committed migration chain at the earliest operation that can still inspect
   the retained H5 job and complete snapshot. Do not add a later migration that can never run after
   0009 has failed, do not rewrite provider/receipt/Communication/action/audit/workflow history, and
   do not weaken H6's legacy nondispatch/replay/portal exclusions.
4. Prove fresh forward, retained forward, reverse at the truthful safe boundary, and reapply from
   0007 through the current leaves. Migration-test cleanup must restore all current leaf migrations
   even when the expected historical failure path is exercised.

## Test Cases
- Copy the architecture-review queued-job probe failing first; make the genuine 0007 queued fixture
  migrate to current while preserving a complete before/after manifest.
- One-field matrices cover job/outbox/advice/payload/actor/request/status/checksum/snapshot drift and
  distinguish an unlinked attempt-less row from the coherent queued job.
- Re-run H6's template-drift, retained legacy, pending, malformed, forward/reverse/reapply, public
  no-redispatch, portal exclusion, and migration-order suites.

## Runtime Capabilities

none

## Database / Migration Impact
Correct one existing pre-release communications data migration in place; add no schema migration and
change no current model, table, constraint, API, or business workflow.

## Risk Level
High

## Acceptance Criteria
- A valid queued H5 job can never block 0007-to-current deployment or lose verified frozen facts.
- Ambiguous/legacy history remains honest, nondispatching, and excluded from current advice truth.

## Done Checklist
- [x] Execution plan written
- [x] Genuine queued-job migration probe written failing first
- [x] Exact coherent-job classification implemented
- [x] Forward/reverse/reapply and legacy matrices green
- [x] Risk, evidence, handoff, state, contract, and digest updated
- [x] Commit delegated to the orchestrator after gates
