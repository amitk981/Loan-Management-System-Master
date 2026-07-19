# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_062443_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1707ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  654ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  672ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1881ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1007ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  420ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2681ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders a stale 409 without retry, synthesis, or refresh  456ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  416ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3105ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  336ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  796ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  417ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  466ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3250ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1805ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1168ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 835ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  308ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1291ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  458ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 891ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  351ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  523ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 752ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  480ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 552ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  465ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 426ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 450ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (4 tests) 308ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 171ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 200ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 163ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6420ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  646ms
   ✓ SanctionWorkbench authenticated container > clears prior rows and totals when a later collection fails with 'OBJECT_ACCESS_DENIED'  399ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  468ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  335ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  336ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  314ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  482ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  412ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  561ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 218ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 86ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4739ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2507ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  334ms
 ✓ src/services/portalApi.test.ts (7 tests) 20ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2353ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2183ms

 Test Files  42 passed (42)
      Tests  349 passed (349)
   Start at  07:22:53
   Duration  9.17s (transform 5.12s, setup 0ms, collect 13.18s, tests 32.91s, environment 7.09s, prepare 2.56s)


Duration milliseconds: 9916
Exit code: 0
