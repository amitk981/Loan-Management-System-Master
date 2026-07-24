# Execution Plan

Selected slice: 011PE-grievance-audit-archive-frontend-wiring

1. Confirm the active worktree is safe and the intended edits are confined to permitted frontend
   and current-run evidence paths. Inspect the two owned prototype pages, the Epic 011 service seam,
   existing focused tests, auth/transport conventions, and the inherited trusted-browser spec.
2. Add focused RED tests for the grievance list/resolve/refetch contract and its loading, empty,
   error, unauthorized, validation, blocked, and success projections. Save the failing output under
   `evidence/terminal-logs/`.
3. Minimally extend the shared Epic 011 API seam and wire `GrievancesHub.tsx` to canonical backend
   projections. Require the server-supported target status and resolution reason, submit through
   the governed action endpoint, and refetch after success. Run and save GREEN focused output.
4. Add focused RED tests for archive list/render/download behavior, read-only controls, audited
   download transport, and canonical refetch. Save the failing output, then minimally wire
   `AuditArchiveHub.tsx` to 011J archive records and save GREEN output.
5. Extend the inherited `default-closure-compliance-staff.e2e.spec.ts` only as required to cover the
   complete S53-S68 staff contract and preserve the five named screenshots. Run the exact complete
   browser spec twice and retain both runs' screenshots and logs.
6. Run focused reverse-consumer tests, frontend typecheck, lint, and build. Run the cheap Django
   system and migration-consistency checks with the mandated Ralph virtualenv interpreter; leave
   the authoritative impacted/full backend lane to the orchestrator.
7. Verify the five original 011P page owners contain no mock imports or inline business fixtures,
   inspect diff stats and targeted hunks against the 30-file/2,000-line limits, then complete the
   role/action/blocker and mock-removal matrices, risk assessment, review packet, and final summary.
   Set the review result exactly to `Ready for independent validation`.

Permissions checked before edits:

- Allowed: `sfpcl-lms/src/**`, the existing frontend E2E path, and
  `.ralph/runs/2026-07-25_032730_normal_run/**`.
- Protected/forbidden paths will not be edited, including `docs/source/**`, workflow scripts,
  `.ralph/config.yaml`, `.ralph/permissions.json`, state/progress, slice status, and protected policy
  documents.
- No dependency installation, git staging, commit, merge, or push will be attempted.
