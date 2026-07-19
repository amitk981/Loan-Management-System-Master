# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_124426_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1515ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  355ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  810ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1649ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  687ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  496ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2367ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  429ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  387ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  335ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2819ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1527ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1004ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3102ms
   ✓ 008M2 documentation workspace contract > keeps S26 facts in the approved queue/card vocabulary without the invented facts grid  339ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  319ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  694ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  467ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  357ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 869ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  319ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1293ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  437ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 613ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  501ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 1146ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  469ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  637ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 852ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  579ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 407ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 470ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 492ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  329ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 213ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 180ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 170ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 167ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6293ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  624ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  417ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  441ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  428ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  500ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  638ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 73ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 42ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 103ms
 ✓ src/services/authSession.test.ts (36 tests) 40ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/services/portalApi.test.ts (7 tests) 25ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4941ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2640ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  327ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 14ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2443ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2198ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  42 passed (42)
      Tests  351 passed (351)
   Start at  13:25:05
   Duration  9.66s (transform 5.45s, setup 0ms, collect 14.44s, tests 32.57s, environment 7.86s, prepare 2.83s)


Duration milliseconds: 10236
Exit code: 0
