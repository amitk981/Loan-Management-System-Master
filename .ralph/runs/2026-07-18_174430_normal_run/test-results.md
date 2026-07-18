# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_174430_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1660ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  530ms
   ✓ mounted witness resource actions > corrects protected identity with an identity-only body  377ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1702ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  694ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  530ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2630ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  509ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  426ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3227ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1226ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1590ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3675ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  685ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  726ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  498ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 967ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  317ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  342ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1144ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  648ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 773ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  586ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 562ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  479ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 320ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 227ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 177ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 241ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 150ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 178ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 39ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 72ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 48ms
 ✓ src/services/authSession.test.ts (36 tests) 43ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 48ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6959ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  567ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  697ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  490ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  467ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  376ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  402ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  439ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  314ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  399ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  363ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  678ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3283ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3071ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4883ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2805ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  18:38:23
   Duration  9.42s (transform 6.87s, setup 0ms, collect 15.06s, tests 33.17s, environment 6.49s, prepare 3.07s)


Duration milliseconds: 10164
Exit code: 0
