# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_031718_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 872ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  313ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1267ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  388ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  668ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1453ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  660ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  410ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2040ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  374ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  326ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 544ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  328ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2559ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  559ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  495ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 311ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 527ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  460ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 177ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1101ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  390ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2233ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1079ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  910ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1046ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  364ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  400ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 376ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 261ms
 ✓ src/services/authSession.test.ts (36 tests) 27ms
 ✓ src/services/portalApi.test.ts (7 tests) 26ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 159ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 316ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 191ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 73ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4265ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2177ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  301ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5621ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  613ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  432ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  312ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  333ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  317ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  577ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 98ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 58ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 45ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 43ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1020ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  918ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  04:04:16
   Duration  8.21s (transform 3.90s, setup 0ms, collect 11.83s, tests 26.92s, environment 5.69s, prepare 2.61s)


Duration milliseconds: 9082
Exit code: 0
