# Review Packet: 2026-07-18_174430_normal_run

## Result
Complete pending independent orchestrator validation

## Slice
009H7-communications-dispatcher-interface-and-idempotency-closure

## What changed

- Added the source-shaped dispatcher `send` interface and one generic communications job identity
  used by generic Email/SMS HTTP and disbursement advice.
- Required and reconciled a bounded explicit `Idempotency-Key` against exact object, payload, and
  actor truth. Exact replay is zero-write; missing/changed/cross-actor/cross-object use fails.
- Added communications migration 0009 with preserved advice job history and generic provider
  evidence. H6 legacy-partial outboxes cannot backfill or attach.
- Made manual/no-provider delivery honestly non-accepting and retained Fake/configured acceptance.
- Removed the lazy disbursement-owner → process → disbursement cycle; views/tasks call top-level
  composition and business modules expose owner decisions only.

## Traceability

- Source `codebase-design.md` §40.1 says the communications module exposes
  `create_from_template`, idempotent `send`, and `retry_failed`; the dispatcher now exposes those
  methods and both generic/advice public tests traverse them.
- Source `integrations.md` §§20.3/21.1-21.2 says external email/SMS effects use explicit keys and
  duplicate identity is `communication_id`; tests
  `test_send_requires_key_and_exact_replay_is_zero_write` and
  `test_send_advice_requires_explicit_idempotency_key_before_writes` verify the missing/exact/
  changed/actor/object matrix.
- Source `integrations.md` §§10.2/10.5 and review finding 1 require genuine provider acceptance;
  `test_configured_fake_delivers_generic_job_once_and_default_manual_does_not` and
  `test_default_manual_mode_cannot_fabricate_provider_acceptance` prove default/manual cannot
  create sent truth.
- Source `codebase-design.md` §§36.1-36.2 says circular dependencies indicate a misplaced seam;
  `test_disbursement_owner_does_not_import_or_register_process_coordinator` proves the owner no
  longer imports/registers the coordinator.
- H6 requires legacy partial provenance remain outside current replay. Migration preservation,
  legacy replay, and all six retained migration tests pass.

## Verification

- RED: missing dispatcher `send`, generic missing-key/replay, advice missing-key, and import-cycle
  probes failed first; GREEN logs are retained beside them.
- Final focused runs: 57 generic/advice/job/migration tests and 11 persistence/H6 migration tests.
- PostgreSQL: all six five-caller queue/worker/generic races passed in two final executions.
- Backend: Django check, migration sync, and compileall green. Full backend coverage is delegated
  to Ralph's independent validator as required.
- Frontend: typecheck, lint, 331 tests, and production build green; no frontend files changed.
- Diff: within 30-file/2,000-line/one-migration limits; protected/source paths unchanged.

## Recommended next action

Run independent Ralph validation and commit, then execute 009H8 followed by 009I2.
