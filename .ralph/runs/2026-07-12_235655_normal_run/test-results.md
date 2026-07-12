# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_235655_normal_run/sfpcl-lms

 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 137ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 253ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 68ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 166ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 986ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  328ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 64ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1250ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1839ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  950ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  692ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/portalApi.test.ts (4 tests) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 4ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3120ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2718ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 6982ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3009ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1152ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  962ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1123ms

 Test Files  29 passed (29)
      Tests  202 passed (202)
   Start at  00:05:32
   Duration  10.06s (transform 4.81s, setup 0ms, collect 7.43s, tests 15.21s, environment 1.70s, prepare 1.65s)

