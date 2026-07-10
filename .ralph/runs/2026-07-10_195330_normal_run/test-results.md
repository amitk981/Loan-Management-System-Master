# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_195330_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 47ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (8 tests) 80ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 81ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 266ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 6ms
 ✓ src/services/portalApi.test.ts (4 tests) 5ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms

 Test Files  16 passed (16)
      Tests  107 passed (107)
   Start at  20:10:34
   Duration  1.22s (transform 1.22s, setup 0ms, collect 3.41s, tests 663ms, environment 2ms, prepare 963ms)

