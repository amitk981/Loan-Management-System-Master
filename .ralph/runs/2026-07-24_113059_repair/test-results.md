# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_103525_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1339ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  603ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  327ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1573ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  500ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  375ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  317ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1700ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  306ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2295ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  496ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  381ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2337ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1118ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  878ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1016ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  562ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1298ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  433ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1144ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  394ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  468ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 682ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  682ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 799ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  307ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 789ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  584ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 505ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 640ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  393ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 424ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 528ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5433ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  429ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  354ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  403ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  302ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  338ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  357ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  668ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 385ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 532ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  443ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 407ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 440ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 404ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 398ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4760ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2372ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  301ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  326ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 199ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 200ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 185ms
 ✓ src/pages/Dashboard.test.tsx (23 tests) 234ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 152ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 204ms
 ✓ src/services/authSession.test.ts (39 tests) 33ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 46ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 55ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 79ms
 ✓ src/services/servicingApi.test.ts (13 tests) 20ms
 ✓ src/services/portalApi.test.ts (10 tests) 24ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 46ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 31ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 18ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 15ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 32ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2404ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2283ms

 Test Files  54 passed (54)
      Tests  435 passed (435)
   Start at  11:41:34
   Duration  10.67s (transform 5.45s, setup 0ms, collect 16.44s, tests 33.95s, environment 9.32s, prepare 3.54s)


Duration milliseconds: 11221
Exit code: 0
