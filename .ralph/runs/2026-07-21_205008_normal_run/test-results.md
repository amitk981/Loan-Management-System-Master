# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_205008_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 988ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  362ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1532ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  700ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  366ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1768ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  523ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  398ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  396ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2095ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  370ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  346ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3080ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  653ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  508ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  433ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 527ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 741ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  451ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1310ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  709ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 445ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 366ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 651ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  528ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1091ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  401ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  461ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 206ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1476ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  503ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (3 tests) 357ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6392ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  632ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  448ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  391ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  336ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  409ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  436ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  394ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  450ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  380ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  685ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2593ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1177ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1121ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 432ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  321ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 360ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (4 tests) 516ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 327ms
 ✓ src/services/portalApi.test.ts (9 tests) 25ms
 ✓ src/services/servicingApi.test.ts (7 tests) 24ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 283ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5452ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2837ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  312ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  350ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  329ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  397ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  318ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 66ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 64ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 289ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 112ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 61ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 14ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 93ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1231ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1122ms

 Test Files  50 passed (50)
      Tests  390 passed (390)
   Start at  21:12:23
   Duration  11.35s (transform 5.35s, setup 0ms, collect 17.95s, tests 35.18s, environment 8.97s, prepare 3.35s)


Duration milliseconds: 11888
Exit code: 0
