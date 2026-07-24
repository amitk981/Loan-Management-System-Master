# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_211119_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1405ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  676ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  350ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1513ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  514ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  323ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  333ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1876ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  310ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  370ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2349ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1128ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  953ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2663ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  482ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  521ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  343ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1366ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  471ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  302ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1305ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  423ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1041ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  364ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  448ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1109ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  658ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 901ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  366ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 646ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  420ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 787ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  582ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 566ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 555ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  476ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 540ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5896ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  517ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  408ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  350ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  305ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  367ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  335ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  411ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  385ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  787ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 459ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 429ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 484ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4941ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2632ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  307ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  300ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (7 tests) 585ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 349ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 353ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 335ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 309ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 273ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 215ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 190ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 200ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 134ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 80ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 160ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 108ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 70ms
 ✓ src/services/authSession.test.ts (39 tests) 33ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/services/servicingApi.test.ts (13 tests) 26ms
 ✓ src/services/portalApi.test.ts (10 tests) 25ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 52ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/recoveryApi.test.ts (1 test) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2400ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2208ms

 Test Files  57 passed (57)
      Tests  464 passed (464)
   Start at  22:51:09
   Duration  11.27s (transform 5.00s, setup 0ms, collect 15.91s, tests 36.91s, environment 9.95s, prepare 3.59s)


Duration milliseconds: 11793
Exit code: 0
