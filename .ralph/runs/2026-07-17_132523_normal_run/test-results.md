# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_132523_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 852ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  334ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1177ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  776ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1679ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  652ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  514ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2115ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  455ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 637ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  409ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2903ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  513ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  595ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  374ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 531ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  445ms
 ✓ src/services/authSession.test.ts (36 tests) 39ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 457ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 599ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  319ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 156ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1402ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  452ms
 ✓ src/services/portalApi.test.ts (6 tests) 42ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 18ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2622ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1157ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1134ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 263ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 511ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 18ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 21ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 139ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 56ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 49ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 65ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 58ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 55ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6681ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  508ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  483ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  324ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  323ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  334ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  552ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  436ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  866ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1553ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1439ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5634ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3396ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  370ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  368ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  363ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  14:20:08
   Duration  9.08s (transform 4.71s, setup 0ms, collect 13.32s, tests 30.41s, environment 5.14s, prepare 3.27s)


Duration milliseconds: 10077
Exit code: 0
