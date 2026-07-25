# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_065407_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1514ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  459ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  336ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  331ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1677ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  313ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1754ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  436ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  477ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  580ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2177ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1104ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  790ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2334ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  495ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  405ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1259ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  484ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1393ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  445ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  341ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1201ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  491ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  367ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1169ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  400ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 973ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  485ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5462ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  425ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  357ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  425ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  345ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  396ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  330ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  665ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 2934ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  868ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  741ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces backend observation validation without exposing details or lifecycle controls  319ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  316ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 992ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  621ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1136ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  332ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  482ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 832ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  355ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4756ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2425ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  345ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 583ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 780ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  590ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 700ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  525ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 882ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  309ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 574ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  484ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 639ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  432ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 479ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 459ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 394ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 455ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 436ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 355ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 363ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 311ms
 ✓ src/services/reportApi.test.ts (5 tests) 9ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 247ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 6ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 221ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 213ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 164ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 151ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 163ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/services/portalApi.test.ts (10 tests) 34ms
 ✓ src/services/authSession.test.ts (40 tests) 37ms
 ✓ src/services/servicingApi.test.ts (13 tests) 32ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 44ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 87ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 27ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 17ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2281ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2107ms

 Test Files  64 passed (64)
      Tests  513 passed (513)
   Start at  07:37:59
   Duration  12.77s (transform 5.12s, setup 0ms, collect 17.68s, tests 43.01s, environment 11.48s, prepare 3.91s)


Duration milliseconds: 13300
Exit code: 0
