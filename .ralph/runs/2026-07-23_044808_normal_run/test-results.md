# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_044808_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 872ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  336ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1304ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  623ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  363ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1677ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  503ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  373ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  374ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1954ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  325ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  312ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 506ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2577ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  527ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  427ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  309ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 963ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  609ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 646ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  427ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 457ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 310ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 450ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 349ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 486ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  418ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 132ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 863ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  368ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1073ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  401ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2149ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1108ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  830ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5737ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  577ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  385ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  362ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  398ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  341ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  357ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  336ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  429ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  388ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  367ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  576ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 399ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4364ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2362ms
 ✓ src/services/authSession.test.ts (39 tests) 43ms
 ✓ src/services/servicingApi.test.ts (13 tests) 24ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 356ms
 ✓ src/services/portalApi.test.ts (9 tests) 28ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 167ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 318ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 200ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 18ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 100ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 72ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 639ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  639ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 208ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 12ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 58ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 75ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 53ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 68ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1085ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  977ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  05:36:57
   Duration  9.92s (transform 4.47s, setup 0ms, collect 14.80s, tests 30.92s, environment 7.90s, prepare 3.41s)


Duration milliseconds: 10664
Exit code: 0
