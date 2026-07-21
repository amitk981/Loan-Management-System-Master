# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_074659_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 976ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  331ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  326ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1180ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  740ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1376ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  615ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  357ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2087ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  387ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  328ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 721ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  431ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 494ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3070ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  628ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  479ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  501ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 556ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  480ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 217ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2583ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1399ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  925ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 953ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  354ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  392ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1192ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  357ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 437ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 220ms
 ✓ src/services/portalApi.test.ts (7 tests) 32ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 166ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 15ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 347ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 84ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 176ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 93ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6127ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  596ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  433ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  304ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  522ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  402ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  364ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  307ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  378ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  374ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  661ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 88ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 15ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5470ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3228ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  301ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  349ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 55ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1032ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  934ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  08:11:26
   Duration  9.20s (transform 3.94s, setup 0ms, collect 12.69s, tests 29.99s, environment 6.79s, prepare 2.87s)


Duration milliseconds: 10034
Exit code: 0
