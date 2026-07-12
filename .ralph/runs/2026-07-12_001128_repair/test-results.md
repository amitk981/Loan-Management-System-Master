# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_001128_repair/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 55ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 80ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 98ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 96ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 234ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 228ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 47ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 48ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 44ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 50ms
 ✓ src/services/authSession.test.ts (15 tests) 38ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 11ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1979ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1838ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1011ms

 Test Files  25 passed (25)
      Tests  166 passed (166)
   Start at  08:01:38
   Duration  3.53s (transform 2.65s, setup 0ms, collect 4.74s, tests 4.10s, environment 346ms, prepare 1.66s)

