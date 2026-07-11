# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_133237_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 40ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 42ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 111ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 116ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 241ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (18 tests) 256ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/authSession.test.ts (15 tests) 17ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 49ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 82ms
 ✓ src/services/portalApi.test.ts (4 tests) 23ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (3 tests) 17ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 17ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms

 Test Files  21 passed (21)
      Tests  138 passed (138)
   Start at  13:50:23
   Duration  1.66s (transform 1.33s, setup 0ms, collect 4.21s, tests 1.14s, environment 3ms, prepare 1.61s)

