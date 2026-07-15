# Execution Plan

Run: `2026-07-14_004058_normal_run`  
Slice: `007J2-settings-hub-panels-wiring-or-lockdown`

## Boundaries and permissions

- Edit only permitted frontend, test, working-document, slice, state, progress, and run-artifact paths.
- Preserve `ApprovalMatrixSettingsPanel` and `approvalRegistersApi` unchanged.
- Do not add backend configuration domains, migrations, dependencies, styling, or mock fixtures.

## Surface classification

| SettingsHub surface | Class | Treatment | Owner |
|---|---|---|---|
| Loan policy/product configuration | Existing source-backed API | Read retained versions from `/api/v1/config/loan-policy/`; allow `config.loan_policy.manage` actors to create a complete new draft version by POST; show loading, empty, denied/error, validation, success, and read-only states | 003E/006C, wired here |
| Approval matrix | Existing source-backed API | Preserve the delivered 007J component and service unchanged | 007J |
| Workflow TAT and escalation | Source-required, no configuration API | Remove illustrative rows/actions and show an explicit inert notice | 012EA |
| Document template management | Source-required, no document-template API yet | Remove illustrative rows/actions and show an explicit inert notice; do not conflate 003F communication content with S72 document files | 008A |
| User and role management | Existing authoritative screen elsewhere | Remove duplicate fixture users/role matrix and direct users to the real Admin User Management route; show no local mutation controls | 002G/002G2 |

## Test-first implementation

1. Add a public-interface SettingsHub test proving retained loan-policy versions load from the authenticated client and a read-only actor sees no mutation path. Run it and save RED evidence.
2. Add the typed loan-policy API client and policy panel, then run the focused test to GREEN.
3. Add a behavior test proving a canonical manager creates a full successor draft version (POST, never PATCH/activate), with validation/server errors rendered. Run RED then GREEN.
4. Add interaction/raw-source regressions proving TAT/templates/users are inert or delegated, approval matrix remains owned by 007J, and no inline policy/rate/threshold/retention/user/template business fixtures remain. Run RED then GREEN.

## Documentation and verification

- Record the classification, source extract, and any interface-composition assumption in working docs.
- Run focused tests regularly, then frontend typecheck, lint, all tests, and build.
- Run backend check, migration sync, and the full coverage gate with the mandated Ralph interpreter because all repository gates remain required even though backend production code is unchanged.
- Attempt the requested visual evidence without fabricating screenshots if the sandbox blocks localhost/Chromium.
- Complete review, risk, changed-file, final-summary, state, progress, handoff, slice status, and next-slice sharpening artifacts.
