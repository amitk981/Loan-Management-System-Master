# Execution Plan

Selected slice: 008L5-current-stage4-and-response-evidence-closure

1. Reproduce the two architecture-review failures through the public bank-decision and MP11 APIs,
   save failing-first terminal output, and inventory each attempted writer's decision/audit/workflow/
   version side effects.
2. Add the smallest vertical bank-authority test and implementation cycle: resolve and lock the
   approval owner's latest terminal sanctioned facts, freeze the exact approval-case and sanction-
   decision identities into immutable bank evidence, and reconcile them for replay/current truth.
3. Extend the public bank matrix across status-only, absent/rejected/returned/replaced/malformed and
   stale-cycle cases, then add the declared PostgreSQL changed-decision/latest-case race with exact
   winner/loser ledgers and execute it twice.
4. Add the smallest vertical MP11 response-chain test and implementation cycle: resolve each current
   immutable response from its exact response event and optional ordered resubmission event; fail
   closed for missing, duplicate, foreign, contradictory, reversed, actor/entity/workflow/state, or
   extra terminal evidence without exposing internal ids.
5. Extend public GET/resubmit tests for the complete evidence matrix and verify invalid evidence
   leaves the staff deficiency open, disables resubmission, and creates no success artifacts.
6. Run focused backend tests after each red/green cycle, then Django check, migration drift,
   configured full backend coverage, and all frontend build/typecheck/lint/test gates. Save the
   terminal logs and sanitized contract/ledger evidence in this run folder.
7. Review scope and risk, update API/digest/assumption documentation only if the implemented public
   contract requires it, sharpen the next one or two Not Started slices from already-open sources,
   and finish the Ralph state/progress/handoff/slice/run artifacts without invoking git writes.
