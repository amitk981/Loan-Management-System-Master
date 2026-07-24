# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_135028_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1745ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  656ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  541ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2560ms
   ✓ SettingsHub Approval Matrix panel > renders active and retained historical rules from the versioned API without local fixtures  355ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1151ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  654ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 3024ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  1167ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  568ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  537ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 3632ms
   ✓ default AppraisalWorkbench authenticated HTTP container > PATCHes only the appraisal allowlist and refreshes the canonical resources once  410ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders HTTP 403 once without retry or refresh  313ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  452ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  457ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 653ms
   ✓ interest and monitoring workspaces > makes loan and invoice 101 reachable and accrues the disclosed complete selection  345ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 4818ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  522ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  1100ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  359ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  734ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  616ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1657ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  380ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  929ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 1078ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  590ms
 ✓ src/pages/Dashboard.test.tsx (23 tests) 628ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 342ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 656ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 958ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 780ms
   ✓ MP15-MP18 portal loan views > loads own loans and preserves explicit account selection for every destination  498ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 863ms
   ✓ MP14 disbursement status > renders only the server projection and downloads through the portal boundary  485ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 1027ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  879ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 1179ms
   ✓ 010N Global Search Results > loads server groups, card fields, and permission-valid quick actions  486ms
   ✓ 010N Global Search Results > submits a replacement query without URL or local-storage caching  322ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3963ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  2102ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1445ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 11421ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  1195ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  660ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  500ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  496ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  420ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  545ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  743ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  438ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  592ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  748ms
   ✓ SanctionWorkbench authenticated container > surfaces CONFLICTED_APPROVER_NOT_ALLOWED without fabricating completion or refetching  379ms
   ✓ SanctionWorkbench authenticated container > surfaces GENERAL_MEETING_APPROVAL_REJECTED without fabricating completion or refetching  315ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1796ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 2161ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 400 failure without refetch  480ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  758ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 9632ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  4793ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  860ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  523ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  579ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  471ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  471ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  445ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  502ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  442ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 1301ms
   ✓ MP19-MP24 member communication views > renders MP19 loading, empty, error, real notice, and download behavior  320ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  812ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 772ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  438ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 591ms
   ✓ 011O auditor read-only view > filters and opens populated Epic 011 records without mutation controls  393ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 2098ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  961ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  791ms
 ✓ src/services/authSession.test.ts (39 tests) 61ms
 ✓ src/services/servicingApi.test.ts (13 tests) 123ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 889ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  328ms
 ✓ src/services/portalApi.test.ts (10 tests) 69ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 454ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 32ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 125ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 1472ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  1472ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 669ms
   ✓ 010N Header search path > navigates the transient query to S02 without building a local result index  667ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 256ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 293ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 617ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 89ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 263ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 100ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 121ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 323ms
   ✓ production demo surface isolation > removes tracer navigation and rejects direct tracer navigation even with permission  322ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/playwright.seed.test.ts (3 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 43ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2107ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1826ms

 Test Files  55 passed (55)
      Tests  437 passed (437)
   Start at  14:28:05
   Duration  19.90s (transform 6.86s, setup 0ms, collect 28.22s, tests 65.75s, environment 19.13s, prepare 6.29s)


Duration milliseconds: 20736
Exit code: 0
