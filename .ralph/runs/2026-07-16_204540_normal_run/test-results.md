# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_204540_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 823ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1317ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  840ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1432ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  676ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  381ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1946ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  325ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 602ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  391ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2642ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  568ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  369ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 538ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  454ms
 ✓ src/services/authSession.test.ts (36 tests) 44ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 199ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 310ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1170ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  374ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 224ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2242ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1143ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  827ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 74ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 42ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 44ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5352ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  540ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  364ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  332ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  343ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  307ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  581ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 17ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 20ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4389ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2471ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  342ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1165ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1061ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  21:26:15
   Duration  7.71s (transform 4.23s, setup 0ms, collect 11.83s, tests 24.96s, environment 4.94s, prepare 2.77s)


Duration milliseconds: 8457
Exit code: 0
