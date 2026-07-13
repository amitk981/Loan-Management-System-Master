# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_053920_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 254ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 802ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  452ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 176ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1078ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  376ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 70ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1358ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 161ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 57ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 35ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2020ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1026ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  770ms
 ✓ src/services/authSession.test.ts (15 tests) 11ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 10ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3339ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2876ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 7177ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3186ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1163ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  981ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1118ms

 Test Files  29 passed (29)
      Tests  207 passed (207)
   Start at  05:51:52
   Duration  10.33s (transform 4.37s, setup 0ms, collect 7.02s, tests 16.85s, environment 2.38s, prepare 1.77s)

