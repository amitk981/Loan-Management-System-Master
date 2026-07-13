# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_182512_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 77ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 95ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 65ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 237ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 173ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 35ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 38ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 12ms
 ✓ src/services/authSession.test.ts (15 tests) 16ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 6ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 325ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 906ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  501ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3402ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2403ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  682ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  316ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1153ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  371ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1400ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1807ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1082ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  597ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2664ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1401ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  18:55:06
   Duration  7.04s (transform 4.62s, setup 0ms, collect 8.65s, tests 12.60s, environment 2.95s, prepare 1.99s)

