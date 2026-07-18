# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_210357_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1328ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  406ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2883ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  558ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1880ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 3073ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1082ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  1094ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 4067ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  543ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders a stale 409 without retry, synthesis, or refresh  505ms
   ✓ default AppraisalWorkbench authenticated HTTP container > clicks 'submit review' through the authenticated boundary and refreshes four reads  426ms
   ✓ default AppraisalWorkbench authenticated HTTP container > clicks 'reviewed decision' through the authenticated boundary and refreshes four reads  303ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  656ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 611ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  395ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 4794ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  445ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  1083ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  469ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  1208ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  393ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 626ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  521ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 287ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 181ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 409ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1203ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  381ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 80ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2310ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1092ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  950ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 211ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 31ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 100ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 48ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 120ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 42ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7545ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  987ms
   ✓ SanctionWorkbench authenticated container > clears prior rows and totals when a later collection fails with 'OBJECT_ACCESS_DENIED'  437ms
   ✓ SanctionWorkbench authenticated container > keeps the newest empty state when an older detail response arrives last  340ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  942ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  424ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  418ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  349ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  318ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  397ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  364ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  676ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 77ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 34ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5163ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2995ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  375ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  300ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1193ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1087ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  21:20:06
   Duration  10.47s (transform 6.19s, setup 0ms, collect 15.78s, tests 36.62s, environment 7.15s, prepare 2.56s)


Duration milliseconds: 11712
Exit code: 0
