# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_190027_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1281ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  613ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  342ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1382ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  440ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1689ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  305ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2278ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1087ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  923ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2334ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  457ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  380ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 826ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  335ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 985ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  565ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 703ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  465ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 292ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 495ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  421ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 161ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 162ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 79ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 58ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 61ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 73ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/services/authSession.test.ts (36 tests) 34ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/services/portalApi.test.ts (6 tests) 22ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 17ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5339ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  470ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  351ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  369ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  333ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  322ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  356ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  310ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  355ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  323ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  559ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 16ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2501ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2152ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4309ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2302ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  303ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  20:06:06
   Duration  7.41s (transform 4.64s, setup 0ms, collect 10.80s, tests 25.31s, environment 4.42s, prepare 2.37s)


Duration milliseconds: 7938
Exit code: 0
