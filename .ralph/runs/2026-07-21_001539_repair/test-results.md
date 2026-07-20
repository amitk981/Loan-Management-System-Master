# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_225941_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1374ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  499ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1557ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  846ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  368ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2138ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  359ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  356ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2590ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1281ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  986ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2990ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  358ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  677ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  463ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  424ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 930ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  504ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1171ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  429ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  464ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 714ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 583ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  342ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 391ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 535ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  439ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 299ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 379ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 134ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 223ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 164ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 167ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 89ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5914ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  736ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  422ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  379ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  358ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  355ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  378ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  329ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  313ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  383ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  375ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  615ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 26ms
 ✓ src/services/authSession.test.ts (36 tests) 27ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 53ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 77ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 47ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 64ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4606ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2467ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  303ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 11ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2325ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2135ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  00:38:57
   Duration  8.96s (transform 4.72s, setup 0ms, collect 12.75s, tests 29.73s, environment 6.55s, prepare 2.71s)


Duration milliseconds: 9489
Exit code: 0
