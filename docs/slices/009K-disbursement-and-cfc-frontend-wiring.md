# Slice 009K: Disbursement and CFC Authorization Frontend Wiring

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Wire the staff finance screens to the backend built in 009A-009H: SAP Customer Code Request/Confirmation (S36/S37), Disbursement Readiness Review (S38), Payment Initiation (S39), CFC Payment Authorisation (S40), and Disbursement Advice (S41).

## User Value
Senior Manager Finance and the CFC run the real money-release workflow — readiness blockers, initiation, authorization, UTR capture, and advice all reflect backend truth instead of mock data.

## Depends On
- 009J

## Source References
- docs/source/screen-spec.md screens S36-S41 and section 9.6 (disbursement rules)
- docs/source/api-contracts.md sections 29 (SAP customer code), 30 (loan account), 31 (disbursement), 45 (idempotency contract)
- docs/source/integrations.md (SAP and bank adapter behaviour, manual/adapter-first for MVP)
- docs/source/Final SOP - Loan Disbursement V10 (1).pdf (disbursement sequence)

## Prototype Reference
- sfpcl-lms/src/pages/disbursement/DisbursementHub.tsx
- sfpcl-lms/src/pages/disbursement/PaymentAuthorisationHub.tsx

## Concrete Requirements
1. Wire `DisbursementHub.tsx`: SAP request/confirmation state (009A/009B), readiness pass/fail with named blockers (009D), payment initiation form (009E) sending an `Idempotency-Key` header per api-contracts §45, UTR capture and transfer-success state (009G), and disbursement advice status (009H).
2. Wire `PaymentAuthorisationHub.tsx` for the CFC role: pending authorizations queue, authorize/reject with reason (009F); actions visible only to CFC and enforced server-side.
3. Amount fields use the Money type (api-contracts §9.2); initiation is blocked in the UI when readiness fails, and the backend rejection is surfaced if attempted anyway.
4. Loading, empty, error, unauthorized, blocked, and success states throughout; existing queue/card patterns only.

## Owned Mock Removals
This slice is the final owner of these files' mock surface — after it, none of them may import `src/data/mockData.ts` or keep inline business fixtures:
- `src/pages/disbursement/DisbursementHub.tsx`
- `src/pages/disbursement/PaymentAuthorisationHub.tsx`

(`src/pages/loan-accounts/LoanAccount360.tsx` is wired initially by 009J; its final mock removal is owned by 010M.)

## Test Cases
- Readiness failure renders named blockers; initiation button disabled and direct API call rejected.
- CFC-only visibility: Senior Manager Finance cannot see authorize actions (frontend) and gets 403 (backend).
- Double-submit of initiation with same idempotency key does not create a duplicate (assert replayed response handling in UI).
- UTR entry validation: duplicate UTR shows the backend error cleanly.

## Out of Scope
Member portal disbursement status (009I done), Loan Account 360 (009J done), repayment screens (010M).

## Risk Level
High

## Acceptance Criteria
- S36-S41 run on backend data end to end; the initiate → authorize → UTR → advice path is walkable in the UI against seeded data.
- No mock-data reads remain in the disbursement screens.
- All gates pass; screenshots of readiness blockers, initiation, CFC authorization, and success saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
