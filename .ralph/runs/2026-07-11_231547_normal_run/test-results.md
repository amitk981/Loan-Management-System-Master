# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_231547_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 72ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 210ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (21 tests) 194ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 27ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 34ms
 ✓ src/services/authSession.test.ts (15 tests) 15ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 37ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 17ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 6ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 4ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1753ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1603ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 944ms

 Test Files  25 passed (25)
      Tests  165 passed (165)
   Start at  23:37:08
   Duration  3.03s (transform 2.33s, setup 0ms, collect 4.02s, tests 3.58s, environment 236ms, prepare 1.36s)

