# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_110705_normal_run/sfpcl-lms

 ✓ src/services/portalApi.test.ts (3 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 44ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 52ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 64ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (8 tests) 89ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 129ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 60ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 404ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 48ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms

 Test Files  16 passed (16)
      Tests  106 passed (106)
   Start at  12:12:00
   Duration  1.39s (transform 1.08s, setup 0ms, collect 3.45s, tests 959ms, environment 2ms, prepare 1.27s)

