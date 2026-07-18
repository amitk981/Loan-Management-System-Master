# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_090956_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1241ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  377ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  408ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2032ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  907ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  526ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1980ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  507ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1120ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 3120ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  607ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  535ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 1112ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  746ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 908ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  796ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 4744ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  909ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  409ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  747ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  828ms
 ✓ src/services/authSession.test.ts (36 tests) 121ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 370ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 122ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 539ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  318ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1999ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 400 failure without refetch  368ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  622ms
   ✓ mounted witness resource actions > corrects protected identity with an identity-only body  403ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 590ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 192ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 16ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3861ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1725ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1660ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 149ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 77ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 94ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 12ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 204ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 89ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 9589ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  760ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  711ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  627ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  627ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  517ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  439ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  623ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  452ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  674ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  762ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1282ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1896ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1710ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 7549ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  4845ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  646ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  555ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  363ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  09:43:32
   Duration  12.36s (transform 6.62s, setup 0ms, collect 17.96s, tests 42.73s, environment 7.94s, prepare 4.21s)


Duration milliseconds: 12980
Exit code: 0
