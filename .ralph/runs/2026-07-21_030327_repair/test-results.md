# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_020140_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1355ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  494ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1423ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  761ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  358ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2111ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  369ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  384ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2644ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1250ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1097ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2723ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  312ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  607ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  376ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  342ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 944ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  523ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1169ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  405ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  494ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 797ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 542ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  358ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 590ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  459ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 395ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 261ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 352ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 209ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 171ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 190ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 70ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5834ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  547ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  357ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  397ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  320ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  337ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  400ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  326ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  431ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  351ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  657ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/services/authSession.test.ts (36 tests) 45ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 80ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 94ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4424ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2194ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2396ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2148ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  03:14:02
   Duration  8.63s (transform 4.89s, setup 0ms, collect 12.62s, tests 29.31s, environment 6.25s, prepare 2.81s)


Duration milliseconds: 9163
Exit code: 0
