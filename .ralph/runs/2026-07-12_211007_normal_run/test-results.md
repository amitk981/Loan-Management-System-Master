# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_211007_normal_run/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 74ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 44ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 78ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 221ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 207ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 4ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (1 test) 25ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2281ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1798ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 768ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 928ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1232ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  703ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  434ms

 Test Files  28 passed (28)
      Tests  183 passed (183)
   Start at  21:17:56
   Duration  3.93s (transform 2.64s, setup 0ms, collect 5.48s, tests 6.19s, environment 1.86s, prepare 1.61s)

