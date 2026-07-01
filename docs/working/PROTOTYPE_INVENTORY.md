# Prototype Inventory

## Location
`sfpcl-lms/`

## Stack
React 19, Vite, TypeScript, Tailwind CSS, React Router, lucide-react, Agentation dev overlay.

## Layout and Shared UI
- Shell: `AppShell`, `Sidebar`, `Header`
- UI primitives: `Modal`, `AlertBanner`, `StatusBadge`, `StageStepper`, `Tabs`, `KPICard`
- Loan components: `EligibilityChecklist`, `LoanLimitCalculator`, `DocumentChecklist`, `DocumentPackModal`, `AuditTimeline`, `ApprovalPanel`, `RepaymentLedger`

## Page Areas
- Auth and dashboard: `LoginScreen`, `Dashboard`
- Applications: `ApplicationList`, `NewApplication`, `ApplicationDetail`, `CompletenessWorkbench`
- Members: `MemberDirectory`, `MemberProfile`, `Borrower360`
- Appraisal and sanction: `AppraisalWorkbench`, `SanctionWorkbench`
- Documentation and disbursement: `DocumentationHub`, `DisbursementHub`, `PaymentAuthorisationHub`
- Servicing: `LoanAccount360`, `RepaymentsHub`, `InterestManagement`, `MonitoringDashboard`
- Default/closure/compliance: `DefaultRecoveryHub`, `LoanClosureHub`, `ComplianceDashboard`, `GrievancesHub`, `AuditArchiveHub`, `RegistersHub`
- Reports/tasks/search/profile/settings: `ReportsMIS`, `TaskInbox`, `GlobalSearchResults`, `NotificationsCenter`, `MyProfile`, `SettingsHub`
- Borrower portal: `BorrowerPortal` and `src/pages/borrower/portal/**`

## Known Prototype Gaps
- Uses mock data instead of APIs.
- Loading, empty, error, retry, and unauthorized states are uneven.
- No real persistence or backend validation.
- No production authentication.
- Current package lacks lint, typecheck, and real test scripts.
