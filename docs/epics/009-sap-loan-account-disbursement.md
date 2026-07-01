# Epic 009-sap-loan-account-disbursement: 009: SAP, Loan Account Creation, and Disbursement

This parent epic preserves the broad planning context from the earlier Ralph slice. Actual implementation work is broken into smaller child slices under `docs/slices/`.

## Source Broad Slice

# Slice 009: SAP, Loan Account Creation, and Disbursement

## Status
Not Started

## Goal
Implement SAP customer profile request/confirmation, loan account creation, disbursement readiness, payment initiation, CFC authorization, UTR capture, disbursement advice, and frontend finance queues.

## User Value
Finance can create loan accounts and release funds only after all sanction, documentation, security, SAP, and bank readiness gates pass.

## Depends On
- Slice 008

## Source References
- `docs/source/implementation-roadmap.md` section 14
- `docs/source/api-contracts.md` sections 33, 34
- `docs/source/data-model.md` finance, SAP, disbursement, loan account tables
- SOP PDFs under `docs/source/`
- `docs/source/functional-spec.md`

## Screens Involved
- SAP request/confirmation
- Loan account creation
- Disbursement readiness
- Payment initiation
- CFC authorization
- Transfer success/UTR
- Disbursement advice
- Loan Account 360 initial view
- Member portal disbursement status

## Prototype Reference
- `DisbursementHub.tsx`
- `PaymentAuthorisationHub.tsx`
- `LoanAccount360.tsx`
- `MP14_DisbursementStatus.tsx`

## Frontend Scope
- Wire finance/disbursement screens to backend APIs.
- Add explicit readiness pass/fail states and blockers.
- Add CFC role action visibility and unauthorized states.
- Add member portal disbursement status from backend.

## Backend/API Scope
- SAP request model/service and Excel/details generation.
- SAP customer code confirmation/reuse logic.
- Loan account creation from sanctioned application.
- Disbursement readiness service.
- Idempotent disbursement initiation.
- CFC authorize/reject API.
- Bank transfer success API with UTR/evidence.
- Disbursement advice communication job.
- Register updates.

## Database/Model Impact
- SAP customer profile requests, SAP customer codes, loan accounts, loan terms, disbursements, bank transfers, loan status histories, communications.

## API Contracts
- SAP request APIs
- Loan account APIs
- Disbursement readiness APIs
- Disbursement APIs

## Permissions
- Senior Manager Finance initiates.
- CFC authorizes.
- Backend must enforce roles and idempotency.

## Validation Rules
- SAP request only after sanction approval.
- Existing borrower SAP code reused.
- Loan account created once.
- Disbursement requires readiness pass.
- Amount cannot exceed sanction.
- UTR required and duplicate UTR blocked.
- Loan active only after successful transfer.

## Test Cases
- SAP request generation and code confirmation.
- Loan account creation idempotency.
- Readiness gate pass/fail.
- Initiation permission/idempotency.
- CFC authorization permission.
- UTR uniqueness and activation.

## Visual Acceptance Criteria
- Finance queues preserve prototype operational density.
- Readiness blockers are visible before payment actions.

## Evidence Required
- API/service tests.
- Screenshots of readiness, payment initiation, CFC authorization, and success.
- API response examples for readiness and transfer success.

## Risk Level
High

## Acceptance Criteria
- Disbursement cannot bypass readiness, roles, or UTR controls.
- Loan account activation is tied to successful transfer.
- Frontend finance screens and member portal status reflect backend truth.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates

