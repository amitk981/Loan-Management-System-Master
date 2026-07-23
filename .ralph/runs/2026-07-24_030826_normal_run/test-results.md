# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_030826_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 826ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  327ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1300ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  616ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  318ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1655ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  545ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  354ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  309ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1967ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  347ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  334ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2575ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  542ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  448ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 451ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 976ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  560ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 617ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  384ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 414ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 215ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 475ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 363ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 342ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 452ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  380ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 507ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5704ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  476ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  382ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  358ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  351ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  375ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  390ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  681ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1154ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  393ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 586ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  441ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2078ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1076ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  791ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4390ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2248ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  321ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 331ms
 ✓ src/services/authSession.test.ts (39 tests) 51ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 993ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  468ms
 ✓ src/services/servicingApi.test.ts (13 tests) 22ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 148ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 214ms
 ✓ src/services/portalApi.test.ts (10 tests) 24ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 311ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 278ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 81ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 114ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 207ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 746ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  745ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 13ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 73ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 71ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1058ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  951ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  03:43:26
   Duration  10.22s (transform 4.35s, setup 0ms, collect 15.37s, tests 31.98s, environment 8.46s, prepare 3.42s)


Duration milliseconds: 10958
Exit code: 0
