# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_095043_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1341ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  648ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  346ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1493ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  461ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  311ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  315ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1747ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  314ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2362ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1157ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  904ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2463ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  463ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  419ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 911ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  499ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1329ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  446ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1107ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  419ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  463ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 807ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  333ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 761ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  761ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 659ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  440ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 533ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 562ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 460ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 622ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  543ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5967ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  476ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  398ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  311ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  331ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  377ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  433ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  813ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 448ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 524ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 447ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 469ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 442ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 168ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 200ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5183ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2768ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  369ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  304ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 262ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 62ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 167ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 69ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 70ms
 ✓ src/services/authSession.test.ts (39 tests) 53ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 56ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 68ms
 ✓ src/services/portalApi.test.ts (10 tests) 26ms
 ✓ src/services/servicingApi.test.ts (13 tests) 29ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 17ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 62ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 13ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 20ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2443ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2306ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  52 passed (52)
      Tests  415 passed (415)
   Start at  14:33:11
   Duration  10.50s (transform 5.10s, setup 0ms, collect 15.48s, tests 34.56s, environment 9.39s, prepare 3.37s)


Duration milliseconds: 11056
Exit code: 0
