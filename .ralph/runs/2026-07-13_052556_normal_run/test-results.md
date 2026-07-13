# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_052556_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 253ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 870ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  465ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 162ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1097ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  376ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1356ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 171ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 89ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 73ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2004ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1034ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  771ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 48ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3388ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2958ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 7032ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3074ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1156ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  967ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1104ms

 Test Files  29 passed (29)
      Tests  207 passed (207)
   Start at  05:37:53
   Duration  10.27s (transform 4.64s, setup 0ms, collect 7.42s, tests 16.84s, environment 2.28s, prepare 1.75s)

