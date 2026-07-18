# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_155947_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 869ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  313ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  305ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1383ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  373ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  775ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1426ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  631ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  416ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1909ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  369ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  307ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 613ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  372ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2701ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  518ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  512ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 650ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  463ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 208ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 219ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 336ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1545ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 400 failure without refetch  304ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  488ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2721ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1350ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1102ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 153ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 13ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 83ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 50ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 12ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6035ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  490ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  430ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  390ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  347ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  423ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  449ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  384ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  375ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  786ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4850ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2979ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1136ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1033ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  16:17:12
   Duration  9.08s (transform 4.38s, setup 0ms, collect 13.15s, tests 27.34s, environment 6.93s, prepare 2.75s)


Duration milliseconds: 10092
Exit code: 0
