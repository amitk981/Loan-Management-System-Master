# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1376ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  663ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  329ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1674ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  553ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  351ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  335ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1999ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  335ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  303ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2517ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1294ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  950ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2643ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  514ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  442ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1276ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  463ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1056ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  339ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  482ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1024ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  566ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 684ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  437ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 823ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 432ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 560ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  448ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 497ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 421ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 380ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5826ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  641ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  355ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  336ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  300ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  350ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  388ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  367ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  743ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 132ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 330ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 158ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 206ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 95ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 83ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 42ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 52ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5010ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2718ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  346ms
 ✓ src/services/portalApi.test.ts (9 tests) 24ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 66ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/servicingApi.test.ts (4 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 20ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 17ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 25ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2482ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2314ms

 Test Files  47 passed (47)
      Tests  379 passed (379)
   Start at  15:15:11
   Duration  9.47s (transform 5.22s, setup 0ms, collect 14.11s, tests 32.17s, environment 7.50s, prepare 2.84s)


Duration milliseconds: 10038
Exit code: 0
