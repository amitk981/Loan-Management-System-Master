# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_110722_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1306ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  395ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  565ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1692ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  428ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1052ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2338ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1081ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  604ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 3018ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  322ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  565ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  409ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 827ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  571ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3759ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  664ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  746ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  564ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 491ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 667ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  558ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 253ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 1073ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  507ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  510ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3028ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1503ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1201ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 280ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 493ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  355ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1700ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  516ms
 ✓ src/services/authSession.test.ts (36 tests) 50ms
 ✓ src/services/portalApi.test.ts (7 tests) 37ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 108ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 285ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 18ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 28ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 600ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 23ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 18ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 396ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 150ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 8286ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  709ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  651ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  510ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  515ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  571ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  452ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  457ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  407ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  473ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  454ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1222ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 12ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 107ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 66ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 51ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 116ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 7221ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3940ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  376ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  313ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  476ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  304ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  461ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  322ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1363ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1201ms

 Test Files  42 passed (42)
      Tests  351 passed (351)
   Start at  12:02:39
   Duration  12.68s (transform 6.89s, setup 0ms, collect 20.44s, tests 39.96s, environment 9.14s, prepare 3.47s)


Duration milliseconds: 13364
Exit code: 0
