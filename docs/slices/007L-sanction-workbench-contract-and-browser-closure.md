# Slice 007L: Sanction Workbench Contract and Browser Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007K

## Runtime Capabilities
- `localhost-e2e-server`

## Goal

Close the remaining S21/S22 workbench contract and prove every required sanction state through the
trusted browser gate that 007I intended but never declared.

## Source / Review References

- `docs/source/screen-spec.md` S21, S22, and S24
- `docs/source/functional-spec.md` M05-FR-002/007/008/011/012
- `docs/source/api-contracts.md` §§25.3-25.8, §25.11, and §44
- `docs/source/codebase-design.md` §§23.3-23.6, 24.4, 26.3, and 42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/007I-sanction-workbench-ui.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_010536_architecture_review`

## Concrete Requirements

1. The S21 request must explicitly send `approval_type=sanction`; the pending queue must also send
   `current_status=pending&assigned_to_me=true`. Preserve the server's actor-scoped count/order and
   do not fetch unrelated approval types or repair rows from another endpoint.
2. Extend the list projection through the approval-owned frozen boundary with the S21 facts needed
   per row: borrower/name/type, requested/recommended/eligible amounts, approval path, exception and
   related-party flags, risk rating, submitted timestamp, current decision status, and a server-
   projected pending-age/TAT display fact. Do not query live appraisal/configuration per row or
   calculate workflow authority/TAT policy in React; where 012EA policy is unavailable, label the
   elapsed fact honestly and do not invent a target breach.
3. Render immutable `approval_actions` history on S22, including actor/role, decision or abstention,
   comments/reason, and acted-at confirmation. Required/effective/excluded authority remains a
   separate frozen projection; history may not disappear when an alternate acts.
4. Keep every approve/reject/return/abstain action as the intersection of enabled resource action
   and `/auth/me` permission. Preserve mandatory comments, stale/conflict/meeting-gate errors,
   canonical refetch after success, old/new cycle isolation, and independent sanction-decision
   permission without register fallback.
5. Put authenticated JSON and multipart upload mechanics behind the shared frontend API-client
   seam. Feature services own typed sanction paths/payloads only; they do not load JWTs, parse
   envelopes, or duplicate auth/error handling.
6. Do not label or treat the three ids on `general_meeting_approval` as currently referenceable
   merely because case metadata exposes them. Reuse requires a document-owned exact-application
   referenceability projection and backend revalidation; until that selector exists, require three
   new accepted uploads for a changed submission. Register/case metadata never grants reference or
   download authority.
7. Keep the approved single-button decision modal and existing queue/card/table patterns. Add no
   new styling or client-owned business calculations.

## Trusted Browser Acceptance

- Spec: `e2e/sanction-workbench.e2e.spec.ts`
- Screenshot: `sanction-pending-special-conflict.png`
- Screenshot: `sanction-approved.png`
- Screenshot: `sanction-rejected.png`
- Screenshot: `sanction-returned.png`
- Screenshot: `sanction-empty.png`
- Screenshot: `sanction-denied.png`
- Screenshot: `sanction-error.png`

## Trusted Browser Scenario

- Open the production routed workbench inside the real app shell with a deterministic authenticated
  backend contract. Exercise queue/detail navigation, a special/conflicted pending case, immutable
  action history, all terminal/history states, empty, object denial, and service error. The spec
  may intercept exact API envelopes for deterministic visual states but must not mount a component
  directly or inject markup.

## Test Cases

- Exact list URL/query, frozen queue-field rendering, and no live per-row request.
- Every action URL/body plus comments/history/time, partial/final outcomes, conflict and gate
  precedence, stale one-call behavior, permission loss, and returned/corrected cycle switching.
- Trusted collection discovers the named spec and produces all seven screenshots in each of the
  orchestrator's two independent runs.

## Risk Level
High

## Acceptance Criteria

- S21/S22/S24 expose all source-required frozen facts and immutable history without client authority.
- The shared API seam owns auth/envelope/upload mechanics.
- All seven trusted screenshots and all configured gates pass.
