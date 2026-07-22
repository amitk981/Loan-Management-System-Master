# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_014100_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1300ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  594ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  337ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1434ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  361ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  393ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  310ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1861ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  338ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2340ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1158ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  907ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2603ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  553ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  410ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  313ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1044ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  352ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  444ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1234ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  421ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 843ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  495ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 764ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 752ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  751ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 565ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  472ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 514ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 541ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  351ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 493ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 389ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 286ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 414ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5755ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  523ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  366ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  306ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  325ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  307ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  402ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  475ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  781ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 419ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4390ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2137ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 345ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 155ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 226ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 135ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 176ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 162ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/services/authSession.test.ts (39 tests) 36ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 95ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 72ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 53ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 33ms
 ✓ src/services/portalApi.test.ts (9 tests) 22ms
 ✓ src/services/servicingApi.test.ts (13 tests) 20ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 44ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 22ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 18ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2241ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2115ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  04:16:15
   Duration  9.61s (transform 4.97s, setup 0ms, collect 14.45s, tests 31.98s, environment 7.68s, prepare 3.20s)


Duration milliseconds: 10144
Exit code: 0
