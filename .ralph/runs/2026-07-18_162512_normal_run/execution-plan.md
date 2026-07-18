# Execution Plan

Selected slice: `009H6-legacy-advice-template-provenance-closure`

## Scope and seams

- Keep the change inside the communications persistence/module seam: exactly one new
  communications migration, matching model state, focused migration/public-interface tests, and
  Ralph bookkeeping/evidence.
- Classify only outboxes whose accepted provider attempt was created by communications migration
  0005 (`legacy:pre-outbox` or `legacy:retained-outbox`). Preserve their outbox, attempt, provider,
  receipt, Communication, action, audit, and workflow identities while clearing template facts that
  0005 reconstructed from a mutable current template.
- Keep genuinely frozen post-0005 outboxes `verified`. Current dispatch/finalization/replay/portal
  interfaces must continue to require a coherent verified template snapshot and must reject
  `legacy_partial` rows without invoking a provider or manufacturing replacement delivery truth.
- No frontend, API response, financial, disbursement, or source-document changes.

## TDD tracer bullets

1. RED: copy the architecture-review provenance probe into the focused migration tests and build a
   genuine historical fixture where the template changes after retained delivery but before the new
   migration. Assert that forward migration marks the exact 0005 outbox `legacy_partial`, clears
   reconstructed facts, and preserves every non-template identity/ledger.
2. GREEN: add communications migration 0008 and matching model constraints/nullability so only the
   deterministic 0005 legacy attempt classes are downgraded; make reverse available only when the
   original verified template facts remain truthfully recoverable, otherwise fail closed.
3. RED/GREEN incrementally: cover retained-outbox, pre-outbox delivery, accepted-not-finalized,
   pending, malformed/ambiguous, and genuinely post-0005 verified rows through
   forward/reverse/reapply manifests.
4. RED/GREEN through public interfaces: prove replay and portal/download selection reject
   `legacy_partial` with zero provider calls and no history deletion/replacement; prove copied
   current template values or a bare status flip cannot upgrade current truth.

## Verification and evidence

- Save focused RED and GREEN output under
  `.ralph/runs/2026-07-18_162512_normal_run/evidence/terminal-logs/` using the mandated Ralph Python
  interpreter.
- Run focused communications migration/public tests, Django check, migration sync, and Python
  compilation. Run the declared PostgreSQL five-race acceptance twice if the local socket is
  available; otherwise record the sandbox limitation and leave the authoritative gate to Ralph.
- Do not run the complete backend suite. Run frontend gates only if a frontend file is impacted.
- Review the final diff against the slice, source clauses, protected-path rules, migration count,
  and configured 30-file/2,000-line limits; then update risk, review packet, final summary,
  changed-files, state, progress, handoff, digest, slice status, and sharpen the next one or two
  already-opened Not Started slices without speculative scope.
