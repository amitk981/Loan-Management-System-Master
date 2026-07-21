# Execution Plan

Selected slice: `010K-cfo-quarterly-mis`

## Scope and seams

- Add quarterly MIS ownership to the backend monitoring module, behind public generate, list/detail,
  drill-down, submit-to-CFO, mark-reviewed, and export interfaces.
- Reuse canonical loan, ledger/allocation, interest, DPD, reminder, document, permission, and audit
  owners. Generation reads those modules but never mutates their records or recalculates DPD/reminders.
- Persist a frozen snapshot plus versioned report identity. Draft exact replay is deterministic;
  submitted/reviewed evidence is immutable and later correction creates a retained revision.
- Expose not-yet-owned Epic 011/012 facts as explicitly unavailable fields, not invented zeroes.
- No frontend work, live BI, notification sending, or default/recovery/closure/compliance implementation.

## TDD tracer bullets

1. Inspect existing monitoring, finance, loan, document/export, audit, permission, pagination, and
   PostgreSQL acceptance patterns; identify the smallest existing public seams to extend.
2. RED then GREEN: generate one cutoff-correct seeded report through the HTTP interface and retain
   immutable snapshot/drill-down source evidence, including exact replay behavior.
3. RED then GREEN: reject invalid FY/quarter/cutoff, missing canonical truth, wrong permission/scope,
   future-dated activity, and duplicate/concurrent authoritative generation.
4. RED then GREEN: submit and review only in order with distinct actor/timestamp audit evidence;
   prove submitted/reviewed report data cannot be overwritten and revisions retain prior evidence.
5. RED then GREEN: bounded drill-down and PDF/Excel exports reconcile to the frozen totals while
   unavailable future-epic metrics remain explicit.
6. Add the two declared PostgreSQL race cases for generation and transition contention and save
   focused RED/GREEN output under `evidence/terminal-logs/`.

## Contract and schema work

- Add no more than one migration, with uniqueness/index/transaction constraints supporting replay,
  revision, and immutable state.
- Seed the three exact monitoring MIS permissions through the existing catalogue mechanism.
- Update `docs/working/API_CONTRACTS.md` and the selected digest section with the implemented request,
  response, pagination, replay/revision, transition, export, and unavailable-field contracts.

## Verification and evidence

- Run focused Django test labels with the mandated Ralph virtualenv interpreter; save explicit RED
  and GREEN logs, reverse-consumer results, query-count output, export samples/hashes, and database
  identity evidence in the current run folder.
- Run the declared PostgreSQL acceptance class locally when the runtime is available; otherwise keep
  the exact class collectible for the orchestrator's trusted two-pass PostgreSQL gate.
- Run backend `manage.py check`, focused impacted tests, and `makemigrations --check`; do not run the
  complete backend suite or coverage because the orchestrator owns those authoritative gates.
- Inspect targeted diffs for source fidelity, permissions, immutability, auditability, financial data
  integrity, and scope. Finish `risk-assessment.md`, `review-packet.md` (exact Ready result), and
  `final-summary.md` without editing orchestrator-owned state/status/changed-file bookkeeping.
