# Execution Plan

Selected slice: `007B-approval-case-creation-from-appraisal`

## Scope and seams

- Extend the approvals-owned `SanctionHandoffModule`; credit remains responsible only for the
  reviewed-appraisal handoff and does not import approval persistence.
- Enrich the unique 006G pending shell from authoritative appraisal/loan-limit snapshots by calling
  the public matrix and committee resolvers exactly once each for the appraisal review date.
- Add the source-required amount, excluded-approver, related-entity, exception/reason, resolver,
  committee, and loan-limit provenance facts to the existing case snapshot representation.
- Add the source §25.2 POST adapter with `approvals.case.create`, strict payload validation,
  idempotent same-snapshot behavior, and stable 400/403/409 envelopes. Preserve the existing 006G
  submit permission path separately.
- No frontend work: 007I owns the sanction workbench wiring and the current routed screen remains
  intentionally disconnected.

## TDD tracer bullets

1. RED/GREEN: submit a reviewed appraisal to create the unrouted shell, enrich it through the
   public module/API, and read the canonical immutable snapshot for the lower threshold route.
2. RED/GREEN: prove upper-threshold and authoritative exception-condition routing, including the
   concrete CFO/director user selection and complete resolver projection.
3. RED/GREEN: prove identical repeats return the same case without writes; conflicting repeats and
   decided cases return 409 without changing the case/audit/workflow ledger.
4. RED/GREEN: prove missing/stale loan-limit provenance, missing/ambiguous effective configuration,
   client entity substitution, and pending/losing proposals leave the unrouted shell unchanged.
5. RED/GREEN: prove 401/403 permission behavior and later approved configuration activation cannot
   mutate the stored historical case projection.

Each RED and GREEN command will use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and be retained
under `evidence/terminal-logs/`.

## Documentation and verification

- Add a migration and update `docs/working/API_CONTRACTS.md` for the enrichment adapter/read fields.
- Run the focused approval-case tests throughout, then backend check, migration sync, full backend
  coverage suite, and all configured frontend build/typecheck/lint/test gates.
- Save API examples, changed-files, risk assessment, review packet, final summary, state/progress/
  handoff updates, mark only 007B complete, and sharpen the next one or two Not Started slices using
  already-opened Epic 007 material.
