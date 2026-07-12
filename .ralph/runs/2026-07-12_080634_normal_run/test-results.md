# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_080634_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 70ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 97ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 96ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 101ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 256ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 322ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 36ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/services/authSession.test.ts (15 tests) 11ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 58ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 34ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 9ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 1ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2062ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1908ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 943ms

 Test Files  25 passed (25)
      Tests  166 passed (166)
   Start at  08:17:32
   Duration  3.55s (transform 2.83s, setup 0ms, collect 5.21s, tests 4.25s, environment 349ms, prepare 1.66s)

