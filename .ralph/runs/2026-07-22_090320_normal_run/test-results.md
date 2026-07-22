# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_090320_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1253ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  447ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  418ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1827ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  909ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  501ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 2201ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  736ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  481ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  516ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2999ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  529ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  686ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 553ms
   ✓ interest and monitoring workspaces > makes loan and invoice 101 reachable and accrues the disclosed complete selection  311ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3994ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  350ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  719ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  687ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  779ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1308ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  317ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  662ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 654ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  435ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 538ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 292ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 544ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 346ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 568ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  489ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 162ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7051ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  865ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  564ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  603ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  602ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  406ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  324ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  309ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  373ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  382ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  393ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  697ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1052ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  358ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1054ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  373ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  433ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 487ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2336ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1179ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  894ms
 ✓ src/services/authSession.test.ts (38 tests) 45ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5694ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3443ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  309ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  353ms
 ✓ src/services/servicingApi.test.ts (13 tests) 22ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 432ms
 ✓ src/services/portalApi.test.ts (9 tests) 36ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 232ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 294ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 370ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 15ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 83ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 85ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 36ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 235ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 13ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 114ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 65ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 56ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 45ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1145ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1038ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  09:37:01
   Duration  11.89s (transform 5.15s, setup 0ms, collect 17.17s, tests 38.37s, environment 10.20s, prepare 3.79s)


Duration milliseconds: 12921
Exit code: 0
