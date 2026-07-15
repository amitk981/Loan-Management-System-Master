# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_043916_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 940ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  562ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1246ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  623ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  303ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1272ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  430ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1584ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 280ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2330ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1150ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  889ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 549ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 196ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 146ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (25 tests) 2922ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  390ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  368ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  375ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  706ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 27ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 40ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 14ms
 ✓ src/services/authSession.test.ts (27 tests) 40ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2650ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2258ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3277ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1929ms

 Test Files  33 passed (33)
      Tests  269 passed (269)
   Start at  05:15:24
   Duration  6.35s (transform 4.84s, setup 0ms, collect 9.17s, tests 17.94s, environment 3.52s, prepare 2.02s)

