# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_152156_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1225ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  732ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1364ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  482ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1503ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  716ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  351ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1960ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  350ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  333ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2492ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1279ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  956ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 273ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 203ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 698ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 209ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 84ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 103ms
 ✓ src/services/authSession.test.ts (36 tests) 35ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 48ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2919ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2391ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5252ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  561ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  419ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  336ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  329ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  364ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  349ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  308ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3641ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2177ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  15:53:20
   Duration  7.49s (transform 5.74s, setup 0ms, collect 10.51s, tests 22.33s, environment 5.38s, prepare 2.12s)

