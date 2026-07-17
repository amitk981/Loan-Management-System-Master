# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_013956_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1489ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  518ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1490ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  674ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  470ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2079ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  448ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2578ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  613ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  464ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2723ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1455ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  924ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1033ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  586ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 887ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  344ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  313ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 581ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  367ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 273ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 492ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  410ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 163ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 67ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 155ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 65ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/services/authSession.test.ts (36 tests) 42ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5691ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  468ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  553ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  305ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  372ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  324ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  350ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  349ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  333ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  660ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2578ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2219ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4370ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2403ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  02:16:49
   Duration  7.79s (transform 4.90s, setup 0ms, collect 11.46s, tests 27.11s, environment 4.35s, prepare 2.36s)


Duration milliseconds: 8335
Exit code: 0
