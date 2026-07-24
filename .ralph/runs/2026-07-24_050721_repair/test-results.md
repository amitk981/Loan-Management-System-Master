# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_041849_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1332ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  637ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  330ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1529ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  504ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  306ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  310ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1762ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  315ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  300ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2333ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1171ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  882ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2693ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  487ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  517ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  340ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 900ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  447ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1225ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  423ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1162ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  433ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  414ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 760ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 750ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  559ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 745ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  422ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 677ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  677ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 508ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  434ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 467ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 610ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5741ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  608ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  360ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  302ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  432ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  365ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  381ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  393ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  681ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4225ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2120ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 439ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 432ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 411ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 338ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 279ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 313ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 191ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 198ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 235ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 173ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 61ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 196ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/services/servicingApi.test.ts (13 tests) 23ms
 ✓ src/services/portalApi.test.ts (10 tests) 21ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/services/authSession.test.ts (39 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 39ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 16ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2342ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2162ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  05:15:43
   Duration  9.95s (transform 4.92s, setup 0ms, collect 14.54s, tests 33.50s, environment 8.64s, prepare 3.29s)


Duration milliseconds: 10655
Exit code: 0
