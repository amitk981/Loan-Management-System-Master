# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_091246_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1522ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  678ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  377ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1568ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  414ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2299ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  340ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  389ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2700ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1413ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  935ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3307ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  399ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  646ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  383ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  467ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 3374ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  821ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  593ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  1876ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 3754ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  322ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  3156ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 3084ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  1222ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  1415ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 1151ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  762ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 841ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  721ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 482ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 472ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 513ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  303ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 393ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 481ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 209ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 214ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 197ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 9707ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  726ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  364ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  388ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  450ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  427ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  573ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  1154ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  1465ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  624ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  605ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1048ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 197ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 92ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 36ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/services/authSession.test.ts (36 tests) 50ms
 ✓ src/services/portalApi.test.ts (8 tests) 54ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 16ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 17ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 14ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 9404ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  6905ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  452ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  312ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2872ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2510ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  44 passed (44)
      Tests  362 passed (362)
   Start at  09:55:29
   Duration  13.19s (transform 5.66s, setup 0ms, collect 17.49s, tests 49.27s, environment 12.03s, prepare 3.26s)


Duration milliseconds: 14076
Exit code: 0
