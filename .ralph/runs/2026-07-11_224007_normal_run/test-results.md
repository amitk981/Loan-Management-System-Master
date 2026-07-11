# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_224007_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 75ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 80ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 174ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (21 tests) 175ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 43ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 16ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1755ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1650ms

 Test Files  24 passed (24)
      Tests  151 passed (151)
   Start at  22:49:10
   Duration  2.20s (transform 2.33s, setup 0ms, collect 4.00s, tests 2.61s, environment 3ms, prepare 1.29s)

