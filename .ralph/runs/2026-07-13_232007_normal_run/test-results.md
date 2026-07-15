# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_232007_normal_run/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 73ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 93ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 211ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 252ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 38ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 48ms
 ✓ src/services/authSession.test.ts (15 tests) 15ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 19ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 840ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  521ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3068ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2130ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  526ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  411ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1089ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  367ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1451ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  306ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 222ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2027ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1064ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  804ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (21 tests) 1955ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  398ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  346ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  398ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2541ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1327ms

 Test Files  29 passed (29)
      Tests  227 passed (227)
   Start at  00:00:14
   Duration  6.70s (transform 4.65s, setup 0ms, collect 8.14s, tests 14.19s, environment 2.76s, prepare 1.74s)

