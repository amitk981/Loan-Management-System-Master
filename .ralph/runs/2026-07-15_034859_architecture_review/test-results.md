# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_034859_architecture_review/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 973ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  600ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1156ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  537ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  312ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1237ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  428ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1633ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 228ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 186ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2375ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1246ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  864ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 616ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 69ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 178ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 17ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/portalApi.test.ts (4 tests) 14ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2695ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2225ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 4752ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  346ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  366ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  300ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  373ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  350ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  499ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3409ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1993ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  04:17:16
   Duration  6.49s (transform 5.09s, setup 0ms, collect 8.97s, tests 19.97s, environment 3.31s, prepare 2.00s)

