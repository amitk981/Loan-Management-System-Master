# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_192235_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1267ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  618ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  341ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1586ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  519ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  338ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  333ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1829ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  331ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2410ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1160ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  953ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2496ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  512ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  442ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1106ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  367ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1048ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  332ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  449ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1028ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  595ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 691ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  690ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 841ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  303ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 438ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 613ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  360ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 637ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 555ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  469ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 419ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5488ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  455ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  345ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  323ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  320ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  317ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  459ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  347ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  637ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 458ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 389ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4821ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2488ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 282ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 314ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 737ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  572ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 279ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 236ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 225ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 56ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 187ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 188ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 26ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 71ms
 ✓ src/services/portalApi.test.ts (10 tests) 27ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/services/authSession.test.ts (39 tests) 41ms
 ✓ src/services/servicingApi.test.ts (13 tests) 27ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 13ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2004ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1895ms

 Test Files  53 passed (53)
      Tests  420 passed (420)
   Start at  20:25:13
   Duration  10.30s (transform 4.81s, setup 0ms, collect 15.30s, tests 33.12s, environment 8.62s, prepare 3.31s)


Duration milliseconds: 10833
Exit code: 0
