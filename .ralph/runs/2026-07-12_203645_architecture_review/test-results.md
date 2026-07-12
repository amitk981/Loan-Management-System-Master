# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_203645_architecture_review/sfpcl-lms

 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 97ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 54ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 138ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 127ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 219ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 207ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 23ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 17ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (1 test) 23ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2641ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2227ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (4 tests) 613ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  386ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 972ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1218ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  719ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  409ms

 Test Files  28 passed (28)
      Tests  177 passed (177)
   Start at  20:52:46
   Duration  4.06s (transform 3.67s, setup 0ms, collect 6.74s, tests 6.58s, environment 1.54s, prepare 1.97s)

