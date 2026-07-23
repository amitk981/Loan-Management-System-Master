# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_192235_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 953ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  374ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1418ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  661ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  399ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1602ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  543ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  350ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  323ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2000ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  364ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  353ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 481ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2832ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  594ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  445ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  393ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 965ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  487ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 622ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  398ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 528ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 214ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 339ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 457ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 331ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 507ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  445ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 513ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5834ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  525ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  432ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  397ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  426ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  356ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  380ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  409ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  662ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 661ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  486ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1098ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  382ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4530ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2389ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  317ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2339ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1191ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  881ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 447ms
 ✓ src/services/authSession.test.ts (39 tests) 41ms
 ✓ src/services/servicingApi.test.ts (13 tests) 28ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1000ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  349ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  417ms
 ✓ src/services/portalApi.test.ts (10 tests) 47ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 176ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 290ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 277ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 25ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 659ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  658ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 85ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 183ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 87ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 52ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 18ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 71ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1035ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  929ms

 Test Files  53 passed (53)
      Tests  420 passed (420)
   Start at  20:13:41
   Duration  10.45s (transform 4.56s, setup 0ms, collect 14.96s, tests 33.01s, environment 8.35s, prepare 3.25s)


Duration milliseconds: 10981
Exit code: 0
