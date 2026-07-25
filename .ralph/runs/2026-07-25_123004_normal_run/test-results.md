# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_123004_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 887ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1417ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  559ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1947ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  370ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2891ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  599ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  428ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  346ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 3190ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  985ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  730ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  391ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1534ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  544ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  321ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  349ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 2114ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  478ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  690ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  680ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1428ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  635ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  360ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1280ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  791ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 608ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1950ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  559ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  546ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  401ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1230ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  684ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  327ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 714ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  464ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6337ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  513ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  496ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  364ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  367ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  408ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  316ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  334ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  417ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  692ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 414ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 915ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  399ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 439ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 265ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5467ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2778ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  458ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  354ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 531ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 411ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 431ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 620ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  514ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 632ms
 ✓ src/services/reportApi.test.ts (5 tests) 11ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 793ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  598ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 908ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  703ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1359ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  480ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 13ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 455ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  323ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2569ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1272ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1002ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1088ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  384ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  405ms
 ✓ src/services/servicingApi.test.ts (13 tests) 28ms
 ✓ src/services/authSession.test.ts (40 tests) 42ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 236ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 173ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 207ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 25ms
 ✓ src/services/portalApi.test.ts (10 tests) 33ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 307ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 115ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 17ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 114ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 221ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 63ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 46ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/playwright.seed.test.ts (5 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 120ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 1200ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1034ms

 Test Files  64 passed (64)
      Tests  515 passed (515)
   Start at  13:03:50
   Duration  14.53s (transform 5.28s, setup 0ms, collect 20.31s, tests 47.94s, environment 12.92s, prepare 4.40s)


Duration milliseconds: 15225
Exit code: 0
