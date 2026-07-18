# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_034024_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1572ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  662ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  454ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1606ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  624ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2035ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  466ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  312ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2703ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1342ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1066ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2800ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  705ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  511ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  369ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 942ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  385ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  527ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 956ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  544ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 808ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 634ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  369ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 488ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  423ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 290ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 460ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  331ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (4 tests) 278ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 157ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 206ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 163ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 163ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 81ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 63ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5859ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  455ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  493ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  367ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  353ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  313ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  457ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  396ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  639ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 53ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4410ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2305ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  303ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/services/disbursementApi.test.ts (2 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2400ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2223ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  42 passed (42)
      Tests  348 passed (348)
   Start at  04:08:38
   Duration  8.40s (transform 4.67s, setup 0ms, collect 11.88s, tests 29.42s, environment 5.87s, prepare 2.52s)


Duration milliseconds: 8924
Exit code: 0
