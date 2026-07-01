# Feature Matrix

| Feature | Business Goal | User Value | Screens | Roles | Backend Entities | API Contracts | Permissions | Tests Required | Priority | Source Reference | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Ralph Bootstrap Verification | Verify AFK automation foundation | User can run one safe command and resume from repo state | None | Maintainer | None | None | Repo automation permissions | Preflight, artifact validation, build | P0 | Ralph v2.1 requirements | Not Started |
| Auth and Role Shell | Secure staff/member entry and role-specific navigation | Users see only relevant work | Login, dashboard, sidebar, member portal auth | All roles | User, Role, Permission, Session | Auth APIs | RBAC, masking | Route guard, permission rendering | P0 | `auth-permissions.md`, `screen-spec.md` | Prototype only |
| Loan Origination | Capture and review applications | Staff and members can submit complete applications | Applications, new application, completeness | Field Officer, Credit, Finance, Borrower | Member, LoanApplication, KYC, Document | Application APIs | Create/view/check application | Form and workflow tests | P0 | `functional-spec.md`, `screen-spec.md` | Prototype only |
| Appraisal and Sanction | Enforce eligibility, limits, and approval rules | Clear credit decision workflow | Appraisal, sanction, special case | Finance, Credit, Sanction, CFO, Directors | Appraisal, LoanLimit, SanctionDecision, Exception | Appraisal and sanction APIs | Approval matrix | Boundary and approval tests | P0 | `functional-spec.md`, `implementation-roadmap.md` | Prototype only |
| Documentation and Security | Complete legal/security package before disbursement | Reduces disbursement risk | Documentation hub, document checklist, security registers | CS, Compliance, Finance | Document, SecurityInstrument, Checklist | Documentation APIs | Documentation management | Gate and checklist tests | P0 | SOP PDFs, `screen-spec.md` | Prototype only |
| Disbursement | Ensure SAP setup, CFC authorization, and payment evidence | Controlled release of funds | Disbursement, CFC authorization | Finance, CFC, CFO | SapRequest, Disbursement, PaymentAdvice | Disbursement APIs | Disbursement initiation/authorization | Gate and payment tests | P0 | `functional-spec.md`, SOP docs | Prototype only |
| Servicing and Monitoring | Track repayment, interest, DPD, and reminders | Operational visibility | Loan account, repayments, interest, monitoring | Accounts, Credit, CFO | LoanAccount, Repayment, InterestAccrual, DPD | Servicing APIs | Account and monitoring permissions | Financial calculation tests | P1 | `data-model.md`, `test-plan.md` | Prototype only |
| Default, Recovery, Closure | Manage delinquency, recovery approval, NOC, and archive | Controlled lifecycle completion | Default, recovery, closure | Credit, CFO, CS, Sanction | DefaultCase, RecoveryAction, Closure, NOC | Default/closure APIs | Recovery/closure permissions | Approval and archive tests | P1 | `functional-spec.md`, `screen-spec.md` | Prototype only |
| Compliance and Reports | Provide statutory trackers, audit, and MIS | Compliance and management visibility | Compliance, registers, reports | Compliance, CFO, CS, Auditor | ComplianceTask, Register, AuditEvent, Report | Compliance/report APIs | Auditor and export masking | Report and audit tests | P1 | `auth-permissions.md`, `api-contracts.md` | Prototype only |

## Slice Backlog Mapping

| Slice | Release Coverage | Primary Outcome |
|---|---|---|
| 002 | R1 Sprint 1 | Platform backend scaffold, JWT auth, RBAC, protected frontend shell |
| 003 | R1 Sprint 2 | Audit, document storage, configuration, dashboard/task foundations |
| 004 | R2 Sprint 3 | Member, KYC, nominee, witness, shareholding, land/crop profile master |
| 005 | R2 Sprint 4 | Application intake, application documents, completeness, deficiencies |
| 006 | R2 Sprint 5-6 | Eligibility, active member rules, loan limit, appraisal, credit review |
| 007 | R3 Sprint 7-8 | Approval matrix, sanction workflow, exception registers |
| 008 | R4 Sprint 9-11 | Documentation, templates, legal/security package, checklist approvals |
| 009 | R5 Sprint 12-13 | SAP workflow, loan account, disbursement readiness/payment |
| 010 | R6 Sprint 14-16 | Repayments, interest, monitoring, member servicing views |
| 011 | R7 Sprint 17-19 | Default, recovery, closure, compliance, grievances |
| 012 | R8 Sprint 20-23 | Reports, exports, audit explorer, hardening, UAT readiness |
