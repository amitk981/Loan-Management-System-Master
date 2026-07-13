# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_150856_normal_run/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 76ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 79ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 178ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 220ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 49ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 42ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/services/authSession.test.ts (15 tests) 13ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 13ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1914ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1714ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 556ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  332ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 963ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1173ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  682ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  412ms

 Test Files  27 passed (27)
      Tests  176 passed (176)
   Start at  15:36:14
   Duration  3.59s (transform 2.67s, setup 0ms, collect 4.99s, tests 5.53s, environment 966ms, prepare 1.69s)

