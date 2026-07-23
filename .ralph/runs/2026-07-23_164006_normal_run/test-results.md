# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 868ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  339ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1308ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  591ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  343ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1642ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  554ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  338ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  352ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1836ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  338ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 453ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2693ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  536ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  500ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  322ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 998ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  562ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 581ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  355ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 458ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 257ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 308ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 506ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 388ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 480ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  408ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 596ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5756ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  507ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  409ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  358ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  393ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  404ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  343ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  696ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1228ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  471ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1026ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  446ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  369ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 337ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2462ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1238ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  970ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4687ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2510ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  319ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 323ms
 ✓ src/services/authSession.test.ts (39 tests) 35ms
 ✓ src/services/servicingApi.test.ts (13 tests) 25ms
 ✓ src/services/portalApi.test.ts (10 tests) 26ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 253ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 654ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  653ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 214ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 182ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 94ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 22ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 13ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 15ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 44ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 92ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 51ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 47ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/playwright.seed.test.ts (3 tests) 4ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1092ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  990ms

 Test Files  52 passed (52)
      Tests  415 passed (415)
   Start at  17:48:34
   Duration  10.18s (transform 4.58s, setup 0ms, collect 15.26s, tests 32.24s, environment 8.26s, prepare 3.34s)


Duration milliseconds: 10921
Exit code: 0
