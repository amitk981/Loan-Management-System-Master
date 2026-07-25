# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_065407_normal_run/sfpcl-lms

 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2003ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  415ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  301ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 2048ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  500ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  669ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  579ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2432ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1155ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1030ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2654ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  528ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  490ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 3319ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  932ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  786ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  402ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1853ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  537ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  362ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  382ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1776ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  675ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  385ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  339ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1656ms
   ✓ 011PA default case and frozen-note read surface > renders list/detail, grace, extension, and frozen note from backend projections  331ms
   ✓ 011PA default case and frozen-note read surface > shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls  303ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  597ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1572ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  662ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  444ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1538ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  611ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6600ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  455ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  460ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  341ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  336ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  451ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  346ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  481ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  387ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  748ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1371ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  803ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  442ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1412ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  878ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1366ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  431ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  402ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  504ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 1099ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  486ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 942ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  667ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6222ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3365ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  301ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  335ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  406ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  333ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  369ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1057ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  309ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  372ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 596ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 796ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  600ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 725ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  475ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 920ms
   ✓ 010N Global Search Results > loads server groups, card fields, and permission-valid quick actions  321ms
   ✓ 010N Global Search Results > submits a replacement query without URL or local-storage caching  314ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 517ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 658ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  522ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 346ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 507ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 420ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 509ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  402ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 408ms
 ✓ src/services/reportApi.test.ts (5 tests) 10ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 276ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 7ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 381ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 235ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 258ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 131ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 101ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 195ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 57ms
 ✓ src/services/servicingApi.test.ts (13 tests) 22ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 86ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 201ms
 ✓ src/services/authSession.test.ts (40 tests) 50ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 61ms
 ✓ src/services/portalApi.test.ts (10 tests) 25ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 63ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 39ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2703ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2538ms

 Test Files  64 passed (64)
      Tests  513 passed (513)
   Start at  07:24:49
   Duration  15.77s (transform 6.98s, setup 0ms, collect 23.34s, tests 52.33s, environment 14.69s, prepare 4.14s)


Duration milliseconds: 16314
Exit code: 0
