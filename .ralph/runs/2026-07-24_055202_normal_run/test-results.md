# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_055202_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 861ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  304ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1292ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  559ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  327ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1614ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  473ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  339ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  324ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1932ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  310ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 462ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2715ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  628ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  428ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  352ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 943ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  491ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 574ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  354ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 444ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 209ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 310ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 519ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 413ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 515ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  421ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 505ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5716ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  441ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  409ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  310ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  330ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  454ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  341ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  333ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  364ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  365ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  641ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 599ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  441ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2199ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1101ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  845ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1203ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  362ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4565ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2381ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  376ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 406ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 989ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  300ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  447ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 263ms
 ✓ src/services/authSession.test.ts (39 tests) 33ms
 ✓ src/services/servicingApi.test.ts (13 tests) 29ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 387ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 245ms
 ✓ src/services/portalApi.test.ts (10 tests) 28ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 166ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 705ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  703ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 192ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 73ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 44ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 28ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 74ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1105ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  996ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  06:35:35
   Duration  10.37s (transform 4.32s, setup 0ms, collect 15.28s, tests 32.68s, environment 8.34s, prepare 3.53s)


Duration milliseconds: 11121
Exit code: 0
