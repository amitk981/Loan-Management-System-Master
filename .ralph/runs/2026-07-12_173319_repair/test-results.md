# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_171448_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 38ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 85ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 195ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 227ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 42ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 47ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 15ms
 ✓ src/services/authSession.test.ts (15 tests) 18ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (1 test) 24ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2349ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1935ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 609ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  372ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1014ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1319ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  758ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  465ms

 Test Files  28 passed (28)
      Tests  177 passed (177)
   Start at  17:43:45
   Duration  3.93s (transform 3.01s, setup 0ms, collect 5.56s, tests 6.28s, environment 1.80s, prepare 1.85s)

