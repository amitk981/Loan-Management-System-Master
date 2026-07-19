# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_022525_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1239ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  577ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  348ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1341ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  437ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1840ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  372ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2311ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1145ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  872ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2415ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  479ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  468ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 957ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  585ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1132ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  337ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  468ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 711ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 521ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  417ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 644ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  403ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 409ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 339ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 161ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 319ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 271ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 155ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5302ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  404ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  352ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  323ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  380ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  328ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  406ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  331ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  582ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 144ms
 ✓ src/services/authSession.test.ts (36 tests) 29ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 64ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 42ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 57ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 33ms
 ✓ src/services/portalApi.test.ts (7 tests) 40ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 15ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4399ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2299ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2420ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2227ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  03:03:07
   Duration  8.18s (transform 4.91s, setup 0ms, collect 12.39s, tests 27.57s, environment 5.80s, prepare 2.60s)


Duration milliseconds: 8714
Exit code: 0
