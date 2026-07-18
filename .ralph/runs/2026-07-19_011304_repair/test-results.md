# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_003418_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1403ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  497ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1680ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  610ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  458ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2444ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  554ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  302ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2853ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1268ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1301ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3403ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  788ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  804ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  326ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 904ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  365ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1317ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  476ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  614ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 643ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  382ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 565ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  476ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (4 tests) 270ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 277ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 146ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 151ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 64ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 66ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 152ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 34ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6149ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  513ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  775ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  304ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  335ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  358ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  331ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  358ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  392ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  327ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  562ms
 ✓ src/services/portalApi.test.ts (7 tests) 38ms
 ✓ src/services/authSession.test.ts (36 tests) 51ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 18ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2853ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2499ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4605ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2587ms

 Test Files  38 passed (38)
      Tests  334 passed (334)
   Start at  01:21:35
   Duration  8.49s (transform 5.61s, setup 0ms, collect 12.58s, tests 30.32s, environment 5.36s, prepare 2.57s)


Duration milliseconds: 8925
Exit code: 0
