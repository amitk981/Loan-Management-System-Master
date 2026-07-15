# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_151653_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1422ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  463ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1438ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  348ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  851ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1587ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  628ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  509ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2899ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  511ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the returned Credit Manager decision once  574ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  467ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3415ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1307ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1725ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (7 tests) 697ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  490ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 549ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  467ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 865ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  360ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 354ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 85ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 229ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 227ms
(node:43140) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 22ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 77ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 95ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 45ms
 ✓ src/services/authSession.test.ts (36 tests) 44ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 22ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2996ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2414ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  374ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6717ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  566ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  1056ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  411ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  340ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  316ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  373ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  312ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  340ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  348ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  619ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4424ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2900ms

 Test Files  35 passed (35)
      Tests  304 passed (304)
   Start at  16:36:12
   Duration  8.90s (transform 6.02s, setup 0ms, collect 12.23s, tests 28.42s, environment 7.47s, prepare 2.64s)

