# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_222951_architecture_review/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 77ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 88ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 201ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 174ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/services/authSession.test.ts (15 tests) 14ms
 ✓ src/services/portalApi.test.ts (4 tests) 13ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 16ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 279ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2853ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1990ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  491ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  372ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 810ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  476ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1009ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  367ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1227ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1774ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1007ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  608ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2485ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1291ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  22:54:40
   Duration  6.36s (transform 4.11s, setup 0ms, collect 7.52s, tests 11.33s, environment 2.38s, prepare 1.80s)

