# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_042414_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 279ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 841ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  487ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 144ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1018ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  363ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1349ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 158ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 73ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1900ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  977ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  726ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/services/authSession.test.ts (15 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 40ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 21ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3339ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2925ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 7199ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3189ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1158ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  988ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1129ms

 Test Files  29 passed (29)
      Tests  207 passed (207)
   Start at  04:42:46
   Duration  10.21s (transform 4.51s, setup 0ms, collect 7.09s, tests 16.74s, environment 2.35s, prepare 1.72s)

