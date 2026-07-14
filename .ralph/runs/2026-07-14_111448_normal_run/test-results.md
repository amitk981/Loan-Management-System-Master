# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_111448_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1192ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  354ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  649ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1450ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  527ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1484ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  699ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  367ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1918ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  401ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  353ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2667ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1305ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1036ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 181ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 337ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 699ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 111ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 170ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 85ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 14ms
 ✓ src/services/authSession.test.ts (36 tests) 35ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 43ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2924ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2364ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  324ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5341ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  583ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  405ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  369ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  365ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  307ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  305ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  361ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  322ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  371ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3649ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2228ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  11:43:04
   Duration  7.23s (transform 5.54s, setup 0ms, collect 10.23s, tests 22.60s, environment 4.51s, prepare 2.14s)

