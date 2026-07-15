# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_064104_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1043ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  565ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1236ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  634ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  308ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1322ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  474ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1697ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  343ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  312ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2363ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1140ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  952ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 308ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (5 tests) 454ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  331ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 676ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 178ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 58ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 169ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 57ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
(node:3530) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (5 tests) 22ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 49ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2754ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2235ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 4974ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  381ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  387ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  305ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  301ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  374ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  366ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  567ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3601ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2021ms

 Test Files  34 passed (34)
      Tests  299 passed (299)
   Start at  07:29:46
   Duration  6.93s (transform 5.09s, setup 0ms, collect 9.84s, tests 21.33s, environment 4.37s, prepare 2.07s)

