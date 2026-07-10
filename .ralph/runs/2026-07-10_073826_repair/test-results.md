# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_073826_repair/sfpcl-lms

 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (3 tests) 127ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 287ms
 ✓ src/services/authSession.test.ts (15 tests) 14ms
 ✓ src/services/portalApi.test.ts (3 tests) 16ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 24ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 42ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms

 Test Files  15 passed (15)
      Tests  98 passed (98)
   Start at  08:25:21
   Duration  1.24s (transform 1.29s, setup 0ms, collect 3.53s, tests 758ms, environment 2ms, prepare 1.15s)

