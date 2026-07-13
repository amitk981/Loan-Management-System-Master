# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_044409_architecture_review/sfpcl-lms

 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 271ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 835ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  452ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1082ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  389ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1378ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  308ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 149ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1924ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  997ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  736ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 37ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/services/authSession.test.ts (15 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 38ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 14ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3361ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2902ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 6967ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3049ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1125ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  954ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1101ms

 Test Files  29 passed (29)
      Tests  207 passed (207)
   Start at  04:58:06
   Duration  10.19s (transform 4.50s, setup 0ms, collect 7.08s, tests 16.65s, environment 2.33s, prepare 1.72s)

