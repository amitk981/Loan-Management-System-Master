# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_105635_architecture_review/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 978ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  393ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  320ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1327ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  725ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1527ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  724ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  406ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2027ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  409ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  301ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 624ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  405ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2729ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  520ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  471ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  450ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 472ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  396ms
 ✓ src/services/authSession.test.ts (36 tests) 46ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 159ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 321ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1184ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  405ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 149ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 68ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2351ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1101ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  972ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 15ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 54ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 51ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5565ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  543ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  427ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  316ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  305ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  330ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  308ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  316ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  626ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 20ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4301ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2236ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  323ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  322ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1203ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1102ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  11:14:48
   Duration  7.97s (transform 4.58s, setup 0ms, collect 12.48s, tests 25.51s, environment 5.40s, prepare 2.64s)


Duration milliseconds: 8715
Exit code: 0
