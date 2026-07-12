# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_105158_normal_run/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 74ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 91ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 215ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 177ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 28ms
 ✓ src/services/authSession.test.ts (15 tests) 15ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1962ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1732ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (2 tests) 325ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (3 tests) 552ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  453ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 911ms

 Test Files  27 passed (27)
      Tests  173 passed (173)
   Start at  11:15:57
   Duration  3.46s (transform 2.72s, setup 0ms, collect 4.93s, tests 4.67s, environment 928ms, prepare 1.70s)

