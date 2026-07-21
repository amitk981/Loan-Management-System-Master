# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1343ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  647ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  344ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1557ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  540ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  312ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1893ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  340ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  335ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2373ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1215ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  868ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2490ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  495ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  427ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1301ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  438ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1133ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  361ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  519ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1153ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  608ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 549ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  328ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 820ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  316ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 323ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 567ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  485ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 415ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 388ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 361ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5721ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  553ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  341ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  308ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  435ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  377ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  700ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 167ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 301ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 144ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 145ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 67ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 81ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4514ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2422ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/services/authSession.test.ts (36 tests) 47ms
 ✓ src/services/portalApi.test.ts (9 tests) 25ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 59ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 17ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/services/servicingApi.test.ts (4 tests) 6ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2272ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2142ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  47 passed (47)
      Tests  379 passed (379)
   Start at  15:40:43
   Duration  9.58s (transform 5.22s, setup 0ms, collect 14.60s, tests 30.49s, environment 7.47s, prepare 3.27s)


Duration milliseconds: 10141
Exit code: 0
