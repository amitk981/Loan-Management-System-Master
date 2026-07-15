# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_030045_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1002ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  578ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1170ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  396ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1388ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  638ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  395ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1673ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  305ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 241ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2309ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1085ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  904ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 185ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 637ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 167ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/services/authSession.test.ts (36 tests) 33ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2678ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2120ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  303ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 4828ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  422ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  304ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  356ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  371ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  433ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3399ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1917ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  03:43:03
   Duration  6.53s (transform 4.75s, setup 0ms, collect 9.04s, tests 20.18s, environment 3.45s, prepare 2.06s)

