# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_174655_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 821ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  314ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1351ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  680ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  320ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1523ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  580ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  318ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  307ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1790ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  331ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2582ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  575ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  418ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  321ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 500ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1026ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  597ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 623ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  340ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1607ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  510ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  364ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  340ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 452ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 451ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 220ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 337ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 535ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 312ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 489ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  402ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5807ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  464ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  380ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  311ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  368ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  340ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  407ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  325ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  451ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  354ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  683ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 568ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4736ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2427ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  329ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1161ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  406ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 642ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  460ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 240ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 400ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2273ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1139ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  882ms
 ✓ src/services/authSession.test.ts (39 tests) 30ms
 ✓ src/services/servicingApi.test.ts (13 tests) 25ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1014ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  336ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  418ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 330ms
 ✓ src/services/portalApi.test.ts (10 tests) 33ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 186ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 217ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 15ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 76ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 652ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  651ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 22ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 212ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 87ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 63ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 47ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 16ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 142ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 1296ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1110ms

 Test Files  56 passed (56)
      Tests  457 passed (457)
   Start at  18:28:45
   Duration  11.18s (transform 4.76s, setup 0ms, collect 16.88s, tests 35.05s, environment 9.35s, prepare 3.63s)


Duration milliseconds: 11910
Exit code: 0
