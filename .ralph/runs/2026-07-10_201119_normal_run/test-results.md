# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_201119_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (8 tests) 72ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 57ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 95ms
 ✓ src/services/authSession.test.ts (15 tests) 13ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 242ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms

 Test Files  16 passed (16)
      Tests  107 passed (107)
   Start at  20:29:43
   Duration  1.16s (transform 1.04s, setup 0ms, collect 3.06s, tests 662ms, environment 2ms, prepare 1.03s)

