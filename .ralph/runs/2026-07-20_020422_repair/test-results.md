# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_011116_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1069ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  340ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  359ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1471ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1020ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1737ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  815ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  466ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2659ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  485ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  379ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 756ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  471ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 398ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3477ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  331ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  738ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  539ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  433ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 681ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  600ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 271ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2660ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1323ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1034ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1392ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  449ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1229ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  478ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  498ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 502ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  305ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 258ms
 ✓ src/services/portalApi.test.ts (7 tests) 25ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 424ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 131ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 576ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 24ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 394ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 121ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7473ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  660ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  483ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  454ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  403ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  418ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  352ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  384ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  338ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  454ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  405ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1168ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 114ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 100ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 15ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 161ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 61ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6563ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3363ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  344ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  342ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  373ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  487ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  346ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 18ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1309ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1201ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  02:11:59
   Duration  11.16s (transform 4.98s, setup 0ms, collect 16.64s, tests 36.24s, environment 8.07s, prepare 3.32s)


Duration milliseconds: 12118
Exit code: 0
