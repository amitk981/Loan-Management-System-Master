# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_154507_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1128ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  670ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1356ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  593ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  389ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1837ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  381ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2289ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1110ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  909ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2451ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  515ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  427ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 803ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  306ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1281ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  430ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 663ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  444ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 576ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  483ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 954ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  367ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  560ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 549ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 546ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 405ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 202ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 210ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 96ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 182ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 283ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 88ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6038ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  542ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  358ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  341ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  330ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  334ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  302ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  451ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  532ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  773ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 94ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 77ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 26ms
 ✓ src/services/portalApi.test.ts (7 tests) 30ms
 ✓ src/services/authSession.test.ts (36 tests) 31ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 60ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5095ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2763ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  414ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  337ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2425ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2170ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  42 passed (42)
      Tests  351 passed (351)
   Start at  16:51:22
   Duration  9.09s (transform 5.03s, setup 0ms, collect 13.06s, tests 29.92s, environment 7.28s, prepare 2.83s)


Duration milliseconds: 9628
Exit code: 0
