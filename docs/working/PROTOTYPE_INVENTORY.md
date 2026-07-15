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
- `AppraisalWorkbench` and Application Detail's credit tab consume Epic 006 staff APIs (006H).
- `SanctionWorkbench` consumes the Epic 007 approval-case, action, general-meeting evidence, and
  independently permissioned sanction-decision APIs (007I); its checklist and authority are frozen
  server projections rather than client calculations. 007L adds the complete frozen S21 queue
  facts, immutable S22 action history, exact sanction/status filters, shared authenticated upload
  transport, and fresh-upload-only changed General Meeting evidence.
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
| `Borrower360` | `GET /api/v1/members/{member_id}/`; Epic 004 member subresources | API-backed member-master 360 | Uses member detail, shareholding, land/crop, nominee, KYC profile/document, bank-account, and cancelled-cheque metadata APIs. PAN/Aadhaar stay masked unless the 004I reveal endpoint returns a temporary full value, bank/cancelled-cheque account numbers stay masked with no reveal control, and loan/application/repayment/communication/risk/audit sections show source-backed empty states until later APIs exist. |
| `NotificationsCenter` | `GET /api/v1/notifications/`; `POST /api/v1/notifications/{notification_id}/mark-read/` | API-backed staff inbox | Uses backend direct/role/team notification rows. Mark-read sends the current `read_state_version`; stale writes surface the existing refresh/error pattern for `409 STALE_WRITE`. No local mock fallback should be reintroduced. |
| `MyProfile` | `GET /api/v1/auth/me/` | API-backed read-only profile | Shows the authenticated user's backend identity, active role, teams, and permissions. Profile editing remains future scope. |
| `TaskInbox` | None implemented yet | Prototype/mock shell | Source S03 requires actionable assigned/role tasks with filters and workflow actions. 003J added only internal `scheduled_jobs` metadata/services and did not add a task inbox endpoint, dashboard task generation, notification generation rules, or scheduler UI. |
| `CompletenessWorkbench` | `GET /api/v1/loan-applications/`; `GET /document-checklist/`; `GET/POST /completeness-check/`; deficiency and rejection-note actions | API-backed staff workbench | 005E2 removes application/member/document mocks, seeded deficiency decisions, and client reference generation. Queue/checklist/history facts and all action outcomes are re-read from backend state; canonical `/auth/me` permission controls interim action visibility. |
| `SanctionWorkbench` | `GET /api/v1/approval-cases/`; case action endpoints; `POST /general-meeting-approval/`; `GET /sanction-decision/` | API-backed committee workbench | Uses exact sanction/status/assignment filters, complete frozen S21 row facts, frozen ten-point review facts, immutable S22 action history, case `available_actions`, optimistic versions, conflict/exclusion facts, three fresh exact-application legal uploads for every changed special-case evidence submission, and an independently permissioned terminal decision read. No register/live appraisal fallback, metadata-id reuse, or local authority matrix remains. |
| `RegistersHub` S23/S25 | `GET /api/v1/credit-sanction-register/`; `GET /api/v1/exception-register/` | API-backed generated registers | Uses independent actor-scoped filters and server pagination. S23 renders the 15 frozen sanction fields; S25 keeps description and business reason distinct. Metadata ids create no case/document actions. Other register tabs remain prototype/mock until 012DA. |
| `SettingsHub` S71 | `GET/PATCH /api/v1/approval-matrix-rules/` | API-backed versioned matrix panel | Renders retained matrix versions. Canonical managers submit complete successor versions as pending maker-checker proposals; the UI never overwrites an active rule or activates its maker's proposal. Remaining SettingsHub panels remain owned by 007J2. |

## API-Backed Borrower Portal Screens

| Screen | Backend path | Current status | Notes |
|---|---|---|---|
| `MP03_Dashboard` | `GET /api/v1/portal/dashboard/` | API-backed own-data shell | Uses the active portal account member scope, own application counts, open-deficiency pending count, and source-backed zero/empty placeholders for future loan, repayment, signature, KYC-update, closure, and notice modules. |
| `MP04_MyProfile` | `GET /api/v1/portal/profile/` | API-backed masked profile | Reuses Epic 004 member subresources for profile, nominees, shareholding, land/crop, KYC, bank accounts, and cancelled cheques. PAN/Aadhaar/bank values stay masked; no portal reveal control exists. |
| `MP05_NewApplication` | `GET /api/v1/portal/application-limit-projection/`; `POST/PATCH /api/v1/portal/applications/`; `POST /submit/` | API-backed draft/submit and limit projection | Displays only the current redacted server limit projection in the approved three-card composition, including unavailable/error/exception states; saves and submits own portal application facts through the active portal account scope. Document upload/checklist and returned-deficiency resubmission remain future portal slices. |
| `MP07_DocumentChecklist`, `MP13_DocumentationActions` | `GET /api/v1/portal/applications/{id}/documentation-actions/`; action upload/download routes | API-backed borrower-safe documentation | Uses the newest own sanctioned application, server-owned applicability/status/actions, immutable upload/re-upload provenance, and audited current Term Sheet/Loan Agreement descriptors. Blank cheque/CDSL remain status-only and no internal/sensitive evidence is rendered. Deficiency response remains 008L2. |
| `MP09_MyApplications` | `GET /api/v1/portal/applications/` | API-backed own list | Renders own draft/submitted/returned application rows with loading, empty, error, and returned-incomplete borrower-action states. No local application mock fallback. |
| `MP10_ApplicationStatus`, `MP11_DeficiencyResponse` | Portal application detail plus application-scoped deficiency list/upload/download/resubmit routes | API-backed own status and rectification | Renders selected own application status and borrower-safe timeline. Returned applications compose MP11 from existing portal card/alert/input/button patterns: strict server-owned upload contracts, immutable re-upload history, authenticated current content, all-item gating, and canonical post-upload/status refetch with no internal completeness authority. |
| `MP22_ProduceSupply` | `GET /api/v1/portal/produce-supply/` | API-backed empty shell | Prototype screen number is supply history, not spec MP22 grievance detail. Returns an empty state until `produce_supply_records` exists in the backend. |

## Epic 003 Component Status

| Prototype reference | Current implementation status |
|---|---|
| `AuditTimeline` | Still prototype/mock data. Backend audit/workflow read APIs exist, but shared audit timeline UI wiring remains future scope. |
| `DocumentPackModal` | Still prototype/mock data. Generic document upload/download APIs exist, but document pack generation, legal document lifecycle, and template-driven packs remain future scope. |
