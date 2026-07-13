# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_100911_architecture_review/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 76ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 87ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 177ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 215ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 60ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 14ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 424ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3462ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2331ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  603ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  528ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1148ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  333ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  656ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1319ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  463ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1622ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1972ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1255ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  594ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2504ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1318ms

 Test Files  29 passed (29)
      Tests  208 passed (208)
   Start at  10:29:22
   Duration  7.08s (transform 4.75s, setup 0ms, collect 8.99s, tests 13.39s, environment 2.86s, prepare 1.93s)

