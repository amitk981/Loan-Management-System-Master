# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_075837_architecture_review/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 886ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  317ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1198ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  716ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1372ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  628ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  360ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1869ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  350ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 561ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  350ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2738ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  549ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  498ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  388ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 574ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  474ms
 ✓ src/services/authSession.test.ts (36 tests) 54ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 256ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 380ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1340ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  457ms
 ✓ src/services/portalApi.test.ts (6 tests) 22ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 176ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2472ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1197ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  974ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 109ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 72ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 49ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 54ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 54ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 45ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 24ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5733ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  460ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  392ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  331ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  336ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  400ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  397ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  325ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  725ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4662ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2614ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  361ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  412ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1297ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1194ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  08:19:36
   Duration  7.96s (transform 4.26s, setup 0ms, collect 11.96s, tests 26.18s, environment 4.67s, prepare 2.72s)


Duration milliseconds: 8747
Exit code: 0
