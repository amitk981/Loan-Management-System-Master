# Execution Plan

Selected slice: `009F-cfc-authorization-rejection`

## Scope and Interface

- Extend the existing deep `disbursements.modules.disbursement_workflow` module with one public
  `authorise` interface; do not create a second workflow owner or call upstream readiness/legal/
  security/SAP owners during authorisation.
- Add the exact `POST /api/v1/disbursements/{disbursement_id}/authorise/` route accepting only
  `decision` (`approved` or `rejected`) and bounded, trimmed `comments`.
- Extend the initiated disbursement aggregate and its migration with immutable nullable checker,
  decision, request/network, evidence-digest, audit, workflow, and action identities needed to
  reconcile one terminal CFC decision.

## TDD Tracer Bullets

1. RED→GREEN: public CFC approval through the workflow interface and HTTP route; assert the safe
   response, immutable decision evidence, completed CFC task, and unchanged transfer/account truth.
2. RED→GREEN: public rejection with the same retained evidence and no transfer-success side effects.
3. RED→GREEN: validation, effective governed-role/permission/maker-checker/object-scope denials,
   stale or incoherent initiation evidence, and nondisclosing missing/cross-object failures.
4. RED→GREEN: exact replay is zero-write while changed/opposite replay conflicts.
5. RED→GREEN: five-caller PostgreSQL approval/rejection races retain one complete winner and no
   loser success evidence; run the declared race contract twice when the local PostgreSQL harness
   is available.

## Verification and Evidence

- Save focused RED and GREEN backend logs, sanitized approve/reject/conflict response examples,
  Django check/migration-sync results, and PostgreSQL race logs under `evidence/terminal-logs/`.
- Run the focused backend authorisation and impacted initiation tests with the mandated Ralph venv.
- Run backend `manage.py check` and `makemigrations --check`; do not run the full backend suite or
  coverage because the orchestrator owns those authoritative gates.
- No frontend production code or screenshots are in scope. Run frontend lint, typecheck, tests, and
  build because the configured Ralph gates require them.
- Update the API contract ledger, Epic 009 digest, assumptions only if needed, slice status, state,
  progress, handoff, changed-files, risk assessment, review packet, and final summary. Sharpen the
  next one or two Not Started slices only with requirements from source material already opened.

## Risk Controls

- Preserve maker-checker separation under row locks and database constraints.
- Never set transfer success, UTR, disbursed time, funded balances, activation, advice, register,
  schedule, repayment, or communication truth.
- Retain only safe identifiers/digests in audit/workflow/task evidence; never expose bank or member
  plaintext, capabilities, tokens, or internal task/workflow identifiers in the response.
