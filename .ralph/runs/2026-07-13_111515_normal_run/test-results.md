# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_111515_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 37ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 97ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 89ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 258ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 243ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/authSession.test.ts (15 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 18ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 10ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 286ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2840ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1933ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  459ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  448ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 886ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  494ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1064ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  354ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1319ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1711ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  972ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  582ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2505ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1319ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  12:04:09
   Duration  6.37s (transform 3.94s, setup 0ms, collect 7.19s, tests 11.67s, environment 2.55s, prepare 1.77s)

