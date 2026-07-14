# Project Context

Refreshed by the owner 2026-07-10. This file describes the stable shape of the project; live
queue/progress truth lives in `.ralph/state.json` and `docs/working/HANDOFF.md` — never record
per-run facts here. The architecture review keeps this file current.

## Product
SFPCL Member Credit Administration and Loan Disbursement Platform. The product supports
member/borrower onboarding, loan application intake, credit appraisal, sanction approvals, legal
documentation, security tracking, SAP/customer-code setup, disbursement, repayments, interest,
monitoring, default/recovery, closure, compliance, reporting, and a member portal.

## Current Repository State
- Frontend: `sfpcl-lms/` — React, Vite, TypeScript, Tailwind, React Router, lucide-react. It
  began as the approved visual prototype and is being wired to the real backend one vertical
  slice at a time. Auth shell, navigation, dashboard, notifications, admin, member/KYC,
  Borrower 360, application intake, member portal (auth/dashboard/profile/applications), and the
  Epic 006 credit screens are API-backed. The Epic 007 sanction workbench, sanction/exception
  registers, approval matrix, and loan-policy settings use authenticated backend boundaries;
  corrective slices 007K-007P completed frozen review facts and terminal evidence, S21/S22/S25
  contract evidence, strict shared pagination, full S21 navigation, prototype-layout fidelity,
  and declared trusted-browser contracts. 007Q restored source-required S23/S25 columns and
  reviewable trusted-browser evidence; 007R/007S then preserved legacy approval/register history,
  froze approver identity, closed final-page/stale-response gaps, and restored the fixed register
  pattern. Corrective 007T now consumes real legacy S23 top-level null purpose/risk values safely,
  keeps action/detail/decision refreshes behind the same newest-request authority, and uses only
  production-valid S21 pagination fixtures.
  Epic 008 has started: 008A/008A2 provide a versioned template catalogue with serialized effective
  ranges, retained file-reference provenance, and explicit borrower-template variant resolution;
  008B adds replay-safe generated-document metadata and frozen merge facts. Corrective 008B2 now
  owns generation/reads in the source-defined `legal_documents` boundary, enforces authority inside
  the module, and retains honest nullable-only loan-account integrity. 008B3 proves genuine bounded
  DOCX/PDF rendering for new rows, and 008C creates the initial post-sanction legal checklist
  atomically through the HTTP completion path. Architecture review found that legacy generated rows
  still lack renderer provenance and that lower-level terminal/refresh seams can bypass creation or
  overwrite later completion. Corrective 008B4 now immutably binds current output to its renderer
  contract/file/checksum, labels legacy rows honestly, excludes them from replay/checklist truth,
  and closes absent-parent errors. Corrective 008C2 now makes terminal checklist creation
  structurally unavoidable, recomputes canonical frozen approval facts, preserves completion-owned
  evidence, separates applicability/linkage ledgers, consumes application-owned cheque facts, and
  centralises checklist read scope before stamp/notary work. 008D then added locked stamp/notary
  current rows, projections, history, and a genuine changed-submission race; 008E added signature
  capture, mismatch evidence, and atomic Bank Verification Letter applicability. Independent review
  found that Compliance can still record checker-owned adverse stamp/notary outcomes and can erase
  an unresolved same-signer mismatch through ordinary capture; signature resolution also leaks
  absent-versus-inaccessible ids and lacks its promised race. Corrective 008D2 restores legal
  evidence ownership and maker-checker verification; corrective 008E2 now closes signature identity,
  lifecycle, nondisclosure, action-contract, and concurrency gaps. 008F adds the locked security
  package and PoA workflow; 008G verifies conditional tri-party agreements only from frozen true
  subsidiary applicability and exact canonical borrower/nominee signatures, while preserving
  checklist, package, repayment, and readiness truth. The full real M05-to-Term-Sheet
  path remains configuration-blocked until governed owners exist for the missing sanction terms;
  renderer fixtures must not be presented as that end-to-end path.
  Other later module screens (documentation, disbursement, servicing, compliance, reports, task
  inbox) still render `src/data/mockData.ts` until their owning wiring slices run —
  `docs/working/PROTOTYPE_GAP_REPORT.md` and
  `PROTOTYPE_INVENTORY.md` are the authoritative ledger.
- Backend: `sfpcl_credit/` — Django modular monolith (identity, members, applications, credit,
  approvals, documents, legal_documents, workflows, communications, dashboard, configurations,
  scheduler, tracer)
  with JWT auth, role and object-level permissions, audit/workflow events, versioned
  configuration, document storage adapter, and seeded demo users.
- Quality gates run on every slice: frontend build, typecheck, ESLint, vitest; backend Django
  check, migration sync, and the full test suite under coverage with a hard floor
  (`coverage_fail_under` in `.ralph/config.yaml`). Playwright e2e + visual regression harness
  lives in `sfpcl-lms/e2e/`. Concurrency-critical credit paths have an authoritative PostgreSQL
  acceptance harness (`sfpcl_credit.config.postgres_test_settings`); the routine gate suite runs
  SQLite until the planned PostgreSQL flip at the Epic 009 boundary.
- Source-of-truth documents: `docs/source/` (read-only). Distilled extracts live in
  `docs/working/digests/`; owner-curated section maps in `docs/working/maps/`.

## Target Users and Roles
Borrower/member, Field Officer, Deputy Manager Finance, Credit Manager, Company Secretary,
Compliance Team, Sanction Committee, CFO, Senior Manager Finance, Chief Financial Controller,
Accounts, Sales Team, Admin/IT, and Auditor.

## Core Workflows
1. Member and KYC verification.
2. Loan application intake and completeness check.
3. Eligibility, loan limit, appraisal, and credit review.
4. Sanction committee approval and special-case approvals.
5. Documentation, security instruments, stamping, notarisation, and final sign-offs.
6. SAP customer-code setup and payment disbursement.
7. Repayments, subsidiary deductions, interest accrual, invoices, and capitalisation.
8. Monitoring, reminders, default, recovery, closure, NOC, and archive.
9. Compliance dashboards, statutory registers, audit logs, reports, and member portal self-service.

## Technical Direction
Implemented as the source docs direct: modular-monolith Django/Python backend, REST APIs with the
standard envelope (`api-contracts.md` §6-8), service-layer business logic behind deep-module
seams, JWT auth, audit events on critical actions, and adapter shells for SAP, bank/payment,
email/SMS, CDSL, and file storage (real transports arrive with their epics or at integration
cutover). PostgreSQL is the production database target.

## Security and Permission Rules
Role-based access and object-level access are central. Sensitive values must be masked except for
authorised users, with reveals audited. Financial, security, document, disbursement, recovery, and
compliance actions require auditability and appropriate maker-checker controls.

## Known Constraints
- `docs/source/` is read-only; on any conflict, source docs win over prototype and digests.
- Frontend changes are bound by `docs/working/FRONTEND_DESIGN_RULES.md` — the prototype's visual
  system is fixed; screens the documents require but the prototype lacks are composed from
  existing components.
- Slices touching auth, permissions, money, or compliance are at least Medium risk and often High
  risk; all run under the owner's standing approval with the veto model.
- Agent sandboxes have no network: the orchestrator pre-installs pinned dependencies; agents never
  run pip/npm install for new packages beyond pinning them.
