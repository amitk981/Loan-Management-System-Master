# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_095043_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1664ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  744ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  479ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1991ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  600ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  464ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  403ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2698ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  403ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  418ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  473ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2875ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1294ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1186ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3823ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  362ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  648ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  602ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  709ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1148ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  323ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  518ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1470ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  448ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 815ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1147ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  439ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  468ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 797ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  796ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 695ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  580ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 753ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  463ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 663ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 568ms
   ✓ interest and monitoring workspaces > makes loan and invoice 101 reachable and accrues the disclosed complete selection  301ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 569ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7299ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  721ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  410ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  445ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  496ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  494ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  410ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  380ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  325ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  395ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  462ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  896ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 429ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 645ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 478ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 495ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6253ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3407ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  372ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  391ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  435ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 396ms
   ✓ 010N Header search path > navigates the transient query to S02 without building a local result index  396ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 685ms
   ✓ 009K disbursement finance workspace > renders named backend blockers and disables initiation while readiness fails  358ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  306ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 248ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 184ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 95ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 259ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 48ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/services/authSession.test.ts (39 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 44ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 95ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 53ms
 ✓ src/services/servicingApi.test.ts (13 tests) 39ms
 ✓ src/services/portalApi.test.ts (10 tests) 56ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 22ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 24ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 23ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2700ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2473ms

 Test Files  52 passed (52)
      Tests  415 passed (415)
   Start at  10:52:15
   Duration  12.70s (transform 5.91s, setup 0ms, collect 19.18s, tests 42.48s, environment 12.54s, prepare 3.66s)


Duration milliseconds: 13547
Exit code: 0
