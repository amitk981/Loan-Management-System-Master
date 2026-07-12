# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_150856_normal_run/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 74ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 78ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 83ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 182ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 186ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 35ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/services/portalApi.test.ts (4 tests) 12ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2038ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1783ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 580ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  350ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 946ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1247ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  713ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  453ms

 Test Files  27 passed (27)
      Tests  176 passed (176)
   Start at  15:27:57
   Duration  3.68s (transform 2.73s, setup 0ms, collect 5.19s, tests 5.70s, environment 850ms, prepare 1.57s)

