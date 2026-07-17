# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_174605_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1540ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  485ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  849ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1868ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  899ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  448ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2380ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  382ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  395ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2725ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1531ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  917ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2996ms
   ✓ 008M2 documentation workspace contract > keeps S26 facts in the approved queue/card vocabulary without the invented facts grid  302ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  404ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  516ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  358ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  340ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 814ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  305ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 985ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  700ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1577ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  666ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 831ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  730ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 408ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 114ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 276ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 90ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 68ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 79ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 47ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/services/authSession.test.ts (36 tests) 48ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 24ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 45ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6599ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  847ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  448ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  409ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  414ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  565ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  411ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  345ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  653ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3264ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2680ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5079ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3084ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  340ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  17:54:28
   Duration  8.95s (transform 5.39s, setup 0ms, collect 12.40s, tests 32.20s, environment 5.39s, prepare 2.34s)


Duration milliseconds: 9505
Exit code: 0
