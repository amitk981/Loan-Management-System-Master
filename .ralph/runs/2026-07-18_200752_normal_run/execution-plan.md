# Execution Plan

Selected slice: CR-011-github-ci-migration-test-schema-isolation

1. Capture the focused red failure by running the approvals migration class followed by the
   communications migration class in one Django test process with the mandated virtualenv Python.
2. Add current-leaf cleanup to `ApprovalReadScopeMigrationTests` and explicit current-leaf setup to
   `GenericCommunicationJobMigrationTests`; do not touch production code or migrations.
3. Capture green evidence for the formerly failing order, reverse order, and focused four-worker run.
4. Run proportional backend gates: Django check and migration-sync check. Record unchanged frontend
   gates as not applicable because no frontend files change; do not run the complete backend suite,
   which is reserved for independent orchestration.
5. Audit every migration-changing `TransactionTestCase` for leaf restoration, review the diff against
   this CR, save evidence and required Ralph artifacts, sharpen the next concrete slices only if the
   already-read requirements reveal an actual missing detail, then update state/progress/handoff and
   mark CR-011 complete pending independent validation.
