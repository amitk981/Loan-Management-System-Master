# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_092630_architecture_review/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 60ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 49ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 60ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 54ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 88ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 282ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (3 tests) 127ms
 ✓ src/services/authSession.test.ts (15 tests) 15ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 43ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 10ms
 ✓ src/services/portalApi.test.ts (3 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms

 Test Files  15 passed (15)
      Tests  98 passed (98)
   Start at  09:52:04
   Duration  1.39s (transform 1.44s, setup 0ms, collect 4.08s, tests 822ms, environment 2ms, prepare 1.19s)

