# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_020758_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 951ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  325ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  353ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1251ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  737ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1464ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  718ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  361ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1905ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  327ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2517ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  620ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  430ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 634ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  411ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 529ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  441ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 288ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (4 tests) 364ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 393ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1337ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  455ms
 ✓ src/services/authSession.test.ts (36 tests) 42ms
 ✓ src/services/portalApi.test.ts (7 tests) 23ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2510ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1174ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1083ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 167ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 182ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 135ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 77ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 63ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 54ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5743ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  443ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  409ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  347ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  465ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  423ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  679ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4522ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2380ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  313ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1194ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1096ms

 Test Files  38 passed (38)
      Tests  334 passed (334)
   Start at  02:41:08
   Duration  8.12s (transform 4.65s, setup 0ms, collect 12.38s, tests 26.59s, environment 5.04s, prepare 2.69s)


Duration milliseconds: 8902
Exit code: 0
