# Execution Plan

Selected slice: `008C2-checklist-lifecycle-authority-and-side-effect-closure`

## Scope and interfaces

- Keep the existing HTTP approval action on the top-level sanction-completion process and make a
  missing terminal completion hook fail before any approval, sanction, register, communication,
  checklist, audit, or workflow write. Migrate direct approval callers to the process interface.
- Make the approvals owner return checklist facts only from the canonical latest-cycle, routable,
  complete frozen package and its matching terminal sanction decision. Require exact boolean
  subsidiary flags instead of Python truthiness.
- Add an application/member-owned public selector for authoritative cancelled-cheque mismatch
  facts; the legal checklist module must not import or query the members ORM.
- Keep checklist applicability synchronisation behind `refresh_for_approved_sanction`, preserve
  completion/verification/checklist/signature facts, return an explicit atomic conflict when an
  applicability change contradicts completion evidence, and classify generated-document linkage
  separately from applicability.
- Resolve post-sanction checklist reads through one permission/object-scope decision before any
  checklist existence query, while retaining A-104's pre-sanction compatibility route.
- Thread request id, IP address, user agent, actor role, and actor team through the sanction process
  and refresh evidence. Creation, applicability changes, linkage changes, replay, denial, and
  rollback must have exact zero/one-write behavior.

## TDD tracer bullets

1. RED then GREEN: a direct final approval without sanction completion is zero-write; HTTP and
   process approval create one atomic sanction/checklist ledger and carry request/actor context.
2. RED then GREEN: stale/malformed approval packages, incomplete subsidiary flag sets, and
   pending/conflicting cheque facts fail closed through owner-facing fact seams.
3. RED then GREEN: pending, completed, and verified checklist items survive unchanged refreshes;
   contradictory applicability changes raise a zero-write conflict.
4. RED then GREEN: current renderer provenance links via linkage-specific evidence without false
   applicability evidence or completion mutation; legacy provenance remains unlinked.
5. RED then GREEN: the full actor/status matrix resolves authority before checklist existence and
   produces nondisclosing 403/404 behavior without read-side writes.
6. Replace the old refresh race with the declared five-worker final-sanction race and run it twice
   on PostgreSQL, asserting one winner, one sanction decision, one checklist, eleven items, and exact
   winner/loser evidence.

## Verification and artifacts

- Save every focused failing and passing backend command under
  `.ralph/runs/2026-07-14_134809_normal_run/evidence/terminal-logs/` using the mandated Ralph venv.
- Run focused suites regularly, then Django check, migration sync, full backend coverage, frontend
  build/typecheck/lint/tests, and the PostgreSQL acceptance twice.
- Run the required independent standards/spec review, address findings, save dependency/audit/API
  examples, then update changed-files, risk, review packet, final summary, progress, handoff, state,
  the selected slice status, and sharpen the next two Not Started slices from already-read sources.
- Do not modify protected/source files and do not run git add/commit/push; the orchestrator owns
  independent validation and commit.
