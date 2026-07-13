# Execution Plan

Selected slice: `005FA4-portal-auth-real-boundary-flag-proof`

## Scope and permissions

- Change only the existing frontend auth boundary tests and trusted Playwright contract unless a
  failing boundary test reveals a production defect.
- Write evidence and run bookkeeping only beneath the permitted `.ralph/runs`, `docs/working`,
  `docs/slices`, and `.ralph` paths.
- Do not modify protected files, `docs/source`, backend code, visual styling, or unrelated product
  behavior.

## Test-first implementation

1. Replace the manually projected `LoginScreen` flag test with module-isolated tests that import
   and render the real `App`/`RoleProvider` boundary for unset, explicit false, and true flag
   environments. Assert unauthenticated authority fields and protected content are absent, and
   true exposes only the approved staff demo controls without portal authority.
2. Run that focused test before adapting production/test seams and save the expected red output in
   `evidence/terminal-logs/`.
3. Make the smallest testability/contract changes required to render the real boundary while
   preserving production behavior. Extend interaction coverage for empty/populated portal login,
   exact request body/count, and failed-transport logout clearing all authority and route state.
4. Update the pinned Playwright spec to use `RALPH_EVIDENCE_DIR`, create its screenshot directory,
   and capture both declared screenshots without a hard-coded run ID.
5. Run focused tests green and save the output, then run lint, typecheck, build, frontend tests,
   backend check, migration sync, and full backend coverage with the mandated interpreter.

## Completion artifacts

- Preserve browser launch/acceptance output honestly; do not fabricate screenshots if Chromium is
  blocked by the sandbox.
- Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update
  progress, handoff, state, the selected slice status, and sharpen the next one or two Not Started
  slices only from source/digest material already opened.
