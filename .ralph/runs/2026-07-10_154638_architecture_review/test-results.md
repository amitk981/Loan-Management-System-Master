# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-10_154638_architecture_review/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (8 tests) 68ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 57ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 110ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 230ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/services/portalApi.test.ts (3 tests) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 21ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 42ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms

 Test Files  16 passed (16)
      Tests  106 passed (106)
   Start at  16:02:58
   Duration  1.17s (transform 1.10s, setup 0ms, collect 3.19s, tests 676ms, environment 2ms, prepare 997ms)

