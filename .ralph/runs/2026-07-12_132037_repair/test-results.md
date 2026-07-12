# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_130806_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 38ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 91ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 251ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 194ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 36ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/services/authSession.test.ts (15 tests) 17ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1953ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1712ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (2 tests) 341ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (3 tests) 576ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  469ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 977ms

 Test Files  27 passed (27)
      Tests  173 passed (173)
   Start at  13:30:38
   Duration  3.19s (transform 2.44s, setup 0ms, collect 4.74s, tests 4.82s, environment 791ms, prepare 1.53s)

