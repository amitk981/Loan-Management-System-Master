# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_000144_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 961ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  394ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  332ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1336ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  650ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  334ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1512ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  494ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  327ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  308ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1720ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2455ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  556ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  438ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 462ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1039ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  555ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 649ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  426ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 454ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 313ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 513ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 306ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 503ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  415ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 183ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 412ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 912ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  343ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  360ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5479ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  455ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  349ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  363ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  366ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  337ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  347ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  358ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  392ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  504ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1030ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  353ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2275ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1124ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  833ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4427ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2233ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 414ms
 ✓ src/services/servicingApi.test.ts (13 tests) 28ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 160ms
 ✓ src/services/authSession.test.ts (39 tests) 75ms
 ✓ src/services/portalApi.test.ts (9 tests) 21ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 367ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 272ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 62ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 17ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 704ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  703ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 107ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 226ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 87ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 41ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 75ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1016ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  910ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  00:29:54
   Duration  9.78s (transform 4.10s, setup 0ms, collect 14.47s, tests 30.78s, environment 7.99s, prepare 3.22s)


Duration milliseconds: 10557
Exit code: 0
