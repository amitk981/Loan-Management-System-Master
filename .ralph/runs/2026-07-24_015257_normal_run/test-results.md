# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_015257_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 905ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  318ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  313ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1382ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  625ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  392ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1569ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  538ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  349ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  353ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1799ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  347ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  332ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 443ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2687ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  547ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  449ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  319ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 982ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  554ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 418ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 688ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  416ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 248ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 464ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 297ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 382ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 512ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  435ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 505ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5558ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  480ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  425ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  305ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  352ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  305ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  317ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  353ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  389ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  339ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  508ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 693ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  503ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1118ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  379ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2219ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1126ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  853ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4503ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2348ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  340ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 396ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 206ms
 ✓ src/services/authSession.test.ts (39 tests) 37ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 981ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  318ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  416ms
 ✓ src/services/servicingApi.test.ts (13 tests) 35ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 311ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 171ms
 ✓ src/services/portalApi.test.ts (10 tests) 30ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 209ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 12ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 767ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  765ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 101ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 21ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 211ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 76ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 35ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1121ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1012ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  02:33:34
   Duration  10.37s (transform 4.57s, setup 0ms, collect 15.60s, tests 32.35s, environment 8.43s, prepare 3.43s)


Duration milliseconds: 11160
Exit code: 0
