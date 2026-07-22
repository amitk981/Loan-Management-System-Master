# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_191406_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1399ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  667ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  346ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1576ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  489ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  307ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  310ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1772ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  320ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2256ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1094ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  879ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2284ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  484ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  377ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 902ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  547ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1114ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  367ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  464ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1429ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  490ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 775ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  773ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 854ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  305ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 580ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 609ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  374ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 533ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  445ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 455ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 595ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5831ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  469ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  377ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  311ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  331ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  358ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  320ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  369ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  420ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  731ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 410ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 349ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 296ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 379ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 330ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4777ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2416ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  301ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 230ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 154ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 65ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 159ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 174ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 64ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/services/portalApi.test.ts (9 tests) 27ms
 ✓ src/services/authSession.test.ts (39 tests) 32ms
 ✓ src/services/servicingApi.test.ts (13 tests) 31ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2126ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2015ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  21:06:01
   Duration  10.03s (transform 4.91s, setup 0ms, collect 14.93s, tests 32.89s, environment 8.09s, prepare 3.33s)


Duration milliseconds: 10563
Exit code: 0
