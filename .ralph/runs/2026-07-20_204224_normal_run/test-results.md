# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_204224_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 893ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  320ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1193ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  707ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1365ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  658ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  358ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1815ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  356ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  308ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 757ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  455ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2844ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  550ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  410ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 469ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 536ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  461ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 179ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 349ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1192ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  370ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 963ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  319ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  400ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2435ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1281ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  916ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 293ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/services/authSession.test.ts (36 tests) 47ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 175ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 152ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 333ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5808ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  482ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  409ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  403ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  354ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  403ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  361ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  373ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  326ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  723ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 130ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 72ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 48ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 56ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 14ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 49ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5117ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2684ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1154ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1053ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  21:55:17
   Duration  9.14s (transform 4.65s, setup 0ms, collect 14.13s, tests 28.67s, environment 6.63s, prepare 2.93s)


Duration milliseconds: 9945
Exit code: 0
