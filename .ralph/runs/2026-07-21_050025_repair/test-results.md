# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_033653_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1329ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  669ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  372ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1352ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  466ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1918ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  348ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  310ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2638ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  597ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  438ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2732ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1362ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1069ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 913ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  530ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 579ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  499ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1063ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  398ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  427ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 629ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  384ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 411ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 315ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 877ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 318ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 137ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 152ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 244ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 159ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 92ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5768ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  570ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  388ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  364ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  317ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  330ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  361ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  371ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  592ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 168ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 97ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 89ms
 ✓ src/services/authSession.test.ts (36 tests) 52ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/services/portalApi.test.ts (7 tests) 22ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 100ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4708ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2344ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  320ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  332ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  336ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2728ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2544ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  05:17:45
   Duration  8.89s (transform 5.37s, setup 0ms, collect 13.39s, tests 29.76s, environment 6.20s, prepare 2.86s)


Duration milliseconds: 9418
Exit code: 0
