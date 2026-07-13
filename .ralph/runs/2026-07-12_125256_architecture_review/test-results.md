# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_125256_architecture_review/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 79ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 103ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 200ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 252ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1971ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1726ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (2 tests) 331ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (3 tests) 559ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  453ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 952ms

 Test Files  27 passed (27)
      Tests  173 passed (173)
   Start at  13:06:41
   Duration  3.28s (transform 2.39s, setup 0ms, collect 4.60s, tests 4.77s, environment 986ms, prepare 1.58s)

