# Execution Plan

Selected slice: `CR-004-member-governance-container-recurring-ci-timeout`

1. Preserve the current exact mounted create journey and establish RED with that named journey
   under an intentionally constrained Vitest default timeout and a single-worker/file-serial
   execution. Save terminal output in `evidence/terminal-logs/`.
2. Add a suite-local integration-test timeout and explicit sequential policy to
   `MemberGovernanceForm.container.test.tsx`; do not alter assertions, production code, or the
   global 5000 ms default.
3. Add one package script for the CI-shaped single-worker/file-serial execution of the complete
   affected container file.
4. Prove GREEN for the exact RED command, the focused CI-shaped command, repeated mounted runs,
   and execution alongside the complete frontend suite. Save all results.
5. Run frontend typecheck, lint, complete tests, and build, plus backend check, migration sync, and
   the full coverage gate with the mandated Ralph Python interpreter.
6. Review the diff against the CR acceptance criteria, sharpen the next one or two eligible
   `Not Started` slices using already-opened source/digest context, and finish Ralph state,
   progress, handoff, evidence, changed-files, risk, review, and summary artifacts.
