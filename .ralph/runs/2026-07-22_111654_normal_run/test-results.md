# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_111654_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 805ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1379ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  633ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  387ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1611ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  491ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  361ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  333ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1906ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  368ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2575ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  532ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  461ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  335ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1070ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  566ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 457ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 772ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  421ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 565ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 674ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 360ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 406ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 504ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  422ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 124ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5994ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  511ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  428ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  390ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  342ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  358ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  439ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  352ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  437ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  413ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  684ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 970ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  359ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  394ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 461ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2385ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1239ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  899ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1318ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  414ms
 ✓ src/services/authSession.test.ts (38 tests) 33ms
 ✓ src/services/servicingApi.test.ts (13 tests) 33ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 348ms
 ✓ src/services/portalApi.test.ts (9 tests) 21ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5084ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2877ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 228ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 274ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 332ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 18ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 243ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 21ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 76ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 226ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 49ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 74ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 26ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 24ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1150ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1049ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  11:57:21
   Duration  10.71s (transform 4.73s, setup 0ms, collect 16.40s, tests 32.82s, environment 8.70s, prepare 3.62s)


Duration milliseconds: 11533
Exit code: 0
