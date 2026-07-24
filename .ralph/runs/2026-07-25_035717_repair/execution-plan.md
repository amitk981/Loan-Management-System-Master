# Execution Plan

Selected slice: 011PE-grievance-audit-archive-frontend-wiring

1. Treat the prior run's authoritative trusted-browser diagnostics as the feedback loop and preserve
   the current candidate. Limit repair scope to the demonstrated browser-spec selector ambiguity.
2. Confirm the exact `Archive` tab is the intended control and change only the ambiguous locator in
   `e2e/default-closure-compliance-staff.e2e.spec.ts`; do not alter application behavior or styling.
3. Run the exact named trusted browser validator/spec until the application assertion passes. Save
   the repair command and output in this run's `evidence/terminal-logs/`; distinguish any
   pre-page Chrome launch failure from a product assertion.
4. Run focused frontend checks appropriate to the E2E-only edit, inspect targeted diff/stat output,
   and confirm no protected or unrelated candidate files were changed by the repair.
5. Save the repair risk assessment, review packet, and final summary. Set the review packet Result
   exactly to `Ready for independent validation`.

Permissions checked before edits:

- Allowed: `.ralph/runs/2026-07-25_035717_repair/**`. The selected slice and repair prompt
  explicitly require the existing `sfpcl-lms/e2e/default-closure-compliance-staff.e2e.spec.ts`;
  that in-worktree path is not listed under either `requires_approval` or `forbidden` in
  `.ralph/permissions.json`.
- Protected/forbidden paths will not be edited, including `docs/source/**`, `scripts/**`,
  `.ralph/config.yaml`, `.ralph/permissions.json`, state/progress, slice status, and protected
  workflow/policy documents.
- No dependency installation, git staging, commit, merge, or push will be attempted.
