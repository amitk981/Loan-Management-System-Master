# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_002010_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 865ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1344ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  636ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  378ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1572ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  496ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  374ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  321ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2013ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  356ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  324ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 462ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2685ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  592ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  510ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1028ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  580ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 622ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  390ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 474ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 227ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 475ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 311ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 348ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 483ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  413ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 536ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5548ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  446ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  340ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  349ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  383ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  303ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  400ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  322ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  611ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 676ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  467ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1120ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  400ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2269ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1142ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  884ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4585ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2442ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  314ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 431ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 229ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 916ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  401ms
 ✓ src/services/authSession.test.ts (39 tests) 50ms
 ✓ src/services/servicingApi.test.ts (13 tests) 24ms
 ✓ src/services/portalApi.test.ts (10 tests) 36ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 298ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 190ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 204ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 637ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  636ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 61ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 78ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 19ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 214ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 57ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 52ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 70ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 4ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1026ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  918ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  01:17:40
   Duration  10.25s (transform 4.24s, setup 0ms, collect 14.98s, tests 32.40s, environment 8.45s, prepare 3.62s)


Duration milliseconds: 11018
Exit code: 0
