# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_095146_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1399ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  429ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1431ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  627ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  469ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2037ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  394ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  308ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2686ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1248ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1125ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2732ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  656ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  521ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  333ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 977ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  593ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 939ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  317ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 619ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  432ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 312ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 476ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  398ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 176ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 183ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 111ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 79ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 33ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 53ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 46ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/services/authSession.test.ts (36 tests) 30ms
 ✓ src/services/portalApi.test.ts (6 tests) 25ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5498ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  481ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  572ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  322ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  310ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  316ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  345ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  333ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  307ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  536ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2610ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2217ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4236ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2270ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  10:36:33
   Duration  7.63s (transform 4.83s, setup 0ms, collect 11.12s, tests 26.87s, environment 4.38s, prepare 2.34s)


Duration milliseconds: 8175
Exit code: 0
