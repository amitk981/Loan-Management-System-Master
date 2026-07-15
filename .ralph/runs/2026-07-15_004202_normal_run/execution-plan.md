# Execution Plan

Selected slice: `008I3-security-legal-evidence-seam-and-race-closure`

## Outcome

Restore the source-defined app graph without changing the public security-package routes or their
retained business contracts. Cross-owner Stage-4 facts will be resolved only by a top-level process
coordinator; security modules will own security policy and accept immutable coordinator-issued facts
through narrow interfaces. Repeated security audit/version/workflow writes will use one redacting
recorder, preserving existing event shapes and attribution.

## Interface and lock design

1. Add a `processes.security_instrument_evidence` coordinator that may import approvals,
   legal-documents, and security-instruments. It resolves current sanction/checklist scope and exact
   legal evidence under one transaction before calling the security owner.
2. Add immutable evidence/scope contracts in `security_instruments` with coordinator-only issuance.
   Public route adapters call the coordinator. Direct security calls without a valid issued contract,
   and forged/missing/stale/cross-application facts, fail before mutation.
3. Document and test the lock order: application/package, retained security instrument, legal
   document/checklist evidence. The coordinator supplies authority; security policy still decides
   applicability, maker-checker separation, custody, pledge, and terminal transitions.
4. Add one internal security evidence recorder that redacts sensitive fields and records audit,
   version, and optional workflow evidence with actor role/team and request/network attribution.

## TDD tracer cycles

1. RED: strengthen AST dependency tests for both permitted directions and removal of the legal PoA
   compatibility module; add coordinator-interface denial tests for missing/forged/stale/cross-app
   PoA facts. GREEN: install coordinator/contracts and migrate PoA route/callers.
2. RED: add equivalent SH-4 and CDSL bypass/rollback tests. GREEN: migrate their legal/checklist and
   approval fact reads/projections behind the coordinator while preserving all route responses.
3. RED: add recorder redaction/attribution/event-shape tests. GREEN: deepen package, PoA, SH-4, and
   CDSL ledger recording behind the shared internal interface.
4. RED/GREEN: strengthen PostgreSQL PoA, tri-party, SH-4, and CDSL changed-payload races to assert one
   material terminal winner, zero loser success evidence, and exact request/actor/audit/version/
   workflow identities; keep exact replay tests separate and execute the race set twice.

## Verification and evidence

- Save every focused RED and GREEN command under `evidence/terminal-logs/` using the mandated Ralph
  Python interpreter.
- Run focused boundary/API suites, backend check, migration sync, full coverage suite, and frontend
  lint/typecheck/build/tests. Run the declared PostgreSQL race contract twice.
- Save an interface diagram and request/response/denial contract examples in the run evidence folder.
- Record changed files, risk assessment, review packet, final summary, and update slice/state/progress/
  handoff only after gates pass. Sharpen the next one or two Not Started slices using already-opened
  Epic 008 material.
