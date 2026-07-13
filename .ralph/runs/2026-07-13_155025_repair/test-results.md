# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_145943_normal_run/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 40ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 204ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 191ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 47ms
 ✓ src/services/authSession.test.ts (15 tests) 14ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 16ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 25ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2344ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1936ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 328ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 953ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  542ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1094ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  369ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1463ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1773ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1041ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  604ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2487ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1304ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  16:02:06
   Duration  6.90s (transform 4.10s, setup 0ms, collect 8.66s, tests 11.39s, environment 3.56s, prepare 1.93s)

