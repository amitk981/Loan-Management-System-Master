# Slice 004J: Bank Account and Cancelled Cheque Profile Foundation

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Deliver this narrow capability as a small, testable Ralph implementation slice.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 004I

## Prior Slice Facts
- 004H2 hardened duplicate member-party KYC profile creates with a stable `400 VALIDATION_ERROR`
  response before the database uniqueness constraint. 004J should not reopen KYC profile creation,
  document verification, or sensitive reveal contracts; it starts after 004I and should stay focused
  on bank-account/cancelled-cheque profile facts.
- Epic 004 digest records that bank account and cancelled-cheque values are sensitive fields:
  full account numbers must be protected/encrypted plus hashed/last-four storage only, and responses
  and audit metadata must expose masked/last-four values only.

## Source References
- `docs/source/data-model.md` §12.3-§12.5 bank accounts, cancelled cheques, and bank verification
  letters
- `docs/source/data-model.md` §28 encrypted sensitive fields
- `docs/source/api-contracts.md` §31.2 disbursement initiation bank account IDs and §45 bank gate
- `docs/source/screen-spec.md` S11 duplicate bank-account warning, S15 signature mismatch bank
  verification letter, and disbursement payment fields
- `docs/working/digests/epic-004-member-kyc-master.md`

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
Member Profile bank/account evidence area only if a backend-backed read or create path is included.
Otherwise none directly; later disbursement/security slices own payment initiation, bank
verification letter workflow UI, blank-dated cheque custody, and disbursement gates.

## Frontend Scope
Prefer backend/API foundation only. If UI is included, wire only a narrow Member Profile bank
account/cancelled-cheque metadata panel using existing profile card, empty-panel, alert, form-field,
and status-badge patterns. Do not implement payment initiation, signature mismatch resolution,
bank-verification-letter generation, blank-dated cheque custody, or disbursement readiness UI here.

## Backend/API Scope
Implement member-owned bank-account and cancelled-cheque profile foundation only if it can stay
small:
- member-scoped bank-account list/create read path for account holder name, masked account number
  last four, IFSC, bank name, branch name, verification status, signature flag, status, and linked
  cancelled-cheque ID;
- cancelled-cheque metadata create/read for member, document ID, masked account number last four,
  IFSC, branch name, verification status, signature mismatch flag, and created timestamp;
- exact full account number must be stored only as protected/encrypted token plus keyed hash/last4,
  never serialized or audited;
- do not implement loan-application-specific bank verification letters unless the slice is split or
  explicitly widened.

If no source-backed endpoint shape exists for this member-profile foundation, create the model and
service boundary behind tests and record the temporary API deferral in `docs/working/ASSUMPTIONS.md`
rather than inventing a broad bank-admin API.

## Database/Model Impact
Non-destructive model/migration changes for the source fields:
- `bank_accounts`: `owner_party_type`, `owner_party_id`, `account_holder_name`,
  `account_number_encrypted`, `account_number_hash`, `account_number_last4`, `ifsc`, `bank_name`,
  `branch_name`, `verification_status`, nullable `cancelled_cheque_id`,
  `signature_verified_flag`, and `status`;
- `cancelled_cheques`: member FK, nullable loan-application boundary only if available,
  `document_id`, `account_number_encrypted`, `ifsc`, `branch_name`, `verification_status`,
  `signature_mismatch_flag`, and `created_at`;
- leave `bank_verification_letters` to the signature-mismatch/documentation workflow unless the
  slice is split and source-backed end-to-end tests are added.

## API Contracts
Create or update the API contract for any endpoint added. The contract must state masking/last-four
semantics, duplicate-bank-account behavior if implemented, and all explicit deferrals.

## Permissions
Use the narrowest source-compatible member/account permissions available in the catalogue. If no
exact bank-account permission exists, follow `DECISION_POLICY.md`: either use a recorded
member-profile assumption or split a permission-catalogue slice first. Do not reuse sensitive
reveal, document download, disbursement, or export permissions for normal bank-account metadata
create/read.

## Audit Requirements
Audit create/update actions with metadata only: member ID, bank-account/cancelled-cheque IDs,
masked last four, IFSC, verification status, signature flags, request/IP/user-agent. Audit logs must
not include full account numbers, encrypted token contents, hashes, cheque images, or file bytes. No
workflow events for simple member-profile metadata create/read.

## Validation Rules
Require account holder name, account number, IFSC, owner/member facts, and document ID for
cancelled-cheque metadata. Reject malformed UUIDs and unsupported verification/status values. Mask
account number everywhere except the protected storage token/hash/last4 fields. Do not invent bank
verification-letter, duplicate-active-borrower, disbursement-blocker, or payment-initiation rules in
this foundation slice.

## Test Cases
TDD: create/read/list success, missing auth, permission separation or recorded assumption,
unknown/soft-deleted member, required-field validation, malformed UUIDs, account-number masking and
hash/protected storage, duplicate active-bank warning only if source-backed behavior is implemented,
metadata-only audit, no workflow event, and frontend loading/empty/error/validation/success states
if UI is touched.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

## Acceptance Criteria
- The named capability works through the intended backend/API/frontend path, where applicable.
- Source-doc business rules are enforced or documented as assumptions.
- Permissions and audit expectations are tested when applicable.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
