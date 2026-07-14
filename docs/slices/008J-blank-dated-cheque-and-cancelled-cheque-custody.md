# Slice 008J: Blank-Dated Cheque and Cancelled Cheque Custody

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Goal
Create and maintain the one source-defined blank-dated security cheque for the retained sanctioned
security package, bind it to the borrower's verified bank/cancelled-cheque facts, protect its number,
and retain maker-checker custody without presenting or returning it.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 008I4

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Source References
- docs/source/implementation-roadmap.md section 13
- docs/source/api-contracts.md sections 26-28
- docs/source/data-model.md document/checklist/security tables
- docs/source/Final SOP - Loan Disbursement V10 (1).pdf
- docs/source/SFPCL_Loan Sanction- Doc & Disbursement-SOP_WhatsLoan-25052026.pdf

## Prototype Reference
- sfpcl-lms/src/pages/documentation/DocumentationHub.tsx
- sfpcl-lms/src/components/loan/DocumentChecklist.tsx
- sfpcl-lms/src/pages/borrower/portal/documents/*

## Screens Involved
None directly.

## Frontend Scope
None. DocumentationHub/security-package wiring remains owned by 008M; do not add mock, reveal, or
hidden cheque actions.

## Backend/API Scope
1. Add §28.6 `POST/GET /api/v1/security-packages/{security_package_id}/blank-dated-cheque/` and
   `PATCH /api/v1/blank-dated-cheques/{blank_dated_cheque_id}/`, accepting exactly member, bank
   account, write-only cheque number, nullable cheque scan document, cheque status, custody
   location, and collected date.
2. Extend the retained 008F2 package/lock. Refresh the blank/cancelled-cheque requirement facts only
   from the application-owned verified bank/cancelled-cheque selector used by 008C2; never infer a
   match from caller text or an account number.
3. Keep one current blank cheque per package. Exact POST/PATCH replay is zero-write; real changes
   retain immutable old/new evidence. `collected` remains Compliance preparation; a distinct Company
   Secretary records terminal `held` custody and its durable §6.3 action.
4. Project masked cheque/custody and canonical cancelled-cheque metadata into checklist/security
   reads without completing the checklist or changing package/disbursement readiness. Do not add the
   generic §28.7 custody-event stream unless the same transaction can make it an unavoidable ledger
   rather than a second mutable source of truth.

## Database/Model Impact
Add §17.5 `blank_dated_cheques` beneath `security_instruments`: one protected package, borrower,
same-member bank account, encrypted cheque number plus indexed hash, nullable protected cheque-scan
file, bounded/indexed `collected`/`held` status, collected date, bounded custody text, immutable
preparer/custodian facts, and protected nullable invocation/return/presentment/amount facts constrained
to null until 011I/013 closure. Preserve one-package-per-application and nullable-only loan-account
integrity; do not duplicate bank accounts or cancelled-cheque rows.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Require `security.package.read` for metadata GET and `security.blank_cheque.manage` for mutation plus
canonical sanctioned package scope. Compliance may prepare/collect; Company Secretary owns held
custody and must remain the retained custodian. Plaintext reveal requires
`security.blank_cheque.reveal`, source-authorised role/object scope, an explicit reveal endpoint or
action, and a separate audit; ordinary GET/audit/version/workflow data is always masked. Other
document/security permissions imply no mutation, reveal, scan download, invocation, or return.

## Audit Requirements
Every real create/change writes attributable audit, version, and workflow evidence with application,
package, member, bank account, cancelled-cheque fact, scan document, masked cheque/hash, preparer,
custodian, request/network/role/team facts. Never log plaintext. Exact replay and denial write no
success evidence; every permitted reveal is separately audited. Projection failure rolls back all
writes.

## Validation Rules
- Member must be the sanctioned borrower; bank account must be the borrower's retained active
  account and must agree with the application-owned verified cancelled-cheque fact. Pending,
  missing, malformed, conflicting, cross-member, or mismatched facts remain blocked.
- Cheque number is write-only, bounded to the source/API six-digit example unless the existing bank
  owner exposes a stricter governed format; encrypt with the repository adapter and use only a
  one-way hash for equality/uniqueness. Ordinary responses show a fixed mask, never recoverable
  fragments unless the security policy explicitly permits them.
- A nullable scan must have exact same-application public-upload legal/security provenance; metadata
  does not grant download. `collected` requires a non-future collected date. `held` requires a
  non-empty bounded custody location and distinct active Company Secretary checker of the exact
  retained Compliance facts.
- Reject `invoked`/`returned`, non-null invocation approval, presented date/amount, and returned date
  with zero writes. Presentation requires later Sanction Committee/Board approval; return belongs to
  closure/NOC.
- Capture never completes the checklist, presents the cheque, changes account/cancelled-cheque
  truth, creates a loan account, or makes the package ready.

## Test Cases
- Create/read/change/replay, strict fields/status/date/custody/number constraints, one current cheque,
  encrypted-at-rest proof, masked ordinary reads, explicit reveal audit, and full retained history.
- Borrower/bank/cancelled-cheque/scan same-application matrices, including missing/pending/conflicting
  verification, cross-member account, duplicate hash, and wrong-file provenance.
- Compliance preparation, distinct Company Secretary custody, read-only/unauthorised/unrelated role
  matrices, and forbidden invoked/returned/presented transitions.
- Checklist/security projections preserve PoA/SH-4/CDSL, completion/verifier/remarks/signatures,
  package status, file access, bank facts, and readiness; projection conflict rolls back every write.
- Five concurrent create/changed-custody attempts retain one current cheque, one terminal custodian,
  and complete attributable winner/zero-success-loser evidence on PostgreSQL, run twice.

## Run-Ahead Sharpening (008H completion, 2026-07-14)

- Extend `security_instruments.SecurityPackage` and reuse its canonical sanction/package lock,
  authority-first HTTP adapter, legal evidence selectors, exact replay/history order, and terminal
  action pattern. Preserve active PoA, SH-4, later CDSL, package status, and readiness truth.
- Use the application-owned cancelled-cheque decision from 008C2; do not query profile cheque tables
  directly from the security module or treat an account-number string as verified authority.
- Keep plaintext cheque values out of serializers, audit/version/workflow JSON, exception text, and
  test snapshots. Invocation/presentment and closure return remain later owners even when a caller
  supplies those fields.

## Architecture-Review Sharpening (2026-07-14 23:49)

- Depend on 008I4 so cheque-number protection reuses the central independently keyed
  `shared.encryption` and `documents.modules.sensitive_data_access` interfaces; do not copy CDSL's
  legacy sealed-token construction or implement local reveal/audit policy.
- Consume legal/cancelled-cheque facts through the corrected 008I3 cross-owner process/interface;
  `security_instruments` must retain no direct `legal_documents` or approvals import.
- The declared PostgreSQL gate must run changed create/custody payloads twice and assert exact
  winner plus zero-success-loser audit/version/workflow/request identities.

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

## 008I3 Completion Sharpening (2026-07-15)

- Add cheque/cancelled-cheque callbacks to `processes.security_instrument_evidence` and the immutable
  evidence contract. `security_instruments` must not import legal, approvals, or application-owned
  cancelled-cheque selectors; the process resolves those owners after package/security locks.
- Reuse `security_instruments.modules.evidence_recorder` for ordinary cheque create/change/custody
  evidence. Raw cheque values are centrally redacted; reveal stays a separate 008I4 sensitive-access
  action and ledger.
- Public views call the process coordinator, and tests reject caller-supplied evidence access plus
  stale/cross-application bank, cancelled-cheque, and scan facts with atomic rollback.
- The twice-run PostgreSQL create/custody matrix asserts one material winner, the exact retained
  workflow id/actor, winner request in audit and version, and no loser request in success evidence.

## 008I4 Completion Sharpening (2026-07-15)

- Encrypt `blank_cheque.cheque_number` only through `shared.encryption.FieldEncryption`; use its
  field-specific lookup hash for replay/duplicate checks and the coordinator-issued central masker
  for every ordinary response/evidence snapshot. Never use `SECRET_KEY`, `members.protected_identity`,
  CDSL token parsing, or a cheque-local crypto adapter.
- Route reason parsing, `security.blank_cheque.reveal`, role/object scope, expiry, rate/re-auth
  decision, decryption, no-store response, and success/denial audit through
  `documents.modules.sensitive_data_access`. The security owner supplies encrypted entity facts;
  the process resolves canonical package/bank/cancelled-cheque scope and serialises concurrent
  reveals under the retained cheque lock.
- Extend the immutable evidence contract with bank/cancelled-cheque/scan callbacks and keep the
  existing `mask_sensitive` callback; tests must reject caller-issued access and any executable
  security import of documents/legal/approvals. Retain 008I4's missing-key, tamper, rotation,
  plaintext-scan, and repeated-reveal regressions for the cheque field.

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
