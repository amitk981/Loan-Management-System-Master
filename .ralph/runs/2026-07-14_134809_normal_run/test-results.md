# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_134809_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1161ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  687ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1417ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  561ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1519ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  777ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  421ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2014ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  433ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  308ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2481ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1285ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  943ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 315ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 222ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 696ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 89ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 167ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 92ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 50ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 40ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 17ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/portalApi.test.ts (4 tests) 12ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3157ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2581ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  421ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5315ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  504ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  407ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  327ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  359ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  333ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  440ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3733ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2361ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  14:31:40
   Duration  7.44s (transform 5.57s, setup 0ms, collect 10.50s, tests 22.80s, environment 4.47s, prepare 2.22s)

