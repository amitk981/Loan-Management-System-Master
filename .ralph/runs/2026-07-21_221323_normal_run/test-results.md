# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_221323_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1327ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  594ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  340ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1586ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  493ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  328ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  328ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1909ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  384ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2345ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1064ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  989ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2511ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  553ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  434ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1017ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  582ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 718ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1238ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  397ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 486ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  308ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1130ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  417ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  450ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 413ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 423ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 524ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  452ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 434ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 395ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 376ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5554ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  580ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  416ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  302ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  382ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  337ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  655ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 301ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 287ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4575ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2267ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  324ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 229ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 170ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 174ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 56ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 161ms
 ✓ src/services/authSession.test.ts (38 tests) 36ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 42ms
 ✓ src/services/portalApi.test.ts (9 tests) 24ms
 ✓ src/services/servicingApi.test.ts (11 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 40ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2181ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2068ms

 Test Files  50 passed (50)
      Tests  400 passed (400)
   Start at  22:55:32
   Duration  8.98s (transform 4.45s, setup 0ms, collect 12.99s, tests 31.01s, environment 6.86s, prepare 2.94s)


Duration milliseconds: 9509
Exit code: 0
