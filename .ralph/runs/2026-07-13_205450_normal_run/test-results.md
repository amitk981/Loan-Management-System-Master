# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_205450_normal_run/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 83ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 57ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 98ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 93ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 206ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 217ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 42ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 17ms
 ✓ src/services/authSession.test.ts (15 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 297ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2772ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1993ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  356ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  423ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1295ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  306ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  785ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1353ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  452ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1779ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  341ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2197ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1298ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  719ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2605ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1415ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  21:11:26
   Duration  7.06s (transform 4.65s, setup 0ms, collect 8.42s, tests 13.31s, environment 2.73s, prepare 1.82s)

