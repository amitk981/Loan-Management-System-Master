# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_133148_normal_run/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 72ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 103ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 200ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 223ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2054ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1826ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (2 tests) 350ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 956ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1245ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  715ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  447ms

 Test Files  27 passed (27)
      Tests  174 passed (174)
   Start at  13:42:08
   Duration  3.52s (transform 2.63s, setup 0ms, collect 4.85s, tests 5.55s, environment 922ms, prepare 1.58s)

