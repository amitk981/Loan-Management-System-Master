# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_044459_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1507ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  490ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  337ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1803ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  306ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  321ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1782ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  495ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  534ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  517ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2300ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1155ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  852ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2342ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  501ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  387ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1494ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  462ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  347ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  348ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1294ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  635ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  331ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1225ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  494ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1022ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  574ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1343ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  442ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5414ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  423ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  336ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  376ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  400ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  420ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  607ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 665ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 944ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  512ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 675ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  539ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 989ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  364ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  391ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 720ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  488ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4692ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2462ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  308ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 461ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 474ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 596ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  387ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 615ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 536ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  449ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 410ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  308ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 427ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (3 tests) 357ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 291ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 385ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 345ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (4 tests) 557ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  330ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 313ms
 ✓ src/services/reportApi.test.ts (2 tests) 19ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 203ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 150ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 175ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 170ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 217ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 255ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 71ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 53ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 52ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 64ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 63ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/authSession.test.ts (40 tests) 39ms
 ✓ src/services/servicingApi.test.ts (13 tests) 23ms
 ✓ src/services/portalApi.test.ts (10 tests) 25ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 12ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 27ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 16ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2264ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2092ms

 Test Files  63 passed (63)
      Tests  499 passed (499)
   Start at  05:09:08
   Duration  11.98s (transform 4.97s, setup 0ms, collect 17.34s, tests 40.00s, environment 10.88s, prepare 3.89s)


Duration milliseconds: 12512
Exit code: 0
