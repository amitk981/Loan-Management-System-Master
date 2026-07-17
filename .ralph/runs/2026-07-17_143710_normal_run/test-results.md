# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_143710_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1440ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  372ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  467ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1697ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1193ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1935ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  809ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  497ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2811ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders HTTP 400 once without retry or refresh  331ms
   ✓ default AppraisalWorkbench authenticated HTTP container > clicks 'create' through the authenticated boundary and refreshes four reads  337ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  403ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  498ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3869ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  933ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  560ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  507ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 1029ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  637ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 628ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  539ms
 ✓ src/services/authSession.test.ts (36 tests) 57ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 197ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 311ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 76ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2618ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1435ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  947ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1170ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  399ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 160ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 21ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 16ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 130ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 77ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 112ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 52ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 49ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 46ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 21ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6983ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  472ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  426ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  528ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  470ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  410ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  454ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  340ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  310ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  402ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  351ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  848ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5239ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3159ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  414ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  337ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1297ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1193ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  15:14:11
   Duration  9.63s (transform 5.35s, setup 0ms, collect 14.62s, tests 32.15s, environment 6.84s, prepare 3.27s)


Duration milliseconds: 10502
Exit code: 0
