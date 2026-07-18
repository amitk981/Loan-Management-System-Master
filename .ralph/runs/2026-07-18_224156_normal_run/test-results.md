# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_224156_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 981ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  323ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  373ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1166ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  694ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1344ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  605ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  396ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1976ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  336ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  332ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2566ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  601ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  471ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  315ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 577ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  343ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 543ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  470ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 150ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 248ms
 ✓ src/services/authSession.test.ts (36 tests) 40ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 350ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1140ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  377ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2175ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1081ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  859ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 80ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 191ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 80ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 17ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 62ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5630ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  543ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  407ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  356ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  308ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  302ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  340ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  314ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  654ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4496ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2406ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1156ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1056ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  23:14:35
   Duration  7.84s (transform 4.10s, setup 0ms, collect 11.59s, tests 25.30s, environment 5.15s, prepare 2.53s)


Duration milliseconds: 8632
Exit code: 0
