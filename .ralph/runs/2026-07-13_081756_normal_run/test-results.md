# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_081756_normal_run/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 206ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 223ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/services/authSession.test.ts (15 tests) 15ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 255ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2745ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1849ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  435ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  460ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 811ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  477ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1028ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  368ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1254ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1715ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  992ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  568ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2523ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1296ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  08:32:32
   Duration  6.31s (transform 3.92s, setup 0ms, collect 7.50s, tests 11.24s, environment 2.22s, prepare 1.77s)

