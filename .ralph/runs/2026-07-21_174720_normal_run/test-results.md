# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_174720_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 796ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  315ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1353ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  591ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  392ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1612ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  514ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  402ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1815ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  323ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2632ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  547ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  445ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  327ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1081ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  547ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 644ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  409ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 491ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 339ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 329ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 519ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  445ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1029ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  328ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  462ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1117ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  392ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 173ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (3 tests) 285ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5574ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  470ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  387ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  310ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  363ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  314ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  390ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  375ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  346ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  602ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2297ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1098ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  922ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 297ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 371ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (4 tests) 407ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 216ms
 ✓ src/services/authSession.test.ts (36 tests) 34ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4514ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2391ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  319ms
 ✓ src/services/portalApi.test.ts (9 tests) 24ms
 ✓ src/services/servicingApi.test.ts (7 tests) 23ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 239ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 18ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 65ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 20ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 166ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 104ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 61ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 21ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 4ms
 ✓ src/playwright.seed.test.ts (3 tests) 4ms
 ✓ src/utils/formatMoney.test.ts (1 test) 4ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1064ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  962ms

 Test Files  50 passed (50)
      Tests  390 passed (390)
   Start at  18:23:23
   Duration  9.52s (transform 4.27s, setup 0ms, collect 13.76s, tests 29.98s, environment 7.34s, prepare 3.10s)


Duration milliseconds: 10034
Exit code: 0
