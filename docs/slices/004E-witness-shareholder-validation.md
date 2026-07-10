# Slice 004E: Witness Shareholder Validation

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Persist and expose an application-scoped witness whose identity resolves to a real member with
verified KYC and an active, positive SFPCL shareholding; never trust caller-supplied verification.

## User Value
Compliance and Company Secretary users can capture documentation witness identity against a real
loan application and receive an evidence-backed shareholder/KYC verification result.

## Depends On
- 004F
- 005A

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 13-18
- docs/source/data-model.md member/KYC/shareholding tables
- docs/source/screen-spec.md member screens

## Prototype Reference
- sfpcl-lms/src/pages/members/*
- sfpcl-lms/src/data/mockData.ts

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
Unblocked 2026-07-10 (owner audit): all three prerequisites are Complete — `004D2` removed the
premature loan-start availability and nominee audit hashes, `004F` persisted
shareholding/shareholder facts, and `005A` established the owning loan-application table/API
boundary. Implement witness capture against those real tables.

`data-model.md` §10.5 and `screen-spec.md` S09 make witnesses application documentation records,
not member-profile records. Implement witness capture only against a real loan application and real
member/shareholding records; do not create a member-level witness API or boolean-only verification
stub.

- Add `GET` and `POST /api/v1/loan-applications/{loan_application_id}/witnesses/` using the
  standard success/list/error envelopes. Unknown query parameters and non-default pagination are
  out of scope because one application may have only the documentation witnesses it explicitly
  captures; return a deterministic created-order list.
- POST accepts `member_id`, `witness_name`, `pan`, and `aadhaar`. The member identifier is required
  so validation cannot be bypassed with only a name or caller-controlled folio. The response also
  returns the resolved member and folio identifiers.
- Keep witness storage and its service/API boundary in the `applications` module because the
  required owning FK is `loan_applications`; reuse member identity/shareholding records only as
  validation evidence.
- Do not implement witness document uploads, signatures, editing, deletion, documentation-stage
  completion, SH-4, Loan Agreement, or frontend UI in this slice.

## Database/Model Impact
Add `witnesses` with UUID PK; protected loan-application and member FKs; witness name; protected
PAN/Aadhaar token columns plus indexed keyed hashes; non-caller-controlled
`shareholder_verified_flag`; verification status; verifier; verification time; and created time.
Index the application FK and identity hashes. Persist no plaintext PAN or Aadhaar column.

## API Contracts
Document the new nested list/create endpoint in `docs/working/API_CONTRACTS.md`. Successful POST
returns masked PAN/Aadhaar objects only, `shareholder_verified_flag: true`,
`verification_status: verified`, verifier/time, and resolved member/folio metadata. Missing
application/member returns 404; malformed/missing fields return the standard 400 validation
envelope; a member without qualifying shareholding returns `WITNESS_NOT_SHAREHOLDER` (400).

## Permissions
The source catalogue has no witness-specific permission code. Record that gap in ASSUMPTIONS and
add narrowly scoped `members.witness.read` and `members.witness.create` codes following the source
`<module>.<resource>.<action>` convention. Assign both to Compliance Team Member and Company
Secretary per `auth-permissions.md` §15.4/§26.4; assign read only to Credit Manager and Internal
Auditor. Require the relevant witness permission plus the existing application object-access
decision. Do not substitute nominee, shareholding, KYC, or generic application mutation permission.

## Audit Requirements
Successful create writes one metadata-only `applications.witness.created` audit row containing
application, witness, resolved member/folio, verification status, actor, request/IP/user-agent, and
no plaintext or identity-derived secret. GET writes no audit/workflow event. No separate workflow
event is required because creation does not transition application state.

## Validation Rules
- Resolve `member_id` to a real member and require the supplied witness name to match that member's
  legal or display name after trim/case normalization.
- A qualifying shareholder has at least one persisted `active` shareholding with
  `number_of_shares > 0`; use its folio as persisted evidence. Otherwise reject with
  `WITNESS_NOT_SHAREHOLDER`.
- Require the resolved member's persisted `kyc_status` to be `verified`; otherwise return a 400
  validation error and do not create a witness.
- PAN and Aadhaar are required and must pass the existing protected-identity format validation.
  Encrypt/tokenize and hash them with the existing members-module protection helpers or an
  equivalent shared seam; responses and audit metadata expose masked values only.
- Reject any caller-supplied verification flag/status/verifier/time fields as unknown fields.
  The service sets verified metadata only after all persisted checks pass.
- Apply application object access before returning or creating any witness. Documentation remains
  incomplete unless a later documentation slice sees a verified witness; do not change current
  application completeness in this slice.

## Test Cases
Drive the public nested API test-first, one red/green cycle at a time: qualifying shareholder with
verified KYC succeeds; list returns only that application's witnesses; zero/inactive/no shareholding
returns `WITNESS_NOT_SHAREHOLDER`; unverified KYC and mismatched name reject; missing application or
member returns 404; missing/invalid identity rejects; caller-supplied verification metadata rejects;
missing witness permission and failed application object access deny; read-only roles cannot create;
stored values are protected and response/audit never leak plaintext; successful verification
metadata and exactly one create audit row are recorded.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
Medium

## Acceptance Criteria
- The application-scoped GET/POST endpoint works with standard API envelopes and real application,
  member, KYC, and shareholding records.
- Only a matching member with verified KYC and active positive shares can be persisted as verified;
  clients cannot forge verification metadata.
- PAN/Aadhaar remain protected at rest and masked in API/audit output.
- Narrow witness permissions, application object access, read-only roles, and metadata-only create
  audit behavior are covered by tests.
- No frontend, document/signature workflow, or application-state transition is added.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
