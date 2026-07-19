# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_154507_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1896ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > renders the approved three-card composition and server advisory only from the mounted projection  365ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  551ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  876ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1958ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  988ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  476ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2819ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  471ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  502ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  352ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3098ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1663ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1135ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3959ms
   ✓ 008M2 documentation workspace contract > keeps S26 facts in the approved queue/card vocabulary without the invented facts grid  364ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  481ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  744ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  618ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  404ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1050ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  379ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  328ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1802ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 400 failure without refetch  303ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  558ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 666ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  396ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 1091ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  517ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  468ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 630ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  551ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 483ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 528ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 346ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 521ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 186ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 89ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 214ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 270ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7741ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  1037ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  534ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  414ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  401ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  387ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  388ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  511ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  423ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  451ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  418ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  839ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 94ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 184ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 87ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 70ms
 ✓ src/services/authSession.test.ts (36 tests) 43ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 39ms
 ✓ src/services/portalApi.test.ts (7 tests) 29ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 42ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 20ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 15ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6590ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3764ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  317ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  413ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  335ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  336ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  343ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 43ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 15ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3391ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3035ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  42 passed (42)
      Tests  351 passed (351)
   Start at  16:31:22
   Duration  11.55s (transform 7.01s, setup 0ms, collect 17.05s, tests 40.08s, environment 8.38s, prepare 3.21s)


Duration milliseconds: 12220
Exit code: 0
