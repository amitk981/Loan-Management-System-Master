# Execution Plan

Selected slice: 006Z7-active-member-relaxation-authority-and-evidence-race-closure

1. Confirm the source-backed BR-003..007 relaxation order, member authority matrix, evidence
   transaction boundary, and existing 006Z6 snapshots. Limit implementation to member-domain
   active-status, supply/service evidence mutations, their API/module tests, and Ralph artifacts.
2. RED: add a public-module regression proving a recent non-active member qualifies only when one
   complete verified supply year and distinct verified relaxation evidence are both persisted.
   Save the focused failing output under `evidence/terminal-logs/`.
3. GREEN: reorder the active-member rule without weakening active four-year/service routes, then
   rerun the focused module and API matrices.
4. RED/GREEN: replace caller-authored global authority with one member-owned policy and exercise
   equivalent registry/active-status owner, global, permission, and object-scope rows through the
   production evaluator (no evaluator mocks).
5. RED/GREEN: centralize the Member/evidence lock order for supply create/verify and service
   create/update mutations; ensure every successful evidence mutation advances member provenance
   so an already-calculated result becomes stale.
6. Add independently selectable PostgreSQL verifier-vs-supply-create, supply-verify/update,
   service-create, and service-update races. Assert the complete member/status/evidence/history/
   audit/workflow snapshot, one coherent winner/current pointer, and zero loser evidence. Retain
   the existing two-verifier race and run the declared PostgreSQL acceptance twice.
7. Remove unreachable service-evidence and authority compatibility code; run dependency/dead-code
   scans, focused module/API matrices, Django check, migration sync, full backend coverage, and all
   configured frontend gates. Save green logs.
8. Complete changed-files, risk, review, summary, state, progress, handoff, digest, selected-slice
   status, and sharpen the next one or two Not Started slices using only already-open source facts.
