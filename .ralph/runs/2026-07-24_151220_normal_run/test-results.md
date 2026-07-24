# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_151220_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1389ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  451ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  540ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2094ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  985ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  561ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 2290ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  868ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  598ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  356ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2986ms
   ✓ default AppraisalWorkbench authenticated HTTP container > PATCHes only the appraisal allowlist and refreshes the canonical resources once  353ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders a stale 409 without retry, synthesis, or refresh  351ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  422ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  395ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 749ms
   ✓ interest and monitoring workspaces > makes loan and invoice 101 reachable and accrues the disclosed complete selection  317ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 4373ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  445ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  1103ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  684ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  640ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1780ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  512ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  852ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 760ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  506ms
 ✓ src/pages/Dashboard.test.tsx (23 tests) 381ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 235ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 319ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 525ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 614ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 586ms
   ✓ MP14 disbursement status > renders only the server projection and downloads through the portal boundary  304ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 871ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  734ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 1178ms
   ✓ 010N Global Search Results > loads server groups, card fields, and permission-valid quick actions  516ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 8580ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  929ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  488ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  388ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  406ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  539ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  408ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  380ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  408ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  433ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  440ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1385ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3326ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1742ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1215ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1684ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  512ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 7869ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  4289ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  592ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  397ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  355ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  447ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  415ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  322ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  304ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 806ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  581ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 292ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 502ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 456ms
 ✓ src/services/authSession.test.ts (39 tests) 37ms
 ✓ src/services/servicingApi.test.ts (13 tests) 50ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1260ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  461ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  528ms
 ✓ src/services/portalApi.test.ts (10 tests) 45ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 388ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 878ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  874ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 12ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 353ms
   ✓ 010N Header search path > navigates the transient query to S02 without building a local result index  352ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 185ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 17ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 114ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 289ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 17ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 77ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 54ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 73ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 61ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 149ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 1425ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1225ms

 Test Files  55 passed (55)
      Tests  437 passed (437)
   Start at  15:49:04
   Duration  15.29s (transform 5.40s, setup 0ms, collect 21.13s, tests 50.21s, environment 15.33s, prepare 4.79s)


Duration milliseconds: 16051
Exit code: 0
