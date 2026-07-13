# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_094433_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 36ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 77ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 76ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 190ms
 ✓ src/services/authSession.test.ts (15 tests) 14ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 210ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 38ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/services/portalApi.test.ts (4 tests) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2045ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1860ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (3 tests) 596ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  470ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1086ms

 Test Files  26 passed (26)
      Tests  171 passed (171)
   Start at  10:37:06
   Duration  3.64s (transform 2.81s, setup 0ms, collect 5.06s, tests 4.65s, environment 736ms, prepare 1.74s)

