# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 918ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  393ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1284ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  567ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  343ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1584ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  521ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  349ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  323ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1890ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  389ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  303ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 514ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2589ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  528ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  453ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1026ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  576ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 619ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  335ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 432ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 311ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 502ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 315ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 516ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  422ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 141ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5460ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  540ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  404ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  369ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  379ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  376ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  304ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  387ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  337ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  503ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 377ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 964ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  362ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  369ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1100ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  351ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2192ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1082ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  860ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4500ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2396ms
 ✓ src/services/authSession.test.ts (39 tests) 57ms
 ✓ src/services/servicingApi.test.ts (13 tests) 20ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 391ms
 ✓ src/services/portalApi.test.ts (9 tests) 22ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 195ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 343ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 240ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 99ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 683ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  682ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 212ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 17ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 64ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 62ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1111ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1004ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  20:01:48
   Duration  10.05s (transform 4.33s, setup 0ms, collect 15.36s, tests 31.02s, environment 8.10s, prepare 3.45s)


Duration milliseconds: 10788
Exit code: 0
