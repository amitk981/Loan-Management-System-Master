# Project Context

This file contains only stable repository and product context. Live queue truth belongs in
`.ralph/state.json`; the current execution boundary belongs in `docs/working/HANDOFF.md`; historical
reviews remain in Git and `docs/working/REVIEW_FINDINGS.md`. Architecture reviews keep this summary
truthful without appending run history.

## Product

SFPCL Member Credit Administration and Loan Disbursement Platform. It covers member onboarding,
loan intake, credit appraisal, approvals, legal documentation, security tracking, SAP/customer-code
setup, disbursement, servicing, monitoring, default/recovery, closure, compliance, reporting, and a
member self-service portal.

## Repository Shape

- `sfpcl_credit/`: Django modular monolith. Implemented owners include identity, members,
  applications, credit, approvals, documents, legal documents, security instruments, workflows,
  communications, configuration, SAP workflow, loans, disbursements, finance, dashboard,
  scheduling, and audit/tracing.
- `sfpcl-lms/`: React + TypeScript + Vite frontend grown from the approved prototype. Completed
  epics progressively replace `src/data/mockData.ts`; the prototype inventory and gap report are
  the binding ledger for remaining wiring.
- `docs/source/`: read-only product truth. Use the owner-curated capability maps to locate exact
  sections and save bounded extracts in `docs/working/digests/`.
- `docs/slices/`: dependency-ordered vertical work. Slice status files and `.ralph/state.json`, not
  this document, determine what Ralph may execute.
- `.ralph/runs/`: independently validated run evidence. Raw agent transcripts are retained outside
  the candidate with bounded retention; committed evidence contains compact summaries and hashes.

## Current Delivery Boundary

- Epics 002–008 established the platform, origination, approval, documentation, security, member
  portal, and their corrective integrity contracts.
- Epic 009's SAP setup/disbursement boundary is complete, including its terminal owner/evidence
  correction and hosted staff/member acceptance.
- Epic 010 servicing is active. Schedule/ledger reads, receipt capture and allocation, statement
  reconciliation, effective-rate versioning, interest invoice/accrual/capitalisation, DPD, and
  reminder and quarterly-MIS foundations are implemented. Rate-current-date and interest-policy/
  reclassification closures are complete. A grouped terminal-repair episode and interest-portfolio
  identity and sensitive global-search corrections remain durable, but the owner-frozen 39-slice
  product baseline executes first. One consolidated architecture review follows that baseline;
  accepted corrections then resume before release completion.
- The remainder of Epics 010–012 owns servicing/repayment, monitoring/default/compliance, reporting,
  operational hardening, end-to-end acceptance, and final release evidence.
- Current slice and dependency facts must be read from `docs/working/HANDOFF.md` and the selected
  slice; do not infer them from this summary.

## Binding Technical Direction

- Django REST Framework APIs use the standard response/error/pagination contracts recorded in
  `docs/working/API_CONTRACTS.md`.
- PostgreSQL is the production database. Concurrency-, locking-, migration-, and financial-
  integrity promises require declared PostgreSQL acceptance evidence. Routine validation uses
  independently mapped impacted tests for localized Low/Medium changes and retains the complete
  configured backend suite and coverage floor for fail-closed classes and periodic checkpoints.
- Business rules live behind the module that owns their source capability. Cross-module
  coordinators exchange immutable evidence/facades rather than importing another owner's private
  models or policy.
- Critical transitions retain immutable actor, role, input, source-evidence, timestamp, and audit
  truth. Mutable labels or caller-supplied projections never prove terminal workflow state.
- External systems use explicit adapters. Manual/fake transports must report their limitations
  honestly and must not claim provider success they did not perform.
- Sensitive values are encrypted at rest, masked by default, revealed only through central
  authorised policy, and audited on access.

## Frontend Direction

- `docs/working/FRONTEND_DESIGN_RULES.md` is binding. Reuse the prototype's components, layout,
  colours, typography, and interaction patterns; do not redesign while wiring real APIs.
- Every owned screen must represent loading, empty, error, unauthorised, validation, and success
  states truthfully.
- A wiring slice removes mock reads only for its declared screens, preserves shared transport and
  permission seams, and supplies deterministic browser/visual evidence when declared.

## Roles and Workflows

Primary roles include borrower/member, Field Officer, Deputy Manager Finance, Credit Manager,
Company Secretary, Compliance Team, Sanction Committee, CFO, Senior Manager Finance, Chief
Financial Controller, Accounts, Sales, Admin/IT, and Auditor.

The end-to-end workflow is:

1. Member/KYC verification and loan application intake.
2. Completeness, eligibility, appraisal, and credit review.
3. Sanction/exception approval and governed term freeze.
4. Legal documentation, security instruments, stamping/notarisation, and ordered sign-offs.
5. SAP/customer setup, payment authorisation, transfer, account activation, and borrower advice.
6. Repayment allocation, subsidiary deductions, interest, invoices, monitoring, and reminders.
7. Default/recovery, settlement/closure, security release, NOC, compliance, and archive.
8. Reports, dashboards, registers, audit evidence, and member self-service throughout.

## Quality and Automation Invariants

- Ralph runs one slice in an isolated worktree, validates independently, commits only green work,
  fast-forwards `staging`, and pushes it. Only the owner promotes `staging` to `main`.
- Backend/business logic uses TDD with retained red/green evidence. Frontend changes run focused
  tests, typecheck, lint, build, and declared browser acceptance.
- Localized low/medium-risk backend candidates run an independently derived impacted regression pack.
  High-risk, shared/schema/infrastructure, ambiguous, broad, rename/delete, every-fourth-slice,
  and release checkpoints retain the complete suite and configured coverage floor.
- Six backend coverage workers are the measured optimum on the current eight-core host; increasing
  workers or running concurrent Ralph loops adds contention and is not supported.
- Protected paths, source documents, frozen-candidate hashes, diff/dependency limits, repair
  signatures, migration sync, and queue semantics fail closed.
- Architecture work is role-pure. Fixed-spec review and independent gates apply to every slice;
  periodic and Epic/project-boundary discovery remain mandatory, while terminal closure verification
  may inspect only inherited identities and reproducers. Significant discovery means Critical/High
  correctness, security, financial/data integrity, or binding source-contract risk.
- During the explicit owner-maintainer completion baseline recorded on 2026-07-22, non-Critical
  architecture barriers are accumulated rather than executed. Only the exact frozen baseline is
  selectable until it completes; one consolidated discovery checkpoint then runs before corrections.
- Terminal finalizers retain every grouped Root ID. An executable recurrence receives one active
  bounded repair episode on that same finalizer contract. Product gates leave it awaiting an
  independent review of every grouped root; a later genuine regression opens a new audited episode,
  never generation one/three, and cannot discard unrelated validated review findings. After the
  configured episode cap, recurrence becomes a release-blocking quarantine while unrelated slices run;
  later bound closure evidence archives and removes that blocker without manual state edits.

## Context Discipline

- Read fixed bootstrap files once, then the selected slice, its parent epic, the digest's shared
  invariants, and only the selected slice section.
- Locate source material with `rg` and capability maps. Never load all of `docs/source/` by default.
- Prefer batched searches and targeted diff hunks; do not repeatedly emit a growing full diff.
- Digests stay below roughly 300 lines. Durable history remains available through Git and linked
  archives instead of being repeated in every run's active context.

## Never Infer

- Do not invent eligibility formulas, monetary thresholds, approval authority, compliance rules,
  provider success, or personal/financial fixture data.
- When the source is silent, follow `docs/working/DECISION_POLICY.md`: use a boring standard default
  only where permitted, record the assumption, and keep any unstated business rule configurable or
  explicitly blocked.
