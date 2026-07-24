# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_225638_normal_run/sfpcl-lms

 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 2851ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  1045ms
   ✓ Task Inbox screen > round-trips assigned-to-me, due-today, and overdue filters through the API  408ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  570ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  574ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 2904ms
   ✓ 010MA Repayments Hub wiring > renders canonical ledger, statement exceptions, and subsidiary reconciliation evidence  436ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  636ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  761ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  599ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3909ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  2011ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1567ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 4005ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  356ms
   ✓ default AppraisalWorkbench authenticated HTTP container > clicks 'create' through the authenticated boundary and refreshes four reads  346ms
   ✓ default AppraisalWorkbench authenticated HTTP container > clicks 'revalidate' through the authenticated boundary and refreshes four reads  387ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  731ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  390ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 5262ms
   ✓ 008M2 documentation workspace contract > keeps S26 facts in the approved queue/card vocabulary without the invented facts grid  340ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  391ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  1190ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  400ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  942ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  425ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2163ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > renders the approved three-card composition and server advisory only from the mounted projection  346ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  439ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1217ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 2479ms
   ✓ 011PA default case and frozen-note read surface > renders list/detail, grace, extension, and frozen note from backend projections  498ms
   ✓ 011PA default case and frozen-note read surface > keeps the latest selected case authoritative when an older detail resolves later  403ms
   ✓ 011PA default case and frozen-note read surface > shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls  544ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  651ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1541ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  474ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1514ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  642ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  410ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1211ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  453ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  488ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 923ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  343ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  321ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 876ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  649ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 719ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  436ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 9045ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  1009ms
   ✓ SanctionWorkbench authenticated container > clears prior rows and totals when a later collection fails with 'MALFORMED_RESPONSE'  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  690ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  540ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  362ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  463ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  572ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  909ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  422ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  437ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  403ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  945ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 815ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 608ms
   ✓ interest and monitoring workspaces > makes loan and invoice 101 reachable and accrues the disclosed complete selection  334ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 447ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 575ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 7851ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  4952ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  384ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  314ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  373ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  311ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 414ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 354ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 425ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 737ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  571ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 430ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 192ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 239ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 427ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 252ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 240ms
 ✓ src/services/authSession.test.ts (39 tests) 55ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 177ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 246ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 106ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 85ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 78ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 89ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 49ms
 ✓ src/services/servicingApi.test.ts (13 tests) 27ms
 ✓ src/services/portalApi.test.ts (10 tests) 32ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 88ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 20ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 16ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/services/recoveryApi.test.ts (2 tests) 5ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 25ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 3277ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3021ms

 Test Files  57 passed (57)
      Tests  469 passed (469)
   Start at  23:32:07
   Duration  16.48s (transform 7.37s, setup 0ms, collect 22.79s, tests 57.86s, environment 14.92s, prepare 4.94s)


Duration milliseconds: 17137
Exit code: 0
