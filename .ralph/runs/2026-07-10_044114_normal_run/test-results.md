# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_044114_normal_run/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 38ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 198ms
 ✓ src/services/authSession.test.ts (15 tests) 16ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (3 tests) 88ms
 ✓ src/services/portalApi.test.ts (3 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms

 Test Files  15 passed (15)
      Tests  98 passed (98)
   Start at  05:16:40
   Duration  1.07s (transform 1.09s, setup 0ms, collect 3.03s, tests 587ms, environment 1ms, prepare 929ms)

