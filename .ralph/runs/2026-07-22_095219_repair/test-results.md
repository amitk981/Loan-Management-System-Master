# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_090320_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1565ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  664ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  403ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1970ms
   ✓ 010MA Repayments Hub wiring > renders canonical ledger, statement exceptions, and subsidiary reconciliation evidence  366ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  570ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  403ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  416ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2141ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  322ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  460ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2501ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1320ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  901ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2874ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  627ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  410ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  384ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1226ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  788ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1084ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  340ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  372ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1153ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  417ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  417ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 609ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  364ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1331ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  450ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 492ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 638ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  532ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 725ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 1070ms
   ✓ 009J Loan Account 360 initial API view > renders canonical ledger and schedule pages without calculating financial truth  401ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 728ms
   ✓ 010N Global Search Results > loads server groups, card fields, and permission-valid quick actions  325ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7141ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  693ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  411ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  375ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  372ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  398ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  344ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  406ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  339ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  375ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  369ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1469ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 587ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  381ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 557ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 445ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 297ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6462ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2973ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  329ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  460ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  586ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  422ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  395ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  332ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 212ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 228ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 154ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 459ms
   ✓ MP15-MP18 portal loan views > loads own loans and preserves explicit account selection for every destination  310ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 335ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 108ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 99ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 132ms
 ✓ src/services/authSession.test.ts (38 tests) 42ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 56ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/portalApi.test.ts (9 tests) 32ms
 ✓ src/services/servicingApi.test.ts (13 tests) 33ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 42ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3038ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2795ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  10:08:44
   Duration  12.34s (transform 6.11s, setup 0ms, collect 19.18s, tests 40.70s, environment 10.95s, prepare 3.77s)


Duration milliseconds: 13117
Exit code: 0
