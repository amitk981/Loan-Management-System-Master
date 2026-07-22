# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_014100_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1339ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  623ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  357ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1555ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  532ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  304ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  320ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1745ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  309ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2240ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1103ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  829ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2405ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  531ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  419ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 982ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  570ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1319ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  447ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1104ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  400ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  463ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 762ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 761ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  760ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 667ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  445ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 513ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 432ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 392ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 519ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  425ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5549ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  513ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  342ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  322ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  330ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  324ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  348ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  389ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  358ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  601ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 321ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 429ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 481ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4290ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2156ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 319ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 292ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 199ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 62ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 170ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 157ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 175ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 52ms
 ✓ src/services/authSession.test.ts (39 tests) 40ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/services/portalApi.test.ts (9 tests) 24ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/services/servicingApi.test.ts (13 tests) 22ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1998ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1889ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  02:55:16
   Duration  9.63s (transform 4.55s, setup 0ms, collect 14.12s, tests 31.60s, environment 8.03s, prepare 3.28s)


Duration milliseconds: 10167
Exit code: 0
