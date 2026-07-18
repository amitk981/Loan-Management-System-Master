# Execution Plan

Selected slice: `009H9D-communications-provenance-and-operator-boundary-closure`

## Boundary

Close only the architecture-review findings assigned to 009H9D: queued-advice provenance
completeness, exact job-kind authority for communication exceptions, source channel vocabulary,
strict exception pagination, and the thin worker/deep communications-module interface. Preserve
all retained H6/H8/H9B/H9C dispatch, retry, lease, replay, provider-evidence, and advice-finalization
contracts. No frontend change is planned.

## Red/Green Sequence

1. Copy the three independent review probes into retained tests and run them RED. Tighten the
   migration test into a one-field drift matrix covering every required frozen template fact,
   malformed variable collections, genuine queued forward/reverse/reapply, and cleared untrusted
   facts.
2. Correct migration `0008` at the earliest historical decision seam and run the provenance
   migration tests GREEN before proceeding.
3. Add public HTTP tests for generic/advice list, detail, and resolution authority, including
   opposite/revoked permission, inactive/cross-owner, stale version, and changed-job zero-write
   behavior. Run RED, move exact authority into the communications owner interface, then GREEN.
4. Add RED public collection tests for strict `page`/`page_size`, unknown parameters, stable pages
   beyond 100 rows, truthful totals, source `email`/`sms` vocabulary, legacy normalization, and
   redaction. Implement one communications-owned paginated evidence interface and any single
   required normalization migration, then run GREEN.
5. Add observable Email/SMS execution and exact/changed/cross-channel idempotency tests plus an
   executable dependency-seam test. Run RED, deepen the communications interface so adapter
   selection, due-job iteration, and safe task evidence remain internal while task/process callers
   only delegate, then run GREEN.

## Validation and Evidence

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Save each focused RED and GREEN command under
  `.ralph/runs/2026-07-19_020758_normal_run/evidence/terminal-logs/`.
- Run impacted communications/process tests, Django check, migration sync, and compilation. Do not
  run the complete backend suite or full coverage; the orchestrator owns those gates.
- Run the declared PostgreSQL five-race acceptance twice if the worktree runtime permits it; retain
  honest logs if the sandbox prevents the socket/browser capability.
- Update the communication exception API contract and the selected Epic 009 digest with only the
  durable resulting facts. Record any source-silent choice in `ASSUMPTIONS.md`.
- Finish with targeted diff/stat review, protected-path audit, `risk-assessment.md`,
  `review-packet.md`, and `final-summary.md`. Leave state, progress, slice status, changed-files,
  handoff mechanics, and all git operations to the orchestrator.
