# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_091510_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 79ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 87ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 233ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 235ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 42ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/services/authSession.test.ts (15 tests) 16ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 14ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 257ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2868ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1989ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  483ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  395ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 791ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  466ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1022ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  369ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1289ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1745ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  999ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  586ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2505ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1286ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  09:38:13
   Duration  6.35s (transform 4.04s, setup 0ms, collect 7.24s, tests 11.47s, environment 2.28s, prepare 1.82s)

