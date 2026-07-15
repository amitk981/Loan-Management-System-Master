# Slice 007Q: Register Source Fields and Visual Evidence Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007O
- 007P

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Close the remaining S23/S25 source-column omissions and replace screenshots that hide the claimed
register evidence outside the captured viewport or contain opaque rendering artefacts.

## Source / Review References

- `docs/source/screen-spec.md` S23 and S25
- `docs/source/functional-spec.md` M05-FR-006 and M05-FR-009
- `docs/source/api-contracts.md` §§6-8, 25.9, and 25.10
- `docs/source/codebase-design.md` §§23.3-23.6, 24.4, 26.3, and 42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/007M-exception-supporting-evidence-and-register-closure.md`
- `docs/slices/007N-register-matrix-settings-contract-and-browser-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_034706_architecture_review`

## Concrete Requirements

1. Extend the immutable Credit Sanction Register projection with the remaining source S23 facts:
   formal entry number, folio, loan type, purpose, per-approver decision times, rejection reason,
   conditions, and communication date/status. Use frozen case/decision/action/communication facts;
   purpose/risk and routed identity/amount facts must consume 007O's immutable
   `source_review_facts_json` copy. Unavailable A-079 decision facts remain explicitly null, never
   copied from live application/member/appraisal rows.
2. Extend the immutable Exception Register projection with borrower, financial impact, requested-
   by actor, and decision date in addition to the delivered description/business reason, risk,
   authority/actions, and supporting metadata. Keep the register read-only and actor-scoped.
3. Render all named source columns using the existing register table/detail composition. If the
   existing horizontal table cannot show the evidence legibly at the trusted viewport, reuse an
   existing row-detail/card pattern; do not redesign or introduce styling. Keep both register
   collections on the 007P shared strict paginated transport: explicit page/page size, exact server
   totals, and atomic row/pagination replacement with malformed success rendered as an error.
4. Keep document ids as metadata. Register visibility, a global document permission, or a frozen
   file name never creates a download control; only a separately returned enabled document action
   may do so.
5. Browser assertions must place approver comments/times, supporting file metadata, and the newly
   restored columns inside the captured viewport. Wait for the stable app-shell/table state and
   reject screenshots containing large opaque/blank rendering artefacts; do not bless an off-screen
   DOM assertion as visual proof.

## Trusted Browser Acceptance

- Spec: `e2e/approval-register-settings.e2e.spec.ts`
- Spec: `e2e/exception-register-evidence.e2e.spec.ts`
- Screenshot: `credit-sanction-register-source-fields.png`
- Screenshot: `exception-register-source-evidence.png`
- Screenshot: `exception-register-document-denied.png`

## Trusted Browser Scenario

Open routed S23 and S25 panels in the production app shell. Capture a complete frozen sanction row
with the restored formal/source facts, then an exception row with borrower/impact/requester/date,
visible action comments/times, and visible supporting metadata. Repeat the exception view without
document action authority and prove no download control exists. Each screenshot must be visually
reviewable at 1280x720 without opaque capture corruption.

## Test Cases

- Backend serialization proves every new field comes from its frozen owner and is unchanged after
  later live application/appraisal/member/communication edits.
- Approved/rejected/empty-null rows distinguish rejection reason, conditions, communication and
  per-approver dates without client calculation.
- S23/S25 UI tests assert all restored values, object-scoped pagination, and no inferred actions.
- Trusted specs assert evidence is in the screenshot viewport and generate three nonempty,
  reviewable outputs in each of two independent runs.

## Evidence Required

Backend/frontend RED/GREEN output, source-field traceability, two-run trusted screenshots, and all
configured gates.

## Risk Level
High

## Acceptance Criteria

- S23 and S25 expose their source-required immutable record facts without live reconstruction.
- Trusted screenshots visibly prove the claimed evidence and contain no opaque capture corruption.
- All configured gates pass.
