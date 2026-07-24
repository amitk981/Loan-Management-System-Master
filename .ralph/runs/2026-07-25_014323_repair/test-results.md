# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_003342_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1536ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  477ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  337ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  313ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1886ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  471ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  586ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  545ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1990ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  402ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2454ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1178ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  922ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2384ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  521ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  342ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1492ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  450ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  360ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1418ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  508ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1570ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  678ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  520ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1085ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  666ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1414ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  576ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1095ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  365ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  474ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 581ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  306ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 754ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 728ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  524ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6165ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  479ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  352ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  331ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  333ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  337ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  402ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  356ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  334ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  453ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  430ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  743ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 562ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  453ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5244ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2498ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  372ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  305ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  394ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  317ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  318ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 459ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 443ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 453ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 698ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 524ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 470ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 342ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 303ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 225ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 310ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 239ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 263ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 134ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 69ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 154ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 162ms
 ✓ src/services/authSession.test.ts (39 tests) 47ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 83ms
 ✓ src/services/servicingApi.test.ts (13 tests) 30ms
 ✓ src/services/portalApi.test.ts (10 tests) 26ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 30ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 22ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 19ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/recoveryApi.test.ts (4 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2851ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2601ms

 Test Files  58 passed (58)
      Tests  477 passed (477)
   Start at  01:50:30
   Duration  12.38s (transform 5.88s, setup 0ms, collect 17.47s, tests 40.92s, environment 10.69s, prepare 4.02s)


Duration milliseconds: 12922
Exit code: 0
