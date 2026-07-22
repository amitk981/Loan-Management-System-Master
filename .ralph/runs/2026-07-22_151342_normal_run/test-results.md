# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_151342_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1246ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  511ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  402ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1819ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  802ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  508ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 2192ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  856ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  475ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  422ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2456ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  352ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  307ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 481ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3311ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  366ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  806ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  356ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  435ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1292ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  429ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  589ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 569ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  349ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 479ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 495ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 336ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 347ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 620ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  537ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 160ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6217ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  817ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  434ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  308ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  354ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  481ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  342ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  366ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  372ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  601ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 950ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  350ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  394ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1152ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  364ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2323ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1074ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  902ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 618ms
 ✓ src/services/authSession.test.ts (38 tests) 33ms
 ✓ src/services/servicingApi.test.ts (13 tests) 24ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 359ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4950ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2739ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  302ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  366ms
 ✓ src/services/portalApi.test.ts (9 tests) 31ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 209ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 355ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 234ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 95ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 95ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 163ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 105ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 56ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 60ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 57ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 17ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1114ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1005ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  15:47:53
   Duration  11.00s (transform 5.27s, setup 0ms, collect 16.98s, tests 35.15s, environment 8.36s, prepare 3.23s)


Duration milliseconds: 11745
Exit code: 0
