# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_233905_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 950ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  413ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1304ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  348ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  733ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1455ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  692ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  370ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2042ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  364ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  311ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 640ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  421ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 415ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2780ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  576ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  513ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  348ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 481ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  407ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 254ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2510ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1154ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1088ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1400ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  373ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1168ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  531ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  386ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 370ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 248ms
 ✓ src/services/authSession.test.ts (36 tests) 40ms
 ✓ src/services/portalApi.test.ts (7 tests) 26ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 194ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 81ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 19ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 235ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 98ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 426ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5968ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  631ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  398ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  386ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  333ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  312ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  530ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  396ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  721ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 108ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 68ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 45ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 49ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5278ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3010ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 91ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1082ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  984ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  00:10:56
   Duration  9.14s (transform 3.94s, setup 0ms, collect 13.09s, tests 29.91s, environment 6.50s, prepare 2.95s)


Duration milliseconds: 9917
Exit code: 0
