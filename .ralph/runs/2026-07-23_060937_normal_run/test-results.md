# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_060937_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 873ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  326ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  308ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1339ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  624ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  373ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1617ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  530ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  343ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  356ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1843ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  354ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  314ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2558ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  584ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  446ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 415ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 967ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  528ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 594ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  381ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 504ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 287ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 542ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 339ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 570ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  469ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 186ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5453ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  504ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  332ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  342ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  316ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  310ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  418ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  314ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  542ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 929ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  325ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  390ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1107ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  371ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 409ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2189ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1132ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  813ms
 ✓ src/services/authSession.test.ts (39 tests) 31ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4386ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2253ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  312ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 297ms
 ✓ src/services/servicingApi.test.ts (13 tests) 21ms
 ✓ src/services/portalApi.test.ts (9 tests) 27ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 169ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 229ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 328ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 63ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 656ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  655ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 195ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 13ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 67ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 54ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 40ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 64ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1082ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  975ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  07:15:31
   Duration  9.90s (transform 4.20s, setup 0ms, collect 14.79s, tests 30.64s, environment 8.00s, prepare 3.27s)


Duration milliseconds: 10664
Exit code: 0
