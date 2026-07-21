# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_174720_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1385ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  661ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1525ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  409ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  344ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  308ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1675ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  339ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2252ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1071ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  899ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2337ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  492ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  402ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 849ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  471ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1343ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  503ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1102ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  387ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  433ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 524ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  318ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 744ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 532ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  464ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 422ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 396ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (4 tests) 416ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 309ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5441ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  425ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  356ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  441ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  329ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  362ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  366ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  593ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 336ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 313ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (3 tests) 250ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 135ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 217ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4385ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2217ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 195ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 56ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 70ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 166ms
 ✓ src/services/authSession.test.ts (36 tests) 35ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 54ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/services/portalApi.test.ts (9 tests) 27ms
 ✓ src/services/servicingApi.test.ts (7 tests) 19ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 6ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2091ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1986ms

 Test Files  50 passed (50)
      Tests  390 passed (390)
   Start at  18:48:14
   Duration  9.07s (transform 4.78s, setup 0ms, collect 13.55s, tests 29.87s, environment 7.29s, prepare 3.04s)


Duration milliseconds: 9588
Exit code: 0
