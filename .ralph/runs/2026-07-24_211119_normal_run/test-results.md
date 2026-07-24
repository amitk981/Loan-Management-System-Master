# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_211119_normal_run/sfpcl-lms

 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1519ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  518ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  300ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  317ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1690ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  537ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  346ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  324ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1850ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  359ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2387ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1180ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  894ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2407ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  543ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  434ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1143ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  406ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  490ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1379ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  627ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  403ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1413ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  464ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 753ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1003ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  585ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 756ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  568ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 611ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 627ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  393ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 480ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 600ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  515ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6128ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  505ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  394ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  300ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  370ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  341ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  426ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  467ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  962ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 433ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 317ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 373ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4777ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2392ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  328ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  310ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 471ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (7 tests) 605ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 352ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 291ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 243ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 184ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 226ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 283ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 143ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 167ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 112ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 60ms
 ✓ src/services/authSession.test.ts (39 tests) 44ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 193ms
 ✓ src/services/portalApi.test.ts (10 tests) 26ms
 ✓ src/services/servicingApi.test.ts (13 tests) 20ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 42ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 29ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/services/recoveryApi.test.ts (1 test) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2624ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2441ms

 Test Files  57 passed (57)
      Tests  464 passed (464)
   Start at  21:36:19
   Duration  11.26s (transform 5.48s, setup 0ms, collect 16.65s, tests 36.97s, environment 9.63s, prepare 3.63s)


Duration milliseconds: 11807
Exit code: 0
