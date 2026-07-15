# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_032113_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 983ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  579ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1219ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  404ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1215ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  572ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  334ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1712ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  309ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  341ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2318ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1154ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  894ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 302ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 167ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 533ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 94ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (22 tests) 2751ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  508ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  439ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  355ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  702ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 74ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 167ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 48ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/services/authSession.test.ts (18 tests) 27ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 16ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2604ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2273ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3401ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2197ms

 Test Files  33 passed (33)
      Tests  257 passed (257)
   Start at  03:43:45
   Duration  6.64s (transform 5.01s, setup 0ms, collect 9.23s, tests 17.93s, environment 3.78s, prepare 1.96s)

