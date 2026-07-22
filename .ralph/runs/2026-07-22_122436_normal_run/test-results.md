# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_122436_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 903ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  306ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1444ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  676ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  358ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1646ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  558ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  360ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  332ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2176ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  372ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  302ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 497ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2947ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  566ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  490ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  448ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1092ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  669ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 639ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  391ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 493ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 316ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 545ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 333ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 553ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  485ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 166ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 965ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  335ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  392ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6006ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  539ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  452ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  347ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  362ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  381ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  373ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  318ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  386ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  377ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  631ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1181ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  417ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2453ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1253ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  917ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 580ms
 ✓ src/services/authSession.test.ts (38 tests) 52ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 497ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  317ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4873ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2575ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  301ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  334ms
 ✓ src/services/servicingApi.test.ts (13 tests) 47ms
 ✓ src/services/portalApi.test.ts (9 tests) 30ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 19ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 281ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 80ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 285ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 455ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 242ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 157ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 112ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 84ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 73ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 14ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1258ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1153ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  12:50:39
   Duration  10.84s (transform 4.97s, setup 0ms, collect 16.78s, tests 33.65s, environment 8.48s, prepare 3.54s)


Duration milliseconds: 11646
Exit code: 0
