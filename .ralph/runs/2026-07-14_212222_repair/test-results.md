# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_201756_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1113ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  683ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1379ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  520ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1489ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  761ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  384ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1875ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  399ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2576ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1334ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  974ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 329ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 180ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 731ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 152ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 81ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 100ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 50ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3533ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3346ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5559ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  500ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  384ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  360ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  300ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  342ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  324ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  387ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  351ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  676ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3532ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2199ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  21:44:09
   Duration  8.03s (transform 7.55s, setup 0ms, collect 12.55s, tests 23.00s, environment 4.62s, prepare 2.30s)

