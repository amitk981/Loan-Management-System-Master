# Slice 009I2: Portal Disbursement Stage and Visual Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make MP14 consume exact documentation/SAP/payment/authorisation/transfer/advice stage truth, remove
client-owned application selection, and satisfy the promised real-browser visual contract.

## Depends On
- 009G6
- 009H8
- 009I

## Source / Review References
- `docs/source/screen-spec-member-portal.md` MP14 and permissions matrix
- `docs/source/functional-spec.md` BR-054 and M08-FR-001-011
- `docs/source/api-contracts.md` §§29-31
- `docs/source/auth-permissions.md` §40.1
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-18_152831_architecture_review`
- Review probe `evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. Pass MP14 the explicit `selectedApplicationId` already owned by `BorrowerPortal`; never rank or
   choose applications from client status strings. When no application was selected, render the
   existing portal empty/navigation pattern directing the borrower to My Applications. Cover two
   finance-relevant applications in opposite list orders and always request only the selected id.
2. The backend projection consumes exact owner decisions for documentation completion, SAP request/
   code completion, payment initiation, terminal CFC decision, transfer, and finalized advice.
   Each timeline row uses its owner timestamp or honest null; never copy `initiated_at` or
   `disbursed_at` onto unrelated earlier stages. Missing/stale/mixed facts stop at the last provable
   stage or borrower-safe blocked copy.
3. A sanctioned account with current SAP completion but no initiation projects documentation/SAP
   complete and payment pending. Pending/approved/rejected CFC, transferred/no-advice, queued advice,
   accepted advice, stale provider/provenance, and changed owner-time cases remain exact and zero-write.
4. Replace local `PortalMessage` and bespoke alert/empty classes with the existing portal/
   `AlertBanner` composition. Preserve the approved MP14 header, completion card, three-fact grid,
   timeline, advice card, spacing, colours, typography, and responsive layout; add no styling or
   component. Keep the deterministic UTF-8 advice decision under uniquely numbered assumption
   `A-133`, while capability claims use honest `artifact_id` vocabulary rather than calling an
   outbox a file.
5. Add a no-write SQL assertion for status GET and full application-selection, stage-time, masking,
   session, download, error, and current-advice interaction coverage.

## Runtime Capabilities

localhost-e2e-server

## Trusted Browser Acceptance
- Spec: `sfpcl-lms/e2e/portal-disbursement-status.spec.ts` authenticates through real Django and
  uses no blanket API interception.
- Save processing/SAP-complete evidence to
  `evidence/screenshots/mp14-processing.png`.
- Save transferred/accepted-advice evidence to
  `evidence/screenshots/mp14-disbursed-advice.png`.
- Save the safe unavailable/error state to
  `evidence/screenshots/mp14-safe-error.png`.
- Run the declared browser contract twice outside the sandbox; the screenshots must preserve the
  existing borrower viewport/composition and expose no full bank/reference/internal evidence.

## Database / Migration Impact
None expected. Reuse corrected communications artifact/capability and owner timestamps.

## Risk Level
High

## Acceptance Criteria
- MP14 never selects an application or calculates stage truth in the client.
- Every stage/status/time is current owner truth or honest null, and advice availability requires
  the corrected accepted worker result.
- All three real-Django screenshots and two external browser runs pass with prototype fidelity.

## Done Checklist
- [ ] Execution plan written
- [ ] Selection/SAP/timestamp/browser probes written failing first
- [ ] Owner-stage projection and explicit application selection implemented
- [ ] Existing visual patterns restored
- [ ] Trusted browser contract passes twice with three screenshots
- [ ] Focused backend/frontend and configured gates green
- [ ] Risk, evidence, handoff, state, contract, assumption, inventory, and digest updated
- [ ] Commit delegated to the orchestrator after gates

