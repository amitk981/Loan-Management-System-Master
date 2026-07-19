# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_154507_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1180ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  306ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  669ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 880ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  338ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1403ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  664ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  364ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1967ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  402ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  315ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 677ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  432ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2763ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  582ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  465ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  333ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 374ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 498ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  410ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 177ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 788ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  358ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  406ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2453ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1224ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  937ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 391ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1179ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  406ms
 ✓ src/services/authSession.test.ts (36 tests) 39ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 265ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 255ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 344ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 189ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 94ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5677ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  487ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  406ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  331ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  349ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  310ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  379ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  304ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  775ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 22ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 112ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 71ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 18ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 53ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 24ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5317ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2527ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  308ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  439ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  391ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  344ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1277ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1174ms

 Test Files  42 passed (42)
      Tests  351 passed (351)
   Start at  16:15:34
   Duration  9.44s (transform 4.85s, setup 0ms, collect 15.31s, tests 28.72s, environment 6.14s, prepare 2.92s)


Duration milliseconds: 9967
Exit code: 0
