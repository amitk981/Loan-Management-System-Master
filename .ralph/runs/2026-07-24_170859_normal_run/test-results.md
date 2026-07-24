# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_170859_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 977ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  364ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  330ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1645ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  686ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  494ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1868ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  724ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  383ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  334ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2242ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  349ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2951ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  339ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  522ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  485ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  397ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 503ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1074ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  516ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1671ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  445ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  403ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  317ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 584ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  357ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 339ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 302ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 660ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 810ms
   ✓ 010O Header notification summary > renders the bounded backend unread summary and real unread count  311ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 431ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 368ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 576ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  481ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6900ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  694ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  447ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  441ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  355ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  366ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  395ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  315ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  324ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  462ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  602ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  743ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 579ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5264ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2548ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  471ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  314ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  346ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1263ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  432ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2348ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1167ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  910ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 659ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  498ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 223ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 401ms
 ✓ src/services/authSession.test.ts (39 tests) 41ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1170ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  473ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  411ms
 ✓ src/services/servicingApi.test.ts (13 tests) 27ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 569ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  327ms
 ✓ src/services/portalApi.test.ts (10 tests) 36ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 308ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 227ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 231ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 174ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 19ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 24ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 912ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  911ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 43ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 73ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 44ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 13ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 115ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 15ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 5ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 175ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 27ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 1406ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1215ms

 Test Files  56 passed (56)
      Tests  457 passed (457)
   Start at  17:43:50
   Duration  12.71s (transform 5.10s, setup 0ms, collect 18.64s, tests 40.43s, environment 10.39s, prepare 4.18s)


Duration milliseconds: 13430
Exit code: 0
