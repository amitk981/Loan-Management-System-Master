# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_225137_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 895ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  302ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1318ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  657ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  345ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1569ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  463ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  326ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  376ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1902ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  324ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2454ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  455ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  414ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 440ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 990ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  535ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 594ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  367ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 435ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 271ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 490ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 370ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 508ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  418ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 157ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5290ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  509ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  388ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  334ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  383ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  308ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  515ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 901ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  332ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  354ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1100ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  372ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2202ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1136ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  816ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 498ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4283ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2252ms
 ✓ src/services/authSession.test.ts (39 tests) 34ms
 ✓ src/services/servicingApi.test.ts (13 tests) 27ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 437ms
 ✓ src/services/portalApi.test.ts (9 tests) 25ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 376ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 256ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 671ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  669ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 79ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 213ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 54ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 60ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 63ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 15ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1016ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  912ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  23:32:34
   Duration  9.76s (transform 4.25s, setup 0ms, collect 14.82s, tests 30.39s, environment 7.98s, prepare 3.35s)


Duration milliseconds: 10541
Exit code: 0
