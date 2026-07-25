# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_134358_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1205ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  309ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  374ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1628ms
   ✓ 011PA default case and frozen-note read surface > shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls  304ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  628ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2103ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  404ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  304ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2855ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  633ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  438ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  352ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 3778ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  993ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  857ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces backend observation validation without exposing details or lifecycle controls  435ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  526ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1950ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  823ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  392ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  353ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 2572ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  472ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  941ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  860ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1814ms
   ✓ SettingsHub Approval Matrix panel > renders active and retained historical rules from the versioned API without local fixtures  382ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  732ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  415ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 2049ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  561ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  507ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  502ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1291ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  311ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  720ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 574ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 698ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  420ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1381ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  835ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  409ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7039ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  628ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  480ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  357ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  322ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  472ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  492ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  418ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  480ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  489ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  953ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 384ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 522ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 950ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  408ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 270ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 312ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6288ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3520ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  406ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  307ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  329ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  307ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 666ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 352ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 587ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  484ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 668ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 791ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  602ms
 ✓ src/services/reportApi.test.ts (5 tests) 7ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 781ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  590ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1319ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  478ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 12ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2594ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1265ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1025ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 380ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1080ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  409ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  455ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 263ms
 ✓ src/services/authSession.test.ts (40 tests) 31ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 342ms
 ✓ src/services/servicingApi.test.ts (13 tests) 28ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 244ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 25ms
 ✓ src/services/portalApi.test.ts (10 tests) 40ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 223ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 20ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 100ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 231ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 14ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 44ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 73ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 34ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/playwright.seed.test.ts (5 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 119ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 1247ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1080ms

 Test Files  64 passed (64)
      Tests  515 passed (515)
   Start at  14:27:08
   Duration  15.71s (transform 5.93s, setup 0ms, collect 21.56s, tests 52.18s, environment 15.32s, prepare 4.81s)


Duration milliseconds: 16912
Exit code: 0
