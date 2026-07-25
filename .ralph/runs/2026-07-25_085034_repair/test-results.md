# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_074057_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1630ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  504ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  334ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  316ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1921ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  412ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  608ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  560ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2317ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1223ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  821ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2334ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  476ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  372ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 2905ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  880ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  634ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  327ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1525ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  535ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  328ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1318ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  498ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1878ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  408ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1431ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  628ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  373ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1359ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  414ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5767ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  425ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  427ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  345ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  355ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  334ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  424ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  342ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  822ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1103ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  588ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 989ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  443ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1155ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  423ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  484ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1071ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  661ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5040ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2604ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  336ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  311ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 886ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  332ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 782ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  611ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 832ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  546ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 709ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  394ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 615ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 594ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 799ms
   ✓ 010N Global Search Results > loads server groups, card fields, and permission-valid quick actions  347ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 446ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 592ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  495ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 485ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 391ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 354ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 374ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 370ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 236ms
 ✓ src/services/reportApi.test.ts (5 tests) 14ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 6ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 219ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 221ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 132ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 168ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 204ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 72ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 46ms
 ✓ src/services/authSession.test.ts (40 tests) 33ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 79ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 47ms
 ✓ src/services/portalApi.test.ts (10 tests) 23ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 12ms
 ✓ src/services/servicingApi.test.ts (13 tests) 51ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 20ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/playwright.seed.test.ts (5 tests) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2665ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2476ms

 Test Files  64 passed (64)
      Tests  515 passed (515)
   Start at  09:07:44
   Duration  13.77s (transform 5.88s, setup 0ms, collect 19.45s, tests 46.42s, environment 12.95s, prepare 4.17s)


Duration milliseconds: 14542
Exit code: 0
