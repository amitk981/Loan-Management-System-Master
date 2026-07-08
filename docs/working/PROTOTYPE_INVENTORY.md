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
- Reports/tasks/search/profile/settings/admin: `ReportsMIS`, `TaskInbox`, `GlobalSearchResults`, `NotificationsCenter`, `MyProfile`, `SettingsHub`, `AdminUsers`
- Dev/integration proof: `TracerBullet`
- Borrower portal: `BorrowerPortal` and `src/pages/borrower/portal/**`

## Known Prototype Gaps
- Most production module screens still use mock data instead of APIs.
- Loading, empty, error, retry, and unauthorized states are uneven.
- Real backend/API wiring exists for auth/current-user, the dev Tracer screen, Admin User Management,
  Dashboard summary cards/tasks, staff Notifications Center, and staff My Profile.

## API-Backed Staff Screens

| Screen | Backend path | Current status | Notes |
|---|---|---|---|
| `Dashboard` | `GET /api/v1/dashboard/` | API-backed shell | Renders backend `role_context`, `cards[]`, and `tasks[]`. Current backend cards are zero-count shells and `tasks[]` is empty until downstream lending/task data exists. |
| `MemberDirectory` | `GET /api/v1/members/` | API-backed directory | Uses the source §13.1 read-only member list with search/type/KYC filters, masked mobile numbers, share/active-member shell fields, and no local `mockData` fallback. Profile detail, Borrower 360, create/update, KYC verification, land/crop, and deeper shareholding panels remain future scope. |
| `MemberProfile` | `GET /api/v1/members/{member_id}/` | API-backed masked profile shell | Uses the source §13.3 read-only member detail with masked PAN/Aadhaar, registered address, profile shell fields, and deferred empty states for tabs whose backend endpoints are not implemented. No `mockData` fallback on this profile path; sensitive reveal, nominee, communications, audit trail, KYC documents, land/crop evidence, and loan rows remain future scope. |
| `NotificationsCenter` | `GET /api/v1/notifications/`; `POST /api/v1/notifications/{notification_id}/mark-read/` | API-backed staff inbox | Uses backend direct/role/team notification rows. Mark-read sends the current `read_state_version`; stale writes surface the existing refresh/error pattern for `409 STALE_WRITE`. No local mock fallback should be reintroduced. |
| `MyProfile` | `GET /api/v1/auth/me/` | API-backed read-only profile | Shows the authenticated user's backend identity, active role, teams, and permissions. Profile editing remains future scope. |
| `TaskInbox` | None implemented yet | Prototype/mock shell | Source S03 requires actionable assigned/role tasks with filters and workflow actions. 003J added only internal `scheduled_jobs` metadata/services and did not add a task inbox endpoint, dashboard task generation, notification generation rules, or scheduler UI. |

## Epic 003 Component Status

| Prototype reference | Current implementation status |
|---|---|
| `AuditTimeline` | Still prototype/mock data. Backend audit/workflow read APIs exist, but shared audit timeline UI wiring remains future scope. |
| `DocumentPackModal` | Still prototype/mock data. Generic document upload/download APIs exist, but document pack generation, legal document lifecycle, and template-driven packs remain future scope. |
