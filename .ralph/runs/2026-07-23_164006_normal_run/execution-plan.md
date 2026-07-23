# Execution Plan

Selected slice: 011N-grievance-workflow

## Scope

Implement the prepared backend grievance vertical slice only:

- Persist generated grievance references, source-object linkage, governed documents, assignment,
  server-derived TAT/overdue state, monotonic history, resolution, acknowledgement/notice truth,
  and audit evidence.
- Expose staff create, filtered/paginated list, scoped detail, assignment/update, and resolution
  endpoints through one grievance workflow module.
- Add the retry-safe overdue/sensitive escalation entry point used by the existing 011K scheduler,
  including recovery-conduct fair-practice linkage without exposing internal recovery notes.
- Supply borrower self-scope serialization primitives for slice 011NA; no frontend work is included.

## Public Test Seam

Use the HTTP grievance endpoints and the scheduled grievance escalation entry point as the observable
interfaces. Exercise real persistence, permission/object-scope policy, communications queuing, audit,
documents, and recovery/default relationships. Mock only external delivery transport if the existing
communications owner requires it.

## TDD Sequence

1. RED/GREEN: authorised creation produces exactly one generated reference, source-scoped linkage,
   configured owner/due date, supporting-document provenance, initial history, and audit.
2. RED/GREEN: scoped list/detail and borrower-safe projection enforce role and object scope without
   leaking other members or internal recovery facts.
3. RED/GREEN: CS assignment/update preserves append-only history and rejects invalid/backward or
   post-close edits.
4. RED/GREEN: resolution requires a nonblank summary, is terminal/retry-safe, retains optional
   governed evidence, and queues an honest borrower notice through communications.
5. RED/GREEN: overdue and recovery-conduct escalation is server-date-derived, retry-safe, linked to
   the applicable default/action/fair-practice evidence, and never resolves the grievance.
6. Add the declared two-test PostgreSQL race acceptance for concurrent reference creation and
   concurrent terminal resolution/escalation behavior.

Each failing and passing focused command will use
`/Users/amitkallapa/LMS/.ralph/venv/bin/python` and be retained under
`evidence/terminal-logs/`.

## Verification

- Focused grievance module/API/permission/object-scope/reverse-consumer tests after each behavior.
- Declared PostgreSQL acceptance label (when the local PostgreSQL runtime is available).
- Django `check` and `makemigrations --check`.
- Targeted API examples and migration-plan evidence.
- Do not run the complete backend suite or coverage locally; independent Ralph validation owns the
  authoritative impacted/full lane.
- Review targeted diff/stat, complete the risk assessment and review packet, and leave the result
  exactly `Ready for independent validation`.

## Guardrails

- One migration maximum; no new dependency.
- Do not edit protected paths, `docs/source/`, orchestrator-owned state/progress/changed-files, or
  unrelated slices.
- Record only genuinely source-silent implementation assumptions in
  `docs/working/ASSUMPTIONS.md`; do not invent TAT, authority, or recovery policy.
