# Execution Plan — 006Y8 Repair

1. Reproduce the trusted-browser contract failure with the repository's own parser and preserve the
   exact red output.
2. Repair only the demonstrated declaration defect: use a project-relative `e2e/*.spec.ts` path,
   list the three screenshot basenames as strict `Screenshot:` entries, and move unchanged scenario
   prose outside the parser-owned section.
3. Re-run the exact contract parser and Playwright collection, then run the configured frontend and
   backend quality gates without altering the quarantined implementation.
4. Save repair evidence, changed files, risk assessment, review packet, and final summary; preserve
   the prior slice/state/progress/handoff completion updates for independent revalidation.

Permissions checked before the slice-file edit: `docs/slices/**` and `.ralph/runs/**` are allowed by
`.ralph/permissions.json`. No protected or forbidden path is in repair scope.
