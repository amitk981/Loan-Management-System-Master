# Slice 009H4: Communications Advice Evidence and Legacy Replay Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make every accepted advice provider fact immutable and current, preserve pre-outbox delivered
history without redispatch, and finish the non-circular communications persistence boundary before
the portal consumes advice truth.

## Depends On
- 009H3BB

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/integrations.md` §§10, 19.3, 21, 29, and 33.3
- `docs/source/codebase-design.md` §§20.6, 22.2, 26.3, 36.1-36.2, 40.1-40.2,
  and 42.4
- `docs/source/data-model.md` §34
- `docs/working/REVIEW_FINDINGS.md` entry for
  `2026-07-18_104345_architecture_review`
- Review probes `red-legacy-advice-outbox-replay.txt` and
  `red-provider-tuple-mutation.txt` in that run's evidence

## Concrete Requirements
1. Add one communications-owned immutable provider-acceptance/attempt ledger. It binds the exact
   outbox, stable key, complete payload digest, provider identity/status/time, adapter kind, and
   accepted/rejected outcome before receipt/finalization. Once accepted, changed provider id,
   status, time, key, payload, adapter, or sibling attempt is a zero-write conflict; finalization
   consumes this retained owner fact rather than trusting mutable outbox columns alone.
2. Freeze the complete 009H3BA template provenance durably before dispatch: template id/code/name/
   type/language/audience/version/approval/effective range/declared variables/source subject/source
   body/checksum plus rendered snapshots. Do not reconstruct missing provenance from a later mutable
   template row when producing or reconciling the delivery decision.
3. Preserve every coherent pre-009H3A delivered row. The migration must backfill an outbox and
   immutable provider fact from the singular retained intent/receipt/Communication/template chain
   without a provider call, new communication, changed id, or rewritten audit/workflow/action.
   Incomplete or ambiguous legacy chains remain honestly non-current and must fail before dispatch;
   terminal intent/Communication truth with an absent outbox can never re-enter a provider path.
4. Remove the persistent communications-to-disbursements dependency. Store advice-intent identity
   as a primitive unique UUID in communications-owned tables, remove the receipt compatibility
   model alias after all callers/tests use the canonical owner, and drop only the cross-app FK
   constraints while retaining physical columns, table names, ids, values, uniqueness, and history.
   No communications model or migration after this correction may import/query disbursement policy.
5. Protect the terminal outbox/provider/receipt chain from ordinary deletion or replacement and
   reconcile every member of the chain on first completion and replay. Missing, extra, duplicate,
   changed, or cross-linked evidence is a safe zero-write conflict.
6. Replace the shallow migration signature proof with exact column type/null/default, FK, unique,
   check, index, table, row, and constraint-definition manifests. Prove forward, reverse to the
   declared safe boundary, and reapply for genuine pre-outbox delivered, accepted-not-finalized,
   pending, and no-advice rows.
7. Add the specified second crash proof at the real transaction boundary: create the protected
   Communication and local audit/workflow evidence, force failure immediately before commit, and
   prove the entire local chain rolls back while the singular accepted provider fact survives for
   exact recovery.

## Test Cases
- Copy both review probes failing first. The legacy/missing-outbox case makes zero adapter calls and
  writes nothing; the changed valid provider tuple never becomes receipt/Communication truth.
- Exhaustive one-field/duplicate/missing provider, template-provenance, outbox, receipt, final
  Communication, audit, workflow, and disbursement-action mutation matrix through the public owner.
- Genuine migration fixtures for delivered legacy rows, accepted crash rows, pending rows, and
  malformed/ambiguous histories; exact ids/schema/history survive forward/reverse/reapply.
- Public role/scope/current-contact/template/upstream/error/masking/no-financial-write regressions
  remain exact. PostgreSQL five-caller tests run twice and retain one immutable provider fact and
  one complete final chain with four clean losers.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
Exactly one communications migration. It adds the immutable provider ledger and complete provenance,
backfills only coherent legacy truth, removes cross-app FK constraints without changing retained
columns/ids, and must be reversible to its declared safe boundary without data loss.

## Risk Level
High

## Acceptance Criteria
- No terminal or migrated advice can call a provider because an outbox is absent, and no mutable
  provider tuple can fabricate delivery truth.
- Communications owns a complete immutable provider/template/outbox/receipt chain with no
  persistent dependency on disbursement models.
- Historical coherent deliveries replay exactly without resending; ambiguous history is honest and
  nondispatching; both crash windows and twice-run races retain one logical delivery.

## Done Checklist
- [x] Execution plan written
- [x] Review probes and migration cases written failing first
- [x] Immutable provider/provenance owner and legacy backfill implemented
- [x] Cross-app persistence dependency and compatibility alias removed
- [x] Exact migration manifests and PostgreSQL races green twice
- [x] Public authority/secrecy/current-truth regressions green
- [x] Risk assessment, handoff, state, digest, and evidence updated
- [x] Commit delegated to the orchestrator after gates
