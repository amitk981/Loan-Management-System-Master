# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_230238_architecture_review/sfpcl-lms

 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (21 tests) 165ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 212ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 33ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 46ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1633ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1532ms

 Test Files  24 passed (24)
      Tests  151 passed (151)
   Start at  23:14:52
   Duration  1.97s (transform 2.04s, setup 0ms, collect 3.94s, tests 2.53s, environment 3ms, prepare 1.35s)

