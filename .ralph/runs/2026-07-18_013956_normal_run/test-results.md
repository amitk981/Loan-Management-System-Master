# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_013956_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 895ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  330ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1114ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  650ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1356ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  600ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  360ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1887ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  391ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  305ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 595ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  400ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2542ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  571ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  447ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 454ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  365ms
 ✓ src/services/authSession.test.ts (36 tests) 34ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 174ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 325ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 62ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1289ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  408ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/services/portalApi.test.ts (6 tests) 22ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 161ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 25ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2377ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1091ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  990ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 98ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 59ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 73ms
 ✓ src/services/tracerApi.test.ts (2 tests) 10ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 54ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5810ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  499ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  443ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  345ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  326ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  325ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  417ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  451ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  692ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4345ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2377ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  310ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  364ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1240ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1126ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  01:57:13
   Duration  7.82s (transform 4.48s, setup 0ms, collect 12.17s, tests 25.21s, environment 4.53s, prepare 2.79s)


Duration milliseconds: 8752
Exit code: 0
