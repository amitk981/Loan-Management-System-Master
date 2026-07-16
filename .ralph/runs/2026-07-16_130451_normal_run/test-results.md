# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_130451_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1725ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  368ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1014ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2006ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  865ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  528ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2733ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  353ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  606ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  384ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3121ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1575ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1259ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (17 tests) 3421ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  377ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  800ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  663ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 803ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  334ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1329ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  458ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 668ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  386ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 595ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  452ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 386ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 184ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 166ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 84ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/services/authSession.test.ts (36 tests) 36ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 48ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
(node:12579) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 23ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 31ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 17ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7017ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  701ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  617ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  540ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  333ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  375ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  351ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  383ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  381ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  879ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2824ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2286ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  306ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4964ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2878ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  342ms

 Test Files  36 passed (36)
      Tests  322 passed (322)
   Start at  14:03:59
   Duration  9.31s (transform 5.83s, setup 0ms, collect 13.24s, tests 32.54s, environment 6.56s, prepare 2.43s)

