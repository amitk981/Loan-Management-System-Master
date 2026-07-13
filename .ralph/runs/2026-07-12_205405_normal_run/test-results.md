# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_205405_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 73ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 128ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 158ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 97ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 311ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 301ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 59ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 33ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/authSession.test.ts (15 tests) 40ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 15ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (1 test) 23ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2927ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2627ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 601ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  365ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 996ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1273ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  738ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  432ms

 Test Files  28 passed (28)
      Tests  177 passed (177)
   Start at  21:08:47
   Duration  4.48s (transform 4.00s, setup 0ms, collect 7.52s, tests 7.19s, environment 1.67s, prepare 1.84s)

