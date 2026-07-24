# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_225638_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1587ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  532ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  357ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  324ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1550ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  628ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1922ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  330ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2267ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1131ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  862ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2560ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  531ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  390ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1139ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  717ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1270ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  445ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1340ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  558ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  335ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1030ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  361ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  425ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 832ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  308ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 685ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  491ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 592ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 531ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  338ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5632ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  528ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  351ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  304ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  309ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  405ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  357ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  667ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 796ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  710ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 464ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1304ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  521ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4871ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2597ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  325ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 489ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 253ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 285ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 396ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 358ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 451ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 185ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 286ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 181ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 185ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 126ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 173ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 164ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/services/authSession.test.ts (39 tests) 47ms
 ✓ src/services/portalApi.test.ts (10 tests) 25ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 72ms
 ✓ src/services/servicingApi.test.ts (13 tests) 24ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 35ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/recoveryApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2466ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2108ms

 Test Files  57 passed (57)
      Tests  469 passed (469)
   Start at  23:42:00
   Duration  11.17s (transform 4.94s, setup 0ms, collect 16.18s, tests 36.88s, environment 9.76s, prepare 3.61s)


Duration milliseconds: 11707
Exit code: 0
