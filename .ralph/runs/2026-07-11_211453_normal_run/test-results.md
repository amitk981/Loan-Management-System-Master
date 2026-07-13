# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_211453_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 59ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 77ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 241ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (20 tests) 219ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1770ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1661ms

 Test Files  24 passed (24)
      Tests  150 passed (150)
   Start at  21:26:45
   Duration  2.13s (transform 2.50s, setup 0ms, collect 4.18s, tests 2.75s, environment 3ms, prepare 1.36s)

