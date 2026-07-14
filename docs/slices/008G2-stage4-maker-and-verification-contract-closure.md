# Slice 008G2: Stage-4 Maker and Verification Contract Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008G

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make Stage-4 stamp, notary, signature, and tri-party evidence retain the actual latest material
maker, preserve consumed execution truth, and follow the documented domain/HTTP/action contracts.

## Source / Review References

- `docs/source/auth-permissions.md` §§15.4-15.5, 18.1-18.2, 19.2-19.4, and 26.4
- `docs/source/codebase-design.md` §§6.3-6.4, 7.2, 9.1-9.2, 14.2-14.3, and 36-37
- `docs/source/api-contracts.md` §§6-8 and 26.6-26.10
- `docs/source/data-model.md` §§16.3 and 16.6-16.8, 30, and 34
- `docs/source/functional-spec.md` M06-FR-008/M06-FR-009/M06-FR-015/M06-FR-016/M06-FR-017
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_185927_architecture_review`

## Concrete Requirements

1. Treat the actor who last materially changes pending stamp/notary preparation or signature
   capture facts as the current maker. A different actor must not inherit the original maker's id
   and then verify/resolve the facts they changed. Preserve every prior maker and old/new snapshot
   in immutable evidence; exact replay remains zero-write and does not transfer maker identity.
2. Enforce current-maker/checker separation by immutable user id across multiple active roles.
   New positive and adverse stamp/notary outcomes require non-null distinct maker/checker facts;
   mismatch resolution requires a non-null distinct current capture maker. Keep A-108/A-109 legacy
   null-maker rows honest and ineligible for change or new downstream truth.
3. Add database constraints for new/current positive and adverse stamp/notary evidence and resolved
   signatures wherever legacy compatibility permits. Direct ORM/bulk paths must not create a
   checker-owned outcome with no verifier or the same maker/checker identity.
4. Restore dependency direction: HTTP serializers parse transport shape and call domain interfaces;
   business modules must not import HTTP request serializers. Direct module callers still cross
   domain validation, permission, idempotency, transaction, and audit rules. Centralise Stage-4
   action authority behind the existing permission/document-authority seam.
5. Return the §6.3 action response for §26.6 tri-party verification, including previous/new state,
   workflow-event identity, and available actions. Map an unresolved mismatch capture overwrite to
   the source-defined `SIGNATURE_MISMATCH_UNRESOLVED` contract rather than generic conflict.
6. Once exact borrower/nominee signatures have supplied a verified tri-party decision, ordinary
   capture must not rewrite those consumed rows and leave the document labelled verified. Retain
   immutable signature ids/names/makers/times in the decision evidence and keep every checklist,
   package, repayment, file, and readiness fact unchanged.
7. Replace metadata-only positive fixtures with one real public generation-to-signature-to-§26.6
   tracer. Run exact and different-remarks five-worker verification races twice on PostgreSQL and
   prove one current decision plus a complete attributable winner/loser ledger.

## Test Cases

- A prepares pending, B changes it, and B then attempts stamp/notary verification, mismatch
  resolution, or another checker action through a secondary role: every attempt fails zero-write;
  C succeeds and all three identities/history entries remain attributable.
- Positive/adverse direct ORM constraint matrices, legacy-null replay/remediation denial, exact
  replay, changed checker decision, projection rollback, and complete audit/version/workflow facts.
- HTTP and direct-module matrices prove transport/domain separation, permission-first denial, strict
  fields, §6.3 verification responses, and the mismatch-specific error code.
- A verified tri-party's consumed signatures cannot be changed to pending/signed/mismatch through
  capture; failed changes retain the verified document and all ledgers unchanged.
- Genuine public generation tracer and twice-run PostgreSQL exact/changed races.

## Evidence Required

Backend RED/GREEN reproductions for maker handoff and consumed-signature mutation, action/error
examples, dependency proof, genuine public tracer, twice-run PostgreSQL races, and all gates.

## Risk Level
High

## Acceptance Criteria

- The actual latest material maker can never check their own Stage-4 evidence.
- Consumed tri-party execution truth cannot be silently invalidated.
- Domain, transport, permission, action, and error seams match source contracts.
- All configured gates pass.

