# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_141135_architecture_review/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 91ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 55ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 122ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 86ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 210ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 208ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 39ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 28ms
 ✓ src/services/portalApi.test.ts (4 tests) 11ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 26ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2212ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1968ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (3 tests) 416ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  332ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 926ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1164ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  670ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  417ms

 Test Files  27 passed (27)
      Tests  175 passed (175)
   Start at  14:27:32
   Duration  3.67s (transform 2.92s, setup 0ms, collect 5.36s, tests 5.77s, environment 1.07s, prepare 1.63s)

