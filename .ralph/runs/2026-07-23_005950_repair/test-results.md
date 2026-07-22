# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_000144_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1376ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  396ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  345ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1476ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  723ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  312ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1827ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  308ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2319ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1142ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  893ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2391ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  453ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  431ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 911ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  524ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 719ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1350ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  448ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 654ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  654ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1062ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  389ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  408ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 664ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  398ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 517ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 562ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  484ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 410ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 418ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 387ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5681ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  629ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  408ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  311ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  343ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  366ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  373ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  301ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  643ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 548ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 327ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 321ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4521ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2207ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  324ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  309ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 303ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 205ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 154ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 149ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 69ms
 ✓ src/services/authSession.test.ts (39 tests) 38ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 148ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 27ms
 ✓ src/services/servicingApi.test.ts (13 tests) 21ms
 ✓ src/services/portalApi.test.ts (9 tests) 22ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 16ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 16ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2148ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2039ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  01:10:50
   Duration  9.73s (transform 4.85s, setup 0ms, collect 14.49s, tests 32.09s, environment 7.69s, prepare 3.22s)


Duration milliseconds: 10259
Exit code: 0
