# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_213220_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 917ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  333ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1189ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  332ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  653ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1384ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  627ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  375ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1924ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  338ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  320ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2439ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  544ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  376ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 584ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  373ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 509ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  418ms
 ✓ src/services/authSession.test.ts (36 tests) 29ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 163ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 286ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 60ms
 ✓ src/services/portalApi.test.ts (6 tests) 21ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 15ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 148ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1241ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  423ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2124ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1015ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  848ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 115ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 27ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 34ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 73ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5564ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  579ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  425ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  323ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  305ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  323ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  696ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4327ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2215ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1124ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1024ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  21:46:19
   Duration  7.28s (transform 3.92s, setup 0ms, collect 10.72s, tests 24.53s, environment 4.50s, prepare 2.32s)


Duration milliseconds: 8061
Exit code: 0
