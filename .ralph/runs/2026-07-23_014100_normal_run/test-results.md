# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_014100_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 876ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  327ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1360ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  611ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  356ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1596ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  521ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  305ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  346ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1754ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  331ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  306ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2512ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  591ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  452ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 426ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1016ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  515ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 573ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  334ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 499ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 508ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 298ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 361ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 491ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  412ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 157ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5347ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  451ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  335ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  312ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  388ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  521ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 893ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  332ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  361ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 439ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1081ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  345ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2214ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1148ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  816ms
 ✓ src/services/authSession.test.ts (39 tests) 40ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4496ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2304ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  311ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  305ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 444ms
 ✓ src/services/portalApi.test.ts (9 tests) 27ms
 ✓ src/services/servicingApi.test.ts (13 tests) 26ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 180ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 342ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 210ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 20ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 648ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  647ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 61ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 92ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 26ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 270ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 63ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 55ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 56ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 66ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1074ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  961ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  02:23:51
   Duration  9.77s (transform 4.26s, setup 0ms, collect 14.68s, tests 30.72s, environment 7.72s, prepare 3.42s)


Duration milliseconds: 10548
Exit code: 0
