# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_081752_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1448ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  427ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  324ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2160ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  346ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1461ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2183ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  655ms
   ✓ SettingsHub remaining panels > loads retained policy versions from the authenticated configuration boundary without exposing edits to a reader  347ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  607ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2784ms
   ✓ default AppraisalWorkbench authenticated HTTP container > clicks 'submit review' through the authenticated boundary and refreshes four reads  431ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  516ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  413ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3657ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  1111ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  324ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  487ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  357ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 714ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  477ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 513ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  449ms
 ✓ src/services/authSession.test.ts (36 tests) 36ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 191ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 343ms
 ✓ src/services/portalApi.test.ts (6 tests) 22ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1230ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  420ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 183ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 96ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 15ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2391ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1103ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  974ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 117ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 75ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 57ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 45ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6630ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  723ms
   ✓ SanctionWorkbench authenticated container > clears prior rows and totals when a later collection fails with 'MALFORMED_RESPONSE'  545ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  481ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  405ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  391ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  399ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  378ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  334ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  311ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  683ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4790ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2763ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1152ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1053ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  08:43:16
   Duration  8.97s (transform 4.98s, setup 0ms, collect 13.47s, tests 31.05s, environment 5.55s, prepare 2.45s)


Duration milliseconds: 10016
Exit code: 0
