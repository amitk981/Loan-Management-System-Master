# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_095043_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 812ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  314ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1313ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  609ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  356ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1662ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  502ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  364ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  330ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1778ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  375ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2458ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  524ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  381ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 481ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1082ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  624ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 452ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 688ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  437ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 207ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 535ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 317ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 379ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 550ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  460ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5582ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  505ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  360ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  306ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  349ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  404ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  399ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  605ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 440ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 925ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  302ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  391ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 299ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1105ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  372ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2182ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1147ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  814ms
 ✓ src/services/authSession.test.ts (39 tests) 43ms
 ✓ src/services/servicingApi.test.ts (13 tests) 29ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4647ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2437ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  309ms
 ✓ src/services/portalApi.test.ts (10 tests) 23ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 338ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 188ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 268ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 98ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 723ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  722ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 210ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 52ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 6ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 59ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 87ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 5ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1026ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  922ms

 Test Files  52 passed (52)
      Tests  415 passed (415)
   Start at  10:39:12
   Duration  10.19s (transform 4.35s, setup 0ms, collect 14.80s, tests 31.33s, environment 8.03s, prepare 3.29s)


Duration milliseconds: 10734
Exit code: 0
