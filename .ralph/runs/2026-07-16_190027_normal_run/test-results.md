# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_190027_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 919ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  322ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  304ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1145ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  626ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1379ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  679ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  338ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1862ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  382ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 618ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  383ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2579ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  569ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  446ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 500ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  431ms
 ✓ src/services/authSession.test.ts (36 tests) 50ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 171ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 273ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/services/portalApi.test.ts (6 tests) 20ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1218ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  421ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 157ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 18ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2353ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1198ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  888ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 102ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 78ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 58ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 61ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 51ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5442ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  483ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  423ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  324ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  308ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  323ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  314ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  707ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4124ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2100ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1247ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1147ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  19:15:41
   Duration  7.60s (transform 4.44s, setup 0ms, collect 11.73s, tests 24.66s, environment 4.59s, prepare 2.51s)


Duration milliseconds: 8347
Exit code: 0
