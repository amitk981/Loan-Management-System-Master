# Epic 009 Digest — SAP, Loan Account, and Disbursement

Sources distilled while sharpening 009A on 2026-07-15: `implementation-roadmap.md` §14,
`integrations.md` §8/§33.1, `data-model.md` §19.1-19.2, `api-contracts.md` §29.1, and
`functional-spec.md` BR-047-BR-050/M07-FR-001-M07-FR-010.

## Architecture Review 2026-07-16 07:41 — SAP Delivery, Replay, Audit, and Owner

- Source codebase-design §§16.1/20.3-20.4/36.2 assigns SAP policy to
  `sap_workflow.modules.sap_customer_profile` behind one Manual/Fake/Future adapter contract. 009A/B
  currently implement it directly in `finance`; 009B2 restores the source owner before loan-account
  and readiness code consume SAP truth.
- Integrations §8.1 says the official Finance handoff includes the Excel details. An executable probe
  found a row marked `sent` while the communication remained pending, had no attachment/capability,
  linked only to completion, and the frozen assignee received 403 for the workbook. 009B2 makes exact
  checksum-verified Annexure delivery/assignee read prerequisite to `sent`.
- 009B reuse completion retains only the code link, so optional values omitted on first completion
  can be added later and still receive replay 200. 009B2 freezes the canonical accepted input/digest
  and makes any later supplied/omitted difference a zero-write 409.
- Auth-permissions §30 requires `sap.customer_code_created` plus role/team at action time. 009B2
  aligns create/send/confirm/reuse audit truth without exposing identity/bank/workbook plaintext.
- 009C now uses `loans.modules.loan_account_lifecycle` and the public SAP selector; 009D uses
  `disbursements.modules.disbursement_readiness`, matching codebase-design §§16.2-16.3.

## 009A SAP Customer Profile Request

- MVP is manual/file-first. After terminal sanction, a Credit Manager creates the request and a
  genuine Excel/Annexure-I artifact for an active Senior Manager Finance assignee; direct SAP API
  integration is future scope.
- `POST /api/v1/loan-applications/{id}/sap-customer-profile-request/` returns the request id,
  `draft` status, Excel file id, and assignee. Canonical borrower/application/sanction facts should
  be server-owned even though the illustrative API body lists them, so a caller cannot forge the
  source evidence.
- Required frozen facts are application number, legal name/type, PAN, registered address, folio,
  sanctioned amount/date, individual-only Aadhaar, and optional email/mobile/current verified-bank
  last-four plus IFSC. Full sensitive values are encrypted at rest and excluded from ordinary
  projections/log/audit evidence.
- The table stores application/member, status (`draft/sent/completed`), requester, assignee, frozen
  fields, linked Excel file, and sent/completed timestamps. Source idempotency identity is
  application plus active request; retries/concurrent creates must not duplicate request, file,
  workflow, or audit facts.
- INT-SAP-001/002/006 and R5-AC-001/002 require post-sanction creation, complete Excel details, and
  audit evidence. Code confirmation, duplicate-code blocking, reuse, and readiness belong to 009B+
  and must not be claimed by 009A.
- Source schema says Aadhaar is non-null while the integration payload says “individual only” and
  the platform supports FPC borrowers. Treat Aadhaar as conditionally required/encrypted for
  individuals and absent for FPCs; do not fabricate an FPC Aadhaar value.

## 009B SAP Request Send, Confirmation, and Reuse

- API §29.2 and integrations §8.2 make `draft -> sent` a real boundary: the Credit Manager sends the
  retained Excel request to its frozen Senior Manager Finance assignee through the communication/
  task adapter. No later slice owns this transition, so 009B must deliver it before confirmation.
- API §29.3 uses `/complete/` and fields `sap_customer_code`, optional `sap_vendor_code`,
  `created_at_sap`, `confirmation_document_id`, and `confirmation_notes`. Preserve this source
  vocabulary instead of inventing a `/confirm/` route or renamed payload fields.
- BR-047/048/050 and M07-FR-001/002/007/008 require one member-level unique active code, assigned
  Senior Manager Finance confirmation, and reuse instead of duplicate creation. Global code
  uniqueness and one-active-code-per-member are database-backed; request/code races retain exact
  winner evidence and zero loser artifacts.
- The source ties reuse to an existing outstanding loan, but Epic 009 has not yet created the loan-
  account owner and OC-019 leaves multi-active-loan semantics open. Reusing an already active code
  for the exact member is conservative; do not infer outstanding state from identity text or invent
  loan statuses. 009C+ may add governed outstanding-loan linkage without rewriting code history.
- Confirmation evidence is optional but recommended and must be a restricted request/application-
  scoped file. Send/complete/read responses and all audit/workflow/communication facts exclude the
  frozen Aadhaar, PAN, address, bank, storage, and signed-capability values.

## 009C Loan Account Creation

- API §30.1 fixes `POST /api/v1/loan-applications/{id}/create-loan-account/` with exactly
  `sanction_decision_id` and `loan_account_number`. Data-model §18.1 makes application and account
  number unique and requires the exact sanction link, positive amount, member, status, balances,
  loan type, rate type, and optional active SAP-code link.
- Initial `loan_account_status` is source vocabulary `sanctioned`; activation belongs only to
  successful disbursement (M08-FR-008). Before transfer, disbursed amount and all outstanding
  balances remain zero so account creation cannot claim a funded receivable.
- Create `loan_terms` atomically from the current terminal sanction/frozen review package: safe
  borrower/nominee/shareholding snapshots, short/long facility type, amount, purpose, governed
  interest/repayment/penalty/charge/security/dispute facts, and current Term Sheet/Loan Agreement
  links where their owner proves them. Missing required governed terms fail closed; do not fill the
  known terminal-sanction nulls with guessed rates or dates.
- `finance.loan_account.create` is source-defined Critical authority but no source role is granted
  it (A-121). Implement exact permission/object checks and explicit-grant tests without seeding a
  role grant. Replay is application + exact sanction + exact normalized account number; changed
  repeats conflict and PostgreSQL races retain one account/terms/status/audit/workflow winner.

## 009D Disbursement Readiness

- API §31.1 fixes a read-only
  `GET /api/v1/loan-accounts/{loan_account_id}/disbursement-readiness/` projection with one aggregate
  flag and ordered pass/fail checks. The API example names sanction, documentation, security, SAP,
  and verified bank; integrations §9.4 and M08 expand those into the complete pre-initiation gate.
- Consume current facts through the approval, legal/checklist, security, application-bank, SAP,
  loan-account, and configuration owners. Conditional exception/general-meeting, SH-4/CDSL, and
  signature checks must never disappear from the response or be inferred from copied status JSON.
- The source workflow orders readiness before Senior Manager Finance initiation and CFC
  authorisation. Those are 009E/009F actions, not readiness rows or synthetic pass conditions; the
  readiness GET creates no payment, approval, balance, account-state, task, communication, audit, or
  borrower truth.
- Fail closed when current relationships/evidence are absent, stale, cross-object, or incoherent.
  If no governed active source-bank configuration owner exists yet, return an honest failed
  `source_bank_account_configured` check rather than inventing an account.
