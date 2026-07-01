# API Screen Map

The current implementation is a frontend prototype with mock data. Future slices should map each prototype screen to real API contracts before replacing mock data.

| Screen/Route Area | Purpose | Data Required | API Endpoints Needed | Actions | Required States | Prototype Reference |
|---|---|---|---|---|---|---|
| Staff login and dashboard | Role-specific entry | User, roles, tasks, alerts, KPIs | Auth, dashboard, notification APIs | Login, switch role in demo, navigate | Loading, invalid login, unauthorized | `LoginScreen`, `Dashboard`, `AppShell` |
| Applications | Intake and queue management | Member, application, KYC, documents | Application and member APIs | Create, submit, review, mark complete | Draft, submitted, deficient, rejected | `ApplicationList`, `NewApplication`, `ApplicationDetail` |
| Members and Borrower 360 | Member lookup and profile | Member, borrower, nominees, loans | Member/profile APIs | Search, view, inspect history | Empty search, unauthorized, masked fields | `MemberDirectory`, `MemberProfile`, `Borrower360` |
| Appraisal | Eligibility and loan limit | Supply history, shareholding, KYC, appraisal | Appraisal and loan-limit APIs | Calculate, save note, submit review | Incomplete eligibility, boundary errors | `AppraisalWorkbench` |
| Sanction | Committee review and decisions | Cases, approvals, exception records | Sanction and approval APIs | Approve, reject, ask clarification | Approval matrix, special case | `SanctionWorkbench` |
| Documentation | Document/security readiness | Documents, securities, checklist, audit | Documentation and security APIs | Upload, verify, sign off | Missing docs, mismatch, blocked disbursement | `DocumentationHub`, loan document components |
| Disbursement and CFC | SAP setup and payment release | SAP code, readiness, payment, UTR | SAP/disbursement/payment APIs | Request SAP, initiate payment, authorize | SAP missing, CFC blocked, payment pending | `DisbursementHub`, `PaymentAuthorisationHub` |
| Loan accounts and repayments | Servicing and ledger | Account, schedule, repayments, invoices | Loan account and repayment APIs | Post repayment, allocate, export | Empty ledger, validation errors | `LoanAccount360`, `RepaymentsHub`, `InterestManagement` |
| Monitoring/default/closure | Risk and end-of-life workflows | DPD, reminder, default, recovery, NOC | Monitoring, default, closure APIs | Remind, approve recovery, close, issue NOC | Blocked recovery, unpaid balance | `MonitoringDashboard`, `DefaultRecoveryHub`, `LoanClosureHub` |
| Compliance/registers/reports | Control and audit visibility | Registers, audit events, compliance trackers | Compliance, audit, report APIs | Review, export, filter | Masked export, no data, error | `ComplianceDashboard`, `RegistersHub`, `ReportsMIS` |
| Member portal | Borrower self-service | Profile, applications, docs, loans, repayments | Member portal APIs | Apply, upload, view status, support | OTP, document deficiency, payment info | `BorrowerPortal`, `MP*` screens |
