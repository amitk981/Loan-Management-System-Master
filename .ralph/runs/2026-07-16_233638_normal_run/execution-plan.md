# Execution Plan

Selected slice: `009D3-readiness-approval-reader-and-boundary-closure`

## Scope and interface

- Preserve the sole public readiness interface at
  `disbursements.modules.disbursement_readiness.evaluate(actor, loan_account_id)` and the existing
  read-only HTTP route/standard envelope.
- Keep the 23 ordered checks and A-126 source-bank blocker unchanged.
- Change only readiness approval/current-evidence reconciliation, required-signer truth, canonical
  reader scope, and the readiness composition seam. No schema, frontend, payment initiation, or
  source-document changes are planned.

## TDD sequence

1. Add a public readiness regression proving a changed current completion version makes
   documentation and all three ordered approvals fail; run it alone and save the failing output.
   Implement exact ordered current completion/action/audit/workflow/version reconciliation and run
   the same test green.
2. Add public regressions for missing/wrong/stale/duplicate signer and mismatch evidence plus
   corrected-copy/current-renderer/security mutations. Run each focused probe red, then make legal
   readiness consume the existing owner decisions and current terminal evidence without `all([])`.
3. Add the HTTP reader matrix for Senior Finance, pre-009E CFC, Credit Manager, CFO, Auditor,
   wrong role/grant, inactive actor, intake owner, absent id, and cross-object ids. Run red, then
   implement canonical loan-account scopes with nondisclosing denial and zero writes.
4. Add a dependency/interface regression proving the disbursement module owns composition and the
   generic `processes` coordinator exposes no readiness pass-through. Run red, remove the shallow
   wrappers, and compose the existing typed security callback directly behind `evaluate`.
5. Exercise a genuine owner-backed fixture through the public route to A-126 and, via only the
   governed source-bank decision seam, all 23 passes. Capture bounded query count and zero-write
   evidence on that complete path.

## Verification and artifacts

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every Django/test command.
- Run focused readiness and impacted legal/loan-account tests only; do not run the complete backend
  suite or full coverage because the orchestrator owns those gates.
- Run Django check and migration-sync; run frontend typecheck, lint, tests, and build only if the
  shared configured gate requires confirmation despite no frontend changes.
- Save red/green and gate logs under `evidence/terminal-logs/`, plus self-contained API/reader/
  ordered-ledger evidence. Complete changed-files, risk assessment, review packet, final summary,
  state, progress, handoff, slice status, digest, and sharpen the next one or two Not Started slices.

## Risk controls

- High risk: readiness protects payment initiation and handles financial/document evidence.
- Fail closed on missing, duplicate, reordered, stale, cross-object, or changed evidence.
- Preserve read-only behavior and safe blocker reasons; never expose owner payloads or sensitive
  values. Do not add a migration or dependency.
