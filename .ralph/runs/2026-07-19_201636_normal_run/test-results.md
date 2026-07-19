# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_201636_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1158ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  431ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  419ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1411ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  380ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  725ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1654ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  788ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  451ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1983ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  332ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  307ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2714ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  324ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  651ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  359ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  372ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 669ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  438ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 335ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 656ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  560ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 181ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2249ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1140ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  859ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 384ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1013ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  368ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  412ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1203ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  386ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
 ✓ src/services/portalApi.test.ts (7 tests) 39ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 309ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 173ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 15ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 161ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 379ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5986ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  757ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  415ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  330ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  318ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  304ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  351ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  851ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4720ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2374ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  307ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  322ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  312ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1106ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1008ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  20:57:24
   Duration  9.01s (transform 4.50s, setup 0ms, collect 12.95s, tests 28.98s, environment 6.20s, prepare 2.73s)


Duration milliseconds: 9570
Exit code: 0
