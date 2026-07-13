# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_193616_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 74ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (8 tests) 84ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 218ms
 ✓ src/services/authSession.test.ts (15 tests) 17ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 13ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms

 Test Files  16 passed (16)
      Tests  107 passed (107)
   Start at  19:52:40
   Duration  1.14s (transform 1.08s, setup 0ms, collect 3.14s, tests 683ms, environment 2ms, prepare 998ms)

