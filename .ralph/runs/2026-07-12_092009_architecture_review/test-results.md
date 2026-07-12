# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_092009_architecture_review/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 80ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 231ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 225ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 43ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/authSession.test.ts (15 tests) 13ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 12ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1826ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1669ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (3 tests) 495ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  397ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 882ms

 Test Files  26 passed (26)
      Tests  171 passed (171)
   Start at  09:34:27
   Duration  3.16s (transform 2.38s, setup 0ms, collect 4.39s, tests 4.17s, environment 688ms, prepare 1.57s)

