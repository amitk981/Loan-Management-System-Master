# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_171448_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 71ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 77ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 181ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 180ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 3ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (1 test) 25ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2395ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2030ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 576ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  354ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 971ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1221ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  712ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  415ms

 Test Files  28 passed (28)
      Tests  177 passed (177)
   Start at  18:00:15
   Duration  3.90s (transform 2.93s, setup 0ms, collect 5.36s, tests 6.04s, environment 1.80s, prepare 1.79s)

