# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_032730_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1591ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  433ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  325ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  361ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1695ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  415ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  473ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  594ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1862ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  346ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2361ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1087ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  962ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2496ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  535ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  406ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  306ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1438ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  409ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  376ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  321ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1421ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  577ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  462ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1394ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  425ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 986ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  588ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1269ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  492ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 688ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  451ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 921ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  523ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5772ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  481ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  362ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  349ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  302ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  323ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  453ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  341ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  705ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1138ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  377ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  513ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 806ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  315ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 787ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  613ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4681ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2250ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  301ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  324ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 558ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 450ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 520ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  445ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 570ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  352ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 492ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 495ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 565ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  377ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (3 tests) 341ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 431ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 309ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 287ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 266ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 323ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 285ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 140ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 146ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 165ms
 ✓ src/services/authSession.test.ts (40 tests) 35ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 58ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 226ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 29ms
 ✓ src/services/portalApi.test.ts (10 tests) 22ms
 ✓ src/services/servicingApi.test.ts (13 tests) 33ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 53ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 59ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/playwright.seed.test.ts (3 tests) 4ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2228ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2046ms

 Test Files  61 passed (61)
      Tests  493 passed (493)
   Start at  03:55:57
   Duration  12.08s (transform 5.14s, setup 0ms, collect 16.86s, tests 40.64s, environment 10.72s, prepare 3.84s)


Duration milliseconds: 12575
Exit code: 0
