# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_100050_normal_run/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 46ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 191ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (4 tests) 112ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 7ms
 ✓ src/services/portalApi.test.ts (3 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 11ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/authSession.test.ts (15 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms

 Test Files  16 passed (16)
      Tests  102 passed (102)
   Start at  10:56:26
   Duration  1.15s (transform 1.17s, setup 0ms, collect 3.13s, tests 622ms, environment 2ms, prepare 1.05s)

