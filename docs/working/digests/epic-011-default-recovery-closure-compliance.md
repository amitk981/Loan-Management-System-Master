# Epic 011 Digest — Default, Recovery, Closure, and Compliance

This is a bounded implementation digest. The cited `docs/source/` sections remain authoritative.

## Shared architecture and controls

- Keep policy in the source-shaped modules: `defaults.modules.default_workflow`,
  `recovery.modules.recovery_workflow`, `closure.modules.loan_closure`, and the three
  `compliance.modules.*` services. Views, tasks, and UI must call these interfaces rather than
  duplicate date, amount, authority, or transition rules. [codebase-design §§18.3-19.4]
- Every high-control transition is atomic, permission checked, object scoped, and append-only
  audited. Return the standard response/error envelopes and `available_actions`; hiding a button is
  never authorization. [api-contracts §§5-10, 35-38; auth-permissions §§20.3, 23-25, 30]
- Preserve one canonical record per loan/case/period where the data model declares `FK/UQ`.
  Exact request replay must not create duplicate cases, notes, decisions, NOCs, returns, archives,
  tasks, or period calculations. [data-model §§21-24]
- Files use the existing document upload/download owner and inherit category sensitivity. Recovery
  evidence, KYC files, Board minutes, legal opinions, acknowledgements, and archive downloads must
  remain restricted and downloads audited. [api-contracts §26; auth-permissions §§19.4, 21-22;
  security-privacy §§23-24, 34]
- Internal Auditor has broad read-only/audit sampling access, never mutation authority. Borrower
  access is self-only. Closed records are read-only except the explicit NOC, security-return, and
  archive actions. [auth-permissions §§19-20, 26.7; product-requirements §11.28]
- Scheduled processors call the same domain services as HTTP, use recorded job outcomes, and are
  safe to retry. No job may silently advance a financial, recovery, or compliance state.
  [implementation-roadmap §16.3; codebase-design §34.3]

## Default and recovery invariants

- A missed scheduled principal repayment opens at most one default case; its grace interval starts
  on the due date and ends three calendar months later. Payment during grace resolves the workflow;
  expiry requires an assessment. [product-requirements §11.26; user-flows §31; data-model §21.1]
- Only the Credit Assessment Team assesses intentionality after grace expiry. Non-intentional
  classification may receive one extension of exactly one year; the Credit Manager owns the
  Extension Note and retained loan-file document. Detailed classification criteria remain
  configurable because the SOP does not define them. [functional-spec M12-FR-004-008;
  component-spec §§17.3-17.4; auth-permissions §20.3]
- A Non-Payment Note is allowed only after an eligible unpaid extension expires. It freezes current
  principal/interest, reasoning, classification, evidence, and recommendation before submission to
  the configured Sanction Committee/Board route. [api-contracts §§35.6-35.7; data-model §21.4]
- Recovery execution requires the matching approved decision, action type, usable security, CS or
  authorised executor, evidence, and audit. It must preserve call/visit/fair-conduct evidence and a
  grievance route. [product-requirements §11.27; security-privacy §23; test-plan §13.18]

## Closure invariants

- Readiness derives principal, interest, charges, ledger/reconciliation, and pending recovery facts;
  callers cannot assert readiness. Financial close is blocked while any amount/blocker remains.
  [api-contracts §§36.1-36.2; screen-spec S58; test-plan §13.19]
- NOC follows a full-repayment closure and is issued by Compliance/CS through the existing document
  and communication owners. Security return covers SH-4, blank cheque, PoA disposition, and CDSL
  unpledge with acknowledgement. [functional-spec M13-FR-004-009; api-contracts §§36.3-36.4]
- Archive records retain physical/digital locations and a server-calculated date at least eight
  years after closure. Destruction is future/governed work, not implied by eligibility.
  [data-model §22.4; component-spec §18.5]
- Source conflict to preserve visibly: API §36.2 reports `loan_account_status=closed` after financial
  close, while functional-spec M13-FR-011/user-flow §33 say terminal closure waits for the full
  checklist. Implement financial close plus controlled post-close tasks without claiming
  `Fully Closed and Archived` until NOC, applicable security return, and archive are complete.

## Compliance and grievance invariants

- A control has code, legal basis, type, frequency, owner role, evidence requirement, risk, and
  status. Generated tasks have period, due date, assignee, optional reviewer, state, evidence, and
  audit. Evidence review is maker-checker; accepted comments/evidence are immutable unless reopened
  through an audited future policy. [data-model §§23.1-23.3; security-privacy §34.2]
- Section 186 calculates `60% * (paid-up capital + free reserves + securities premium)` and
  `100% * (free reserves + securities premium)`, uses the higher amount, and flags excess exposure.
  NBFC triggers only when both asset and income ratios are strictly above 50%; one ratio alone is a
  warning/no trigger. [api-contracts §§37.5-37.6; test-plan §§21.2-21.3]
- Re-KYC is due every two years, with due/30-day-warning/overdue visibility. It reuses the governed
  member/KYC evidence and verification owners; the tracker does not mutate KYC facts directly.
  [user-flows §34; component-spec §19.3; test-plan §21.4]
- The annual money-lending review stores state, exemption/applicability, restricted legal opinion,
  Board note, CS owner, and period. Stamp-duty facts remain owned by Epic 008 and are consumed rather
  than duplicated. [api-contracts §37.7; data-model §§23.7-23.8]
- Grievances capture member, optional loan/application, category, description, channel, owner, due
  date, supporting evidence, status, resolution, borrower notice, and audit. Recovery grievances
  link to the applicable loan/default and receive fair-practice attention. [functional-spec M15;
  user-flows §36; data-model §24.3]

## Slice-ready contracts

### 011A — Default case opening
- Own the `default_cases` model, idempotent missed-principal detector, POST open, GET detail/list, and
  `default.case_opened` evidence. Consume 010 repayment/schedule/DPD truth; never accept a caller-made
  outstanding result. [api-contracts §§35.1-35.3; data-model §21.1]

### 011B — Grace tracking and assessment
- Own grace date/state processing, payment-during-grace resolution, expiry processor, assessment
  model/API, and Credit Assessment authority. Test month-end/leap dates and premature/duplicate
  assessment. [api-contracts §35.4; test-plan MOD-DEF-002-006]

### 011C — Extension Note
- Own one-year extension eligibility, one note per case, retained document reference, configured
  approval status, expiry processor, and exact replay. Reject intentional/unclear, pre-expiry,
  already-paid, duplicate, and wrong-scope cases. [api-contracts §35.5; data-model §21.3]

### 011D — Non-Payment Note
- Own draft/frozen note, source-derived balances, document generation, submit transition, and
  Sanction Committee task. Reject unexpired/no-extension/paid cases and post-submit mutation.
  [api-contracts §§35.6-35.7; screen-spec S55]

### 011E — Recovery decision approval
- Compose the existing approval matrix/case owner with one recovery decision; decision must match a
  submitted note and terminal approved case. Reject self-approval, rejected/pending approval,
  changed action, and duplicate decision. [api-contracts §35.8; auth-permissions §§18, 20.3]

### 011F — Recovery action execution
- Own initiate/complete APIs and the S57 execution surface for SH-4/CDSL/cheque/legal actions. Call
  the existing security owners, require evidence and approved matching action, update recovery
  amounts without inventing ledger posting, and retain fair-conduct logs. [api-contracts
  §§35.9-35.10; screen-spec S57; security-privacy §23]

### 011G — Closure readiness and financial close
- Own server-derived readiness and close APIs/record. Return named blockers; block outstanding,
  unresolved ledger/recovery, duplicate close, non-authority, and direct closed-record mutation.
  Create explicit downstream NOC/security/archive requirements. [api-contracts §§36.1-36.2;
  product-requirements §11.28]

### 011H — NOC issuance
- Own one NOC per eligible full-repayment closure, required document/signatory/delivery facts, audit,
  and communication handoff. Reject pre-close, recovery/write-off unless source eligibility is
  proven, foreign document, duplicate, and unauthorised issue. [api-contracts §36.3; screen-spec S59]

### 011I — Security return and CDSL unpledge
- Own one security-return aggregate with item applicability, custody, acknowledgement, SH-4/cheque/
  PoA outcomes, and detailed PSN/URF/DP unpledge evidence. Do not mark complete while an applicable
  item is pending or rejected. [api-contracts §36.4; screen-spec S60; component-spec §§18.3-18.4]

### 011J — Archive and retention
- Own one archive record after closure prerequisites, both locations where available, server-derived
  minimum retention, restricted manifest/read, and audit. Reject early dates and archive-before-
  closure/security completion. [api-contracts §36.5; data-model §22.4]

### 011K — Compliance foundation
- Own controls, frequency-based task generation, evidence submit/review, escalation/overdue state,
  and annual money-lending review record. Reuse 008 stamp evidence and existing document/jobs/audit
  owners. [api-contracts §§37.1-37.4, 37.7; functional-spec M14]

### 011L — Section 186 and NBFC calculators
- Own quarterly, unique, Decimal calculations and review evidence. Test zero denominators, exact 50%
  boundaries, one-ratio warnings, higher-of-two Section 186 limit, breach flags, and concurrent
  duplicate creation. [api-contracts §§37.5-37.6; test-plan §§21.2-21.3]

### 011M — KYC/re-KYC tracker
- Own `kyc_reviews`, two-year due-date generation, due/overdue queries and reminders, linking back to
  governed KYC verification. Test FPC/individual completeness and restricted evidence access.
  [data-model §23.6; user-flows §34; test-plan §21.4]

### 011M2 — Portal KYC correction
- Preserve the existing slice decision gate: either full evidence-backed correction request through
  governed verification, or an explicit owner-approved deferral with no edit affordance. Never
  mutate member/KYC records from the portal request. [screen-spec-member-portal KYC screens]

### 011N — Grievance workflow
- Own staff create/list/resolve, assignment/TAT/overdue escalation, supporting document, borrower
  notification, and audit. Resolve requires a nonblank summary; self-scope is supplied to 011NA.
  [api-contracts §38; functional-spec M15; test-plan §21.6]

### 011NA — Member communication surfaces
- Preserve the existing slice: self-only notices/downloads, grievance submit/status, notifications,
  help content, and closure/NOC/security status using 003/005/007/010/011 owner APIs.

### 011O — Auditor read-only views
- Add auditor GET/query scope across Epic 011 records and a read-only existing-pattern UI. Mutation
  actions and `available_actions` are absent; every POST/PATCH remains 403 and restricted downloads
  remain audited. Audit observations/export tooling stays in Epic 012. [auth-permissions §§15.11,
  19-20, 26.7; security-privacy §34]

### 011P — Staff frontend wiring
- Preserve the existing final owner for S53-S68 staff screens and mock removal. Consume prior APIs;
  do not reimplement workflow rules in React. [screen-spec S53-S68; API_SCREEN_MAP]

## Required cross-slice regression evidence

- Targeted service/API/permission/audit tests plus reverse-consumer tests named in each slice.
- Migration sync and forward/reverse/reapply coverage for new schemas; PostgreSQL races for unique
  case/note/decision/closure/NOC/return/archive/period rows or scheduled claims.
- Full backend coverage gate, frontend typecheck/lint/tests/build when touched, and real-browser
  screenshots for 011F/011M2/011NA/011O/011P. [test-plan §§13.17-13.20, 14.11, 16.14-16.17]
