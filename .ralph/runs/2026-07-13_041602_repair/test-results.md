# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_033219_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 261ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 847ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  493ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 159ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1099ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  369ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1363ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 145ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 61ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 36ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1998ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1017ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  756ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/portalApi.test.ts (4 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3383ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2868ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 12ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 10ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 7070ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3066ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1153ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  976ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1137ms

 Test Files  29 passed (29)
      Tests  207 passed (207)
   Start at  04:22:13
   Duration  10.20s (transform 4.46s, setup 0ms, collect 7.23s, tests 16.81s, environment 2.34s, prepare 1.74s)

