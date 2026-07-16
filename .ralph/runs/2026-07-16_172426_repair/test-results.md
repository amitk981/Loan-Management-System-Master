# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_165237_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 493ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  432ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 694ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  428ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2113ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  345ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2454ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1252ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  925ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2803ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  756ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  432ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  350ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1218ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  414ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1312ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  568ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  359ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 531ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  347ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1631ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1136ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 338ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1175ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  409ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  488ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 141ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 138ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 151ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 317ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 43ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 71ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 44ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/services/authSession.test.ts (36 tests) 50ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/services/portalApi.test.ts (6 tests) 118ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 36ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 17ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 91ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 16ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 18ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7468ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  479ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  379ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  308ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  398ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  504ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  556ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  394ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1045ms
   ✓ SanctionWorkbench authenticated container > surfaces action error state 'VALIDATION_ERROR' without retry  342ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 4426ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3335ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  718ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  372ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6198ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3682ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  439ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  587ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  393ms

 Test Files  36 passed (36)
      Tests  323 passed (323)
   Start at  17:31:28
   Duration  10.13s (transform 5.91s, setup 0ms, collect 13.84s, tests 34.21s, environment 6.80s, prepare 4.56s)


Duration milliseconds: 10818
Exit code: 0
