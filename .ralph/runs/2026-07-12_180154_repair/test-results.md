# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_171448_normal_run/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 35ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 199ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 184ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 46ms
 ✓ src/services/authSession.test.ts (15 tests) 17ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 20ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 13ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 18ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (1 test) 26ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2386ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1999ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 560ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  335ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 924ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1215ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  704ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  416ms

 Test Files  28 passed (28)
      Tests  177 passed (177)
   Start at  18:13:30
   Duration  3.91s (transform 3.06s, setup 0ms, collect 5.62s, tests 6.03s, environment 1.86s, prepare 1.89s)

