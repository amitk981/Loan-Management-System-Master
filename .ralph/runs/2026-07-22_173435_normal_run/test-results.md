# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_173435_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 751ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1407ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  602ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  426ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1900ms
   ✓ 010MA Repayments Hub wiring > renders canonical ledger, statement exceptions, and subsidiary reconciliation evidence  329ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  486ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  336ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  449ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2085ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  384ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  324ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3067ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  651ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  486ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  466ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 551ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1284ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  752ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 672ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  403ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 497ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 305ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 534ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 359ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 473ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  397ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 177ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5883ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  386ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  372ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  347ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  391ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  508ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  346ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  343ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  451ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  340ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  683ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 972ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  334ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  406ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1176ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  393ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 421ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2377ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1180ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  922ms
 ✓ src/services/authSession.test.ts (38 tests) 33ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 349ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 338ms
 ✓ src/services/servicingApi.test.ts (13 tests) 34ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4811ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2627ms
 ✓ src/services/portalApi.test.ts (9 tests) 31ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 298ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 687ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  686ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 83ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 107ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 214ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 17ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 53ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 52ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1070ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  969ms

 Test Files  52 passed (52)
      Tests  412 passed (412)
   Start at  18:17:27
   Duration  10.51s (transform 5.05s, setup 0ms, collect 15.87s, tests 33.45s, environment 8.36s, prepare 3.42s)


Duration milliseconds: 11209
Exit code: 0
