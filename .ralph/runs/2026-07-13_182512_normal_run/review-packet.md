# Review Packet: 2026-07-13_182512_normal_run

## Result

Success — ready for independent Ralph validation and orchestrator commit.

## Slice

`007G-general-meeting-evidence-for-special-cases`

## What Changed

- Added the source §15.8 General Meeting evidence model, immutable supersession chain, indexes and
  constraints, and a nullable case-cycle reference in migration `approvals.0015`.
- Added §25.11 POST validation/authorization, exact replay, audit/workflow evidence, and standard
  envelopes behind one approvals-owned module interface.
- Added the final-sanction missing/pending/rejected gate after canonical authority checks and
  exposed the exact frozen meeting record on collection/detail/action projections.
- Recorded A-085, updated API contracts/digest, and sharpened 007H/007I from the opened Epic 007
  requirements.

## Source Traceability (non-developer summary)

- The source says related Director/relative/committee-member borrowing needs General Meeting
  notice, minutes, resolution, and an outcome (`api-contracts.md` §25.11; `data-model.md` §15.8;
  M05-FR-012). The code stores all three existing document references and the bounded outcome in
  immutable history. Verified by
  `test_authorized_recorder_creates_approved_general_meeting_evidence`,
  `test_general_meeting_exact_replay_is_zero_write_and_changed_status_supersedes`, and the negative
  payload/document matrix.
- The source says COI-004 evidence is required before sanction while conflicted actors remain
  excluded (`auth-permissions.md` §17.2). The code checks the frozen 007E2 flag only after conflict
  and distinct authority, blocks missing/pending/rejected outcomes without inserting an action,
  and preserves `CONFLICTED_APPROVER_NOT_ALLOWED`. Verified by the final-gate, pending/rejected,
  conflict-precedence, and Exception Register zero-write tests.
- The sharpened slice says historical cycles must not follow later application evidence. The code
  freezes the consumed record on final approval and the applicable record on return. Verified by
  `test_latest_general_meeting_outcome_gates_and_is_frozen_on_the_case_cycle` and
  `test_returned_cycle_keeps_its_applicable_general_meeting_reference`.

## Validation

- Backend: Django check and migration sync pass; 664 tests pass with 19 expected PostgreSQL-only
  SQLite skips; total coverage 93% (floor 85%).
- Frontend: build, typecheck, lint, and all 208 tests pass.
- Targeted: 90 approval-routing tests and the three witness historical-migration tests pass.
- Hygiene: `git diff --check` passes; no debug instrumentation, protected paths, source docs, or
  dependencies changed; one migration only; diff remains within configured limits.

## Review Notes

- The generated migration initially depended on applications 0014, breaking a historical witness
  migration test that rolls applications back to 0011. The correct hypothesis was that the new
  schema needs only the existing LoanApplication table; pinning the dependency to the already-used
  0011 leaf fixed the exact repro and full suite without changing production schema semantics.
- No frontend work is expected in this backend-only slice; 007I owns the reachable UI and was
  sharpened with the exact backend contract.

## Recommended Next Action

Run independent validation, then execute `007H-credit-sanction-register`.
