# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_122527_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 78ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 94ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 103ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 182ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 206ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 36ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 18ms
 ✓ src/services/authSession.test.ts (15 tests) 13ms
 ✓ src/services/portalApi.test.ts (4 tests) 13ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 265ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2785ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1935ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  449ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  400ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 810ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  470ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1011ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  387ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1236ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1709ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1007ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  551ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2507ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1323ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  12:51:16
   Duration  6.26s (transform 3.86s, setup 0ms, collect 7.20s, tests 11.29s, environment 2.34s, prepare 1.77s)

