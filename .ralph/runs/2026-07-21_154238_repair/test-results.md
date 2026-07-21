# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1448ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  685ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  435ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1850ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  601ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  384ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  365ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2064ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  381ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2609ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1388ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  915ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2773ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  690ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  454ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  348ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 989ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  523ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1389ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  476ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1222ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  481ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  461ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 510ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  435ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 788ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 423ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 607ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  411ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 374ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 366ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 448ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 158ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 291ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6169ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  527ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  440ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  370ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  356ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  349ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  346ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  390ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  441ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  683ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 178ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 204ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 90ms
 ✓ src/services/authSession.test.ts (36 tests) 42ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 66ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 63ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4850ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2549ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  301ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  332ms
 ✓ src/services/portalApi.test.ts (9 tests) 24ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 45ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 48ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 17ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/servicingApi.test.ts (4 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 4ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2458ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2295ms

 Test Files  47 passed (47)
      Tests  379 passed (379)
   Start at  15:52:27
   Duration  9.40s (transform 5.36s, setup 0ms, collect 14.21s, tests 32.76s, environment 6.90s, prepare 2.89s)


Duration milliseconds: 10136
Exit code: 0
