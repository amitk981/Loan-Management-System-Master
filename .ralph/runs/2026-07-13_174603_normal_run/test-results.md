# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_174603_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 54ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 98ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 99ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 94ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 222ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 328ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 40ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 53ms
 ✓ src/services/authSession.test.ts (15 tests) 16ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/services/portalApi.test.ts (4 tests) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 25ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 81ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 16ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 26ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 20ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 48ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2995ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2647ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 459ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1328ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  381ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  724ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1415ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  436ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2264ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  682ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2609ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1281ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1132ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2886ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1653ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  18:21:43
   Duration  8.92s (transform 5.66s, setup 0ms, collect 11.40s, tests 15.30s, environment 3.87s, prepare 2.42s)

