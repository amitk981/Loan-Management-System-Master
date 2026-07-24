# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_071133_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1314ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  601ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  364ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1608ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  515ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  333ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1786ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  354ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2232ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1036ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  921ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2448ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  509ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  425ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  309ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1031ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  588ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1097ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  420ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  418ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 790ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1185ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  373ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 697ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  516ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 728ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  727ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 597ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  368ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 540ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  478ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 513ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 523ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5610ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  447ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  348ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  335ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  318ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  369ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  359ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  694ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 469ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 401ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 401ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 325ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4916ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2628ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 386ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 348ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 246ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 186ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 187ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 153ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 231ms
 ✓ src/services/authSession.test.ts (39 tests) 43ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 81ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
 ✓ src/services/servicingApi.test.ts (13 tests) 24ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/portalApi.test.ts (10 tests) 28ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2157ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2030ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  07:53:50
   Duration  10.41s (transform 5.21s, setup 0ms, collect 15.52s, tests 33.66s, environment 9.00s, prepare 3.36s)


Duration milliseconds: 10942
Exit code: 0
