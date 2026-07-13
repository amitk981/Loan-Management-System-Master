# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_190759_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (3 tests) 56ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 110ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 119ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 375ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (18 tests) 362ms
 ✓ src/services/authSession.test.ts (15 tests) 20ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 45ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 51ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 26ms
 ✓ src/services/portalApi.test.ts (4 tests) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 18ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 16ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 11ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms

 Test Files  24 passed (24)
      Tests  146 passed (146)
   Start at  19:16:24
   Duration  1.80s (transform 1.46s, setup 0ms, collect 4.36s, tests 1.39s, environment 4ms, prepare 1.92s)

