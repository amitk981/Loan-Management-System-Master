# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_150856_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 83ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 96ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 119ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 163ms
 ✓ src/services/portalApi.test.ts (4 tests) 56ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 218ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 46ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/authSession.test.ts (15 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 16ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 18ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2652ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2243ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 710ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  444ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1149ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1412ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  849ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  473ms

 Test Files  27 passed (27)
      Tests  176 passed (176)
   Start at  15:46:37
   Duration  4.48s (transform 3.14s, setup 0ms, collect 5.92s, tests 6.98s, environment 1.37s, prepare 2.05s)

