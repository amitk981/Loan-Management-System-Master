# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1249ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  603ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  341ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1480ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  483ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  307ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1689ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  360ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2199ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  504ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  401ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2239ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1112ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  865ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 957ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  572ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1298ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  486ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 738ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  737ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1163ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  358ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  547ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 745ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 537ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  457ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 652ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  413ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 422ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 502ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 508ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5715ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  479ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  370ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  362ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  441ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  414ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  374ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  689ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 368ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 476ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 327ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 331ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 364ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4656ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2325ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 189ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 147ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 101ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 155ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 178ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 92ms
 ✓ src/services/authSession.test.ts (39 tests) 30ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 80ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 40ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 48ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/services/portalApi.test.ts (9 tests) 43ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 41ms
 ✓ src/services/servicingApi.test.ts (13 tests) 26ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 14ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 21ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2151ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2042ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  20:13:54
   Duration  9.83s (transform 4.67s, setup 0ms, collect 14.60s, tests 32.10s, environment 8.22s, prepare 3.13s)


Duration milliseconds: 10377
Exit code: 0
