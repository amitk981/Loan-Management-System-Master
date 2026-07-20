# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_010045_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 952ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  331ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  360ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1106ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  620ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1465ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  709ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  361ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1808ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  372ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2549ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  534ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  456ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 636ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  400ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 311ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 484ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  383ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 210ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 334ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2435ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1139ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1046ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1086ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  398ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  425ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1328ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  383ms
 ✓ src/services/authSession.test.ts (36 tests) 35ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 278ms
 ✓ src/services/portalApi.test.ts (7 tests) 30ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 181ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 295ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 143ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5657ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  493ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  427ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  309ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  446ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  329ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  388ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  336ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  661ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 21ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 67ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4735ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2506ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  308ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 45ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 17ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1066ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  968ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  01:39:34
   Duration  8.76s (transform 4.35s, setup 0ms, collect 13.01s, tests 27.64s, environment 6.35s, prepare 2.66s)


Duration milliseconds: 9521
Exit code: 0
