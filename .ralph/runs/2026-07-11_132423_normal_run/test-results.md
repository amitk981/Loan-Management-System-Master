# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_132423_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 42ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 60ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 62ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 126ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 154ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 365ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 15ms
 ✓ src/services/authSession.test.ts (15 tests) 16ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (17 tests) 357ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 64ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 47ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 22ms
 ✓ src/services/applicationIntakeApi.test.ts (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (3 tests) 25ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms

 Test Files  21 passed (21)
      Tests  137 passed (137)
   Start at  13:31:12
   Duration  1.81s (transform 1.58s, setup 0ms, collect 4.88s, tests 1.40s, environment 3ms, prepare 1.72s)

