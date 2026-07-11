# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-11_191720_architecture_review/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (3 tests) 60ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 92ms
 ✓ src/pages/members/MemberProfile.test.tsx (25 tests) 220ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (18 tests) 221ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 25ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 34ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (4 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/portalApi.test.ts (4 tests) 13ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 3ms

 Test Files  24 passed (24)
      Tests  146 passed (146)
   Start at  19:32:59
   Duration  1.61s (transform 1.52s, setup 0ms, collect 4.33s, tests 973ms, environment 3ms, prepare 1.47s)

