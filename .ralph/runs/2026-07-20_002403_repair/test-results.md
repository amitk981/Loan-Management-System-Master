# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_233905_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1626ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  570ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1599ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  760ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  426ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2602ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  505ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  413ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3002ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1441ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1227ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3601ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  679ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  538ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  534ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1589ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  316ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  891ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1608ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  536ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  341ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  689ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 792ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  481ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1053ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  375ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  303ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 784ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  662ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 475ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 498ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 382ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 651ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  397ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 228ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 332ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 319ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 98ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 150ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7980ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  682ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  579ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  424ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  411ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  436ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  500ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  415ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  360ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  553ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  538ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  941ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 133ms
 ✓ src/services/authSession.test.ts (36 tests) 51ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 42ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 57ms
 ✓ src/services/portalApi.test.ts (7 tests) 20ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 24ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 19ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 16ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 7026ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3934ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  426ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  391ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  354ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  350ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  310ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 28ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3412ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3020ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  00:31:52
   Duration  11.77s (transform 6.33s, setup 0ms, collect 16.88s, tests 40.37s, environment 9.02s, prepare 3.38s)


Duration milliseconds: 12474
Exit code: 0
