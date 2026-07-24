# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_123250_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1396ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  669ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  352ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1595ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  534ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  315ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  326ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1910ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  329ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  383ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2332ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1156ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  917ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2648ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  546ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  468ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  363ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 928ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  481ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1567ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  556ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1156ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  484ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  429ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 791ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 674ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  673ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 888ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  657ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 429ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 584ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 588ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  364ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 508ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  426ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5630ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  528ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  342ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  334ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  315ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  305ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  357ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  335ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  697ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 422ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 437ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4762ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2385ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  317ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  307ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 431ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 361ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 424ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 439ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 194ms
 ✓ src/pages/Dashboard.test.tsx (23 tests) 255ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 188ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 219ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 207ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 173ms
 ✓ src/services/authSession.test.ts (39 tests) 29ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 156ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 88ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/services/portalApi.test.ts (10 tests) 22ms
 ✓ src/services/servicingApi.test.ts (13 tests) 21ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2476ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2291ms

 Test Files  55 passed (55)
      Tests  437 passed (437)
   Start at  13:01:06
   Duration  10.89s (transform 5.34s, setup 0ms, collect 16.05s, tests 35.26s, environment 9.73s, prepare 3.48s)


Duration milliseconds: 11431
Exit code: 0
