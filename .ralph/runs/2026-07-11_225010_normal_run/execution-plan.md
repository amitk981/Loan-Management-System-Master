# Execution Plan — 006X MVP End-to-End Happy Path Tracer Bullet

1. Inspect the existing public credit APIs, fixtures, action projections, audit/workflow models,
   and 006H Playwright conventions. Reuse them without adding workflow or production UI.
2. RED: add one backend API integration tracer that uses distinct Deputy Manager Finance and
   Credit Manager clients to carry the same application through eligible assessment, in-limit
   calculation, appraisal create/PATCH/submit, independent review, sanction submission/readback,
   permission denials, exact linked IDs, metadata-only evidence, and idempotent repeat submission.
   Save the failing focused output under `evidence/terminal-logs/`.
3. GREEN: add only narrow missing fixture/test glue or contract code required by the public path;
   rerun the focused backend test and save passing output. No schema or business-rule expansion is
   planned.
4. Add a Playwright cross-role 006H path that consumes enabled resource actions, proves a global
   permission cannot override a disabled/missing resource action, checks the exact writable PATCH
   allowlist and canonical four-read refresh, verifies API/UI IDs, and declares reviewed and
   pending-sanction screenshots for independent browser validation.
5. Run focused feedback, then lint, typecheck, frontend tests/build, backend check, migration sync,
   and the full backend coverage suite using the mandated Ralph Python interpreter. Save logs.
6. Review the diff against the slice and source digest; sharpen the next one or two eligible
   Not Started slices using already-opened digests; write changed-files, risk, review, final
   summary, state/progress/handoff, and mark only 006X complete.

Permissions checked: intended edits are limited to `sfpcl_credit/**`, `sfpcl-lms/e2e/**`,
`docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and this run folder;
all are allowed. Protected, approval-required, forbidden, and `docs/source/**` paths will not be
modified.
