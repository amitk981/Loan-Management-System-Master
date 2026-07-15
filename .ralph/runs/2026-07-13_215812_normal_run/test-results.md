# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_215812_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 92ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 89ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 135ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 297ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 375ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 73ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 48ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 71ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 16ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/authSession.test.ts (15 tests) 24ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 9ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 335ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 952ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  559ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3600ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2745ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  535ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  320ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1143ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  325ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1440ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1775ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  966ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  668ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2739ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1392ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  22:26:49
   Duration  7.32s (transform 5.82s, setup 0ms, collect 9.17s, tests 13.38s, environment 2.81s, prepare 1.76s)

