# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1285ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  624ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  353ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1533ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  543ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  314ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  315ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1819ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2257ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  554ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  396ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2424ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1223ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  913ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 997ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  339ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  414ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1203ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  410ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 997ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  552ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 774ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 751ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  544ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 577ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  384ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 733ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  733ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 552ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 363ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 508ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  431ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5436ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  478ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  379ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  310ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  306ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  421ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  326ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  606ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 430ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 410ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 419ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 328ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 311ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4662ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2291ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  396ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 321ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 196ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 144ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 254ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 220ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 215ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 62ms
 ✓ src/services/authSession.test.ts (39 tests) 34ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/services/portalApi.test.ts (10 tests) 21ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
 ✓ src/services/servicingApi.test.ts (13 tests) 24ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 18ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2196ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2084ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  22:51:58
   Duration  10.09s (transform 4.63s, setup 0ms, collect 14.64s, tests 32.88s, environment 8.61s, prepare 3.42s)


Duration milliseconds: 10617
Exit code: 0
