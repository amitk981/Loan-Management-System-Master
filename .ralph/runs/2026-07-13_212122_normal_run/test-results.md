# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_212122_normal_run/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 83ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 80ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 173ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 180ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 261ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2938ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2089ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  457ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  391ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 816ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  450ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1025ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  362ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1273ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1721ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  975ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  589ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2511ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1292ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  21:54:31
   Duration  6.50s (transform 4.06s, setup 0ms, collect 7.88s, tests 11.41s, environment 2.35s, prepare 1.76s)

