# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_150856_normal_run/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 70ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 93ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 174ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 183ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms
 ✓ src/services/authSession.test.ts (15 tests) 11ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 4ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2040ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1774ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 571ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  347ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 974ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1232ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  705ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  446ms

 Test Files  27 passed (27)
      Tests  176 passed (176)
   Start at  15:20:01
   Duration  3.56s (transform 2.79s, setup 0ms, collect 4.93s, tests 5.68s, environment 903ms, prepare 1.62s)

