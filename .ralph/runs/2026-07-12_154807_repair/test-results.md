# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_150856_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 33ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 78ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 189ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 198ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 45ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 12ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/services/authSession.test.ts (15 tests) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 13ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2204ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1925ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 564ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  349ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 959ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1214ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  728ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  396ms

 Test Files  27 passed (27)
      Tests  176 passed (176)
   Start at  15:55:07
   Duration  3.70s (transform 2.85s, setup 0ms, collect 5.35s, tests 5.87s, environment 1.06s, prepare 1.65s)

