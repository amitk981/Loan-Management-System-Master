# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_210636_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 64ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 90ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 184ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (18 tests) 193ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 35ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1805ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1703ms

 Test Files  24 passed (24)
      Tests  148 passed (148)
   Start at  21:14:00
   Duration  2.19s (transform 2.62s, setup 0ms, collect 4.44s, tests 2.70s, environment 3ms, prepare 1.48s)

