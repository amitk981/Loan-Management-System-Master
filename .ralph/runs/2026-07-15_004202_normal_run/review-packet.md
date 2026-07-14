# Review Packet: 2026-07-15_004202_normal_run

## Result

Ready for independent validation.

## Slice

`008I3-security-legal-evidence-seam-and-race-closure`

## What changed

- Added one top-level process coordinator and immutable evidence-access contract for approval/legal/
  security composition; migrated all public views and PostgreSQL test callers.
- Removed executable approvals/legal imports from `security_instruments` and deleted the temporary
  legal PoA compatibility alias.
- Replaced four repeated ordinary evidence writers with one redacting security recorder.
- Added observed-versus-locked tri-party correction conflict detection and strengthened PoA,
  tri-party, SH-4, and CDSL winner/loser evidence assertions.
- Sharpened 008I4 and 008J to extend the corrected seams.

## Traceability for a non-developer

- Source codebase-design §36.2 says security instruments may depend on members, applications,
  documents, and audit, while legal documents may consume security. Code now enforces that direction
  with the process as the only cross-owner composer; test
  `test_source_dependency_graph_uses_only_top_level_cross_owner_process` verifies it.
- Source codebase-design §§9.3/28.1 says audit complexity belongs behind a deep interface and a
  forwarding shell adds no value. Code deletes the PoA alias and uses `record_security_evidence`;
  `test_security_evidence_recorder_redacts_sensitive_values_recursively` verifies mandatory
  redaction.
- Auth §§18-19 and Stage 4 §26.4 require object scope and maker-checker separation. The coordinator
  re-resolves owner facts and rejects forged access; existing PoA/SH-4/CDSL public matrices plus
  `test_top_level_process_rejects_caller_supplied_evidence_authority` verify this.
- API §28 requires the retained package/PoA/SH-4/CDSL routes and data-model §34 requires atomic
  evidence. Public focused suites remain green with unchanged routes/envelopes, and projection
  conflict tests prove rollback.
- Slice requirement 6 requires one material race winner and zero loser success evidence. The four
  security/legal concurrency classes passed twice on PostgreSQL with exact actor, request,
  audit/version, and retained workflow linkage.

## Validation evidence

- TDD RED/GREEN: `evidence/terminal-logs/008i3-{red,green}-*.log`
- Focused: `evidence/terminal-logs/008i3-focused-green-2.log` (39 passed)
- PostgreSQL: `evidence/terminal-logs/008i3-postgresql-races-run-{1,2}.log` (10 passed each)
- Backend: check and migrations clean; 832 tests passed; 92% coverage.
- Frontend: lint/typecheck/build clean; 293 tests passed.
- Interface/contract: `evidence/security-evidence-interface.md`

## Recommended next action

Run independent Ralph validation, then let the orchestrator commit/merge/push. Next eligible slice
is sharpened 008I4.
