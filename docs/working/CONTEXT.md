# Project Context

## Product
SFPCL Member Credit Administration and Loan Disbursement Platform. The product supports member/borrower onboarding, loan application intake, credit appraisal, sanction approvals, legal documentation, security tracking, SAP/customer-code setup, disbursement, repayments, interest, monitoring, default/recovery, closure, compliance, reporting, and a member portal.

## Current Repository State
- Frontend prototype: `sfpcl-lms/`, built with React, Vite, TypeScript, Tailwind, React Router, and lucide-react.
- Source-of-truth documents: `docs/source/`.
- Backend/database implementation is not present yet; backend architecture and contracts are described in source docs.
- Demo data currently lives in `sfpcl-lms/src/data/mockData.ts`.

## Target Users and Roles
Borrower/member, Field Officer, Deputy Manager Finance, Credit Manager, Company Secretary, Compliance Team, Sanction Committee, CFO, Senior Manager Finance, Chief Financial Controller, Accounts, Sales Team, Admin/IT, and Auditor.

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
Source docs recommend a modular-monolith backend, Django/Python, PostgreSQL, JWT auth, service-layer business logic, REST APIs, audit events, and external adapters for SAP, bank/payment, email/SMS, CDSL, and file storage. The current codebase is only the frontend prototype.

## Security and Permission Rules
Role-based access and object-level access are central. Sensitive values must be masked except for authorised users. Financial, security, document, disbursement, recovery, and compliance actions require auditability and appropriate maker-checker controls.

## Current Development Status
Ralph has been set up to drive future one-slice AFK implementation. No product feature implementation has been started by Ralph yet.

## Known Constraints
- `docs/source/` is read-only.
- Current app has no real backend/API integration.
- Current package has a build script, but no dedicated lint, typecheck, or real test script yet.
- Future slices that add backend, auth, permissions, database, or financial logic are at least Medium risk and may be High risk.
