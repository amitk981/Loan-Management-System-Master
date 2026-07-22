# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_084434_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1337ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  608ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  319ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1575ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  510ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  335ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  305ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1719ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2396ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1164ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  953ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2464ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  521ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  432ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1046ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  627ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1399ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  532ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1264ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  441ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  508ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 644ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  353ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 848ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 652ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  579ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 485ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 566ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 485ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 459ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6035ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  515ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  370ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  302ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  386ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  345ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  409ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  354ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  404ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  390ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  747ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 505ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 413ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 343ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4896ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2395ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  338ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  382ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  304ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 250ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 212ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 211ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 205ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 147ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 86ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 88ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 59ms
 ✓ src/services/portalApi.test.ts (9 tests) 22ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 50ms
 ✓ src/services/authSession.test.ts (38 tests) 31ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 62ms
 ✓ src/services/servicingApi.test.ts (13 tests) 33ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 45ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 14ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/playwright.seed.test.ts (3 tests) 4ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2469ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2329ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  09:01:13
   Duration  10.28s (transform 5.13s, setup 0ms, collect 14.63s, tests 33.66s, environment 8.40s, prepare 3.31s)


Duration milliseconds: 10841
Exit code: 0
