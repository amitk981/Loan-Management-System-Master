# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_190359_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1483ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  333ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  853ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1572ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  800ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  353ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2207ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  311ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  376ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  322ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2581ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1325ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  980ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2787ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  606ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  464ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  353ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 775ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 621ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  397ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1328ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  441ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 577ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  506ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 316ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 221ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 88ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 173ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 76ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 218ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 40ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/services/portalApi.test.ts (7 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5605ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  613ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  394ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  383ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  306ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  316ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  307ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  390ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  311ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  352ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  542ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4395ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2498ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2462ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2192ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  19:56:42
   Duration  7.91s (transform 5.09s, setup 0ms, collect 11.87s, tests 27.89s, environment 5.73s, prepare 2.37s)


Duration milliseconds: 8640
Exit code: 0
