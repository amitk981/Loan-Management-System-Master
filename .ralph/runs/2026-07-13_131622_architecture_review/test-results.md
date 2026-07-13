# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_131622_architecture_review/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 78ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 96ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 49ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 246ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 297ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 55ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/services/authSession.test.ts (15 tests) 21ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 88ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 31ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 15ms
 ✓ src/services/portalApi.test.ts (4 tests) 15ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2980ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2121ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  381ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  477ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 392ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1091ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  578ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1184ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  369ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1576ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1959ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1098ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  701ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2799ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1469ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  13:47:25
   Duration  7.42s (transform 4.58s, setup 0ms, collect 8.64s, tests 13.15s, environment 3.15s, prepare 2.22s)

